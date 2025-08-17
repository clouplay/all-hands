from typing import List, Dict, Any, Optional
import re
import ast
import logging

from .base_agent import BaseAgent
from models.message import Message, MessageType
from models.session import Session
from core.llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class CodeAgent(BaseAgent):
    """Kod yazma ve analiz etme konusunda uzmanlaşmış AI agent"""
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(
            llm_provider=llm_provider,
            name="CodeAgent",
            description="Kod yazma, analiz etme, refactoring ve debugging konularında uzman AI asistanı"
        )
    
    async def process_message(self, session: Session, message: Message) -> List[Message]:
        """Kod ile ilgili mesajları işle"""
        try:
            content = message.content
            responses = []
            
            # Kod analizi gerekli mi kontrol et
            if self._needs_code_analysis(content):
                analysis_response = await self._analyze_code(session, content)
                responses.append(analysis_response)
            
            # Kod üretimi gerekli mi kontrol et
            if self._needs_code_generation(content):
                generation_response = await self._generate_code(session, content)
                responses.append(generation_response)
            
            # Genel kod sorusu ise
            if not responses:
                general_response = await self._handle_general_code_question(session, content)
                responses.append(general_response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Error in CodeAgent.process_message: {e}")
            return [self.create_error_message(str(e))]
    
    def _needs_code_analysis(self, content: str) -> bool:
        """İçerikte kod analizi gerekip gerekmediğini kontrol et"""
        analysis_keywords = [
            "analiz", "analyze", "review", "check", "bug", "hata", 
            "problem", "optimize", "refactor", "improve"
        ]
        return any(keyword in content.lower() for keyword in analysis_keywords)
    
    def _needs_code_generation(self, content: str) -> bool:
        """İçerikte kod üretimi gerekip gerekmediğini kontrol et"""
        generation_keywords = [
            "yaz", "write", "create", "generate", "implement", 
            "build", "make", "develop", "code", "function", "class"
        ]
        return any(keyword in content.lower() for keyword in generation_keywords)
    
    async def _analyze_code(self, session: Session, content: str) -> Message:
        """Kod analizi yap"""
        system_prompt = """Sen bir uzman kod analisti ve code reviewer'sın.
        Verilen kodu analiz et ve şu konularda değerlendirme yap:
        1. Kod kalitesi ve best practices
        2. Potansiyel buglar ve güvenlik açıkları
        3. Performance iyileştirme önerileri
        4. Refactoring önerileri
        
        Analizi Türkçe yap ve yapıcı öneriler sun."""
        
        response = await self.generate_response(session, content, system_prompt)
        
        return self.create_message(
            content=response,
            metadata={"action": "code_analysis", "type": "analysis"}
        )
    
    async def _generate_code(self, session: Session, content: str) -> Message:
        """Kod üret"""
        system_prompt = """Sen uzman bir yazılım geliştiricisisin.
        Kullanıcının isteğine göre temiz, okunabilir ve best practices'e uygun kod yaz.
        
        Kod yazarken:
        1. Açıklayıcı değişken ve fonksiyon isimleri kullan
        2. Gerekli yerlerde yorum ekle
        3. Error handling ekle
        4. Type hints kullan (Python için)
        5. Modüler ve test edilebilir kod yaz
        
        Kodu markdown code block içinde ver ve Türkçe açıklama ekle."""
        
        response = await self.generate_response(session, content, system_prompt)
        
        # Kod bloklarını tespit et
        code_blocks = self._extract_code_blocks(response)
        
        return self.create_message(
            content=response,
            metadata={
                "action": "code_generation", 
                "type": "generation",
                "code_blocks": code_blocks
            }
        )
    
    async def _handle_general_code_question(self, session: Session, content: str) -> Message:
        """Genel kod sorularını yanıtla"""
        system_prompt = """Sen deneyimli bir yazılım geliştirici ve mentorsun.
        Programlama ile ilgili soruları net, anlaşılır ve öğretici şekilde yanıtla.
        
        Yanıtlarında:
        1. Konuyu açık şekilde açıkla
        2. Gerekirse örnek kod ver
        3. Best practices'i belirt
        4. Alternatif yaklaşımları göster
        
        Türkçe yanıt ver ve teknik terimleri açıkla."""
        
        response = await self.generate_response(session, content, system_prompt)
        
        return self.create_message(content=response)
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Metinden kod bloklarını çıkar"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for language, code in matches:
            code_blocks.append({
                "language": language or "text",
                "code": code.strip()
            })
        
        return code_blocks
    
    def _validate_python_syntax(self, code: str) -> Dict[str, Any]:
        """Python kod syntax'ını kontrol et"""
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False, 
                "error": f"Syntax error at line {e.lineno}: {e.msg}"
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}