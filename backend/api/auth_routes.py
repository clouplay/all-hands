"""
Authentication API routes
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from core.auth import auth_manager, get_current_user, get_current_admin
from models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

class GitHubCallbackRequest(BaseModel):
    code: str

class AuthResponse(BaseModel):
    access_token: str
    user: dict
    message: str

@router.post("/github/callback", response_model=AuthResponse)
async def github_callback(request: GitHubCallbackRequest):
    """Handle GitHub OAuth callback"""
    try:
        # Exchange code for GitHub access token and user data
        github_data = await auth_manager.exchange_github_code(request.code)
        
        # Create or update user
        user = await auth_manager.create_or_update_user(github_data)
        
        # Create JWT token
        jwt_token = auth_manager.create_jwt_token(user)
        
        return AuthResponse(
            access_token=jwt_token,
            user=user.to_dict(),
            message=f"Welcome, {user.username}!"
        )
        
    except Exception as e:
        logger.error(f"GitHub OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user": current_user.to_dict(),
        "message": "User information retrieved successfully"
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return {
        "message": "Logged out successfully"
    }

@router.get("/github/login-url")
async def get_github_login_url():
    """Get GitHub OAuth login URL"""
    import os
    
    client_id = os.getenv("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth not configured"
        )
    
    # In production, this should be your actual domain
    redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:12000/auth/github/callback")
    
    github_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=user:email"
        f"&state=random_state_string"
    )
    
    return {
        "login_url": github_url,
        "client_id": client_id
    }

# Admin routes
@router.get("/admin/users")
async def get_all_users(admin_user: User = Depends(get_current_admin)):
    """Get all users (admin only)"""
    users = await auth_manager.get_all_users()
    return {
        "users": [user.to_dict() for user in users],
        "total": len(users)
    }

@router.post("/admin/users/{user_id}/credits")
async def update_user_credits(
    user_id: str,
    amount: float,
    operation: str = "add",
    admin_user: User = Depends(get_current_admin)
):
    """Update user credits (admin only)"""
    success = await auth_manager.update_user_credits(user_id, amount, operation)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or insufficient credits"
        )
    
    return {
        "message": f"Credits {operation}ed successfully",
        "user_id": user_id,
        "amount": amount,
        "operation": operation
    }