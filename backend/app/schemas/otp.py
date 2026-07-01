"""
OTP Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class OTPConfigResponse(BaseModel):
    """OTP 配置响应"""
    enabled: bool
    required_for_roles: list[str] = []


class OTPStatusResponse(BaseModel):
    """OTP 状态响应"""
    enabled: bool
    verified: bool


class OTPSetupResponse(BaseModel):
    """OTP 设置响应"""
    secret: str = Field(..., description="OTP Secret，只在此时返回")
    otpauth_uri: str = Field(..., description="用于扫描的 otpauth URI")
    qr_code_base64: str = Field(..., description="QR 码 Base64 编码")


class OTPVerifyRequest(BaseModel):
    """OTP 验证请求"""
    code: str = Field(..., min_length=6, max_length=6, description="6 位验证码")


class OTPDisableRequest(BaseModel):
    """OTP 禁用请求"""
    code: str = Field(..., min_length=6, max_length=6, description="6 位验证码")


class OTPLoginVerifyRequest(BaseModel):
    """OTP 登录验证请求"""
    temp_token: str
    code: str = Field(..., min_length=6, max_length=6)


class TokenResponseWithOTP(BaseModel):
    """带 2FA 状态的登录响应"""
    access_token: Optional[str] = None
    temp_token: Optional[str] = None
    requires_otp: bool = False
    token_type: str = "bearer"