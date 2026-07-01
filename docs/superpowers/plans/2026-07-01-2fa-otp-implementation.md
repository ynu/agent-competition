# 2FA OTP (TOTP) 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为智能体大赛网站添加 TOTP 二次认证功能

**Architecture:** 使用 pyotp 生成/验证 TOTP，cryptography 的 Fernet 进行 secret 加密存储。前端扩展登录页支持两步验证，用户管理页面支持 2FA 状态显示和管理员重置功能。

**Tech Stack:** pyotp, cryptography (Fernet), Vue 3 + Pinia + TailwindCSS

---

## 文件结构

```
backend/
├── app/
│   ├── api/
│   │   ├── otp.py          # 新建: 2FA OTP API
│   │   ├── auth.py         # 修改: 登录流程扩展
│   │   ├── users.py        # 修改: 管理员重置 2FA
│   │   └── __init__.py     # 修改: 注册 otp router
│   ├── models/
│   │   └── user.py         # 修改: 添加 otp 字段
│   ├── schemas/
│   │   ├── otp.py          # 新建: OTP schemas
│   │   └── user.py         # 修改: TokenResponse 扩展
│   └── core/
│       ├── config.py       # 修改: 添加 OTP_ENCRYPTION_KEY
│       └── security.py     # 新建: OTP 加密/解密工具函数
frontend/
├── src/
│   ├── api/
│   │   ├── otp.ts          # 新建: OTP API 客户端
│   │   └── index.ts        # 修改: 导出 otpApi
│   ├── pages/
│   │   └── LoginPage.vue   # 修改: 两步登录流程
│   └── pages/admin/
│       ├── ProfilePage.vue # 修改: 2FA 管理卡片
│       └── UsersPage.vue   # 修改: 2FA 状态列和重置按钮
```

---

## Task 1: 安装依赖

**Files:**
- Modify: `backend/pyproject.toml` 或直接安装

- [ ] **Step 1: 安装 pyotp 和 cryptography**

```bash
cd C:/Users/admin/code/ai/agent-competition/backend
uv pip install pyotp cryptography
```

- [ ] **Step 2: 验证安装**

```bash
uv run python -c "import pyotp; import cryptography; print('OK')"
```
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "chore: add pyotp and cryptography dependencies"
```

---

## Task 2: User 模型扩展

**Files:**
- Modify: `backend/app/models/user.py`
- Test: `backend/app/models/test_user.py` (可选)

- [ ] **Step 1: 添加 OTP 相关字段**

在 `User` 类中添加以下字段（在 `passkey_required` 后）：

```python
# 2FA OTP 字段
otp_secret_encrypted = Column(String(500), nullable=True, comment="加密的 OTP Secret")
otp_enabled = Column(Boolean, default=False, comment="是否启用 2FA")
otp_verified = Column(Boolean, default=False, comment="是否完成 2FA 绑定验证")
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/user.py && git commit -m "feat: add OTP fields to User model"
```

---

## Task 3: OTP 加密工具

**Files:**
- Create: `backend/app/core/otp.py`
- Modify: `backend/app/core/config.py` (添加 ENCRYPTION_KEY)

- [ ] **Step 1: 添加 ENCRYPTION_KEY 配置**

在 `backend/app/core/config.py` 的 `Settings` 类中添加：

```python
# 2FA 加密密钥
OTP_ENCRYPTION_KEY: str = Field(
    default="",
    description="TOTP Secret 加密密钥，32字节 base64 编码"
)
```

在文件末尾添加：

```python
def get_otp_encryption_key() -> str:
    """获取或生成 OTP 加密密钥"""
    if settings.OTP_ENCRYPTION_KEY:
        return settings.OTP_ENCRYPTION_KEY
    # 生成新的 32 字节密钥并返回（仅用于开发环境）
    import base64
    import secrets
    return base64.b64encode(secrets.token_bytes(32)).decode()
```

- [ ] **Step 2: 创建 OTP 加密模块**

创建 `backend/app/core/otp.py`：

```python
"""
OTP 加密工具模块
使用 Fernet 对称加密存储 OTP Secret
"""
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import settings, get_otp_encryption_key


def _get_fernet() -> Fernet:
    """获取 Fernet 实例"""
    key = get_otp_encryption_key()
    if len(key) == 44 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'):
        # 已经是有效的 Fernet 密钥
        try:
            return Fernet(key.encode())
        except Exception:
            pass
    # 从密码派生出 Fernet 密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"otp_secret_salt",  # 生产环境应使用随机盐并存储
        iterations=480000,
    )
    derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
    return Fernet(derived_key)


def encrypt_otp_secret(secret: str) -> str:
    """加密 OTP Secret"""
    fernet = _get_fernet()
    return fernet.encrypt(secret.encode()).decode()


def decrypt_otp_secret(encrypted: str) -> str:
    """解密 OTP Secret"""
    fernet = _get_fernet()
    return fernet.decrypt(encrypted.encode()).decode()
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/core/config.py backend/app/core/otp.py && git commit -m "feat: add OTP encryption utilities"
```

---

## Task 4: OTP Schemas

**Files:**
- Create: `backend/app/schemas/otp.py`

- [ ] **Step 1: 创建 OTP Schemas**

创建 `backend/app/schemas/otp.py`：

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/otp.py && git commit -m "feat: add OTP schemas"
```

---

## Task 5: OTP API 实现

**Files:**
- Create: `backend/app/api/otp.py`

- [ ] **Step 1: 创建 OTP API**

创建 `backend/app/api/otp.py`：

```python
"""
2FA OTP (TOTP) 认证 API
"""
import pyotp
import qrcode
import io
import base64
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, create_access_token, verify_password
from app.core.otp import encrypt_otp_secret, decrypt_otp_secret
from app.core.config import settings, get_base_url
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/otp.py && git commit -m "feat: add OTP API endpoints"
```

---

## Task 6: 修改登录流程支持 2FA

**Files:**
- Modify: `backend/app/api/auth.py`

- [ ] **Step 1: 添加临时 token 存储**

在 `auth.py` 顶部添加：

```python
# 临时 token 存储（2FA 两步验证用，生产环境应使用 Redis）
_temp_token_store = {}
```

添加生成临时 token 的函数：

```python
def create_temp_token(user_id: int, db: Session) -> str:
    """创建临时 token（用于 2FA 两步验证）"""
    import secrets
    temp_token = secrets.token_urlsafe(32)
    _temp_token_store[temp_token] = {
        "user_id": user_id,
        "expire_at": datetime.utcnow() + timedelta(minutes=5)
    }
    return temp_token


def verify_temp_token(temp_token: str) -> int | None:
    """验证临时 token，返回 user_id 或 None"""
    data = _temp_token_store.pop(temp_token, None)
    if not data:
        return None
    if datetime.utcnow() > data["expire_at"]:
        return None
    return data["user_id"]
```

- [ ] **Step 2: 修改 login 函数**

修改 `login` 函数的返回逻辑：

```python
@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    # ... 现有验证逻辑保持不变 ...

    # 检查是否启用了 2FA
    if user.otp_enabled and user.otp_verified:
        # 需要 2FA 验证，返回临时 token
        temp_token = create_temp_token(user.id, db)
        return {
            "access_token": None,
            "temp_token": temp_token,
            "requires_otp": True,
            "token_type": "bearer"
        }

    # 创建 token
    access_token = create_access_token(data={"sub": str(user.id)})

    # 记录登录日志
    add_log(...)

    return {
        "access_token": access_token,
        "temp_token": None,
        "requires_otp": False,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }
```

- [ ] **Step 3: 添加 2FA 登录验证端点**

在 `auth.py` 中添加：

```python
@router.post("/otp-login", response_model=TokenResponse)
async def otp_login(
    request: OTPLoginVerifyRequest,
    db: Session = Depends(get_db)
):
    """2FA 登录验证（第二步）"""
    user_id = verify_temp_token(request.temp_token)
    if not user_id:
        raise HTTPException(status_code=400, detail="临时令牌无效或已过期")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户无效或已禁用")

    # 验证 OTP
    if not user.otp_secret_encrypted:
        raise HTTPException(status_code=400, detail="2FA 未配置")

    try:
        secret = decrypt_otp_secret(user.otp_secret_encrypted)
        totp = pyotp.TOTP(secret)

        if not totp.verify(request.code):
            raise HTTPException(status_code=400, detail="验证码错误")

        # 创建正式 token
        access_token = create_access_token(data={"sub": str(user.id)})

        add_log(db, user.id, "login", "auth",
                details=f"用户 {user.username} 通过 2FA 登录",
                ip_address=request.client.host if request.client else None)

        return {
            "access_token": access_token,
            "user": UserResponse.model_validate(user)
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail=f"验证失败: {str(e)}")
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/auth.py && git commit -m "feat: add 2FA login flow to auth API"
```

---

## Task 7: 管理员重置用户 2FA

**Files:**
- Modify: `backend/app/api/users.py`

- [ ] **Step 1: 添加管理员重置 2FA 端点**

在 `users.py` 的 `admin_router` 中添加：

