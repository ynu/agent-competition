# Passkey（通行密钥）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在系统中添加 WebAuthn/FIDO2 通行密钥支持，允许用户通过生物识别或硬件密钥登录

**Architecture:** 使用 pywebauthn 库实现 WebAuthn 协议，创建独立的 user_passkeys 表存储凭证，在登录页添加 Passkey 登录入口，支持用户在个人设置中管理 Passkey

**Tech Stack:** Python (FastAPI, pywebauthn), Vue 3 (TypeScript, WebAuthn API)

---

## 文件结构

### 后端新增文件
- `backend/app/models/passkey.py` - Passkey 数据模型
- `backend/app/api/passkey.py` - Passkey 认证 API
- `backend/app/schemas/passkey.py` - Passkey Pydantic schemas

### 后端修改文件
- `backend/app/models/user.py` - 添加 passkey_required 字段
- `backend/app/api/auth.py` - 添加 Passkey 配置端点
- `backend/app/api/users.py` - 添加管理员 Passkey 管理端点
- `backend/requirements.txt` - 添加 pywebauthn 依赖

### 前端新增文件
- `frontend/src/pages/ProfilePage.vue` - 个人设置页（包含 Passkey 管理）
- `frontend/src/api/passkey.ts` - Passkey API 客户端

### 前端修改文件
- `frontend/src/pages/LoginPage.vue` - 添加 Passkey 登录入口
- `frontend/src/pages/admin/UsersPage.vue` - 显示 Passkey 状态和操作
- `frontend/src/pages/admin/SettingsPage.vue` - 添加 Passkey 系统设置
- `frontend/src/api/index.ts` - 导出 passkeyApi
- `frontend/src/router/index.ts` - 添加 ProfilePage 路由

---

## Task 1: 安装依赖并创建数据模型

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/models/passkey.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/models/user.py`

- [ ] **Step 1: 添加 pywebauthn 到 requirements.txt**

```txt
# 在 requirements.txt 末尾添加
pywebauthn>=9.0.0
```

- [ ] **Step 2: 创建 Passkey 模型**

```python
"""
Passkey (通行密钥) 模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserPasskey(Base):
    """用户 Passkey 表"""
    __tablename__ = "user_passkeys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    credential_id = Column(String(255), unique=True, nullable=False, comment="公钥凭证ID")
    public_key = Column(Text, nullable=False, comment="公钥")
    counter = Column(Integer, default=0, comment="签名计数器（防重放）")
    device_name = Column(String(255), nullable=True, comment="设备名称")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User", backref="passkeys")

    def __repr__(self):
        return f"<UserPasskey {self.credential_id[:20]}...>"
```

- [ ] **Step 3: 更新 user.py 添加 passkey_required 字段**

在 `User` 模型的 `updated_at` 字段后添加：
```python
passkey_required = Column(Boolean, default=False, comment="是否强制要求绑定 Passkey")
```

- [ ] **Step 4: 更新 models/__init__.py 导出 UserPasskey**

在 `from .user import User, UserRole` 后添加：
```python
from .passkey import UserPasskey
```

- [ ] **Step 5: 运行数据库迁移**

```bash
cd backend
uv run python -c "from app.core.database import engine, Base; from app.models.passkey import UserPasskey; from app.models.user import User; Base.metadata.create_all(engine); print('Tables created')"
```

- [ ] **Step 6: 提交**

```bash
git add backend/requirements.txt backend/app/models/passkey.py backend/app/models/user.py backend/app/models/__init__.py
git commit -m "feat: add UserPasskey model and passkey_required field"
```

---

## Task 2: 创建 Passkey Schemas

**Files:**
- Create: `backend/app/schemas/passkey.py`

- [ ] **Step 1: 创建 Passkey Schemas**

```python
"""
Passkey Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PasskeyRegisterOptions(BaseModel):
    """注册选项响应"""
    challenge: str
    rp: dict
    user: dict
    pubKeyCredParams: list
    timeout: int
    attestation: str
    excludeCredentials: list
    authenticatorSelection: dict


