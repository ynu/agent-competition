"""
安全模块 - JWT认证、密码哈希、权限检查
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.permission import Permission, Role

# 密码哈希上下文 - 支持多种格式以兼容旧数据
# bcrypt用于验证旧密码，sha256_crypt用于新密码
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto", sha256_crypt__rounds=100000)

# OAuth2 认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Convert to int (sub is now a string)
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """从token字符串获取用户"""
    if not token:
        return None

    payload = decode_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user


async def get_current_active_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前活跃用户（可选，未登录返回None）"""
    # 手动从 Authorization header 提取 token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    payload = decode_token(token)
    if payload is None:
        return None

    user_id: int = payload.get("sub")
    if user_id is None:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return None

    return user


def require_role(*roles: str):
    """角色权限装饰器"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker


def get_user_permissions(db: Session, user: User) -> List[str]:
    """获取用户所有权限代码列表"""
    # 管理员拥有所有权限
    if user.role == UserRole.ADMIN:
        permissions = db.query(Permission).all()
        return [p.code for p in permissions]

    # 根据角色获取权限
    role_code = user.role.value
    role = db.query(Role).filter(Role.code == role_code).first()
    if role:
        return [p.code for p in role.permissions]

    # 默认用户权限
    return []


def has_permission(db: Session, user: User, permission_code: str) -> bool:
    """检查用户是否有指定权限"""
    # 管理员拥有所有权限
    if user.role == UserRole.ADMIN:
        return True

    # 根据角色获取权限
    role_code = user.role.value
    role = db.query(Role).filter(Role.code == role_code).first()
    if role:
        # 管理员角色拥有所有权限
        if role.code == "admin":
            return True
        return any(p.code == permission_code for p in role.permissions)

    return False


def require_permission(*permission_codes: str):
    """权限检查装饰器"""
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 检查是否有任意一个权限
        for code in permission_codes:
            if has_permission(db, current_user, code):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return permission_checker