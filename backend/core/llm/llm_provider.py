import os
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import openai
import anthropic
from datetime import datetime

from models.message import Message, MessageType

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """LLM provider'ların temel sınıfı"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None,
                              context_messages: Optional[List[Message]] = None) -> str:
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None,
                              context_messages: Optional[List[Message]] = None) -> str:
        try:
            messages = []
            
            # System prompt ekle
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Context mesajlarını ekle
            if context_messages:
                for msg in context_messages[-5:]:  # Son 5 mesaj
                    if msg.type == MessageType.USER:
                        messages.append({"role": "user", "content": msg.content})
                    elif msg.type == MessageType.ASSISTANT:
                        messages.append({"role": "assistant", "content": msg.content})
            
            # Ana prompt'u ekle
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek provider (OpenAI API uyumlu)"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None,
                              context_messages: Optional[List[Message]] = None) -> str:
        try:
            messages = []
            
            # System prompt ekle
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Context mesajlarını ekle
            if context_messages:
                for msg in context_messages[-5:]:  # Son 5 mesaj
                    if msg.type == MessageType.USER:
                        messages.append({"role": "user", "content": msg.content})
                    elif msg.type == MessageType.ASSISTANT:
                        messages.append({"role": "assistant", "content": msg.content})
            
            # Ana prompt'u ekle
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None,
                              context_messages: Optional[List[Message]] = None) -> str:
        try:
            messages = []
            
            # Context mesajlarını ekle
            if context_messages:
                for msg in context_messages[-5:]:  # Son 5 mesaj
                    if msg.type == MessageType.USER:
                        messages.append({"role": "user", "content": msg.content})
                    elif msg.type == MessageType.ASSISTANT:
                        messages.append({"role": "assistant", "content": msg.content})
            
            # Ana prompt'u ekle
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt or "Sen yardımcı bir AI asistanısın.",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

class LLMProvider:
    """LLM provider'ları yöneten ana sınıf"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Mevcut API key'lere göre provider'ları başlat"""
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers["openai"] = OpenAIProvider(
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", "gpt-4")
            )
            if not self.default_provider:
                self.default_provider = "openai"
        
        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.providers["anthropic"] = AnthropicProvider(
                api_key=anthropic_key,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            )
            if not self.default_provider:
                self.default_provider = "anthropic"
        
        # DeepSeek
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.providers["deepseek"] = DeepSeekProvider(
                api_key=deepseek_key,
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            )
            if not self.default_provider:
                self.default_provider = "deepseek"
        
        if not self.providers:
            logger.warning("No LLM providers configured. Please set API keys.")
        else:
            logger.info(f"Initialized LLM providers: {list(self.providers.keys())}")
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None,
                              context_messages: Optional[List[Message]] = None,
                              provider: Optional[str] = None) -> str:
        """LLM'den yanıt üret"""
        
        # Provider seç
        provider_name = provider or self.default_provider
        if not provider_name or provider_name not in self.providers:
            if not self.providers:
                return "LLM provider yapılandırılmamış. Lütfen API key'lerini ayarlayın."
            provider_name = list(self.providers.keys())[0]
        
        try:
            provider_instance = self.providers[provider_name]
            response = await provider_instance.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                context_messages=context_messages
            )
            
            logger.info(f"Generated response using {provider_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response with {provider_name}: {e}")
            
            # Fallback: Diğer provider'ları dene
            for fallback_name, fallback_provider in self.providers.items():
                if fallback_name != provider_name:
                    try:
                        response = await fallback_provider.generate_response(
                            prompt=prompt,
                            system_prompt=system_prompt,
                            context_messages=context_messages
                        )
                        logger.info(f"Generated response using fallback {fallback_name}")
                        return response
                    except Exception as fallback_error:
                        logger.error(f"Fallback {fallback_name} also failed: {fallback_error}")
            
            # Tüm provider'lar başarısız
            return f"LLM yanıt üretme hatası: {str(e)}"
    
    def get_available_providers(self) -> List[str]:
        """Kullanılabilir provider'ları döndür"""
        return list(self.providers.keys())
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Provider bilgilerini döndür"""
        info = {}
        for name, provider in self.providers.items():
            info[name] = {
                "model": getattr(provider, 'model', 'unknown'),
                "type": provider.__class__.__name__,
                "is_default": name == self.default_provider
            }
        return info