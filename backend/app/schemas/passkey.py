"""
Passkey Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PasskeyCredentialResponse(BaseModel):
    """凭证响应（不含敏感信息）"""
    id: int
    device_name: Optional[str]
    created_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


class PasskeyConfigResponse(BaseModel):
    """Passkey 配置响应"""
    enabled: bool
    require_for_roles: List[str]


class PasskeyLoginRequest(BaseModel):
    """Passkey 登录验证请求"""
    username: str
    credential_id: str
    options: str


class PasskeyLoginDiscoverableRequest(BaseModel):
    """Passkey 无用户名登录验证请求"""
    options: str


class PasskeyRegisterRequest(BaseModel):
    """Passkey 注册验证请求"""
    options: str
    device_name: Optional[str] = None


class ForcePasskeyRequest(BaseModel):
    """强制 Passkey 请求"""
    passkey_required: bool