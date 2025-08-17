import asyncio
import subprocess
import os
import logging
from typing import List, Dict, Any, Optional
import shlex

from .base_agent import BaseAgent
from models.message import Message, MessageType
from models.session import Session
from core.llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class TerminalAgent(BaseAgent):
    """Terminal komutları çalıştırmak için uzmanlaşmış AI agent"""
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(
            llm_provider=llm_provider,
            name="TerminalAgent",
            description="Terminal komutları çalıştırma ve sistem yönetimi konularında uzman AI asistanı"
        )
        self.allowed_commands = {
            "ls", "pwd", "cat", "echo", "grep", "find", "head", "tail",
            "python", "python3", "pip", "npm", "node", "git", "curl",
            "mkdir", "touch", "cp", "mv", "rm", "chmod", "chown"
        }
        self.dangerous_commands = {
            "rm -rf", "sudo", "su", "passwd", "shutdown", "reboot",
            "mkfs", "fdisk", "dd", "format"
        }
    
    async def process_message(self, session: Session, message: Message) -> List[Message]:
        """Terminal ile ilgili mesajları işle"""
        try:
            content = message.content
            provider = message.metadata.get('provider') if message.metadata else None
            responses = []
            
            # Komut çalıştırma isteği mi kontrol et
            if self._is_command_request(content):
                command = self._extract_command(content)
                if command:
                    execution_response = await self._execute_command(session, command)
                    responses.append(execution_response)
                else:
                    # LLM'den komut önerisi al
                    suggestion_response = await self._suggest_command(session, content, provider)
                    responses.append(suggestion_response)
            else:
                # Genel terminal sorusu
                general_response = await self._handle_general_terminal_question(session, content, provider)
                responses.append(general_response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Error in TerminalAgent.process_message: {e}")
            return [self.create_error_message(str(e))]
    
    def _is_command_request(self, content: str) -> bool:
        """İçerikte komut çalıştırma isteği var mı kontrol et"""
        command_keywords = [
            "run", "execute", "çalıştır", "komut", "command", "terminal",
            "bash", "shell", "script"
        ]
        return any(keyword in content.lower() for keyword in command_keywords)
    
    def _extract_command(self, content: str) -> Optional[str]:
        """İçerikten komutu çıkar"""
        # Backtick içindeki komutları ara
        import re
        backtick_pattern = r'`([^`]+)`'
        matches = re.findall(backtick_pattern, content)
        if matches:
            return matches[0].strip()
        
        # "run" veya "execute" kelimesinden sonraki kısmı al
        patterns = [
            r'(?:run|execute|çalıştır)\s+(.+)',
            r'komut[:\s]+(.+)',
            r'command[:\s]+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    async def _execute_command(self, session: Session, command: str) -> Message:
        """Komutu güvenli şekilde çalıştır"""
        try:
            # Güvenlik kontrolü
            if not self._is_command_safe(command):
                return self.create_error_message(
                    f"Güvenlik nedeniyle bu komut çalıştırılamaz: {command}"
                )
            
            # Çalışma dizinini ayarla
            workspace_path = session.get_context("workspace_path", "/workspace")
            if not os.path.exists(workspace_path):
                os.makedirs(workspace_path, exist_ok=True)
            
            # Komutu çalıştır
            result = await self._run_command_safely(command, workspace_path)
            
            return self.create_message(
                content=f"Komut çalıştırıldı: `{command}`\n\n```\n{result['output']}\n```",
                metadata={
                    "action": "command_execution",
                    "command": command,
                    "exit_code": result["exit_code"],
                    "execution_time": result.get("execution_time", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return self.create_error_message(f"Komut çalıştırılırken hata: {str(e)}")
    
    def _is_command_safe(self, command: str) -> bool:
        """Komutun güvenli olup olmadığını kontrol et"""
        command_lower = command.lower()
        
        # Tehlikeli komutları kontrol et
        for dangerous in self.dangerous_commands:
            if dangerous in command_lower:
                return False
        
        # İzin verilen komutları kontrol et
        first_word = command.split()[0] if command.split() else ""
        return first_word in self.allowed_commands or first_word.startswith("python")
    
    async def _run_command_safely(self, command: str, cwd: str) -> Dict[str, Any]:
        """Komutu güvenli ortamda çalıştır"""
        try:
            # Timeout ile komut çalıştır
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=cwd,
                env=os.environ.copy()
            )
            
            # 30 saniye timeout
            stdout, _ = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0
            )
            
            output = stdout.decode('utf-8', errors='replace')
            
            return {
                "output": output,
                "exit_code": process.returncode,
                "execution_time": 0  # TODO: Gerçek execution time hesapla
            }
            
        except asyncio.TimeoutError:
            return {
                "output": "Komut zaman aşımına uğradı (30 saniye)",
                "exit_code": -1,
                "execution_time": 30
            }
        except Exception as e:
            return {
                "output": f"Hata: {str(e)}",
                "exit_code": -1,
                "execution_time": 0
            }
    
    async def _suggest_command(self, session: Session, content: str, provider: Optional[str] = None) -> Message:
        """Kullanıcının isteğine göre komut öner"""
        system_prompt = """Sen bir terminal uzmanısın. 
        Kullanıcının isteğine göre uygun terminal komutlarını öner.
        
        Komut önerirken:
        1. Güvenli komutlar öner
        2. Komutun ne yaptığını açıkla
        3. Gerekirse alternatif komutlar ver
        4. Dikkat edilmesi gereken noktaları belirt
        
        Türkçe açıklama yap ve komutları backtick içinde ver."""
        
        response = await self.generate_response(session, content, system_prompt, provider)
        
        return self.create_message(
            content=response,
            metadata={"action": "command_suggestion", "type": "suggestion"}
        )
    
    async def _handle_general_terminal_question(self, session: Session, content: str, provider: Optional[str] = None) -> Message:
        """Genel terminal sorularını yanıtla"""
        system_prompt = """Sen deneyimli bir sistem yöneticisi ve terminal uzmanısın.
        Terminal, bash, shell scripting ve sistem yönetimi konularında sorulara yanıt ver.
        
        Yanıtlarında:
        1. Konuyu net şekilde açıkla
        2. Örnek komutlar ver
        3. Best practices'i belirt
        4. Güvenlik uyarıları yap
        
        Türkçe yanıt ver ve teknik terimleri açıkla."""
        
        response = await self.generate_response(session, content, system_prompt, provider)
        
        return self.create_message(content=response)