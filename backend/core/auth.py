"""
Authentication system with GitHub OAuth
"""

import os
import jwt
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User, UserCreate, UserRole
import logging

logger = logging.getLogger(__name__)

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Admin users (GitHub emails)
ADMIN_EMAILS = ["bodrunnet@gmail.com"]

security = HTTPBearer()

class AuthManager:
    """Authentication manager"""
    
    def __init__(self):
        self.users = {}  # In-memory user storage (will be replaced with database)
        
    async def exchange_github_code(self, code: str) -> Dict[str, Any]:
        """Exchange GitHub OAuth code for access token"""
        if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GitHub OAuth not configured"
            )
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange GitHub code"
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received from GitHub"
                )
            
            # Get user info from GitHub
            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from GitHub"
                )
            
            github_user = user_response.json()
            
            # Get user email (might be private)
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            primary_email = github_user.get("email")
            if not primary_email and email_response.status_code == 200:
                emails = email_response.json()
                for email_info in emails:
                    if email_info.get("primary", False):
                        primary_email = email_info.get("email")
                        break
            
            if not primary_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not get email from GitHub account"
                )
            
            return {
                "access_token": access_token,
                "github_user": github_user,
                "email": primary_email
            }
    
    async def create_or_update_user(self, github_data: Dict[str, Any]) -> User:
        """Create or update user from GitHub data"""
        github_user = github_data["github_user"]
        email = github_data["email"]
        access_token = github_data["access_token"]
        
        github_id = github_user["id"]
        username = github_user["login"]
        full_name = github_user.get("name")
        avatar_url = github_user.get("avatar_url")
        
        # Check if user exists
        existing_user = None
        for user in self.users.values():
            if user.github_id == github_id:
                existing_user = user
                break
        
        if existing_user:
            # Update existing user
            existing_user.username = username
            existing_user.email = email
            existing_user.full_name = full_name
            existing_user.avatar_url = avatar_url
            existing_user.github_access_token = access_token
            existing_user.last_login = datetime.now()
            existing_user.updated_at = datetime.now()
            return existing_user
        else:
            # Create new user
            user_create = UserCreate(
                github_id=github_id,
                username=username,
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
                github_access_token=access_token
            )
            
            user = User(
                id=f"user_{github_id}",
                github_id=user_create.github_id,
                username=user_create.username,
                email=user_create.email,
                full_name=user_create.full_name,
                avatar_url=user_create.avatar_url,
                role=UserRole.ADMIN if email in ADMIN_EMAILS else UserRole.USER,
                credits=10.0,  # Initial $10 credit
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_login=datetime.now(),
                github_access_token=user_create.github_access_token
            )
            
            self.users[user.id] = user
            logger.info(f"Created new user: {username} ({email}) - Role: {user.role}")
            return user
    
    def create_jwt_token(self, user: User) -> str:
        """Create JWT token for user"""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Get current authenticated user"""
        token = credentials.credentials
        payload = self.verify_jwt_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    async def require_admin(self, current_user: User = Depends(lambda: auth_manager.get_current_user)) -> User:
        """Require admin role"""
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    async def get_all_users(self) -> list[User]:
        """Get all users (admin only)"""
        return list(self.users.values())
    
    async def update_user_credits(self, user_id: str, amount: float, operation: str = "add") -> bool:
        """Update user credits"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        if operation == "add":
            user.add_credits(amount)
        elif operation == "deduct":
            if not user.deduct_credits(amount):
                return False
        
        user.updated_at = datetime.now()
        return True

# Global auth manager instance
auth_manager = AuthManager()

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user dependency"""
    return await auth_manager.get_current_user(credentials)

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user dependency"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Optional authentication (for public endpoints that can work with or without auth)
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return await auth_manager.get_current_user(credentials)
    except HTTPException:
        return None