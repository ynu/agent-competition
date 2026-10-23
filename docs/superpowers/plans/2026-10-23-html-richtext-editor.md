# HTML 富文本编辑器（wangEditor 5）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 内容管理弹窗中，当内容格式选 HTML 时用 wangEditor 5 替代 textarea，支持粘贴保留格式、所见即所得编辑、源码查看/编辑。

**Architecture:** 新建独立组件 `RichTextEditor.vue`（Toolbar + Editor + 源码 textarea 三态切换），通过 v-model 与父页面通信；`ContentsPage.vue` 按 `content_format` 分流到 RichTextEditor 或现有 textarea。Markdown 路径完全不动。

**Tech Stack:** `@wangeditor/editor` + `@wangeditor/editor-for-vue@next`（Vue 3 适配）、Vue 3 Composition API、TailwindCSS 4。

**Spec:** `docs/superpowers/specs/2026-10-23-html-richtext-editor-design.md`

**验证方式说明:** 前端无测试框架（package.json 无 vitest），组件验证 = `npm run build`（vue-tsc 类型检查 + 构建）+ 浏览器手工验证清单。

---

### Task 1: 安装依赖

**Files:**
- Modify: `frontend/package.json`（由 npm 自动写入）
- Modify: `frontend/package-lock.json`（由 npm 自动写入）

- [ ] **Step 1: 安装 wangEditor**

```bash
cd frontend
npm i @wangeditor/editor @wangeditor/editor-for-vue@next
```

Expected: 安装成功，package.json dependencies 出现 `"@wangeditor/editor": "^5.x"` 和 `"@wangeditor/editor-for-vue": "^5.x"`。

- [ ] **Step 2: 验证类型声明可用**

```bash
cd frontend
node -e "console.log(Object.keys(require('./package.json').dependencies).filter(d => d.includes('wangeditor')))"
```

Expected: `[ '@wangeditor/editor', '@wangeditor/editor-for-vue' ]`

- [ ] **Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: add wangEditor dependencies"
```

---

### Task 2: RichTextEditor 组件

**Files:**
- Create: `frontend/src/components/RichTextEditor.vue`

- [ ] **Step 1: 创建组件**

完整文件内容：

```vue
<script setup lang="ts">
/**
 * wangEditor 5 富文本编辑器
 * v-model 绑定 HTML 字符串
 * - 粘贴网页内容保留格式（内置）
 * - 所见即所得编辑
 * - 工具栏「源码」按钮切换 WYSIWYG ⇄ 源码模式（源码可编辑）
 */
import { onBeforeUnmount, ref, shallowRef, watch, nextTick } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import type { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor/editor'
import '@wangeditor/editor/dist/css/style.css'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  minHeight?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editorRef = shallowRef<IDomEditor | null>(null)
const htmlValue = ref(props.modelValue || '') // Editor 组件的 v-model（挂载期用）
const showSource = ref(false)
const sourceValue = ref('')
// 外部赋值时避免 onChange 回写循环
let silent = false

const toolbarConfig: Partial<IToolbarConfig> = {
  excludeKeys: ['group-video'],
}

const editorConfig: Partial<IEditorConfig> = {
  placeholder: props.placeholder || '请输入内容...',
  MENU_CONF: {},
}

const handleCreated = (editor: IDomEditor) => {
  editorRef.value = editor
}

const handleChange = (editor: IDomEditor) => {
  if (silent) return
  emit('update:modelValue', editor.getHtml())
}

// 源码模式 ⇄ 编辑模式切换
function toggleSource() {
  if (!showSource.value) {
    // 进入源码模式：把当前 HTML 放入 textarea
    sourceValue.value = editorRef.value ? editorRef.value.getHtml() : (props.modelValue || '')
    showSource.value = true
  } else {
    // 回到编辑模式：textarea 内容写回编辑器
    showSource.value = false
    silent = true
    htmlValue.value = sourceValue.value
    nextTick(() => {
      editorRef.value?.setHtml(sourceValue.value || '<p><br></p>')
      nextTick(() => { silent = false })
    })
    emit('update:modelValue', sourceValue.value)
  }
}

// 外部 modelValue 变化时同步（与当前 HTML 不同才回写，防循环）
watch(() => props.modelValue, (val) => {
  if (showSource.value) {
    // 源码模式下外部赋值直接刷新 textarea
    sourceValue.value = val || ''
    return
  }
  const current = editorRef.value ? editorRef.value.getHtml() : htmlValue.value
  if ((val || '') !== current) {
    silent = true
    htmlValue.value = val || ''
    nextTick(() => {
      editorRef.value?.setHtml(val || '<p><br></p>')
      nextTick(() => { silent = false })
    })
  }
})

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor) editor.destroy()
})
</script>

