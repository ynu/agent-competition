# 智能体大赛网站 - 技术规格说明

## 1. 项目概述

- **项目名称**: 智能体大赛网站 (Agent Competition)
- **项目类型**: 全栈 Web 应用 (FastAPI + Vue/Vite/TailwindCSS)
- **核心功能**: 智能体大赛报名、作品展示、评审管理的一站式平台
- **目标用户**: 参赛学生、评审专家、赛事管理员
- **依赖管理**: uv (Python), npm (Node.js)

## 2. 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据库**: SQLite (默认) / MySQL / PostgreSQL
- **认证**: JWT + 统一身份认证 (OAuth2/LDAP)
- **静态页面生成**: Jinja2
- **依赖管理**: uv

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite 8
- **CSS**: TailwindCSS 4
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP**: Axios

## 3. 数据库设计

### 3.1 枚举类型

```python
# 用户角色
class UserRole(str, Enum):
    USER = "user"        # 普通用户
    REVIEWER = "reviewer"  # 评审用户
    ADMIN = "admin"      # 超级用户

# 队伍状态
class TeamStatus(str, Enum):
    PENDING = "pending"    # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝

# 作品状态
class WorkStatus(str, Enum):
    PENDING = "pending"    # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝

# 内容类型
class ContentType(str, Enum):
    PAGE = "page"        # 页面
    CATEGORY = "category"  # 栏目
    POST = "post"        # 文章

# 内容格式
class ContentFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
```

### 3.2 用户表 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| username | String(100) | 用户名（学工号），唯一 |
| nickname | String(100) | 显示名称 |
| email | String(255) | 邮箱，唯一 |
| hashed_password | String(255) | 密码哈希 |
| role | Enum | 普通用户/评审用户/超级用户 |
| auth_source | String(50) | 认证来源 (local/unified) |
| is_active | Boolean | 是否启用 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.3 队伍表 (teams)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| name | String(100) | 队名 |
| description | Text | 队伍描述 |
| leader_id | Integer | 队长用户ID，外键 |
| status | Enum | 待审核/通过/拒绝 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.4 队伍成员表 (team_members)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| team_id | Integer | 队伍ID，外键 |
| user_id | Integer | 用户ID，外键 |
| student_id | String(50) | 学工号 |
| name | String(100) | 姓名 |
| is_leader | Boolean | 是否队长 |
| created_at | DateTime | 创建时间 |

### 3.5 作品表 (works)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| team_id | Integer | 队伍ID，外键 |
| name | String(200) | 作品名称 |
| description | Text | 作品描述 |
| theme | String(100) | 主题 |
| agent_url | String(500) | 智能体URL |
| agent_editor_url | String(500) | 智能体编排URL |
| pdf_file | String(500) | PDF文件路径 |
| video_file | String(500) | 视频文件路径 |
| vote_count | Integer | 投票数 |
| score | Float | 评审分数 |
| status | Enum | 待审核/通过/拒绝 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.6 投票表 (votes)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| user_id | Integer | 用户ID，外键 |
| work_id | Integer | 作品ID，外键 |
| created_at | DateTime | 投票时间 |

### 3.7 评审表 (reviews)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| work_id | Integer | 作品ID，外键 |
| user_id | Integer | 评审用户ID，外键 |
| score | Float | 分数 (0-100) |
| comment | Text | 评价 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.8 内容表 (contents)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| title | String(200) | 标题 |
| slug | String(200) | 别名（URL），唯一 |
| type | Enum | 页面/栏目/文章 |
| content | Text | 内容 |
| content_format | Enum | markdown/html |
| parent_id | Integer | 父级ID，外键 |
| order | Integer | 排序 |
| is_published | Boolean | 是否发布 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.9 配置表 (settings)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| key | String(100) | 键，唯一 |
| value | Text | 值 |
| description | String(500) | 描述 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.10 日志表 (logs)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| user_id | Integer | 用户ID，外键 |
| action | String(50) | 操作类型 |
| resource | String(50) | 资源类型 |
| details | Text | 详情 |
| ip_address | String(50) | IP地址 |
| created_at | DateTime | 创建时间 |

## 4. API 设计

### 4.1 认证 API

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | /api/auth/login | 账号密码登录 | 否 |
| POST | /api/auth/unified-auth | 统一身份认证登录 | 否 |
| POST | /api/auth/logout | 登出 | 是 |
| GET | /api/auth/me | 获取当前用户 | 是 |

### 4.2 用户 API

| 方法 | 路径 | 描述 | 认证 | 权限 |
|------|------|------|------|------|
| GET | /api/users | 用户列表 | 是 | 管理员 |
| POST | /api/users | 创建用户 | 是 | 管理员 |
| GET | /api/users/{id} | 用户详情 | 是 | 管理员 |
| PUT | /api/users/{id} | 更新用户 | 是 | 管理员 |
| DELETE | /api/users/{id} | 删除用户 | 是 | 管理员 |

### 4.3 队伍 API

| 方法 | 路径 | 描述 | 认证 | 权限 |
|------|------|------|------|------|
| GET | /api/teams | 队伍列表 | 是 | 全部 |
| POST | /api/teams | 创建队伍 | 是 | 登录用户 |
| GET | /api/teams/{id} | 队伍详情 | 是 | 全部 |
| PUT | /api/teams/{id} | 更新队伍 | 是 | 队长 |
| DELETE | /api/teams/{id} | 删除队伍 | 是 | 队长 |
| POST | /api/teams/{id}/join | 加入队伍 | 是 | 登录用户 |
| PUT | /api/teams/{id}/audit | 审核队伍 | 是 | 评审/管理员 |
| GET | /api/teams/my/team | 我的队伍 | 是 | 登录用户 |

### 4.4 作品 API

| 方法 | 路径 | 描述 | 认证 | 权限 |
|------|------|------|------|------|
| GET | /api/works | 作品列表 | 否 | 全部 |
| POST | /api/works | 创建作品 | 是 | 队长 |
| GET | /api/works/{id} | 作品详情 | 是 | 全部 |
| PUT | /api/works/{id} | 更新作品 | 是 | 队长 |
| DELETE | /api/works/{id} | 删除作品 | 是 | 队长 |
| POST | /api/works/{id}/vote | 投票 | 是 | 登录用户 |
| GET | /api/works/my/works | 我的作品 | 是 | 队长 |

### 4.5 评审 API

| 方法 | 路径 | 描述 | 认证 | 权限 |
|------|------|------|------|------|
| GET | /api/reviews | 评审列表 | 是 | 评审/管理员 |
| POST | /api/reviews | 创建评审 | 是 | 评审 |
| PUT | /api/reviews/{id} | 更新评审 | 是 | 评审 |
| GET | /api/reviews/my-reviews | 我的评审 | 是 | 评审 |

### 4.6 内容 API

| 方法 | 路径 | 描述 | 认证 | 权限 |
|------|------|------|------|------|
| GET | /api/contents | 内容列表 | 否 | 全部 |
| GET | /api/contents/tree | 内容树 | 是 | 全部 |
| GET | /api/contents/slug/{slug} | 内容(别名) | 否 | 全部 |
| POST | /api/contents | 创建内容 | 是 | 登录用户 |
| PUT | /api/contents/{id} | 更新内容 | 是 | 登录用户 |
| DELETE | /api/contents/{id} | 删除内容 | 是 | 登录用户 |
| POST | /api/contents/{id}/generate-static | 生成静态 | 是 | 登录用户 |

### 4.7 配置 API

| 方法 | 路径 | 描述 | 认证 | 权限 |
|------|------|------|------|------|
| GET | /api/settings | 配置列表 | 是 | 管理员 |
| GET | /api/settings/{key} | 配置详情 | 是 | 管理员 |
| PUT | /api/settings/{key} | 更新配置 | 是 | 管理员 |
| POST | /api/settings/init | 初始化配置 | 是 | 管理员 |

### 4.8 日志 API

| 方法 | 路径 | 描述 | 认证 | 权限 |
|------|------|------|------|------|
| GET | /api/logs | 日志列表 | 是 | 评审/管理员 |
| GET | /api/logs/actions | 操作类型 | 是 | 评审/管理员 |
| GET | /api/logs/resources | 资源类型 | 是 | 评审/管理员 |
| GET | /api/logs/statistics | 统计信息 | 是 | 评审/管理员 |

## 5. 功能模块

### 5.1 前台功能

#### 5.1.1 首页 (/)
- 展示大赛主题（标题、副标题）
- 展示最新动态（从内容管理系统获取）
- 展示参赛作品列表
- 统计信息：参赛作品数、奖项数、奖金总额
- 大赛流程时间轴
- 快捷导航：查看作品、立即报名

#### 5.1.2 作品展览 (/works)
- 网格展示所有已通过审核的作品
- 显示：作品名称、描述、主题、投票数
- 投票功能（需登录，每人每天5票，可投不同作品）
- 分页显示

#### 5.1.3 统一身份认证登录
- 支持两种登录方式：
  1. 账号密码登录
  2. 统一身份认证（SSO）
- SSO 模式支持：
  - 从 Header 自动获取用户信息 (X-Remote-User, X-Remote-Nickname, X-Remote-Email)
  - 授权码登录 (格式: username|nickname|email)
- 首次登录自动创建用户（默认为普通用户）

#### 5.1.4 内容展示
- 静态页面展示
- 支持 Markdown/HTML 渲染

### 5.2 后台管理

#### 5.2.1 仪表盘 (/admin)
- 统计卡片：用户数、队伍数、作品数、投票数
- 最近操作日志

#### 5.2.2 用户管理 (/admin/users)
- 用户列表表格（分页、搜索）
- 角色分配：普通用户、评审用户、超级用户
- 启用/禁用
- 手动创建用户

#### 5.2.3 队伍管理 (/admin/teams)
- 队伍列表表格（分页、状态筛选）
- 成员管理（学工号、姓名验证）
- 审核功能（审批加入申请）
- 业务规则：
  - 成员1-5人
  - 不能重复组队
  - 学工号唯一性校验

