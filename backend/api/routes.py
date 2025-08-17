from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from models.message import Message, MessageType
from models.session import Session
from core.agent_manager import AgentManager
from core.session_manager import SessionManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Global managers (main.py'dan inject edilecek)
agent_manager: Optional[AgentManager] = None
session_manager: Optional[SessionManager] = None

def get_agent_manager() -> AgentManager:
    if not agent_manager:
        raise HTTPException(status_code=500, detail="Agent manager not initialized")
    return agent_manager

def get_session_manager() -> SessionManager:
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    return session_manager

@router.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.post("/sessions")
async def create_session(
    user_id: Optional[str] = None,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Yeni oturum oluştur"""
    try:
        import uuid
        session_id = str(uuid.uuid4())
        
        session = await session_mgr.create_session(session_id, user_id)
        
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Oturum bilgilerini getir"""
    try:
        session = await session_mgr.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "message_count": len(session.messages),
            "workspace_path": session.workspace_path
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Oturum mesajlarını getir"""
    try:
        session = await session_mgr.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = session.get_recent_messages(limit)
        
        return {
            "session_id": session_id,
            "messages": [msg.to_dict() for msg in messages],
            "total_count": len(session.messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    message_data: Dict[str, Any],
    session_mgr: SessionManager = Depends(get_session_manager),
    agent_mgr: AgentManager = Depends(get_agent_manager)
):
    """Oturuma mesaj gönder"""
    try:
        session = await session_mgr.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Mesaj oluştur
        message = Message(
            type=MessageType.USER,
            content=message_data.get("content", ""),
            timestamp=datetime.now(),
            metadata=message_data.get("metadata")
        )
        
        # Agent'a işlet
        responses = await agent_mgr.process_message(session, message)
        
        # Session'ı güncelle
        await session_mgr.update_session(session)
        
        return {
            "message_sent": message.to_dict(),
            "responses": [resp.to_dict() for resp in responses],
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Oturumu sil"""
    try:
        await session_mgr.delete_session(session_id)
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_agents(
    agent_mgr: AgentManager = Depends(get_agent_manager)
):
    """Kullanılabilir agent'ları listele"""
    try:
        agents = await agent_mgr.get_agent_status()
        return {
            "agents": agents,
            "available_agents": agent_mgr.get_available_agents()
        }
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/llm/providers")
async def get_llm_providers(
    agent_mgr: AgentManager = Depends(get_agent_manager)
):
    """LLM provider bilgilerini getir"""
    try:
        provider_info = agent_mgr.llm_provider.get_provider_info()
        available_providers = agent_mgr.llm_provider.get_available_providers()
        
        return {
            "providers": provider_info,
            "available": available_providers
        }
    except Exception as e:
        logger.error(f"Error getting LLM providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    session_mgr: SessionManager = Depends(get_session_manager),
    agent_mgr: AgentManager = Depends(get_agent_manager)
):
    """Sistem istatistiklerini getir"""
    try:
        session_count = await session_mgr.get_session_count()
        active_sessions = await session_mgr.get_active_sessions()
        
        return {
            "session_count": session_count,
            "active_sessions": len(active_sessions),
            "available_agents": len(agent_mgr.get_available_agents()),
            "available_llm_providers": len(agent_mgr.llm_provider.get_available_providers()),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))