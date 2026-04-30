# 项目说明

基于 Vue 3 + Vite + Element Plus 的前端项目，支持登录鉴权、路由守卫与持久化状态。

---

## 一、目录结构

```
workspace/
├── .env                    # 环境变量（根配置）
├── .env.development        # 开发环境变量
├── .env.production         # 生产环境变量
├── .gitignore
├── .vscode/                # VS Code 工作区配置
│   └── extensions.json    # 推荐扩展
├── index.html              # 应用入口 HTML
├── jsconfig.json           # JS 路径别名等配置（@ -> src）
├── package.json            # 依赖与脚本
├── pnpm-lock.yaml          # pnpm 锁文件
├── pnpm-workspace.yaml     # pnpm 工作区配置
├── vite.config.js          # Vite 构建配置（Vue、Tailwind、路径别名）
├── public/                 # 静态资源（不经过 Vite 处理）
│   └── vite.svg
├── README.md
└── src/
    ├── main.js             # 应用入口，挂载 Vue 应用
    ├── App.vue              # 根组件
    ├── api/                 # 接口封装
    │   ├── index.js         # 统一导出接口
    │   └── user.js          # 用户相关接口（如 myuserinfo）
    ├── assets/              # 资源文件
    │   └── styles/
    │       └── main.css     # 全局样式（含 Tailwind 入口）
    ├── composables/         # 组合式逻辑复用
    │   └── useHttp.js       # Axios 实例、请求/响应拦截、Token、错误提示
    ├── router/
    │   └── index.js         # Vue Router 配置、路由守卫（登录鉴权）
    ├── store/
    │   └── user.js          # Pinia 用户状态（userInfo、token、持久化）
    └── views/               # 页面级组件
        ├── home/
        │   └── index.vue    # 首页（需登录）
        └── login/
            └── index.vue    # 登录页
```

---

## 二、依赖说明

### 生产依赖（dependencies）

| 依赖 | 作用 |
|------|------|
| **vue** | Vue 3 核心框架 |
| **vue-router** | 单页路由，配合路由守卫做登录鉴权 |
| **pinia** | 状态管理（用户信息、登录态） |
| **pinia-plugin-persistedstate** | Pinia 持久化插件，将指定 state 存到 localStorage |
| **element-plus** | UI 组件库 |
| **@element-plus/icons-vue** | Element Plus 图标库 |
| **axios** | HTTP 请求，在 `useHttp.js` 中封装为带 Token 与错误处理的实例 |
| **dayjs** | 日期时间处理 |
| **tailwindcss** | 原子化 CSS 框架 |
| **@tailwindcss/vite** | Tailwind 的 Vite 插件 |
| **typed.js** | 打字机效果等动效 |

### 开发依赖（devDependencies）

| 依赖 | 作用 |
|------|------|
| **vite** | 构建与开发服务器 |
| **@vitejs/plugin-vue** | Vite 的 Vue 3 支持 |

---

## 三、环境要求与命令

- **Node**：建议使用 `~22.14.0`（见 `package.json` 中 `engines`）
- **包管理器**：推荐使用 **pnpm**

### 安装依赖

```bash
pnpm install
```

### 本地开发

```bash
pnpm dev
```

启动后访问控制台给出的本地地址（一般为 `http://localhost:5173`）。  
开发环境接口基础地址由 `.env.development` 中的 `VITE_APP_BASE_URL` 决定。

### 生产构建

```bash
pnpm build
```

构建产物默认输出到项目根目录的 `dist/`，可用于部署到静态服务器或配合后端使用。

### 预览构建结果

```bash
pnpm preview
```

在本地启动静态服务预览 `dist/` 内容，用于上线前自测。

---

## 四、环境变量说明

- **VITE_APP_BASE_URL**：接口基础地址，在 `.env.development` / `.env.production` 中配置，供 `useHttp.js` 中 axios 的 `baseURL` 使用。

如需新增变量，请以 `VITE_` 开头，方可在前端代码中通过 `import.meta.env.VITE_*` 访问。