```python
@admin_router.post("/users/{user_id}/reset-otp")
async def admin_reset_user_otp(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员重置用户 2FA"""
    # 检查权限
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")

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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/users.py && git commit -m "feat: add admin reset OTP endpoint"
```

---

## Task 8: 注册 OTP Router

**Files:**
- Modify: `backend/app/api/__init__.py`

- [ ] **Step 1: 注册 OTP Router**

在 `backend/app/api/__init__.py` 中添加：

```python
from app.api.otp import router as otp_router

# 在 main.py 或 app 初始化时注册
# app.include_router(otp_router)
```

- [ ] **Step 2: 在 main.py 中注册**

检查并修改 `backend/app/main.py`，添加 OTP router 注册：

```python
from app.api.otp import router as otp_router

app.include_router(otp_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/__init__.py backend/app/main.py && git commit -m "feat: register OTP router"
```

---

## Task 9: 前端 OTP API 客户端

**Files:**
- Create: `frontend/src/api/otp.ts`
- Modify: `frontend/src/api/index.ts`

- [ ] **Step 1: 创建 OTP API 客户端**

创建 `frontend/src/api/otp.ts`：

```typescript
import api from './index'

export interface OTPConfigResponse {
  enabled: boolean
  required_for_roles: string[]
}

export interface OTPStatusResponse {
  enabled: boolean
  verified: boolean
}

export interface OTPSetupResponse {
  secret: string
  otpauth_uri: string
  qr_code_base64: string
}

export const otpApi = {
  // 获取 2FA 配置
  getConfig: () => api.get<OTPConfigResponse>('/auth/otp/config'),

  // 获取 2FA 状态
  getStatus: () => api.get<OTPStatusResponse>('/auth/otp/status'),

  // 开始 2FA 绑定
  setup: () => api.post<OTPSetupResponse>('/auth/otp/setup'),

  // 验证 OTP 完成绑定
  verifySetup: (code: string) => api.post('/auth/otp/verify-setup', { code }),

  // 禁用 2FA
  disable: (code: string) => api.post('/auth/otp/disable', { code }),

  // 2FA 登录验证
  verifyLogin: (temp_token: string, code: string) =>
    api.post('/auth/otp/verify-login', { temp_token, code }),
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/otp.ts && git commit -m "feat: add OTP API client"
```

---

## Task 10: 前端登录页扩展

**Files:**
- Modify: `frontend/src/pages/LoginPage.vue`

- [ ] **Step 1: 添加 2FA 验证步骤**

在 `LoginPage.vue` 中添加以下响应式变量：

```typescript
// 2FA 验证状态
const requiresOtp = ref(false)
const tempToken = ref('')
const otpCode = ref('')
const otpLoading = ref(false)
```

添加 2FA 验证函数：

```typescript
async function handleOtpVerify() {
  if (!otpCode.value || otpCode.value.length !== 6) {
    showNotification('error', '请输入6位验证码')
    return
  }

  otpLoading.value = true
  try {
    const res = await otpApi.verifyLogin(tempToken.value, otpCode.value)
    token.value = res.data.access_token
    localStorage.setItem('token', res.data.access_token)
    await authStore.fetchUser()
    showNotification('success', '登录成功')
    router.push('/')
  } catch (e: any) {
    showNotification('error', '验证码错误', e.response?.data?.detail)
    otpCode.value = ''
  } finally {
    otpLoading.value = false
  }
}
```

修改登录函数处理 2FA 流程：

```typescript
async function handleLogin() {
  // ... 现有验证 ...

  try {
    const res = await api.post('/auth/login', {
      username: username.value,
      password: password.value,
      turnstile_token: turnstileToken.value
    })

    if (res.data.requires_otp && res.data.temp_token) {
      // 需要 2FA 验证
      requiresOtp.value = true
      tempToken.value = res.data.temp_token
      showNotification('info', '请输入验证码完成登录')
    } else {
      // 直接登录成功
      token.value = res.data.access_token
      localStorage.setItem('token', res.data.access_token)
      await authStore.fetchUser()
      showNotification('success', '登录成功')
      router.push('/')
    }
  } catch (e: any) {
    // 错误处理...
  }
}
```

- [ ] **Step 2: 添加 2FA 验证码输入 UI**

在模板中添加（条件渲染）：

```vue
<!-- 2FA 验证码输入 -->
<div v-if="requiresOtp" class="space-y-4">
  <div class="text-center">
    <p class="text-gray-600 mb-2">请输入 authenticator APP 中的验证码</p>
    <div class="flex justify-center gap-2">
      <input
        v-model="otpCode"
        type="text"
        maxlength="6"
        placeholder="000000"
        class="w-32 text-center text-2xl tracking-widest px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        @keyup.enter="handleOtpVerify"
      />
    </div>
  </div>

  <button
    @click="handleOtpVerify"
    :disabled="otpLoading"
    class="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
  >
    <svg v-if="otpLoading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
    </svg>
    {{ otpLoading ? '验证中...' : '验证并登录' }}
  </button>

  <button
    @click="requiresOtp = false; otpCode = ''; tempToken = ''"
    class="w-full py-2 text-gray-600 hover:text-gray-800 text-sm"
  >
    返回重新登录
  </button>
</div>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/LoginPage.vue && git commit -m "feat: add 2FA verification to login page"
```

---

## Task 11: 个人设置页面添加 2FA 管理

**Files:**
- Modify: `frontend/src/pages/admin/ProfilePage.vue`

- [ ] **Step 1: 添加 2FA 相关响应式变量**

```typescript
// 2FA
const otpConfig = ref<{ enabled: boolean; required_for_roles: string[] }>({ enabled: false, required_for_roles: [] })
const otpStatus = ref<{ enabled: boolean; verified: boolean }>({ enabled: false, verified: false })
const showOtpSetupModal = ref(false)
const otpSetupData = ref<{ secret: string; otpauth_uri: string; qr_code_base64: string } | null>(null)
const otpVerifyCode = ref('')
const otpLoading = ref(false)
const otpError = ref('')
```

- [ ] **Step 2: 添加 2FA 相关函数**

```typescript
async function loadOtpConfig() {
  try {
    const res = await otpApi.getConfig()
    otpConfig.value = res.data
  } catch (e) {
    console.error('Failed to load OTP config:', e)
  }
}

async function loadOtpStatus() {
  try {
    const res = await otpApi.getStatus()
    otpStatus.value = res.data
  } catch (e) {
    console.error('Failed to load OTP status:', e)
  }
}

async function handleOtpSetup() {
  otpError.value = ''
  otpLoading.value = true
  try {
    const res = await otpApi.setup()
    otpSetupData.value = res.data
    showOtpSetupModal.value = true
  } catch (e: any) {
    otpError.value = e.response?.data?.detail || '获取 2FA 设置失败'
  } finally {
    otpLoading.value = false
  }
}

async function handleOtpVerify() {
  if (!otpVerifyCode.value || otpVerifyCode.value.length !== 6) {
    otpError.value = '请输入6位验证码'
    return
  }

  otpLoading.value = true
  otpError.value = ''
  try {
    await otpApi.verifySetup(otpVerifyCode.value)
    showOtpSetupModal.value = false
    await loadOtpStatus()
    showNotification('success', '2FA 已启用')
  } catch (e: any) {
    otpError.value = e.response?.data?.detail || '验证失败'
  } finally {
    otpLoading.value = false
    otpVerifyCode.value = ''
  }
}

async function handleOtpDisable() {
  const code = prompt('请输入当前 authenticator APP 中的验证码以禁用 2FA：')
  if (!code) return

  try {
    await otpApi.disable(code)
    await loadOtpStatus()
    showNotification('success', '2FA 已禁用')
  } catch (e: any) {
    showNotification('error', '禁用失败', e.response?.data?.detail)
  }
}
```

- [ ] **Step 3: 在 onMounted 中加载数据**

```typescript
onMounted(async () => {
  await loadUserInfo()
  await loadPasskeyConfig()
  await loadCredentials()
  await loadOtpConfig()
  await loadOtpStatus()
})
```

- [ ] **Step 4: 添加 2FA 卡片 UI**

在模板中（在 Passkey 卡片后）添加：

```vue
<!-- 2FA Card -->
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-lg font-semibold">双因素认证 (2FA)</h2>
    <span v-if="otpStatus.enabled" class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">已启用</span>
    <span v-else class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">未启用</span>
  </div>

  <p class="text-sm text-gray-500 mb-4">
    使用 authenticator APP 生成验证码进行二次验证，提高账户安全性。
  </p>

  <div v-if="otpError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
    {{ otpError }}
  </div>

  <div class="flex gap-2">
    <button
      v-if="!otpStatus.enabled && otpConfig.enabled"
      @click="handleOtpSetup"
      :disabled="otpLoading"
      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
    >
      {{ otpLoading ? '加载中...' : '启用 2FA' }}
    </button>
    <button
      v-if="otpStatus.enabled"
      @click="handleOtpDisable"
      class="px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50"
    >
      禁用 2FA
    </button>
    <span v-if="!otpConfig.enabled" class="text-sm text-gray-400">
      系统未启用 2FA 功能
    </span>
  </div>
</div>

<!-- 2FA Setup Modal -->
<div v-if="showOtpSetupModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
  <div class="bg-white rounded-xl p-6 max-w-md w-full mx-4">
    <h3 class="text-lg font-semibold mb-4">启用双因素认证</h3>

    <div class="space-y-4">
      <div>
        <p class="text-sm text-gray-600 mb-2">1. 扫描下方二维码</p>
        <div class="flex justify-center">
          <img v-if="otpSetupData?.qr_code_base64"
               :src="`data:image/png;base64,${otpSetupData.qr_code_base64}`"
               alt="QR Code"
               class="w-48 h-48" />
        </div>
      </div>

      <div>
        <p class="text-sm text-gray-600 mb-1">2. 或手动输入密钥：</p>
        <code class="block bg-gray-100 p-2 rounded text-sm break-all">{{ otpSetupData?.secret }}</code>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">3. 输入 APP 中的验证码：</label>
        <input
          v-model="otpVerifyCode"
          type="text"
          maxlength="6"
          placeholder="000000"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div v-if="otpError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
        {{ otpError }}
      </div>

      <div class="flex gap-2 justify-end">
        <button
          @click="showOtpSetupModal = false; otpVerifyCode = ''"
          class="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          取消
        </button>
        <button
          @click="handleOtpVerify"
          :disabled="otpLoading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {{ otpLoading ? '验证中...' : '验证并启用' }}
        </button>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/admin/ProfilePage.vue && git commit -m "feat: add 2FA management to profile page"
```

---

## Task 12: 用户管理页面添加 2FA 列和重置功能

**Files:**
- Modify: `frontend/src/pages/admin/UsersPage.vue`

- [ ] **Step 1: 添加重置 2FA 按钮**

在操作列添加：

```vue
<button
  @click="handleResetOtp(user.id)"
  class="p-1.5 text-orange-500 hover:bg-orange-50 rounded"
  title="重置 2FA"
>
  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
  </svg>
</button>
```

- [ ] **Step 2: 添加 2FA 状态列**

在表格中添加状态图标列：

```vue
<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">2FA</th>
```

单元格：

```vue
<td class="px-4 py-3">
  <span v-if="user.otp_enabled" class="text-green-600" title="已启用">
    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
    </svg>
  </span>
  <span v-else class="text-gray-300" title="未启用">
    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
    </svg>
  </span>
</td>
```

- [ ] **Step 3: 添加重置函数**

```typescript
async function handleResetOtp(userId: number) {
  if (!confirm('确定要重置该用户的 2FA 吗？')) return

  try {
    await adminApi.resetUserOtp(userId)
    showNotification('success', '2FA 已重置')
    await loadUsers()
  } catch (e: any) {
    showNotification('error', '重置失败', e.response?.data?.detail)
  }
}
```

- [ ] **Step 4: 在 adminApi 中添加 resetUserOtp**

修改 `frontend/src/api/index.ts` 或创建 `frontend/src/api/admin.ts`：

```typescript
// 在 adminApi 中添加
resetUserOtp: (userId: number) => api.post(`/admin/users/${userId}/reset-otp`)
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/admin/UsersPage.vue frontend/src/api/index.ts && git commit -m "feat: add 2FA status and reset in users page"
```

---

## Task 13: 验证和测试

- [ ] **Step 1: 启动后端服务**

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- [ ] **Step 2: 检查数据库迁移**

确认 User 模型的新字段已添加到数据库：

```bash
cd backend
uv run python -c "from app.models.user import User; print([c.name for c in User.__table__.columns])"
```

- [ ] **Step 3: 添加系统设置**

在系统设置中添加：
- `totp_enabled`: `true`
- `totp_required_for_roles`: `["admin", "reviewer"]`

- [ ] **Step 4: 启动前端并测试**

```bash
cd frontend
npm run dev
```

测试流程：
1. 登录账号
2. 访问 /admin/profile
3. 启用 2FA（扫描二维码或手动输入 secret）
4. 退出登录
5. 重新登录，验证两步验证流程
6. 测试管理员重置 2FA

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: complete 2FA OTP implementation"
```

---

## 依赖汇总

```bash
# 后端依赖
uv pip install pyotp cryptography qrcode[pil]
```

---

## 注意事项

1. **临时 Token 存储**: 当前使用内存存储，生产环境应使用 Redis
2. **加密密钥**: 生产环境需要配置 `OTP_ENCRYPTION_KEY` 环境变量
3. **数据库迁移**: 需要确保数据库有 `otp_secret_encrypted`、`otp_enabled`、`otp_verified` 字段