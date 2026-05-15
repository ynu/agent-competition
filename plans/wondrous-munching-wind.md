# 文件选择器功能模块实现计划

## Context

需要实现一个文件选择器功能，用于：
1. Markdown 文本编辑器工具栏中插入文件
2. 图片路径输入框旁添加文件选择按钮
3. 左侧树状目录结构，右侧文件列表（详情/缩略图模式）
4. 支持上传文件（点击上传或拖拽），显示圆形进度条
5. 双击或右键打开预览
6. **支持用户创建和管理目录（真实文件系统）**

## 实现方案

### 1. 后端 API（backend/app/api/media.py）

基于配置的 `MEDIA_DIR` 进行文件管理：

```python
# 目录操作
@router.get("/dirs")                    # 获取目录树
@router.post("/dirs")                   # 创建目录
@router.delete("/dirs")                 # 删除目录

# 文件操作
@router.get("/files")                   # 获取文件列表
@router.post("/upload")                 # 上传文件（支持指定目录）
@router.delete("/{path:path}")          # 删除文件
@router.post("/move")                   # 移动/重命名文件

# 预览
@router.get("/preview/{path:path}")     # 预览文件
@router.get("/download/{path:path}")    # 下载文件
```

关键特性：
- 基于配置的 `MEDIA_DIR` 进行文件浏览
- 支持目录树结构和文件列表
- 文件类型过滤（图片、PDF、音视频等）
- 上传进度跟踪
- 支持目录创建、文件移动/重命名
- 返回文件 URL 用于插入编辑器

### 2. 配置更新（backend/app/core/config.py）

```python
# 媒体文件配置
MEDIA_DIR: str = "./media"  # 统一媒体目录
MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
MEDIA_ALLOWED_EXTENSIONS: list = ["pdf", "jpg", "jpeg", "png", "gif", "svg", "webp", "mp4", "webm", "mp3", "wav", "doc", "docx", "zip"]
```

### 3. 前端 API（frontend/src/api/index.ts）

添加媒体 API：

```typescript
export const mediaApi = {
  listDirs: () => api.get('/media/dirs'),
  createDir: (data: { name: string; parent?: string }) => api.post('/media/dirs', data),
  deleteDir: (path: string) => api.delete(`/media/dirs?path=${encodeURIComponent(path)}`),
  listFiles: (params: { path?: string }) => api.get('/media/files', { params }),
  upload: (data: FormData, onProgress?: (p: number) => void) => api.post('/media/upload', data, { onUploadProgress: onProgress }),
  deleteFile: (path: string) => api.delete(`/media/${encodeURIComponent(path)}`),
  moveFile: (data: { from: string; to: string }) => api.post('/media/move', data),
  getUrl: (path: string) => `${import.meta.env.VITE_API_URL}/media/preview/${encodeURIComponent(path)}`
}
```

### 4. 文件选择器组件（frontend/src/components/FileSelector.vue）

核心功能：
- **目录树**（左侧）：显示文件夹结构，点击切换目录，支持创建目录
- **文件列表**（右侧）：支持列表视图和缩略图视图切换
- **文件上传**：支持点击选择和拖拽上传，显示圆形进度条
- **文件预览**：双击或右键菜单打开预览（图片/PDF/音视频）
- **选择回调**：选中文件后回调返回 URL 或路径

Props:
```typescript
interface Props {
  show: boolean
  mode?: 'insert' | 'select'  // insert=插入编辑器, select=选择文件路径
  accept?: string  // 文件类型过滤，如 'image/*,.pdf,.mp4'
  initialPath?: string
}
```

Emits:
```typescript
emit('select', { path: string, url: string })
emit('close')
```

### 5. 工具栏按钮集成（编辑页面）

在 ContentsPage.vue 等编辑页面的 Markdown 工具栏添加按钮：
- 插入图片按钮
- 插入文件按钮
- 点击打开 FileSelector 组件
- 选择后自动插入 Markdown 语法

```html
<div class="editor-toolbar">
  <button @click="openFileSelector('image')" title="插入图片">
    <IconImage />
  </button>
  <button @click="openFileSelector('file')" title="插入文件">
    <IconFile />
  </button>
</div>

<FileSelector
  :show="showFileSelector"
  mode="insert"
  :accept="fileAccept"
  @select="onFileSelected"
  @close="showFileSelector = false"
/>
```

### 6. 输入框文件选择按钮（frontend/src/components/FileInput.vue）

可复用的输入框组件，带文件选择按钮：

```html
<div class="relative">
  <input v-model="modelValue" />
  <button @click="openFileSelector">选择文件</button>
</div>
```

Props: `modelValue`, `accept`, `placeholder`
Emits: `update:modelValue`

## 关键文件

### 新建文件
- `backend/app/api/media.py` - 后端媒体管理 API
- `frontend/src/components/FileSelector.vue` - 文件选择器组件
- `frontend/src/components/FileInput.vue` - 文件输入框组件

### 修改文件
- `backend/app/core/config.py` - 添加 MEDIA_DIR 配置
- `frontend/src/api/index.ts` - 添加 mediaApi
- `frontend/src/pages/admin/ContentsPage.vue` - 集成文件选择器

## 验证步骤

1. 启动后端服务
2. 启动前端服务
3. 访问内容管理页面，点击创建/编辑内容
4. 在编辑器工具栏或封面图片输入框旁点击文件选择按钮
5. 测试文件浏览、上传、选择功能
6. 验证插入 Markdown 后渲染效果