import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from models.message import Message, MessageType
from core.agent_manager import AgentManager
from core.session_manager import SessionManager

logger = logging.getLogger(__name__)

class WebSocketHandler:
    """WebSocket bağlantılarını yöneten sınıf"""
    
    def __init__(self, agent_manager: AgentManager, session_manager: SessionManager):
        self.agent_manager = agent_manager
        self.session_manager = session_manager
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}
    
    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """Yeni WebSocket bağlantısını işle"""
        await websocket.accept()
        
        # Bağlantıyı kaydet
        connection_id = f"{session_id}_{id(websocket)}"
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id}")
        
        try:
            # Oturum var mı kontrol et, yoksa oluştur
            session = await self.session_manager.get_session(session_id)
            if not session:
                session = await self.session_manager.create_session(session_id)
            
            # Hoş geldin mesajı gönder
            await self._send_message(websocket, {
                "type": "connection_established",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Aieditor'a hoş geldiniz! Size nasıl yardımcı olabilirim?"
            })
            
            # Mesaj döngüsü
            while True:
                data = await websocket.receive_text()
                await self._handle_message(websocket, session_id, data)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {connection_id}: {e}")
            await self._send_error(websocket, str(e))
        finally:
            # Bağlantıyı temizle
            await self._cleanup_connection(connection_id, session_id)
    
    async def _handle_message(self, websocket: WebSocket, session_id: str, data: str):
        """Gelen mesajı işle"""
        try:
            message_data = json.loads(data)
            message_type = message_data.get("type", "message")
            
            if message_type == "message":
                await self._handle_chat_message(websocket, session_id, message_data)
            elif message_type == "ping":
                await self._send_message(websocket, {"type": "pong"})
            elif message_type == "get_history":
                await self._send_message_history(websocket, session_id)
            else:
                await self._send_error(websocket, f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error(websocket, str(e))
    
    async def _handle_chat_message(self, websocket: WebSocket, session_id: str, message_data: Dict):
        """Chat mesajını işle"""
        try:
            # Session'ı al
            session = await self.session_manager.get_session(session_id)
            if not session:
                await self._send_error(websocket, "Session not found")
                return
            
            # Kullanıcı mesajını oluştur
            user_message = Message(
                type=MessageType.USER,
                content=message_data.get("content", ""),
                timestamp=datetime.now(),
                metadata=message_data.get("metadata")
            )
            
            # Mesajı gönderildi olarak işaretle
            await self._send_message(websocket, {
                "type": "message_received",
                "message": user_message.to_dict()
            })
            
            # Typing indicator gönder
            await self._send_message(websocket, {
                "type": "typing",
                "agent": "thinking..."
            })
            
            # Agent'a işlet
            responses = await self.agent_manager.process_message(session, user_message)
            
            # Typing indicator'ı durdur
            await self._send_message(websocket, {
                "type": "typing_stop"
            })
            
            # Yanıtları gönder
            for response in responses:
                await self._send_message(websocket, {
                    "type": "message",
                    "message": response.to_dict()
                })
            
            # Session'ı güncelle
            await self.session_manager.update_session(session_id)
            
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await self._send_error(websocket, f"Mesaj işlenirken hata: {str(e)}")
    
    async def _send_message_history(self, websocket: WebSocket, session_id: str):
        """Mesaj geçmişini gönder"""
        try:
            session = await self.session_manager.get_session(session_id)
            if not session:
                await self._send_error(websocket, "Session not found")
                return
            
            messages = session.get_recent_messages(50)
            
            await self._send_message(websocket, {
                "type": "message_history",
                "messages": [msg.to_dict() for msg in messages],
                "total_count": len(session.messages)
            })
            
        except Exception as e:
            logger.error(f"Error sending message history: {e}")
            await self._send_error(websocket, str(e))
    
    async def _send_message(self, websocket: WebSocket, data: Dict):
        """WebSocket üzerinden mesaj gönder"""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    async def _send_error(self, websocket: WebSocket, error: str):
        """Hata mesajı gönder"""
        await self._send_message(websocket, {
            "type": "error",
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _cleanup_connection(self, connection_id: str, session_id: str):
        """Bağlantıyı temizle"""
        # Active connections'dan kaldır
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Session connections'dan kaldır
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
    
    async def broadcast_to_session(self, session_id: str, data: Dict):
        """Bir session'daki tüm bağlantılara mesaj gönder"""
        if session_id not in self.session_connections:
            return
        
        connections_to_remove = []
        
        for connection_id in self.session_connections[session_id]:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await self._send_message(websocket, data)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    connections_to_remove.append(connection_id)
        
        # Başarısız bağlantıları temizle
        for connection_id in connections_to_remove:
            await self._cleanup_connection(connection_id, session_id)
    
    def get_active_connections_count(self) -> int:
        """Aktif bağlantı sayısını döndür"""
        return len(self.active_connections)
    
    def get_session_connections_count(self, session_id: str) -> int:
        """Belirli bir session'ın bağlantı sayısını döndür"""
        return len(self.session_connections.get(session_id, set()))