<template>
  <div class="rte-wrap">
    <div v-if="!showSource" class="rte-editor">
      <Toolbar
        class="rte-toolbar"
        :editor="editorRef"
        :default-config="toolbarConfig"
        mode="default"
      />
      <Editor
        v-model="htmlValue"
        class="rte-content"
        :default-config="editorConfig"
        :style="{ minHeight: minHeight || '320px', height: 'auto', overflowY: 'hidden' }"
        mode="default"
        @on-created="handleCreated"
        @on-change="handleChange"
      />
    </div>
    <div v-else class="rte-source">
      <div class="rte-source-bar">
        <span class="text-xs text-gray-500">HTML 源码（可直接编辑）</span>
      </div>
      <textarea
        v-model="sourceValue"
        rows="18"
        spellcheck="false"
        class="w-full px-4 py-3 border-0 focus:ring-0 font-mono text-sm resize-y"
        :style="{ minHeight: minHeight || '320px' }"
      ></textarea>
    </div>
    <div class="rte-modebar">
      <button
        type="button"
        class="rte-mode-btn"
        :class="{ 'rte-mode-btn-active': showSource }"
        @click="toggleSource"
      >
        {{ showSource ? '编辑视图' : '</> 源码' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.rte-wrap {
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  background: #fff;
  z-index: 0;
}

.rte-wrap:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.rte-toolbar {
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.rte-content {
  /* wangEditor 默认 z-index 较高，收在弹窗层级内 */
  z-index: 1;
}

.rte-source-bar {
  padding: 6px 12px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.rte-source textarea {
  outline: none;
  display: block;
}

.rte-modebar {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  padding: 4px 8px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.rte-mode-btn {
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  color: #4b5563;
  transition: all 0.15s;
}

.rte-mode-btn:hover {
  background: #e8f0fe;
  color: #1d4ed8;
}

.rte-mode-btn-active {
  background: #e8f0fe;
  color: #1d4ed8;
}
</style>
```

- [ ] **Step 2: 类型检查通过**

```bash
cd frontend && npm run build
```

Expected: vue-tsc 无错误，构建成功。（此时组件尚未被引用，仅验证自身无类型错误。）

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/RichTextEditor.vue
git commit -m "feat: add RichTextEditor component based on wangEditor 5"
```

---

### Task 3: ContentsPage 按 content_format 分流接入

**Files:**
- Modify: `frontend/src/pages/admin/ContentsPage.vue`

- [ ] **Step 1: script 部分引入组件**

在 `frontend/src/pages/admin/ContentsPage.vue:8` 的 `import MarkdownEditor ...` 之后添加：

```ts
import RichTextEditor from '@/components/RichTextEditor.vue'
```

- [ ] **Step 2: 内容编辑区按格式分流**

找到模板中内容编辑区（`<div v-if="formData.type !== 'shortcut'">` 包裹的块，约 924-977 行），整块替换为：

```vue
          <!-- Content editor with preview -->
          <div v-if="formData.type !== 'shortcut'">
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-sm font-medium text-gray-700">内容</label>
              <div v-if="formData.content_format !== 'html'" class="flex items-center gap-2">
                <button
                  type="button"
                  @click="openFileSelector('image')"
                  class="px-2 py-1 text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded flex items-center gap-1"
                  title="插入图片"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  图片
                </button>
                <button
                  type="button"
                  @click="openFileSelector('file')"
                  class="px-2 py-1 text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded flex items-center gap-1"
                  title="插入文件"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                  </svg>
                  文件
                </button>
                <button
                  type="button"
                  @click="previewMode = !previewMode"
                  class="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  {{ previewMode ? '编辑' : '预览' }}
                </button>
              </div>
            </div>
            <div v-if="formData.content_format === 'html'" class="border-0">
              <RichTextEditor v-model="formData.content" placeholder="富文本编辑，可直接粘贴网页内容..." />
            </div>
            <div v-else class="border border-gray-200 rounded-xl overflow-hidden">
              <textarea
                v-if="!previewMode"
                v-model="formData.content"
                rows="15"
                placeholder="支持 Markdown 格式..."
                class="w-full px-4 py-3 border-0 focus:ring-0 rewidth-none font-mono text-sm"
              ></textarea>
              <div
                v-else
                class="p-4 min-h-[300px] prose prose-sm max-w-none"
                v-html="renderMarkdown(formData.content)"
              ></div>
            </div>
            <p class="text-xs text-gray-500 mt-1.5">
              {{ formData.content_format === 'html'
                ? '富文本编辑，可粘贴网页内容保留格式，支持源码模式。'
                : '支持 Markdown 格式。切换到预览模式查看效果。' }}
            </p>
          </div>
```

要点：
- HTML 格式时隐藏「图片/文件/预览」按钮组（wangEditor 自带图片菜单与实时预览）
- 其余（textarea、Markdown 提示）原样保留

- [ ] **Step 3: 构建验证**

```bash
cd frontend && npm run build
```

Expected: vue-tsc 无错误，构建成功。

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/admin/ContentsPage.vue
git commit -m "feat: use RichTextEditor for HTML content format in contents page"
```

---

### Task 4: 浏览器手工验证

**Files:** 无代码改动（此任务只验证；发现问题则修复后重新验证）

前置：后端 `cd backend && uv run python main.py`（http://localhost:8000），前端 `cd frontend && npm run dev`（http://localhost:5173），用 `admin / admin123` 登录。

- [ ] **Step 1: HTML 格式编辑器验证**

1. 进入 内容管理 → 新建内容 → 类型选「页面」，内容格式选「HTML」
   Expected: 出现 wangEditor 工具栏 + 编辑区，无 图片/文件/预览 按钮
2. 打开任一网页（如新闻页），选中一段带标题、加粗、链接、表格的内容复制，粘贴进编辑区
   Expected: 标题、加粗、链接、表格格式保留；图片保留外链 src
3. 在编辑区内直接点击文字修改、加粗、建列表
   Expected: 所见即所得正常
4. 点击底部「源码」按钮
   Expected: 切换为 textarea 显示 HTML 源码；修改源码（如把 `<p>abc</p>` 改成 `<h2>abc</h2>`）
5. 点击「编辑视图」按钮
   Expected: 回到 WYSIWYG，刚才的源码修改生效（abc 变为 H2）
6. 保存内容，刷新页面重新编辑该条
   Expected: 内容回填完整，与保存前一致

- [ ] **Step 2: Markdown 路径回归**

1. 新建内容，格式保持「Markdown」
   Expected: 仍是原 textarea + 图片/文件/预览按钮，行为与改动前一致
2. 编辑一条已有的快捷入口（shortcut）内容
   Expected: 不出现内容编辑区（与改动前一致）

- [ ] **Step 3: 弹窗交互回归**

1. 打开 HTML 编辑器，点击编辑区/工具栏操作
   Expected: 无层级错乱、无下拉菜单被弹窗遮挡（z-index 正常）
2. 切换 content_format 下拉 Markdown ⇄ HTML
   Expected: 编辑器切换，内容字符串原样保留（不转换）

- [ ] **Step 4: 修复问题（如有）并提交**

若验证发现 bug：修复 → 重跑对应验证步骤 → 

```bash
git add -A
git commit -m "fix: address issues from rich text editor manual verification"
```

若无问题，跳过提交。
