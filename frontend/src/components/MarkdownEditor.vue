<script setup lang="ts">
/**
 * Milkdown 所见即所得 Markdown 编辑器（带常用工具栏）
 * v-model 绑定 Markdown 字符串
 */
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx, editorViewCtx, serializerCtx, parserCtx, prosePluginsCtx } from '@milkdown/core'
import { commonmark, toggleStrongCommand, toggleEmphasisCommand, toggleInlineCodeCommand, toggleLinkCommand, wrapInHeadingCommand, wrapInBlockquoteCommand, wrapInBulletListCommand, wrapInOrderedListCommand, insertHardbreakCommand, insertHrCommand, createCodeBlockCommand, insertImageCommand } from '@milkdown/preset-commonmark'
import { gfm, toggleStrikethroughCommand, insertTableCommand } from '@milkdown/preset-gfm'
import { callCommand } from '@milkdown/utils'
import { history, undo as pmUndo, redo as pmRedo } from '@milkdown/prose/history'
import { Plugin } from '@milkdown/prose/state'
import '@milkdown/theme-nord/style.css'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  minHeight?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const container = ref<HTMLDivElement | null>(null)
let editorInstance: Editor | null = null
let silent = false // 外部赋值时避免回写循环
let pendingValue: string | null = null

function getMarkdown(): string {
  if (!editorInstance) return ''
  return editorInstance.action((ctx) => {
    const serializer = ctx.get(serializerCtx)
    const view = ctx.get(editorViewCtx)
    return serializer(view.state.doc)
  })
}

function setMarkdown(md: string) {
  if (!editorInstance) return
  editorInstance.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const parser = ctx.get(parserCtx)
    const doc = parser(md || '')
    if (doc) {
      silent = true
      const { state } = view
      view.dispatch(
        state.tr.replaceWith(0, state.doc.content.size, doc.content)
      )
      silent = false
    }
  })
}

// 执行命令
function run(...calls: ReturnType<typeof callCommand>[]) {
  if (!editorInstance) return
  editorInstance.action((ctx) => {
    calls.forEach((call) => call(ctx))
  })
}

// 工具栏定义
interface ToolbarItem {
  key: string
  label: string
  title: string
  run: () => void
  cls?: string
}

function makeToolbar(): ToolbarItem[] {
  const view = getEditorView()
  return [
    { key: 'h1', label: 'H1', title: '一级标题', run: () => run(callCommand(wrapInHeadingCommand.key, 1)) },
    { key: 'h2', label: 'H2', title: '二级标题', run: () => run(callCommand(wrapInHeadingCommand.key, 2)) },
    { key: 'h3', label: 'H3', title: '三级标题', run: () => run(callCommand(wrapInHeadingCommand.key, 3)) },
    { key: 'bold', label: 'B', title: '加粗', run: () => run(callCommand(toggleStrongCommand.key)), cls: 'font-bold' },
    { key: 'italic', label: 'I', title: '斜体', run: () => run(callCommand(toggleEmphasisCommand.key)), cls: 'italic font-serif' },
    { key: 'strike', label: 'S', title: '删除线', run: () => run(callCommand(toggleStrikethroughCommand.key)), cls: 'line-through' },
    { key: 'code', label: '</>', title: '行内代码', run: () => run(callCommand(toggleInlineCodeCommand.key)), cls: 'font-mono text-xs' },
    { key: 'codeblock', label: '▤', title: '代码块', run: () => run(callCommand(createCodeBlockCommand.key)), cls: 'font-mono text-xs' },
    { key: 'ul', label: '•≡', title: '无序列表', run: () => run(callCommand(wrapInBulletListCommand.key)) },
    { key: 'ol', label: '1≡', title: '有序列表', run: () => run(callCommand(wrapInOrderedListCommand.key)) },
    { key: 'quote', label: '❝', title: '引用', run: () => run(callCommand(wrapInBlockquoteCommand.key)) },
    { key: 'link', label: '🔗', title: '链接', run: () => {
        const url = window.prompt('请输入链接地址：', 'https://')
        if (url) run(callCommand(toggleLinkCommand.key, { href: url }))
      } },
    { key: 'image', label: '🖼', title: '图片', run: () => {
        const url = window.prompt('请输入图片地址：', 'https://')
        if (url) run(callCommand(insertImageCommand.key, { src: url }))
      } },
    { key: 'table', label: '⊞', title: '表格', run: () => run(callCommand(insertTableCommand.key, { row: 3, col: 3 })) },
    { key: 'hr', label: '—', title: '分割线', run: () => run(callCommand(insertHrCommand.key)) },
    { key: 'br', label: '↵', title: '换行', run: () => run(callCommand(insertHardbreakCommand.key)) },
    { key: 'undo', label: '↺', title: '撤销', run: () => runHistory(pmUndo) },
    { key: 'redo', label: '↻', title: '重做', run: () => runHistory(pmRedo) },
  ]
}