class PasskeyLoginOptions(BaseModel):
    """登录选项响应"""
    challenge: str
    rp_id: str
    allow_credentials: list
    timeout: int
    user_verification: str


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


class ForcePasskeyRequest(BaseModel):
    """强制 Passkey 请求"""
    passkey_required: bool
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/schemas/passkey.py
git commit -m "feat: add passkey schemas"
```

---

## Task 3: 实现 Passkey 认证 API

**Files:**
- Create: `backend/app/api/passkey.py`

- [ ] **Step 1: 创建 Passkey 认证 API**

```python
"""
Passkey (通行密钥) 认证 API
"""
import json
import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    json_to_options
)
from webauthn.helpers import parse_credential_id
from webauthn.helpers.options import RegistrationOptions, AuthenticationOptions
from app.core.database import get_db
from app.core.security import get_current_user, create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.passkey import UserPasskey
from app.models.setting import Setting, Log
from app.schemas.passkey import (
    PasskeyConfigResponse, PasskeyCredentialResponse, PasskeyRegisterOptions,
    PasskeyLoginOptions, PasskeyLoginRequest, PasskeyRegisterRequest
)
from app.schemas.user import TokenResponse, UserResponse
from app.api.auth import add_log as add_auth_log

router = APIRouter(prefix="/auth/passkey", tags=["Passkey 认证"])

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
    from app.core.config import settings
    setting = db.query(Setting).filter(Setting.key == "base_url").first()
    return setting.value if setting and setting.value else settings.BASE_URL


