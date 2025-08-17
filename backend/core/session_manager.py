import logging
from typing import Dict, Optional, List
from datetime import datetime
import uuid

from models.session import Session
from models.message import Message

logger = logging.getLogger(__name__)

class SessionManager:
    """Basit in-memory session manager"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self._messages: Dict[str, List[Message]] = {}
        logger.info("SessionManager initialized with in-memory storage")
    
    async def create_session(self, session_id: str = None, user_id: Optional[str] = None) -> Session:
        """Yeni bir oturum oluştur"""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            message_count=0
        )
        
        self.sessions[session_id] = session
        self._messages[session_id] = []
        
        logger.info(f"Session created: {session_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Oturum bilgilerini getir"""
        return self.sessions.get(session_id)
    
    async def update_session_activity(self, session_id: str):
        """Oturum aktivitesini güncelle"""
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.now()
    
    async def add_message(self, session_id: str, message: Message):
        """Oturuma mesaj ekle"""
        if session_id not in self._messages:
            self._messages[session_id] = []
        
        self._messages[session_id].append(message)
        
        # Session message count'u güncelle
        if session_id in self.sessions:
            self.sessions[session_id].message_count = len(self._messages[session_id])
            await self.update_session_activity(session_id)
    
    async def get_messages(self, session_id: str, limit: int = 50) -> List[Message]:
        """Oturum mesajlarını getir"""
        messages = self._messages.get(session_id, [])
        return messages[-limit:] if limit else messages
    
    async def delete_session(self, session_id: str) -> bool:
        """Oturumu sil"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self._messages:
                del self._messages[session_id]
            logger.info(f"Session deleted: {session_id}")
            return True
        return False
    
    async def get_all_sessions(self) -> List[Session]:
        """Tüm oturumları getir"""
        return list(self.sessions.values())
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Eski oturumları temizle"""
        current_time = datetime.now()
        sessions_to_delete = []
        
        for session_id, session in self.sessions.items():
            age = current_time - session.last_activity
            if age.total_seconds() > max_age_hours * 3600:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            await self.delete_session(session_id)
        
        if sessions_to_delete:
            logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions")