"""
Passkey (通行密钥) 认证 API
"""
import json
import secrets
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json
)
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.structs import PublicKeyCredentialDescriptor, AuthenticatorTransport, UserVerificationRequirement, ResidentKeyRequirement, AuthenticatorSelectionCriteria
from app.core.database import get_db
from app.core.security import get_current_user, create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.passkey import UserPasskey
from app.models.setting import Setting, Log
from app.schemas.passkey import (
    PasskeyConfigResponse, PasskeyCredentialResponse, PasskeyLoginRequest,
    PasskeyRegisterRequest, PasskeyLoginDiscoverableRequest
)
from app.schemas.user import TokenResponse, UserResponse

router = APIRouter(prefix="/auth/passkey", tags=["Passkey 认证"])
management_router = APIRouter(prefix="/passkey", tags=["Passkey 管理"])

# 存储中的 challenge（生产环境应使用 Redis）
_challenge_store = {}


def get_passkey_config(db: Session) -> dict:
    """获取 Passkey 配置"""
    enabled = db.query(Setting).filter(Setting.key == "passkey_enabled").first()
    require_for_roles = db.query(Setting).filter(Setting.key == "passkey_require_for_roles").first()
    return {
        "enabled": enabled.value.lower() == "true" if enabled else False,
        "require_for_roles": json.loads(require_for_roles.value) if require_for_roles and require_for_roles.value else []
    }


def get_base_url(db: Session) -> str:
    """获取应用基础URL"""
    setting = db.query(Setting).filter(Setting.key == "base_url").first()
    return setting.value if setting and setting.value else settings.BASE_URL


def get_rp_id(db: Session) -> str:
    """获取 RP ID（域名）"""
    base_url = get_base_url(db)
    from urllib.parse import urlparse
    netloc = urlparse(base_url).netloc
    # 移除端口号，WebAuthn 要求 rp_id 只能是域名
    if ':' in netloc:
        netloc = netloc.split(':')[0]
    return netloc or "localhost"


def add_log(db: Session, user_id: int, action: str, resource: str = None,
            resource_id: int = None, details: str = None):
    """添加日志"""
    log = Log(user_id=user_id, action=action, resource=resource,
              resource_id=resource_id, details=details)
    db.add(log)
    db.commit()


# ============== 认证 API ==============

@router.get("/config", response_model=PasskeyConfigResponse)
async def get_passkey_config_endpoint(db: Session = Depends(get_db)):
    """获取 Passkey 配置（是否启用）"""
    config = get_passkey_config(db)
    return PasskeyConfigResponse(
        enabled=config["enabled"],
        require_for_roles=config["require_for_roles"]
    )


@router.get("/register-options")
async def get_register_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 Passkey 注册选项"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    rp_id = get_rp_id(db)

    # 获取用户已有的凭证 ID（用于排除）
    existing_credentials = db.query(UserPasskey).filter(
        UserPasskey.user_id == current_user.id
    ).all()
    exclude_credentials = [
        PublicKeyCredentialDescriptor(id=base64url_decode(cred.credential_id))
        for cred in existing_credentials
    ]

    # 生成 challenge - 使用 token_bytes 得到原始字节，避免 base64url 双重编码问题
    challenge_bytes = secrets.token_bytes(32)
    _challenge_store[f"register_{current_user.id}"] = challenge_bytes  # 存储原始字节

    options = generate_registration_options(
        rp_id=rp_id,
        rp_name="智能体大赛",
        user_id=str(current_user.id).encode('utf-8'),
        user_name=current_user.username,
        user_display_name=current_user.nickname or current_user.username,
        exclude_credentials=exclude_credentials,
        timeout=60000,
        challenge=challenge_bytes,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED
        )
    )

    return {
        "options": options_to_json(options),
        "challenge": bytes_to_base64url(challenge_bytes)  # 返回 base64url 编码的 challenge
    }


@router.post("/register-verify")
async def verify_registration(
    request: PasskeyRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证 Passkey 注册响应"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    # 验证 challenge
    stored_challenge = _challenge_store.pop(f"register_{current_user.id}", None)
    if not stored_challenge:
        raise HTTPException(status_code=400, detail="注册会话已过期，请重新开始")

    rp_id = get_rp_id(db)
    base_url = get_base_url(db)

    try:
        verification = verify_registration_response(
            credential=request.options,
            expected_rp_id=rp_id,
            expected_origin=base_url,
            expected_challenge=stored_challenge  # challenge_bytes 直接使用，不需要编码
        )

        # 保存凭证
        from webauthn.helpers import bytes_to_base64url
        import json
        passkey = UserPasskey(
            user_id=current_user.id,
            credential_id=bytes_to_base64url(verification.credential_id),  # 存储为 base64url 字符串
            public_key=json.dumps(bytes(verification.credential_public_key).hex()),  # 存储为十六进制字符串
            counter=0,
            device_name=request.device_name or f"Passkey {current_user.id}_{len(current_user.passkeys) + 1}"
        )
        db.add(passkey)
        db.commit()

        add_log(db, current_user.id, "register_passkey", "passkey",
                details=f"注册 Passkey: {passkey.device_name}")

        return {"message": "Passkey 注册成功"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"注册验证失败: {str(e)}")


def base64url_decode(data: str) -> bytes:
    """将 base64url 字符串解码为字节"""
    if not data:
        return b""
    # 添加 padding
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    # 替换字符
    data = data.replace("-", "+").replace("_", "/")
    import base64
    return base64.b64decode(data)


@router.post("/login-options")
async def get_login_options(
    request: dict,
    db: Session = Depends(get_db)
):
    """获取 Passkey 登录选项"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    username = request.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="需要提供用户名")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户的凭证
    credentials = db.query(UserPasskey).filter(
        UserPasskey.user_id == user.id
    ).all()

    if not credentials:
        raise HTTPException(status_code=400, detail="该用户尚未注册 Passkey")

    rp_id = get_rp_id(db)

    # 生成 challenge - 使用 bytes，和注册流程保持一致
    challenge_bytes = secrets.token_bytes(32)
    _challenge_store[f"login_{username}"] = challenge_bytes

    options = generate_authentication_options(
        rp_id=rp_id,
        challenge=challenge_bytes,
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=base64url_decode(cred.credential_id), transports=[AuthenticatorTransport.INTERNAL, AuthenticatorTransport.HYBRID])
            for cred in credentials
        ],
        timeout=60000,
        user_verification=UserVerificationRequirement.PREFERRED
    )

    return {
        "options": options_to_json(options),
        "challenge": bytes_to_base64url(challenge_bytes),
        "username": username
    }


@router.post("/login-options-discoverable")
async def get_login_options_discoverable(
    db: Session = Depends(get_db)
):
    """获取无需用户名的登录选项（可发现凭证）"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    rp_id = get_rp_id(db)

    # 生成 challenge
    challenge_bytes = secrets.token_bytes(32)
    _challenge_store["login_discoverable"] = challenge_bytes

    options = generate_authentication_options(
        rp_id=rp_id,
        challenge=challenge_bytes,
        allow_credentials=[],  # 空数组表示不限制，允许任何已注册的凭证
        timeout=60000,
        user_verification=UserVerificationRequirement.PREFERRED
    )

    return {
        "options": options_to_json(options),
        "challenge": bytes_to_base64url(challenge_bytes)
    }


@router.post("/login-verify", response_model=TokenResponse)
async def verify_login(
    request: PasskeyLoginRequest,
    db: Session = Depends(get_db)
):
    """验证 Passkey 登录响应"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    username = request.username
    stored_challenge = _challenge_store.pop(f"login_{username}", None)
    if not stored_challenge:
        raise HTTPException(status_code=400, detail="登录会话已过期，请重新开始")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")

    # 获取用户的凭证
    passkey = db.query(UserPasskey).filter(
        UserPasskey.user_id == user.id,
        UserPasskey.credential_id == request.credential_id
    ).first()

    if not passkey:
        raise HTTPException(status_code=400, detail="凭证不匹配")

    rp_id = get_rp_id(db)

    try:
        import json
        # 将十六进制字符串转换回 bytes
        public_key_bytes = bytes.fromhex(json.loads(passkey.public_key))
        verification = verify_authentication_response(
            credential=request.options,
            expected_rp_id=rp_id,
            expected_origin=get_base_url(db),
            expected_challenge=stored_challenge,
            credential_public_key=public_key_bytes,
            credential_current_sign_count=passkey.counter
        )

        # 更新计数器
        passkey.counter = verification.new_sign_count
        passkey.last_used_at = datetime.utcnow()
        db.commit()

        # 创建 token
        access_token = create_access_token(data={"sub": str(user.id)})

        add_log(db, user.id, "login", "passkey",
                details=f"Passkey 登录: {user.username}")

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"登录验证失败: {str(e)}")


@router.post("/login-verify-discoverable", response_model=TokenResponse)
async def verify_login_discoverable(
    request: PasskeyLoginDiscoverableRequest,
    db: Session = Depends(get_db)
):
    """验证无需用户名的登录响应（可发现凭证）"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    stored_challenge = _challenge_store.pop("login_discoverable", None)
    if not stored_challenge:
        raise HTTPException(status_code=400, detail="登录会话已过期，请重新开始")

    try:
        options_dict = json.loads(request.options)
        credential_id = options_dict.get("id", "")

        # 通过 credential_id 查找用户
        passkey = db.query(UserPasskey).filter(
            UserPasskey.credential_id == credential_id
        ).first()

        if not passkey:
            raise HTTPException(status_code=400, detail="凭证不匹配")

        user = db.query(User).filter(User.id == passkey.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="用户已被禁用")

        rp_id = get_rp_id(db)

        import json as json_module
        public_key_bytes = bytes.fromhex(json_module.loads(passkey.public_key))
        verification = verify_authentication_response(
            credential=request.options,
            expected_rp_id=rp_id,
            expected_origin=get_base_url(db),
            expected_challenge=stored_challenge,
            credential_public_key=public_key_bytes,
            credential_current_sign_count=passkey.counter
        )

        # 更新计数器
        passkey.counter = verification.new_sign_count
        passkey.last_used_at = datetime.utcnow()
        db.commit()

        # 创建 token
        access_token = create_access_token(data={"sub": str(user.id)})

        add_log(db, user.id, "login", "passkey",
                details=f"Passkey 登录（无用户名）: {user.username}")

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"登录验证失败: {str(e)}")