def get_rp_id(db: Session) -> str:
    """获取 RP ID（域名）"""
    base_url = get_base_url(db)
    from urllib.parse import urlparse
    return urlparse(base_url).netloc or "localhost"


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
    base_url = get_base_url(db)

    # 获取用户已有的凭证 ID（用于排除）
    existing_credentials = db.query(UserPasskey).filter(
        UserPasskey.user_id == current_user.id
    ).all()
    exclude_credentials = [
        {"type": "public-key", "id": cred.credential_id}
        for cred in existing_credentials
    ]

    # 生成 challenge
    challenge = secrets.token_urlsafe(32)
    _challenge_store[f"register_{current_user.id}"] = challenge

    options = generate_registration_options(
        rp_id=rp_id,
        rp_name="智能体大赛",
        user_id=str(current_user.id),
        user_name=current_user.username,
        user_display_name=current_user.nickname or current_user.username,
        exclude_credentials=exclude_credentials,
        timeout=60000
    )

    return {
        "options": options_to_json(options),
        "challenge": challenge
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

    try:
        options = json_to_options(request.options)
        # 用存储的 challenge 替换响应中的 challenge
        options.challenge = stored_challenge.encode()

        verification = verify_registration_response(
            credential=options,
            expected_rp_id=rp_id,
            expected_origin=get_base_url(db)
        )

        # 解析设备名称
        device_name = None
        if request.device_name:
            device_name = request.device_name
        elif request.options and "attestedCredential" in request.options:
            # 尝试从 attestation 中获取设备信息
            try:
                device_name = f"Passkey {current_user.id}_{len(current_user.passkeys) + 1}"
            except:
                device_name = f"Passkey {current_user.id}_{len(current_user.passkeys) + 1}"

        # 保存凭证
        passkey = UserPasskey(
            user_id=current_user.id,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            counter=0,
            device_name=device_name
        )
        db.add(passkey)
        db.commit()

        add_auth_log(
            db, current_user.id, "register_passkey", "passkey",
            details=f"注册 Passkey: {device_name}"
        )

        return {"message": "Passkey 注册成功"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"注册验证失败: {str(e)}")


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

    # 生成 challenge
    challenge = secrets.token_urlsafe(32)
    _challenge_store[f"login_{username}"] = challenge

    options = generate_authentication_options(
        rp_id=rp_id,
        challenge=challenge.encode(),
        allow_credentials=[
            {"type": "public-key", "id": cred.credential_id, "transports": ["internal", "hybrid"]}
            for cred in credentials
        ],
        timeout=60000,
        user_verification="preferred"
    )

    return {
        "options": options_to_json(options),
        "challenge": challenge,
        "username": username
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
        options = json_to_options(request.options)
        options.challenge = stored_challenge.encode()

        verification = verify_authentication_response(
            credential=options,
            expected_rp_id=rp_id,
            expected_origin=get_base_url(db),
            expected_credential_id=passkey.credential_id.encode(),
            credential_public_key=passkey.public_key,
            credential_counter=passkey.counter
        )

        # 更新计数器
        passkey.counter = verification.new_credential_counter
        passkey.last_used_at = datetime.utcnow()
        db.commit()

        # 创建 token
        access_token = create_access_token(data={"sub": str(user.id)})

        add_auth_log(
            db, user.id, "login", "passkey",
            details=f"Passkey 登录: {user.username}",
            ip_address=None
        )

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"登录验证失败: {str(e)}")


# 用户 Passkey 管理 API
management_router = APIRouter(prefix="/passkey", tags=["Passkey 管理"])


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
    config = get_passkey_config(db)
    if current_user.passkey_required and len(current_user.passkeys) <= 1:
        raise HTTPException(status_code=400, detail="已强制要求绑定 Passkey，无法删除最后一个")

    device_name = passkey.device_name
    db.delete(passkey)
    db.commit()

    add_auth_log(
        db, current_user.id, "delete_passkey", "passkey",
        details=f"删除 Passkey: {device_name}"
    )

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
```

- [ ] **Step 2: 添加缺失的 import**

在 `backend/app/api/passkey.py` 顶部添加：
```python
from datetime import datetime
```

- [ ] **Step 3: 在 main.py 中注册路由**

```bash
# 在 backend/app/main.py 中添加路由注册
# 找到其他 router 注册的位置，添加：
from app.api.passkey import router as passkey_router, management_router as passkey_management_router

# 注册 passkey 路由
app.include_router(passkey_router)
app.include_router(passkey_management_router)
```

- [ ] **Step 4: 安装依赖并测试导入**

```bash
cd backend
uv pip install pywebauthn>=9.0.0
uv run python -c "from app.api.passkey import router; print('Import successful')"
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/api/passkey.py backend/app/main.py
git commit -m "feat: implement passkey authentication API"
```

---

## Task 4: 实现管理员 Passkey 管理 API

**Files:**
- Modify: `backend/app/api/users.py`

- [ ] **Step 1: 在 users.py 中添加管理端点**

在文件末尾（`reset_user_password` 函数后）添加：

```python
# ============== Passkey 管理 ==============

@router.get("/{user_id}/passkey-credentials")
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


@router.post("/{user_id}/reset-passkey")
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


@router.put("/{user_id}/force-passkey")
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
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/api/users.py
git commit -m "feat: add admin passkey management API"
```

---

## Task 5: 添加系统设置 API 支持

**Files:**
- Modify: `backend/app/api/settings.py`

- [ ] **Step 1: 在 settings.py 中添加默认设置**

找到初始化设置的函数（如果有），确保添加了 Passkey 相关设置：
- `passkey_enabled`: false
- `passkey_require_for_roles`: "[]"

如果没有专门的初始化函数，可以跳过此步，这些设置会在首次访问时动态创建。

- [ ] **Step 2: 提交**

```bash
git add backend/app/api/settings.py
git commit -m "feat: ensure passkey settings available in settings API"
```

---

## Task 6: 创建前端 Passkey API 客户端

**Files:**
- Create: `frontend/src/api/passkey.ts`

- [ ] **Step 1: 创建 Passkey API 客户端**

```typescript
import api from './index'

// Passkey 相关类型
export interface PasskeyConfig {
  enabled: boolean
  require_for_roles: string[]
}

export interface PasskeyCredential {
  id: number
  device_name: string | null
  created_at: string
  last_used_at: string | null
}

export interface PasskeyLoginOptions {
  options: string
  challenge: string
  username: string
}

export interface PasskeyRegisterOptions {
  options: string
  challenge: string
}

// Passkey API
export const passkeyApi = {
  // 配置
  getConfig: () => api.get<PasskeyConfig>('/auth/passkey/config'),

  // 注册流程
  getRegisterOptions: () => api.get<PasskeyRegisterOptions>('/auth/passkey/register-options'),
  verifyRegistration: (data: {
    options: string
    device_name?: string
  }) => api.post('/auth/passkey/register-verify', data),

  // 登录流程
  getLoginOptions: (username: string) => api.post<PasskeyLoginOptions>('/auth/passkey/login-options', { username }),
  verifyLogin: (data: {
    username: string
    credential_id: string
    options: string
  }) => api.post<{ access_token: string; token_type: string; user: any }>('/auth/passkey/login-verify', data),

  // 用户凭证管理
  getMyCredentials: () => api.get<PasskeyCredential[]>('/passkey/credentials'),
  deleteCredential: (credentialId: number) => api.delete(`/passkey/credentials/${credentialId}`),
  renameCredential: (credentialId: number, deviceName: string) =>
    api.patch(`/passkey/credentials/${credentialId}/rename`, { device_name: deviceName })
}

// WebAuthn 类型声明
declare global {
  interface Navigator {
    credentials: CredentialManagement
  }

  interface CredentialManagement {
    create(options: CredentialCreationOptions): Promise<PublicKeyCredential | null>
    get(options: CredentialRequestOptions): Promise<PublicKeyCredential | null>
    store(credential: Credential): Promise<void>
  }

  interface CredentialCreationOptions {
    publicKey: PublicKeyCredentialCreationOptions
  }

  interface CredentialRequestOptions {
    publicKey: PublicKeyCredentialRequestOptions
  }

  interface PublicKeyCredentialRequestOptions {
    challenge: BufferSource
    rpId?: string
    allowCredentials?: PublicKeyCredentialDescriptor[]
    timeout?: number
    userVerification?: 'required' | 'preferred' | 'discouraged'
  }
}
```

- [ ] **Step 2: 在 api/index.ts 中导出 passkeyApi**

在文件末尾添加：
```typescript
export { passkeyApi } from './passkey'
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/api/passkey.ts frontend/src/api/index.ts
git commit -m "feat: add passkey API client"
```

---

## Task 7: 修改登录页添加 Passkey 登录

**Files:**
- Modify: `frontend/src/pages/LoginPage.vue`

- [ ] **Step 1: 添加 Passkey 登录标签页**

在 `<script setup>` 中添加：
```typescript
// Passkey 相关
const passkeyEnabled = ref(false)
const passkeyLoading = ref(false)
const passkeyError = ref('')

// 检测浏览器是否支持 WebAuthn
const webAuthnSupported = computed(() => {
  return !!(navigator.credentials && navigator.credentials.create && navigator.credentials.get)
})

async function loadPasskeyConfig() {
  try {
    const res = await passkeyApi.getConfig()
    passkeyEnabled.value = res.data.enabled
  } catch (e) {
    console.error('Failed to load passkey config:', e)
  }
}

async function handlePasskeyLogin() {
  if (!username.value) {
    passkeyError.value = '请先输入用户名'
    return
  }

  passkeyError.value = ''
  passkeyLoading.value = true

  try {
    // 获取登录选项
    const optionsRes = await passkeyApi.getLoginOptions(username.value)
    const options = JSON.parse(optionsRes.data.options)

    // 调用 WebAuthn
    const credential = await navigator.credentials.get({
      publicKey: options
    })

    if (!credential) {
      passkeyError.value = '认证已取消'
      return
    }

    // 验证登录
    const verifyRes = await passkeyApi.verifyLogin({
      username: username.value,
      credential_id: credential.id,
      options: JSON.stringify(credential)
    })

    // 保存 token 并跳转
    localStorage.setItem('token', verifyRes.data.access_token)
    const redirect = route.query.redirect as string || '/admin'
    window.location.href = redirect
  } catch (e: any) {
    console.error('Passkey login failed:', e)
    passkeyError.value = e.response?.data?.detail || 'Passkey 登录失败'
  } finally {
    passkeyLoading.value = false
  }
}

// 修改 onMounted
onMounted(async () => {
  // ... existing code ...

  // 加载 Passkey 配置
  await loadPasskeyConfig()
})
```

在 `<template>` 中，在登录模式切换处修改为：
```vue
<!-- Login Mode Toggle (show if passkey enabled or showBothTabs) -->
<div v-if="passkeyEnabled || showBothTabs" class="flex bg-gray-100 rounded-xl p-1 mb-6">
  <button
    v-if="passkeyEnabled"
    @click="showPasswordTab = false"
    class="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
    :class="!showPasswordTab ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
  >
    通行密钥
  </button>
  <button
    @click="showPasswordTab = true"
    class="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
    :class="showPasswordTab ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
  >
    账号密码
  </button>
  <button
    v-if="!showBothTabs && !passkeyEnabled"
    @click="handleCasLogin"
    class="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 text-gray-500 hover:text-gray-700"
  >
    统一身份认证
  </button>
</div>
```

添加 Passkey 登录表单：
```vue
<!-- Passkey Login -->
<template v-if="passkeyEnabled && !showPasswordTab">
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">用户名/学工号</label>
    <div class="relative">
      <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </div>
      <input
        v-model="username"
        type="text"
        required
        class="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
        placeholder="请输入用户名"
      />
    </div>
  </div>

  <!-- Error Message -->
  <div v-if="passkeyError" class="flex items-center gap-2 text-red-500 text-sm bg-red-50 p-3 rounded-lg">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
    {{ passkeyError }}
  </div>

  <!-- Passkey Login Button -->
  <button
    type="button"
    @click="handlePasskeyLogin"
    :disabled="passkeyLoading"
    class="w-full bg-gradient-to-r from-green-600 to-teal-600 text-white py-3.5 rounded-xl font-medium hover:shadow-lg hover:shadow-green-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
  >
    <svg v-if="passkeyLoading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
    </svg>
    {{ passkeyLoading ? '验证中...' : '使用通行密钥登录' }}
  </button>

  <p v-if="!webAuthnSupported" class="text-xs text-amber-600 text-center mt-2">
    您的浏览器不支持通行密钥，请使用账号密码登录
  </p>
</template>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/pages/LoginPage.vue
git commit -m "feat: add passkey login to LoginPage"
```

---

## Task 8: 创建个人设置页面

**Files:**
- Create: `frontend/src/pages/ProfilePage.vue`

- [ ] **Step 1: 创建 ProfilePage.vue**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { passkeyApi, type PasskeyCredential, type PasskeyConfig } from '@/api/passkey'

const router = useRouter()
const authStore = useAuthStore()

const passkeyConfig = ref<PasskeyConfig>({ enabled: false, require_for_roles: [] })
const credentials = ref<PasskeyCredential[]>([])
const loading = ref(false)
const registering = ref(false)
const error = ref('')
const success = ref('')

// WebAuthn 支持检测
const webAuthnSupported = !!(navigator.credentials && navigator.credentials.create && navigator.credentials.get)

onMounted(async () => {
  await loadConfig()
  await loadCredentials()
})

async function loadConfig() {
  try {
    const res = await passkeyApi.getConfig()
    passkeyConfig.value = res.data
  } catch (e) {
    console.error('Failed to load passkey config:', e)
  }
}

async function loadCredentials() {
  try {
    const res = await passkeyApi.getMyCredentials()
    credentials.value = res.data
  } catch (e) {
    console.error('Failed to load credentials:', e)
  }
}

async function handleRegisterPasskey() {
  if (!webAuthnSupported) {
    error.value = '您的浏览器不支持通行密钥'
    return
  }

  error.value = ''
  success.value = ''
  registering.value = true

  try {
    // 获取注册选项
    const optionsRes = await passkeyApi.getRegisterOptions()
    const options = JSON.parse(optionsRes.data.options)

    // 调用 WebAuthn 创建凭证
    const credential = await navigator.credentials.create({
      publicKey: options
    })

    if (!credential) {
      error.value = '注册已取消'
      return
    }

    // 验证注册
    await passkeyApi.verifyRegistration({
      options: JSON.stringify(credential),
      device_name: await getDeviceName()
    })

    success.value = '通行密钥注册成功'
    await loadCredentials()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败，请重试'
  } finally {
    registering.value = false
  }
}

async function handleDeleteCredential(id: number) {
  if (!confirm('确定要删除这个通行密钥吗？')) return

  try {
    await passkeyApi.deleteCredential(id)
    success.value = '通行密钥已删除'
    await loadCredentials()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '删除失败'
  }
}

async function handleRenameCredential(id: number, currentName: string) {
  const newName = prompt('请输入新的设备名称：', currentName)
  if (!newName || newName === currentName) return

  try {
    await passkeyApi.renameCredential(id, newName)
    success.value = '设备名称已更新'
    await loadCredentials()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '重命名失败'
  }
}

async function getDeviceName(): Promise<string> {
  // 尝试获取设备名称
  const ua = navigator.userAgent
  if (ua.includes('iPhone')) return `iPhone ${ua.match(/iPhone\s+(\d+)/)?.[1] || ''}`
  if (ua.includes('iPad')) return `iPad ${ua.match(/iPad\s+(\d+)/)?.[1] || ''}`
  if (ua.includes('Android')) return 'Android Device'
  if (ua.includes('Mac OS')) return 'Mac'
  if (ua.includes('Windows')) return 'Windows PC'
  if (ua.includes('Linux')) return 'Linux PC'
  return 'Unknown Device'
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '从未使用'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="max-w-2xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">个人设置</h1>

    <!-- Alerts -->
    <div v-if="error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
      {{ error }}
    </div>
    <div v-if="success" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
      {{ success }}
    </div>

    <!-- Passkey Section -->
    <div v-if="passkeyConfig.enabled" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">通行密钥</h2>
        <span class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">已启用</span>
      </div>

      <p class="text-sm text-gray-500 mb-4">
        通行密钥允许您使用指纹、面容或硬件密钥安全登录，无需输入密码。
      </p>

      <!-- Credentials List -->
      <div v-if="credentials.length > 0" class="space-y-3 mb-4">
        <div
          v-for="cred in credentials"
          :key="cred.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">{{ cred.device_name || '未命名设备' }}</p>
              <p class="text-xs text-gray-500">
                注册于 {{ formatDate(cred.created_at) }}
                <span v-if="cred.last_used_at"> · 最后使用 {{ formatDate(cred.last_used_at) }}</span>
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="handleRenameCredential(cred.id, cred.device_name || '')"
              class="p-2 text-gray-400 hover:text-gray-600 transition"
              title="重命名"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
            <button
              @click="handleDeleteCredential(cred.id)"
              class="p-2 text-gray-400 hover:text-red-600 transition"
              title="删除"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-4 text-gray-500 text-sm mb-4">
        您还没有注册任何通行密钥
      </div>

      <!-- Register Button -->
      <button
        v-if="webAuthnSupported"
        @click="handleRegisterPasskey"
        :disabled="registering"
        class="w-full py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg font-medium hover:shadow-lg transition disabled:opacity-50 flex items-center justify-center gap-2"
      >
        <svg v-if="registering" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
        </svg>
        {{ registering ? '注册中...' : '添加通行密钥' }}
      </button>

      <p v-if="!webAuthnSupported" class="text-xs text-amber-600 text-center mt-2">
        您的浏览器不支持通行密钥
      </p>
    </div>

    <!-- User Info -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 class="text-lg font-semibold mb-4">账户信息</h2>
      <div class="space-y-3 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">用户名</span>
          <span class="font-medium">{{ authStore.user?.username }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">昵称</span>
          <span class="font-medium">{{ authStore.user?.nickname || '-' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">邮箱</span>
          <span class="font-medium">{{ authStore.user?.email || '-' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">角色</span>
          <span class="font-medium capitalize">{{ authStore.user?.role }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: 添加路由**

在 `frontend/src/router/index.ts` 中添加：
```typescript
{
  path: '/profile',
  name: 'Profile',
  component: () => import('@/pages/ProfilePage.vue'),
  meta: { requiresAuth: true }
}
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/ProfilePage.vue
git commit -m "feat: add ProfilePage with passkey management"
```

---

## Task 9: 修改用户管理页面显示 Passkey 状态

**Files:**
- Modify: `frontend/src/pages/admin/UsersPage.vue`

- [ ] **Step 1: 添加 Passkey 列和操作**

在用户列表中添加 Passkey 列：
```vue
<!-- 在角色列之后添加 -->
<el-table-column label="Passkey" width="100" align="center">
  <template #default="{ row }">
    <el-tag v-if="row.passkeyCount > 0" type="success" size="small">
      {{ row.passkeyCount }} 个
    </el-tag>
    <span v-else class="text-gray-400 text-xs">无</span>
  </template>
</el-table-column>
```

添加操作按钮：
```vue
<!-- 在操作列中添加 -->
<el-dropdown-item @click="handleResetPasskey(row)">
  <span class="flex items-center gap-2">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
    </svg>
    重置 Passkey
  </span>
</el-dropdown-item>
<el-dropdown-item @click="handleForcePasskey(row)">
  <span class="flex items-center gap-2">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
    </svg>
    {{ row.passkeyRequired ? '取消强制 Passkey' : '强制 Passkey' }}
  </span>
</el-dropdown-item>
```

添加方法：
```typescript
import { userApi } from '@/api'

// 获取用户 Passkey 信息
async function loadUserPasskeyInfo() {
  for (const user of users.value) {
    try {
      const res = await api.get(`/users/${user.id}/passkey-credentials`)
      user.passkeyCount = res.data.credentials?.length || 0
      user.passkeyRequired = res.data.passkey_required || false
    } catch {
      user.passkeyCount = 0
      user.passkeyRequired = false
    }
  }
}

async function handleResetPasskey(row: any) {
  if (!confirm(`确定要重置用户 ${row.username} 的所有 Passkey 吗？`)) return

  try {
    await api.post(`/users/${row.id}/reset-passkey`)
    ElMessage.success('Passkey 已重置')
    await loadUserPasskeyInfo()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '重置失败')
  }
}

