import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .agents.base_agent import BaseAgent
from .agents.code_agent import CodeAgent
from .agents.terminal_agent import TerminalAgent
from .agents.file_agent import FileAgent
from .llm.llm_provider import LLMProvider
from models.message import Message, MessageType
from models.session import Session

logger = logging.getLogger(__name__)

class AgentManager:
    """AI Agent'larını yöneten merkezi sınıf"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_provider = LLMProvider()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Temel agent'ları başlat"""
        self.agents = {
            "code": CodeAgent(self.llm_provider),
            "terminal": TerminalAgent(self.llm_provider),
            "file": FileAgent(self.llm_provider)
        }
        logger.info(f"Initialized {len(self.agents)} agents")
    
    async def process_message(self, session: Session, message: Message) -> List[Message]:
        """Gelen mesajı uygun agent'a yönlendir ve yanıt üret"""
        try:
            # Mesaj tipine göre agent seç
            agent = self._select_agent(message)
            
            if not agent:
                return [Message(
                    type=MessageType.ERROR,
                    content="Uygun agent bulunamadı",
                    timestamp=datetime.now()
                )]
            
            # Agent'a mesajı işlet
            responses = await agent.process_message(session, message)
            
            # Session'a mesajları ekle
            session.add_message(message)
            for response in responses:
                session.add_message(response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return [Message(
                type=MessageType.ERROR,
                content=f"Mesaj işlenirken hata oluştu: {str(e)}",
                timestamp=datetime.now()
            )]
    
    def _select_agent(self, message: Message) -> Optional[BaseAgent]:
        """Mesaj içeriğine göre uygun agent'ı seç"""
        content = message.content.lower()
        
        # Terminal komutları
        if any(cmd in content for cmd in ["run", "execute", "terminal", "command", "bash", "shell"]):
            return self.agents.get("terminal")
        
        # Dosya işlemleri
        if any(word in content for word in ["file", "read", "write", "save", "open", "create", "delete"]):
            return self.agents.get("file")
        
        # Varsayılan olarak kod agent'ı
        return self.agents.get("code")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Tüm agent'ların durumunu döndür"""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "name": agent.name,
                "description": agent.description,
                "active": True,
                "last_used": getattr(agent, 'last_used', None)
            }
        return status
    
    def get_available_agents(self) -> List[str]:
        """Kullanılabilir agent'ların listesini döndür"""
        return list(self.agents.keys())