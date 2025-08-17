"""
User model for authentication and user management
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseModel):
    """User model"""
    id: Optional[str] = None
    github_id: Optional[int] = None
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    credits: float = 10.0  # Initial $10 credit
    total_credits_used: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    github_access_token: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "github_id": self.github_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "role": self.role.value,
            "status": self.status.value,
            "credits": self.credits,
            "total_credits_used": self.total_credits_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def has_credits(self, amount: float) -> bool:
        """Check if user has enough credits"""
        return self.credits >= amount
    
    def deduct_credits(self, amount: float) -> bool:
        """Deduct credits from user account"""
        if self.has_credits(amount):
            self.credits -= amount
            self.total_credits_used += amount
            return True
        return False
    
    def add_credits(self, amount: float):
        """Add credits to user account"""
        self.credits += amount

class UserCreate(BaseModel):
    """User creation model"""
    github_id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    github_access_token: Optional[str] = None

class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    credits: Optional[float] = None

class CreditTransaction(BaseModel):
    """Credit transaction model"""
    id: Optional[str] = None
    user_id: str
    amount: float
    transaction_type: str  # "debit", "credit", "purchase"
    description: str
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "description": self.description,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }