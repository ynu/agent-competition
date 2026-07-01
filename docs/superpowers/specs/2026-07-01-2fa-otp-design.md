# 2FA OTP (TOTP) 实现方案

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为智能体大赛网站添加 TOTP 二次认证功能，支持用户绑定 authenticator APP，管理员可强制要求特定角色启用 2FA。

**Architecture:**
- 后端：扩展 User 模型添加 2FA 字段，使用 pyotp 生成/验证 TOTP，cryptography 进行 secret 加密存储
- 前端：扩展登录页支持两步验证，扩展个人设置页面管理 2FA，扩展用户管理页面显示状态和重置功能
- 系统设置：支持全局开关和角色级别强制要求

**Tech Stack:** pyotp, cryptography (Fernet), Vue 3 + Pinia + TailwindCSS

---

## 1. 后端数据模型

### 1.1 User 模型扩展

在 `backend/app/models/user.py` 中添加字段：

```python
otp_secret_encrypted = Column(String(500), nullable=True, comment="加密的 OTP Secret")
otp_enabled = Column(Boolean, default=False, comment="是否启用 2FA")
otp_verified = Column(Boolean, default=False, comment="是否完成 2FA 绑定验证")
```

### 1.2 OTP Secret 存储

- Secret 生成后立即加密存储
- 验证时解密后使用
- 使用 Fernet 对称加密（AES-128-CBC）

---

## 2. 后端 API 设计

### 2.1 用户 2FA API (`backend/app/api/otp.py`)

```
GET  /auth/otp/config
     - 获取 2FA 配置
     - 返回: { enabled: bool, required_for_roles: str[] }

POST /auth/otp/setup
     - 开始 2FA 绑定
     - 返回: { secret: str, otpauth_uri: str, qr_code_base64: str }
     - 说明: secret 只在此接口返回一次

POST /auth/otp/verify-setup
     - 验证 OTP 完成绑定
     - 请求: { code: str }
     - 验证成功后设置 otp_enabled=true, otp_verified=true

POST /auth/otp/disable
     - 禁用 2FA
     - 请求: { code: str }
     - 验证当前 OTP 后禁用

GET  /auth/otp/status
     - 获取当前用户 2FA 状态
     - 返回: { enabled: bool, verified: bool }
```

### 2.2 登录流程 API

```
POST /auth/login
     - 第一步验证
     - 返回 TokenResponse 中增加字段: { requires_otp: bool, temp_token?: str }
     - 如果 requires_otp=true，不返回 access_token，改为返回 temp_token

POST /auth/otp/verify-login
     - 第二步验证 OTP
     - 请求: { temp_token: str, code: str }
     - 验证成功后返回完整的 TokenResponse
```

### 2.3 管理员 API

在 `backend/app/api/users.py` 中添加：

```
POST /admin/users/{id}/reset-otp
     - 重置用户 2FA
     - 清除 otp_secret_encrypted, otp_enabled, otp_verified
```

---

## 3. 系统设置

### 3.1 设置项

```
totp_enabled: bool = true
totp_required_for_roles: str[] = ["admin", "reviewer"]
```

### 3.2 强制要求逻辑

- 登录时，如果用户角色在 required_for_roles 中但未启用 2FA，强制引导到绑定页面
- 用户绑定完成前无法访问系统功能

---

## 4. 前端设计

### 4.1 登录页扩展 (`pages/LoginPage.vue`)

```
第一步: 用户名 + 密码 + Turnstile（现有）
       ↓
第二步（仅当 requires_otp=true）: OTP 验证码输入
       - 6 位数字输入
       - 60 秒倒计时显示（可选）
       - 返回重试选项
       ↓
完成: 获取 token，跳转到首页
```

### 4.2 个人设置页面扩展 (`pages/admin/ProfilePage.vue`)

在通行密钥卡片旁添加 2FA 卡片：

```
┌─────────────────────────────┐
│ 双因素认证 (2FA)            │
├─────────────────────────────┤
│ 状态: ✅ 已启用 / ❌ 未启用 │
│                             │
│ [启用 2FA] 按钮（未启用时） │
│ [查看密钥] [禁用 2FA]       │
│   （已启用时）              │
└─────────────────────────────┘
```

#### 启用流程弹窗

```
┌──────────────────────────────────────┐
│ 启用双因素认证                        │
├──────────────────────────────────────┤
│                                      │
│ 1. 扫描二维码                         │
│    [QR Code Image]                   │
│                                      │
│ 2. 或手动输入密钥:                    │
│    XXXX XXXX XXXX XXXX XXXX XXXX     │
│                                      │
│ 3. 输入 APP 中的验证码:               │
│    [______]                          │
│                                      │
│        [取消]  [验证并启用]           │
└──────────────────────────────────────┘
```

### 4.3 用户管理页面扩展 (`pages/admin/UsersPage.vue`)

- 列表增加 2FA 状态列（图标：绿色已启用/灰色未启用）
- 操作列增加"重置 2FA"按钮

---

## 5. 依赖安装

```bash
# 后端
uv pip install pyotp cryptography
```

---

## 6. 安全考虑

1. **Secret 加密**: 使用 Fernet 对称加密存储 OTP Secret
2. **Secret 只返回一次**: setup 接口返回 secret 后不再暴露
3. **暴力破解防护**: 登录时 OTP 验证失败锁定（可选，5次失败后锁定5分钟）
4. **日志记录**: 2FA 启用/禁用/重置操作记录到 Log 表

---

## 7. 测试计划

1. 后端 TOTP 生成和验证测试
2. 登录流程：普通用户（无 2FA）
3. 登录流程：普通用户（已启用 2FA）
4. 登录流程：强制 2FA 用户（未绑定）
5. 管理员重置 2FA
6. 前端 UI 交互测试