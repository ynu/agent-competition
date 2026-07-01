"""
用户 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


# 用户基础 schema
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None


# 创建用户 schema
class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=6)
    role: UserRole = UserRole.USER


# 更新用户 schema
class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# 用户响应 schema
class UserResponse(UserBase):
    id: int
    role: UserRole
    auth_source: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 登录请求 schema
class LoginRequest(BaseModel):
    username: str
    password: str
    turnstile_token: Optional[str] = Field(None, description="Cloudflare Turnstile verification token")


# 统一身份认证登录请求
class UnifiedAuthLoginRequest(BaseModel):
    code: Optional[str] = Field(None, description="统一身份认证返回的授权码(可选，不填时自动创建用户)")


# Token 响应 schema
class TokenResponse(BaseModel):
    access_token: Optional[str] = None
    temp_token: Optional[str] = None
    requires_otp: bool = False
    token_type: str = "bearer"
    user: Optional[UserResponse] = None