# ============== 用户 Passkey 管理 API ==============

@management_router.get("/credentials", response_model=List[PasskeyCredentialResponse])
async def get_my_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有 Passkey"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    credentials = db.query(UserPasskey).filter(
        UserPasskey.user_id == current_user.id
    ).order_by(UserPasskey.created_at.desc()).all()

    return [PasskeyCredentialResponse.model_validate(c) for c in credentials]


@management_router.delete("/credentials/{credential_id}")
async def delete_credential(
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除指定的 Passkey"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    passkey = db.query(UserPasskey).filter(
        UserPasskey.id == credential_id,
        UserPasskey.user_id == current_user.id
    ).first()

    if not passkey:
        raise HTTPException(status_code=404, detail="Passkey 不存在")

    # 检查是否是强制要求
    if current_user.passkey_required and len(current_user.passkeys) <= 1:
        raise HTTPException(status_code=400, detail="已强制要求绑定 Passkey，无法删除最后一个")

    device_name = passkey.device_name
    db.delete(passkey)
    db.commit()

    add_log(db, current_user.id, "delete_passkey", "passkey",
            details=f"删除 Passkey: {device_name}")

    return {"message": "Passkey 已删除"}


@management_router.patch("/credentials/{credential_id}/rename")
async def rename_credential(
    credential_id: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """重命名 Passkey 设备名称"""
    if not get_passkey_config(db)["enabled"]:
        raise HTTPException(status_code=400, detail="Passkey 功能未启用")

    passkey = db.query(UserPasskey).filter(
        UserPasskey.id == credential_id,
        UserPasskey.user_id == current_user.id
    ).first()

    if not passkey:
        raise HTTPException(status_code=404, detail="Passkey 不存在")

    new_name = request.get("device_name", "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="设备名称不能为空")

    passkey.device_name = new_name
    db.commit()

    return {"message": "设备名称已更新"}