#### 5.2.4 作品管理 (/admin/works)
- 作品列表（分页、状态筛选）
- 作品信息：
  - 名称（必填）
  - 描述（必填）
  - 主题（下拉选择）
  - 智能体URL（可选）
  - 智能体编排URL（可选）
  - PDF文档（≤10MB）
  - 视频MP4（≤50MB）
- 审核功能

#### 5.2.5 评审管理 (/admin/reviews)
- 待评审作品列表
- 筛选功能：
  - 按队伍名称
  - 按作品名称
  - 按是否已打分
- 快捷操作：
  - 点击URL新窗口打开
  - PDF/MP4弹窗显示/播放
  - 打分（0-100分）
  - 输入评价
  - 保存、详情按钮
- 点击作品名称进入详情页

#### 5.2.6 内容管理 (/admin/contents)
- 栏目管理（树形结构）
- 内容管理
- 编辑器：Markdown/HTML 双模式
- 实时预览
- 发布/取消发布
- 一键生成静态页面

#### 5.2.7 配置管理 (/admin/settings)

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| max_votes | 5 | 每人最大投票数（0表示不限制） |
| max_team_members | 5 | 队伍最大成员数 |
| max_works_per_team | 5 | 每队最大作品数 |
| registration_start | - | 报名开始时间 (ISO格式) |
| registration_end | - | 报名结束时间 (ISO格式) |
| submission_start | - | 作品提交开始时间 (ISO格式) |
| submission_end | - | 作品提交截止时间 (ISO格式) |
| voting_start | - | 投票开始时间 (ISO格式) |
| voting_end | - | 投票结束时间 (ISO格式) |
| competition_theme | 智能体创新大赛 | 主题名称 |
| competition_description | - | 主题描述 |
| themes | 智能问答,Agent工作流,... | 作品主题选项(逗号分隔) |
| cas_enabled | true | 是否启用统一身份认证 |
| cas_base_url | https://ids.ynu.edu.cn/authserver | CAS服务地址 |
| base_url | http://localhost:5173 | 应用基础URL |

#### 5.2.8 日志管理 (/admin/logs)
- 日志列表（分页）
- 筛选：时间范围、操作用户、操作类型
- 日志类型：登录、新增、编辑、删除

## 6. 权限设计 (RBAC)

### 6.1 角色说明

| 角色 | 权限 |
|------|------|
| 普通用户 (user) | 报名、创建队伍、加入队伍、提交作品、投票 |
| 评审用户 (reviewer) | 审核队伍、审核作品、评审打分、查看日志 |
| 超级用户 (admin) | 全部权限 |

### 6.2 路由权限

- `/admin` - 需要登录
- `/admin/users` - 需要管理员权限
- `/admin/settings` - 需要管理员权限
- `/admin/reviews` - 需要评审权限
- `/admin/logs` - 需要评审权限
- `/admin/teams` - 需要登录
- `/admin/works` - 需要登录
- `/admin/contents` - 需要登录

## 7. 统一身份认证

### 7.1 SSO Header 模式
从 HTTP Header 获取用户信息：
- `X-Remote-User`: 用户名
- `X-Remote-Nickname`: 昵称
- `X-Remote-Email`: 邮箱

### 7.2 授权码模式
格式：`username|nickname|email`

## 8. 项目结构

```
agent-competition/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── teams.py
│   │   │   ├── works.py
│   │   │   ├── reviews.py
│   │   │   ├── contents.py
│   │   │   ├── settings.py
│   │   │   └── logs.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── team.py
│   │   │   ├── work.py
│   │   │   ├── content.py
│   │   │   └── setting.py
│   │   └── schemas/
│   ├── main.py
│   ├── init_db.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── admin/
│   │   │   ├── HomePage.vue
│   │   │   ├── WorksPage.vue
│   │   │   ├── LoginPage.vue
│   │   │   └── ...
│   │   ├── router/
│   │   ├── stores/
│   │   └── App.vue
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── README.md
└── SPEC.md
```

## 9. 快速开始

### 9.1 后端启动

```bash
cd backend

# 安装依赖
uv pip install -e .

# 初始化数据库
uv run python init_db.py

# 启动服务
uv run python main.py
```

后端地址: http://localhost:8000
API文档: http://localhost:8000/docs

### 9.2 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端地址: http://localhost:5173

### 9.3 登录信息

- 管理员账号: admin / admin123

## 10. 配置说明

### 10.1 数据库配置

修改 `backend/app/core/config.py` 或创建 `.env` 文件：

```env
# SQLite (默认)
DATABASE_URL=sqlite:///./agent_competition.db

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 10.2 JWT 配置

```env
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 11. UI 设计

### 11.1 前台页面

- **首页**: 渐变背景、动画效果、统计卡片、大赛流程时间轴
- **作品展览**: 卡片布局、投票按钮、分页
- **登录页**: 现代化设计、图标输入框、加载动画

### 11.2 后台页面

- **仪表盘**: 统计卡片、最近操作
- **管理页面**: 表格列表、筛选、分页、操作按钮
- **评审页面**: 快捷操作、弹窗预览、打分评价