async function handleForcePasskey(row: any) {
  const action = row.passkeyRequired ? '取消强制' : '强制'
  if (!confirm(`确定要${action}用户 ${row.username} 使用 Passkey 吗？`)) return

  try {
    await api.put(`/users/${row.id}/force-passkey`, { passkey_required: !row.passkeyRequired })
    ElMessage.success(`已${action} Passkey`)
    await loadUserPasskeyInfo()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/pages/admin/UsersPage.vue
git commit -m "feat: add passkey management to UsersPage"
```

---

## Task 10: 修改系统设置页面

**Files:**
- Modify: `frontend/src/pages/admin/SettingsPage.vue`

- [ ] **Step 1: 添加 Passkey 设置区块**

在设置列表中或单独的 tab 添加 Passkey 设置：
```vue
<!-- Passkey Settings Card -->
<el-card v-if="isAdmin" class="mb-4">
  <template #header>
    <div class="flex items-center justify-between">
      <span class="font-medium">通行密钥设置</span>
    </div>
  </template>

  <el-form label-width="140px">
    <el-form-item label="启用 Passkey">
      <el-switch
        v-model="passkeyEnabled"
        @change="handleUpdatePasskeyEnabled"
      />
      <span class="text-xs text-gray-500 ml-2">
        允许用户使用通行密钥（WebAuthn）登录
      </span>
    </el-form-item>

    <el-form-item label="强制角色">
      <el-select
        v-model="passkeyRequireRoles"
        multiple
        placeholder="选择需要强制 Passkey 的角色"
        @change="handleUpdatePasskeyRoles"
      >
        <el-option label="普通用户" value="user" />
        <el-option label="评审用户" value="reviewer" />
        <el-option label="管理员" value="admin" />
      </el-select>
      <span class="text-xs text-gray-500 ml-2">
        选中的角色必须绑定 Passkey 才能使用系统
      </span>
    </el-form-item>
  </el-form>
</el-card>
```

添加相关数据和方法：
```typescript
const passkeyEnabled = ref(false)
const passkeyRequireRoles = ref<string[]>([])

async function loadPasskeySettings() {
  try {
    const configRes = await passkeyApi.getConfig()
    passkeyEnabled.value = configRes.data.enabled
    passkeyRequireRoles.value = configRes.data.require_for_roles || []
  } catch (e) {
    console.error('Failed to load passkey config:', e)
  }
}

async function handleUpdatePasskeyEnabled(value: boolean) {
  try {
    await settingsApi.update('passkey_enabled', { value: String(value) })
    ElMessage.success('设置已更新')
  } catch (e: any) {
    ElMessage.error('更新失败')
    passkeyEnabled.value = !value // 回滚
  }
}

async function handleUpdatePasskeyRoles(roles: string[]) {
  try {
    await settingsApi.update('passkey_require_for_roles', { value: JSON.stringify(roles) })
    ElMessage.success('设置已更新')
  } catch (e: any) {
    ElMessage.error('更新失败')
  }
}

// 在 onMounted 中调用
onMounted(async () => {
  await loadPasskeySettings()
  // ... existing code
})
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/pages/admin/SettingsPage.vue
git commit -m "feat: add passkey settings to SettingsPage"
```

---

## Task 11: 添加初始化 Passkey 设置脚本

**Files:**
- Modify: `backend/init_db.py`

- [ ] **Step 1: 添加 Passkey 默认设置**

在 `init_db.py` 的初始化设置函数中添加：
```python
# Passkey 设置
settings.extend([
    Setting(key="passkey_enabled", value="false", description="是否启用 Passkey 功能"),
    Setting(key="passkey_require_for_roles", value="[]", description="强制要求绑定 Passkey 的角色列表"),
])
```

- [ ] **Step 2: 提交**

```bash
git add backend/init_db.py
git commit -m "feat: add passkey default settings to init_db"
```

---

## Task 12: 测试和验证

**Files:**
- Test manually in browser

- [ ] **Step 1: 安装依赖**

```bash
cd backend
uv pip install -e .
uv pip install pywebauthn>=9.0.0
```

- [ ] **Step 2: 启动后端服务**

```bash
cd backend
uv run python main.py
```

访问 http://localhost:8000/docs 查看新的 API 端点

- [ ] **Step 3: 启动前端服务**

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173

- [ ] **Step 4: 测试流程**

1. 使用管理员账号登录
2. 进入系统设置，启用 Passkey
3. 进入个人设置，添加通行密钥
4. 退出登录，在登录页使用通行密钥登录
5. 进入用户管理，查看用户 Passkey 状态，测试重置功能

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "feat: complete passkey (WebAuthn) implementation

- Add UserPasskey model for storing credentials
- Implement passkey registration and login APIs
- Add admin passkey management (view, reset, force)
- Create ProfilePage for passkey management
- Update LoginPage with passkey login option
- Add passkey settings to admin SettingsPage
- Add passkey status to UsersPage"
```

---

## 自检清单

- [ ] 所有后端 API 端点已实现并注册
- [ ] UserPasskey 模型已创建并可迁移
- [ ] 前端登录页支持 Passkey 登录
- [ ] 个人设置页可管理 Passkey
- [ ] 用户管理页显示 Passkey 状态
- [ ] 系统设置页可配置 Passkey
- [ ] 依赖已添加到 requirements.txt
- [ ] 所有代码已提交