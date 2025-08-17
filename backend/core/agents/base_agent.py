from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from models.message import Message, MessageType
from models.session import Session
from core.llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Tüm AI agent'ların temel sınıfı"""
    
    def __init__(self, llm_provider: LLMProvider, name: str, description: str):
        self.llm_provider = llm_provider
        self.name = name
        self.description = description
        self.last_used = None
    
    @abstractmethod
    async def process_message(self, session: Session, message: Message) -> List[Message]:
        """Gelen mesajı işle ve yanıt üret"""
        pass
    
    async def generate_response(self, session: Session, prompt: str, system_prompt: Optional[str] = None) -> str:
        """LLM'den yanıt üret"""
        try:
            # Context mesajlarını hazırla
            context_messages = session.get_context_messages()
            
            # System prompt'u hazırla
            if not system_prompt:
                system_prompt = self._get_default_system_prompt()
            
            # LLM'den yanıt al
            response = await self.llm_provider.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                context_messages=context_messages
            )
            
            self.last_used = datetime.now()
            return response
            
        except Exception as e:
            logger.error(f"Error generating response in {self.name}: {e}")
            return f"Yanıt üretilirken hata oluştu: {str(e)}"
    
    def _get_default_system_prompt(self) -> str:
        """Varsayılan system prompt'u döndür"""
        return f"""Sen {self.name} adında bir AI asistanısın. 
        Görevin: {self.description}
        
        Kullanıcıya yardımcı ol ve net, anlaşılır yanıtlar ver.
        Türkçe yanıt ver ve profesyonel bir dil kullan."""
    
    def create_message(self, content: str, message_type: MessageType = MessageType.ASSISTANT, 
                      metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Yeni bir mesaj oluştur"""
        return Message(
            type=message_type,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata,
            agent_name=self.name
        )
    
    def create_error_message(self, error: str) -> Message:
        """Hata mesajı oluştur"""
        return self.create_message(
            content=f"Hata: {error}",
            message_type=MessageType.ERROR
        )
    
    def create_action_message(self, action: str, details: Optional[Dict[str, Any]] = None) -> Message:
        """Aksiyon mesajı oluştur"""
        return self.create_message(
            content=action,
            message_type=MessageType.ACTION,
            metadata=details
        )
    
    def create_result_message(self, result: str, details: Optional[Dict[str, Any]] = None) -> Message:
        """Sonuç mesajı oluştur"""
        return self.create_message(
            content=result,
            message_type=MessageType.RESULT,
            metadata=details
        )