// 撤销/重做（需先注册 history 插件）
function runHistory(cmd: (state: any, dispatch?: any) => boolean) {
  if (!editorInstance) return
  editorInstance.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    cmd(view.state, view.dispatch)
  })
}

function getEditorView(): any | null {
  if (!editorInstance) return null
  try {
    let v: any = null
    editorInstance.action((ctx) => {
      v = ctx.get(editorViewCtx)
    })
    return v
  } catch {
    return null
  }
}

const toolbarItems = ref<ToolbarItem[]>([])

onMounted(async () => {
  if (!container.value) return

  editorInstance = await Editor.make()
    .config((ctx) => {
      ctx.set(rootCtx, container.value)
      ctx.set(defaultValueCtx, props.modelValue || '')
      // 注册 prosemirror-history 插件（支持撤销/重做）
      ctx.update(prosePluginsCtx, (prev) => [...prev, history() as Plugin])
      ctx.update(editorViewOptionsCtx, (prev) => ({
        ...prev,
        attributes: {
          ...prev.attributes,
          class: 'milkdown-editor-content',
          spellcheck: 'false',
        },
      }))
    })
    .use(commonmark)
    .use(gfm)
    .create()

  // 拦截 dispatchTransaction 以监听文档变化
  editorInstance.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const originalDispatch = view.dispatch.bind(view)
    view.dispatch = (tr: Parameters<typeof view.dispatch>[0]) => {
      originalDispatch(tr)
      if (tr.docChanged && !silent) {
        emit('update:modelValue', getMarkdown())
      }
    }
  })

  toolbarItems.value = makeToolbar()

  // 外部初始值在挂载后传入（如编辑回填发生在创建之前）
  if (pendingValue !== null && pendingValue !== (props.modelValue || '')) {
    setMarkdown(pendingValue)
    pendingValue = null
  }
})

onBeforeUnmount(() => {
  editorInstance?.destroy()
  editorInstance = null
})

watch(() => props.modelValue, (val) => {
  if (!editorInstance) {
    pendingValue = val
    return
  }
  const current = getMarkdown()
  if ((val || '') !== current) {
    setMarkdown(val || '')
  }
})
</script>

<template>
  <div class="milkdown-editor-wrap">
    <!-- 工具栏 -->
    <div class="md-toolbar">
      <template v-for="(item, i) in toolbarItems" :key="item.key">
        <span v-if="item.key === 'ul'" class="md-toolbar-divider"></span>
        <button
          type="button"
          :title="item.title"
          :class="item.cls"
          class="md-toolbar-btn"
          @mousedown.prevent
          @click="item.run()"
        >{{ item.label }}</button>
      </template>
    </div>
    <div ref="container"></div>
  </div>
</template>

<style scoped>
.milkdown-editor-wrap {
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  background: #fff;
}

.milkdown-editor-wrap:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.md-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px;
  padding: 6px 8px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.md-toolbar-btn {
  min-width: 28px;
  height: 28px;
  padding: 0 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 13px;
  color: #4b5563;
  transition: all 0.15s;
}

.md-toolbar-btn:hover {
  background: #e8f0fe;
  color: #1d4ed8;
}

.md-toolbar-divider {
  width: 1px;
  height: 16px;
  background: #e0e0e0;
  margin: 0 4px;
}

.milkdown-editor-wrap :deep(.milkdown) {
  background: #fff;
}

.milkdown-editor-wrap :deep(.ProseMirror) {
  min-height: v-bind("minHeight || '220px'");
  max-height: 420px;
  overflow-y: auto;
  padding: 16px 18px;
  outline: none;
  font-size: 14px;
  line-height: 1.75;
}

.milkdown-editor-wrap :deep(.ProseMirror p:first-child) {
  margin-top: 0;
}

.milkdown-editor-wrap :deep(.ProseMirror img) {
  max-width: 100%;
}

.milkdown-editor-wrap :deep(.ProseMirror pre) {
  background: #f6f8fa;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
}

.milkdown-editor-wrap :deep(.ProseMirror blockquote) {
  border-left: 4px solid #d1d5db;
  color: #6b7280;
  padding-left: 12px;
}

/* 空内容占位符 */
.milkdown-editor-wrap :deep(.ProseMirror p.is-editor-empty:first-child)::before {
  content: attr(data-placeholder);
  color: #9ca3af;
  float: left;
  height: 0;
  pointer-events: none;
}
</style>
