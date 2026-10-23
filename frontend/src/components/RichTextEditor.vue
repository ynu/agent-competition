<script setup lang="ts">
/**
 * wangEditor 5 HTML 富文本编辑器（所见即所得 + 源码模式）
 * v-model 绑定 HTML 字符串
 *
 * 注意：本组件输出未经消毒的 HTML，消费方若使用 v-html 渲染，
 * 需自行 sanitize（防 XSS）。
 */
import { ref, shallowRef, watch, onBeforeUnmount } from 'vue'
import type { DefineComponent } from 'vue'
// @wangeditor/editor-for-vue 的 package.json exports 未声明 types（TS7016），
// 组件类型按其 dist/src/*.d.ts 手工声明
// @ts-expect-error 库类型声明无法通过 exports 解析
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import type { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor/editor'
import '@wangeditor/editor/dist/css/style.css'

const EditorComp = Editor as unknown as DefineComponent<{
  mode?: string
  defaultHtml?: string
  defaultConfig?: Partial<IEditorConfig>
  modelValue?: string
}>

const ToolbarComp = Toolbar as unknown as DefineComponent<{
  editor?: IDomEditor
  mode?: string
  defaultConfig?: Partial<IToolbarConfig>
}>

const props = defineProps<{
  modelValue: string
  placeholder?: string
  minHeight?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editorRef = shallowRef<IDomEditor | undefined>(undefined)
let silent = false // 外部赋值时避免回写循环
let pendingValue: string | null = null
let lastEmitted: string | null = null
const showSource = ref(false)
const sourceText = ref('')

const editorConfig: Partial<IEditorConfig> = {
  placeholder: props.placeholder || '请输入内容...',
}

const toolbarConfig: Partial<IToolbarConfig> = {
  excludeKeys: ['group-video'],
}

// 统一 emit 入口：与上次 emitted 值相同则跳过（避免纯光标移动等重复 emit）
function emitValue(v: string) {
  if (v === lastEmitted) return
  lastEmitted = v
  emit('update:modelValue', v)
}

const handleCreated = (editor: IDomEditor) => {
  editorRef.value = editor
  // 挂载后传入的外部值（如编辑回填发生在创建之前）
  if (pendingValue !== null) {
    if (pendingValue !== editor.getHtml()) {
      silent = true
      editor.setHtml(pendingValue)
      silent = false
    }
    pendingValue = null
  }
}

const handleChange = (editor: IDomEditor) => {
  if (silent) return
  emitValue(editor.getHtml())
}

// 外部 modelValue 变化时，仅当与编辑器当前内容不同才写回
watch(
  () => props.modelValue,
  (val) => {
    const v = val ?? ''
    if (showSource.value) {
      // 源码模式下暂存外部更新，退出源码时应用；
      // 同时同步到 textarea，避免退出时用过期内容覆盖外部更新
      pendingValue = v
      if (v !== sourceText.value) sourceText.value = v
      return
    }
    const editor = editorRef.value
    if (!editor) {
      pendingValue = v
      return
    }
    if (v !== editor.getHtml()) {
      silent = true
      editor.setHtml(v)
      silent = false
    }
  }
)

// 源码模式下编辑内容实时 emit，避免直接保存时丢失修改
watch(sourceText, (val) => {
  emitValue(val)
})

// 进入源码模式
function enterSource() {
  const editor = editorRef.value
  if (!editor) return
  sourceText.value = editor.getHtml()
  pendingValue = null
  emitValue(sourceText.value)
  showSource.value = true
}

// 退出源码模式，将源码内容写回编辑器（外部更新优先）
function exitSource() {
  const editor = editorRef.value
  const val = pendingValue !== null ? pendingValue : sourceText.value
  pendingValue = null
  // 先切回视图，保证任何情况下都能退出源码模式
  showSource.value = false
  if (!editor) return
  // 复位 selection：源码中清空内容后编辑器 selection 可能指向已不存在的节点，
  // 不复位会导致 setHtml 抛 Slate 内部错误（"Cannot resolve a Slate point..."）
  try {
    editor.deselect()
  } catch {
    // 忽略复位 selection 的异常
  }
  try {
    silent = true
    editor.setHtml(val)
    silent = false
  } catch {
    silent = false
    // setHtml 失败（如 Slate 内部错误）时仍保证视图已切回，不阻塞页面
  }
  emitValue(editor.getHtml())
}

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor && !editor.isDestroyed) {
    editor.destroy()
  }
  editorRef.value = undefined
})
</script>

<template>
  <div class="rich-editor-wrap">
    <!-- WYSIWYG 视图（v-show 保持编辑器实例跨切换存活） -->
    <div v-show="!showSource">
      <ToolbarComp
        class="rich-editor-toolbar"
        :editor="editorRef"
        :default-config="toolbarConfig"
        mode="default"
      />
      <EditorComp
        class="rich-editor-content"
        :default-config="editorConfig"
        :model-value="modelValue"
        mode="default"
        @on-created="handleCreated"
        @on-change="handleChange"
      />
    </div>
    <!-- 源码视图 -->
    <div v-show="showSource">
      <div class="rich-editor-source-head">
        <span class="rich-editor-source-tip">HTML 源码</span>
        <button type="button" class="rich-editor-source-btn" @click="exitSource">编辑视图</button>
      </div>
      <textarea
        v-model="sourceText"
        class="rich-editor-source"
        spellcheck="false"
        :style="{ minHeight: minHeight || '220px' }"
      ></textarea>
    </div>
    <!-- 右下角源码切换按钮 -->
    <button
      v-show="!showSource"
      type="button"
      class="rich-editor-source-toggle"
      title="编辑 HTML 源码"
      @click="enterSource"
    >源码</button>
  </div>
</template>

<style scoped>
.rich-editor-wrap {
  position: relative;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  background: #fff;
  z-index: 10;
}

.rich-editor-wrap:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.rich-editor-toolbar {
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  border-radius: 0.75rem 0.75rem 0 0;
}

.rich-editor-content {
  min-height: v-bind("minHeight || '220px'");
  max-height: 420px;
  overflow-y: auto;
  border-radius: 0 0 0.75rem 0.75rem;
}

/* 源码视图 */
.rich-editor-source-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  border-radius: 0.75rem 0.75rem 0 0;
}

.rich-editor-source-tip {
  font-size: 12px;
  color: #6b7280;
}

.rich-editor-source-btn {
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  color: #4b5563;
  transition: all 0.15s;
}

.rich-editor-source-btn:hover {
  background: #e8f0fe;
  color: #1d4ed8;
}

.rich-editor-source {
  display: block;
  width: 100%;
  padding: 14px 16px;
  border: none;
  outline: none;
  resize: vertical;
  background: #fff;
  border-radius: 0 0 0.75rem 0.75rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #374151;
}

/* 右下角源码切换按钮 */
.rich-editor-source-toggle {
  position: absolute;
  right: 8px;
  bottom: 8px;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  color: #9ca3af;
  background: rgba(255, 255, 255, 0.85);
  transition: all 0.15s;
  z-index: 10;
}

.rich-editor-source-toggle:hover {
  background: #e8f0fe;
  color: #1d4ed8;
}
</style>
