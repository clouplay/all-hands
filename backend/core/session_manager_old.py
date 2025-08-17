import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import json

from models.session import Session
from models.message import Message

logger = logging.getLogger(__name__)

class SessionManager:
    """Kullanıcı oturumlarını yöneten sınıf"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        # In-memory storage for development
        self._messages: Dict[str, list] = {}
    
    def _initialize_storage(self):
        """Storage'ı başlat (in-memory for development)"""
        logger.info("In-memory storage initialized")
    
    async def create_session(self, session_id: str, user_id: Optional[str] = None) -> Session:
        """Yeni bir oturum oluştur"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[session_id] = session
        
        # Redis'e kaydet
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"session:{session_id}",
                    3600,  # 1 saat TTL
                    session.to_json()
                )
            except Exception as e:
                logger.error(f"Failed to save session to Redis: {e}")
        
        logger.info(f"Created new session: {session_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Oturum bilgilerini getir"""
        # Önce memory'den kontrol et
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_activity = datetime.now()
            return session
        
        # Redis'ten yükle
        if self.redis_client:
            try:
                session_data = await self.redis_client.get(f"session:{session_id}")
                if session_data:
                    session = Session.from_json(session_data)
                    session.last_activity = datetime.now()
                    self.sessions[session_id] = session
                    return session
            except Exception as e:
                logger.error(f"Failed to load session from Redis: {e}")
        
        return None
    
    async def update_session(self, session: Session):
        """Oturum bilgilerini güncelle"""
        session.last_activity = datetime.now()
        self.sessions[session.session_id] = session
        
        # Redis'e kaydet
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"session:{session.session_id}",
                    3600,
                    session.to_json()
                )
            except Exception as e:
                logger.error(f"Failed to update session in Redis: {e}")
    
    async def delete_session(self, session_id: str):
        """Oturumu sil"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        if self.redis_client:
            try:
                await self.redis_client.delete(f"session:{session_id}")
            except Exception as e:
                logger.error(f"Failed to delete session from Redis: {e}")
        
        logger.info(f"Deleted session: {session_id}")
    
    async def cleanup_expired_sessions(self):
        """Süresi dolmuş oturumları temizle"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > timedelta(hours=1):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.delete_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def get_active_sessions(self) -> Dict[str, Session]:
        """Aktif oturumları döndür"""
        return self.sessions.copy()
    
    async def get_session_count(self) -> int:
        """Toplam oturum sayısını döndür"""
        return len(self.sessions)