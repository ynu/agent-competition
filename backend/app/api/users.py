"""
用户管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role, get_password_hash
from app.models.user import User, UserRole
from app.models.setting import Log
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.passkey import ForcePasskeyRequest
from app.schemas.common import PageResponse
from app.services.webhook import trigger_webhook_and_notification
from app.models.webhook import WebhookEventType

router = APIRouter(prefix="/users", tags=["用户管理"])


def add_log(db: Session, user_id: int, action: str, resource: str = None,
            resource_id: int = None, details: str = None):
    """添加日志"""
    log = Log(user_id=user_id, action=action, resource=resource,
              resource_id=resource_id, details=details)
    db.add(log)
    db.commit()


@router.get("", response_model=PageResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """获取用户列表（仅管理员）"""
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.nickname.contains(keyword)) |
            (User.email.contains(keyword))
        )

    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[UserResponse.model_validate(u) for u in users]
    )


@router.get("/{user_id:int}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户详情"""
    # 普通用户只能查看自己，管理员可以查看所有
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="权限不足")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """创建用户（仅管理员）"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    if user_data.email and db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被使用")

    user = User(
        username=user_data.username,
        nickname=user_data.nickname,
        email=user_data.email,
        role=user_data.role,
        hashed_password=user_data.password if user_data.password else None
    )
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    add_log(db, current_user.id, "create", "user", user.id, f"创建用户: {user.username}")

    response = UserResponse.model_validate(user)

    # 触发 Webhook
    await trigger_webhook_and_notification(db, WebhookEventType.USER_REGISTERED, {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else user.role
    }, "registered")

    return response


@router.put("/{user_id:int}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新用户信息"""
    # 普通用户只能更新自己，管理员可以更新所有
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="权限不足")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新字段
    update_data = user_data.model_dump(exclude_unset=True)

    # 非管理员不能修改角色
    if current_user.role != UserRole.ADMIN:
        update_data.pop("role", None)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    add_log(db, current_user.id, "update", "user", user.id, f"更新用户: {user.username}")

    return UserResponse.model_validate(user)


@router.delete("/{user_id:int}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """删除用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账户")

    username = user.username
    db.delete(user)
    db.commit()

    add_log(db, current_user.id, "delete", "user", user_id, f"删除用户: {username}")

    return {"message": "删除成功"}


class ResetPasswordRequest(BaseModel):
    new_password: str


@router.post("/{user_id:int}/reset-password")
async def reset_user_password(
    user_id: int,
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """重置用户密码（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能重置自己的密码
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能重置自己的密码")

    # 更新密码
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    add_log(db, current_user.id, "update", "user", user_id, f"重置用户密码: {user.username}")

    return {"message": "密码重置成功"}


# ============== Passkey 管理 ==============

@router.get("/{user_id:int}/passkey-credentials")
async def get_user_passkey_credentials(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """管理员查看用户的 Passkey（不含私钥）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    from app.models.passkey import UserPasskey
    from app.schemas.passkey import PasskeyCredentialResponse

    credentials = db.query(UserPasskey).filter(
        UserPasskey.user_id == user_id
    ).order_by(UserPasskey.created_at.desc()).all()

    return {
        "user_id": user_id,
        "username": user.username,
        "passkey_required": user.passkey_required,
        "credentials": [PasskeyCredentialResponse.model_validate(c) for c in credentials]
    }


@router.post("/{user_id:int}/reset-passkey")
async def reset_user_passkey(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """管理员重置用户的所有 Passkey"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能重置自己的 Passkey")

    from app.models.passkey import UserPasskey

    # 删除所有凭证
    deleted_count = db.query(UserPasskey).filter(
        UserPasskey.user_id == user_id
    ).delete()
    db.commit()

    add_log(db, current_user.id, "reset_passkey", "user", user_id,
            f"重置用户 Passkey: {user.username}，删除了 {deleted_count} 个凭证")

    return {"message": f"已重置用户 {user.username} 的所有 Passkey，共 {deleted_count} 个"}


@router.put("/{user_id:int}/force-passkey")
async def set_force_passkey(
    user_id: int,
    data: ForcePasskeyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """管理员设置用户是否必须绑定 Passkey"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的强制 Passkey 设置")

    user.passkey_required = data.passkey_required
    db.commit()

    add_log(db, current_user.id, "set_force_passkey", "user", user_id,
            f"设置用户 {user.username} 强制 Passkey: {data.passkey_required}")

    return {"message": f"已设置用户 {user.username} 强制 Passkey: {data.passkey_required}"}


# ============== 2FA 管理 ==============

@router.post("/{user_id:int}/reset-otp")
async def admin_reset_user_otp(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """管理员重置用户 2FA"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 重置 2FA
    user.otp_enabled = False
    user.otp_verified = False
    user.otp_secret_encrypted = None
    db.commit()

    # 记录日志
    add_log(
        db, current_user.id, "admin_reset_otp", "user",
        resource_id=user_id,
        details=f"管理员 {current_user.username} 重置用户 {user.username} 的 2FA"
    )

    return {"message": "用户 2FA 已重置"}