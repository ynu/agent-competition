"""
2FA OTP (TOTP) 认证 API
"""
import pyotp
import qrcode
import io
import base64
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, create_access_token
from app.core.otp import encrypt_otp_secret, decrypt_otp_secret
from app.models.user import User
from app.models.setting import Setting, Log
from app.schemas.otp import (
    OTPConfigResponse, OTPStatusResponse, OTPSetupResponse,
    OTPVerifyRequest, OTPDisableRequest, OTPLoginVerifyRequest,
    TokenResponseWithOTP
)
from app.schemas.user import TokenResponse, UserResponse

router = APIRouter(prefix="/auth/otp", tags=["2FA OTP"])


def get_otp_config(db: Session) -> dict:
    """获取 OTP 配置"""
    enabled = db.query(Setting).filter(Setting.key == "totp_enabled").first()
    required_for_roles = db.query(Setting).filter(Setting.key == "totp_required_for_roles").first()
    return {
        "enabled": enabled.value.lower() == "true" if enabled and enabled.value else False,
        "required_for_roles": json.loads(required_for_roles.value) if required_for_roles and required_for_roles.value else []
    }


def get_base_url(db: Session) -> str:
    """获取应用基础URL"""
    from app.core.config import settings
    setting = db.query(Setting).filter(Setting.key == "base_url").first()
    return setting.value if setting and setting.value else settings.BASE_URL


def add_log(db: Session, user_id: int, action: str, resource: str = None,
            resource_id: int = None, details: str = None):
    """添加日志"""
    log = Log(user_id=user_id, action=action, resource=resource,
              resource_id=resource_id, details=details)
    db.add(log)
    db.commit()


@router.get("/config", response_model=OTPConfigResponse)
async def get_otp_config_endpoint(db: Session = Depends(get_db)):
    """获取 2FA 配置"""
    config = get_otp_config(db)
    return OTPConfigResponse(
        enabled=config["enabled"],
        required_for_roles=config["required_for_roles"]
    )


@router.get("/status", response_model=OTPStatusResponse)
async def get_otp_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户 2FA 状态"""
    return OTPStatusResponse(
        enabled=current_user.otp_enabled or False,
        verified=current_user.otp_verified or False
    )


@router.post("/setup", response_model=OTPSetupResponse)
async def setup_otp(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """开始 2FA 绑定流程"""
    if not get_otp_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="2FA 功能未启用")

    if current_user.otp_enabled and current_user.otp_verified:
        raise HTTPException(status_code=400, detail="2FA 已启用，如需更换设备请先禁用")

    # 生成新的 secret
    secret = pyotp.random_base32()

    # 生成 otpauth URI
    issuer = "智能体大赛"
    account_name = current_user.username
    totp = pyotp.TOTP(secret)
    otpauth_uri = totp.provisioning_uri(name=account_name, issuer_name=issuer)

    # 生成 QR 码
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(otpauth_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    # 加密存储 secret（临时，未验证）
    encrypted_secret = encrypt_otp_secret(secret)
    current_user.otp_secret_encrypted = encrypted_secret
    current_user.otp_verified = False
    db.commit()

    return OTPSetupResponse(
        secret=secret,
        otpauth_uri=otpauth_uri,
        qr_code_base64=qr_code_base64
    )


@router.post("/verify-setup")
async def verify_setup(
    request: OTPVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证 OTP 完成绑定"""
    if not current_user.otp_secret_encrypted:
        raise HTTPException(status_code=400, detail="请先获取 OTP Secret")

    try:
        secret = decrypt_otp_secret(current_user.otp_secret_encrypted)
        totp = pyotp.TOTP(secret)

        if not totp.verify(request.code):
            raise HTTPException(status_code=400, detail="验证码错误")

        current_user.otp_enabled = True
        current_user.otp_verified = True
        db.commit()

        add_log(db, current_user.id, "enable_otp", "otp",
                details=f"用户 {current_user.username} 启用 2FA")

        return {"message": "2FA 已启用"}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail=f"验证失败: {str(e)}")


@router.post("/disable")
async def disable_otp(
    request: OTPDisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """禁用 2FA"""
    if not current_user.otp_enabled:
        raise HTTPException(status_code=400, detail="2FA 未启用")

    try:
        secret = decrypt_otp_secret(current_user.otp_secret_encrypted)
        totp = pyotp.TOTP(secret)

        if not totp.verify(request.code):
            raise HTTPException(status_code=400, detail="验证码错误")

        current_user.otp_enabled = False
        current_user.otp_verified = False
        current_user.otp_secret_encrypted = None
        db.commit()

        add_log(db, current_user.id, "disable_otp", "otp",
                details=f"用户 {current_user.username} 禁用 2FA")

        return {"message": "2FA 已禁用"}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail=f"验证失败: {str(e)}")