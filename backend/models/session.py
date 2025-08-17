from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .message import Message

class Session(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    messages: List[Message] = []
    context: Dict[str, Any] = {}
    workspace_path: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_message(self, message: Message):
        """Oturuma yeni mesaj ekle"""
        message.session_id = self.session_id
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Son N mesajı getir"""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages
    
    def get_context_messages(self, limit: int = 5) -> List[Message]:
        """AI için context olarak kullanılacak son mesajları getir"""
        return self.get_recent_messages(limit)
    
    def clear_messages(self):
        """Tüm mesajları temizle"""
        self.messages = []
        self.last_activity = datetime.now()
    
    def set_workspace(self, workspace_path: str):
        """Çalışma dizinini ayarla"""
        self.workspace_path = workspace_path
        self.context["workspace_path"] = workspace_path
    
    def update_context(self, key: str, value: Any):
        """Context bilgisini güncelle"""
        self.context[key] = value
        self.last_activity = datetime.now()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Context bilgisini getir"""
        return self.context.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Session'ı dictionary'ye çevir"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
            "context": self.context,
            "workspace_path": self.workspace_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Dictionary'den Session oluştur"""
        messages = [Message.from_dict(msg_data) for msg_data in data.get("messages", [])]
        
        return cls(
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            messages=messages,
            context=data.get("context", {}),
            workspace_path=data.get("workspace_path")
        )
    
    def to_json(self) -> str:
        """Session'ı JSON string'e çevir"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "Session":
        """JSON string'den Session oluştur"""
        data = json.loads(json_str)
        return cls.from_dict(data)