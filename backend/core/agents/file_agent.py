import os
import aiofiles
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import mimetypes

from .base_agent import BaseAgent
from models.message import Message, MessageType
from models.session import Session
from core.llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class FileAgent(BaseAgent):
    """Dosya işlemleri için uzmanlaşmış AI agent"""
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(
            llm_provider=llm_provider,
            name="FileAgent",
            description="Dosya okuma, yazma, düzenleme ve yönetimi konularında uzman AI asistanı"
        )
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {
            '.txt', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml',
            '.md', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf',
            '.sh', '.bat', '.sql', '.csv', '.log'
        }
    
    async def process_message(self, session: Session, message: Message) -> List[Message]:
        """Dosya ile ilgili mesajları işle"""
        try:
            content = message.content
            provider = message.metadata.get('provider') if message.metadata else None
            responses = []
            
            # Dosya okuma isteği
            if self._is_read_request(content):
                file_path = self._extract_file_path(content)
                if file_path:
                    read_response = await self._read_file(session, file_path)
                    responses.append(read_response)
                else:
                    responses.append(self.create_error_message("Dosya yolu belirtilmedi"))
            
            # Dosya yazma isteği
            elif self._is_write_request(content):
                write_response = await self._handle_write_request(session, content)
                responses.append(write_response)
            
            # Dosya listesi isteği
            elif self._is_list_request(content):
                list_response = await self._list_files(session, content)
                responses.append(list_response)
            
            # Genel dosya sorusu
            else:
                general_response = await self._handle_general_file_question(session, content, provider)
                responses.append(general_response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Error in FileAgent.process_message: {e}")
            return [self.create_error_message(str(e))]
    
    def _is_read_request(self, content: str) -> bool:
        """Dosya okuma isteği mi kontrol et"""
        read_keywords = [
            "oku", "read", "open", "show", "display", "görüntüle", 
            "içeriği", "content", "dosyayı aç"
        ]
        return any(keyword in content.lower() for keyword in read_keywords)
    
    def _is_write_request(self, content: str) -> bool:
        """Dosya yazma isteği mi kontrol et"""
        write_keywords = [
            "yaz", "write", "save", "kaydet", "create", "oluştur",
            "dosya oluştur", "create file"
        ]
        return any(keyword in content.lower() for keyword in write_keywords)
    
    def _is_list_request(self, content: str) -> bool:
        """Dosya listesi isteği mi kontrol et"""
        list_keywords = [
            "list", "listele", "ls", "dir", "dosyalar", "files",
            "klasör", "directory", "dizin"
        ]
        return any(keyword in content.lower() for keyword in list_keywords)
    
    def _extract_file_path(self, content: str) -> Optional[str]:
        """İçerikten dosya yolunu çıkar"""
        import re
        
        # Backtick içindeki yolları ara
        backtick_pattern = r'`([^`]+)`'
        matches = re.findall(backtick_pattern, content)
        for match in matches:
            if '.' in match or '/' in match:
                return match.strip()
        
        # Dosya uzantılı kelimeleri ara
        words = content.split()
        for word in words:
            if any(word.endswith(ext) for ext in self.allowed_extensions):
                return word.strip()
        
        return None
    
    async def _read_file(self, session: Session, file_path: str) -> Message:
        """Dosyayı oku"""
        try:
            # Güvenlik kontrolü
            safe_path = self._get_safe_path(session, file_path)
            if not safe_path:
                return self.create_error_message("Geçersiz dosya yolu")
            
            # Dosya var mı kontrol et
            if not os.path.exists(safe_path):
                return self.create_error_message(f"Dosya bulunamadı: {file_path}")
            
            # Dosya boyutu kontrolü
            file_size = os.path.getsize(safe_path)
            if file_size > self.max_file_size:
                return self.create_error_message(
                    f"Dosya çok büyük ({file_size} bytes). Maksimum {self.max_file_size} bytes."
                )
            
            # Dosyayı oku
            async with aiofiles.open(safe_path, 'r', encoding='utf-8', errors='replace') as f:
                content = await f.read()
            
            # MIME type'ı tespit et
            mime_type, _ = mimetypes.guess_type(safe_path)
            
            return self.create_message(
                content=f"Dosya içeriği: `{file_path}`\n\n```\n{content}\n```",
                metadata={
                    "action": "file_read",
                    "file_path": file_path,
                    "file_size": file_size,
                    "mime_type": mime_type
                }
            )
            
        except Exception as e:
            logger.error(f"Error reading file '{file_path}': {e}")
            return self.create_error_message(f"Dosya okuma hatası: {str(e)}")
    
    async def _handle_write_request(self, session: Session, content: str) -> Message:
        """Dosya yazma isteğini işle"""
        try:
            # LLM'den dosya yazma planı al
            system_prompt = """Sen bir dosya yönetimi uzmanısın.
            Kullanıcının isteğine göre dosya yazma işlemini planla.
            
            Eğer kullanıcı:
            1. Dosya adı ve içerik belirtmişse, dosyayı oluştur
            2. Sadece dosya adı belirtmişse, boş dosya oluştur
            3. İçerik belirtip dosya adı belirtmemişse, uygun dosya adı öner
            
            Yanıtında dosya adı ve içeriği net şekilde belirt."""
            
            response = await self.generate_response(session, content, system_prompt)
            
            # TODO: LLM yanıtından dosya adı ve içeriği çıkar ve dosyayı oluştur
            
            return self.create_message(
                content=response,
                metadata={"action": "file_write_plan", "type": "planning"}
            )
            
        except Exception as e:
            logger.error(f"Error handling write request: {e}")
            return self.create_error_message(f"Dosya yazma hatası: {str(e)}")
    
    async def _list_files(self, session: Session, content: str) -> Message:
        """Dosyaları listele"""
        try:
            # Çalışma dizinini al
            workspace_path = session.get_context("workspace_path", "/workspace")
            
            # Dizin var mı kontrol et
            if not os.path.exists(workspace_path):
                os.makedirs(workspace_path, exist_ok=True)
            
            # Dosyaları listele
            files = []
            for item in os.listdir(workspace_path):
                item_path = os.path.join(workspace_path, item)
                is_dir = os.path.isdir(item_path)
                size = os.path.getsize(item_path) if not is_dir else 0
                
                files.append({
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "size": size,
                    "path": item_path
                })
            
            # Sonuçları formatla
            file_list = []
            for file_info in sorted(files, key=lambda x: (x["type"], x["name"])):
                if file_info["type"] == "directory":
                    file_list.append(f"📁 {file_info['name']}/")
                else:
                    size_str = self._format_file_size(file_info["size"])
                    file_list.append(f"📄 {file_info['name']} ({size_str})")
            
            content_text = f"Dosyalar ({workspace_path}):\n\n" + "\n".join(file_list)
            
            return self.create_message(
                content=content_text,
                metadata={
                    "action": "file_list",
                    "directory": workspace_path,
                    "file_count": len([f for f in files if f["type"] == "file"]),
                    "directory_count": len([f for f in files if f["type"] == "directory"])
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return self.create_error_message(f"Dosya listeleme hatası: {str(e)}")
    
    def _get_safe_path(self, session: Session, file_path: str) -> Optional[str]:
        """Güvenli dosya yolu oluştur"""
        try:
            workspace_path = session.get_context("workspace_path", "/workspace")
            
            # Relative path ise workspace'e göre ayarla
            if not os.path.isabs(file_path):
                full_path = os.path.join(workspace_path, file_path)
            else:
                full_path = file_path
            
            # Path traversal saldırılarını önle
            full_path = os.path.normpath(full_path)
            if not full_path.startswith(workspace_path):
                return None
            
            return full_path
            
        except Exception:
            return None
    
    def _format_file_size(self, size: int) -> str:
        """Dosya boyutunu okunabilir formatta döndür"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    async def _handle_general_file_question(self, session: Session, content: str, provider: Optional[str] = None) -> Message:
        """Genel dosya sorularını yanıtla"""
        system_prompt = """Sen bir dosya sistemi uzmanısın.
        Dosya yönetimi, dosya formatları ve dosya işlemleri konularında sorulara yanıt ver.
        
        Yanıtlarında:
        1. Konuyu net şekilde açıkla
        2. Örnek komutlar ver
        3. Best practices'i belirt
        4. Güvenlik uyarıları yap
        
        Türkçe yanıt ver ve teknik terimleri açıkla."""
        
        response = await self.generate_response(session, content, system_prompt, provider)
        
        return self.create_message(content=response)