# Passkey（通行密钥）设计方案

**日期：** 2026-07-01
**状态：** 已批准

## 1. 功能概述

在系统中添加 WebAuthn/FIDO2 通行密钥支持，允许用户通过生物识别（指纹、面容）或硬件密钥登录，替代传统的用户名密码。

## 2. 用户流程

### 2.1 注册 Passkey（登录后）

- 用户登录后进入「个人设置」页面
- 点击「绑定通行密钥」按钮
- 浏览器弹出 WebAuthn 注册窗口（使用设备指纹、面部识别或硬件密钥）
- 注册成功后，显示已绑定的 Passkey 设备列表

### 2.2 登录（支持 Passkey + 密码）

- 登录页显示两个入口：通行密钥登录、账号密码登录
- 用户可任选一种方式登录
- Passkey 登录时浏览器自动弹出认证窗口

### 2.3 管理员管理

- 用户列表显示 Passkey 绑定状态
- 管理员可重置用户 Passkey（删除所有凭证）
- 管理员可强制要求指定角色必须绑定 Passkey

## 3. 数据库设计

### 3.1 新增表：`user_passkeys`

```sql
CREATE TABLE user_passkeys (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    credential_id VARCHAR(255) NOT NULL UNIQUE,  -- 公钥凭证ID
    public_key TEXT NOT NULL,                    -- 公钥
    counter INTEGER DEFAULT 0,                   -- 签名计数器（防重放）
    device_name VARCHAR(255),                    -- 设备名称（如 "iPhone 15"）
    created_at DATETIME DEFAULT NOW(),
    last_used_at DATETIME
);
-- 一个用户可绑定多个 Passkey
CREATE INDEX idx_user_passkeys_user ON user_passkeys(user_id);
```

### 3.2 用户表扩展

在 `User` 模型中添加字段：
- `passkey_required`: Boolean, default=False（是否强制要求绑定 Passkey）

### 3.3 新增系统设置

| Key | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `passkey_enabled` | Boolean | false | 是否启用 Passkey 功能 |
| `passkey_require_for_roles` | JSON | [] | 强制要求绑定 Passkey 的角色列表 |

## 4. API 设计

### 4.1 认证 API（`/api/auth/passkey/`）

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/config` | GET | 获取 Passkey 配置（是否启用） | 否 |
| `/register-options` | GET | 获取注册选项（challenge, RP信息） | 是 |
| `/register-verify` | POST | 验证注册响应，保存凭证 | 是 |
| `/login-options` | POST | 获取登录选项（允许的凭证列表） | 否 |
| `/login-verify` | POST | 验证登录响应，签发 JWT | 否 |

### 4.2 用户 Passkey API（`/api/passkey/`）

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/credentials` | GET | 获取当前用户的所有 Passkey | 是 |
| `/credentials/{id}` | DELETE | 删除指定的 Passkey | 是 |
| `/rename-credential/{id}` | PATCH | 重命名 Passkey 设备名称 | 是 |

### 4.3 管理 API（`/api/users/{id}/`）

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/passkey-credentials` | GET | 管理员查看用户的 Passkey（不含私钥） | 管理员 |
| `/reset-passkey` | POST | 管理员重置用户的所有 Passkey | 管理员 |
| `/force-passkey` | PUT | 管理员设置用户是否必须绑定 Passkey | 管理员 |

## 5. 前端页面

### 5.1 登录页 (`LoginPage.vue`)

- 添加「通行密钥登录」标签页（默认选中）
- 点击后调用 `/passkey/login-options` 获取挑战
- 调用 `navigator.credentials.get()` 弹出认证窗口
- 验证成功后跳转到首页

### 5.2 个人设置页（扩展或新建）

- 「通行密钥」区块：
  - 显示已绑定的设备列表（设备名称、创建时间）
  - 「绑定新设备」按钮
  - 每条记录可删除/重命名
- 调用 `/passkey/register-options` 获取注册选项
- 调用 `navigator.credentials.create()` 完成注册

### 5.3 用户管理页（`UsersPage.vue`）

- 列表增加「Passkey」列（显示绑定的设备数量）
- 用户详情可重置 Passkey、设置强制绑定

### 5.4 系统设置页（`SettingsPage.vue`）

- 增加 Passkey 设置区块：
  - 启用/禁用 Passkey 功能
  - 配置哪些角色必须绑定 Passkey

## 6. 依赖

### 6.1 后端

```bash
uv pip install pywebauthn>=9.0.0
```

### 6.2 前端

- WebAuthn API 已内置于现代浏览器，无需额外依赖
- 可选添加 TypeScript 类型定义

## 7. WebAuthn 流程

### 7.1 注册流程

1. 前端请求 `GET /api/auth/passkey/register-options` → 后端生成 challenge，返回 RP 信息
2. 前端调用 `navigator.credentials.create({ publicKey })`
3. 前端将 `credential` 发送到 `POST /api/auth/passkey/register-verify`
4. 后端验证签名，保存公钥和 credential_id

### 7.2 登录流程

1. 前端请求 `POST /api/auth/passkey/login-options`（带 username）
2. 后端返回该用户允许的 credential IDs 和 challenge
3. 前端调用 `navigator.credentials.get({ publicKey })`
4. 前端将 authenticatorResponse 发送到 `POST /api/auth/passkey/login-verify`
5. 后端验证签名，检查 counter，签发 JWT

## 8. 安全考虑

- Challenge 使用后立即失效，防止重放攻击
- 签名计数器用于检测设备克隆
- RP ID 限制在当前域名
- 管理员重置 Passkey 时记录审计日志
- 用户的 Passkey 强制绑定状态仅管理员可修改

## 9. 实现任务

1. 安装 pywebauthn 依赖
2. 创建 UserPasskey 模型
3. 添加 passkey_required 字段到 User 模型
4. 添加系统设置项
5. 实现 Passkey 认证 API
6. 实现用户 Passkey 管理 API
7. 实现管理员 Passkey 管理 API
8. 修改登录页添加 Passkey 登录入口
9. 创建/扩展个人设置页面
10. 修改用户管理页面
11. 修改系统设置页面