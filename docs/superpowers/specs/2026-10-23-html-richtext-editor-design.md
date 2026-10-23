# HTML 富文本编辑器设计（wangEditor 5）

日期：2026-10-23

## 目标

在内容管理（ContentsPage）弹窗中，当 `content_format` 选 **HTML** 时，用 wangEditor 5 富文本编辑器替代现有 textarea，实现：

1. **粘贴保留格式** — 从网页复制内容粘贴后保留标题、加粗、链接、表格、图片等格式
2. **所见即所得编辑** — 直接在编辑区编辑
3. **源码查看/编辑** — 工具栏按钮一键切换 WYSIWYG ⇄ 源码模式，源码可编辑

## 决策记录

- 编辑器选型：**wangEditor 5**（`@wangeditor/editor` + `@wangeditor/editor-for-vue@next`）。粘贴保留格式、WYSIWYG、模式切换均为内置能力，中文文档友好，开发量最小。
- 应用范围：**仅 HTML 格式启用**。Markdown 格式仍用现有 Milkdown / textarea，不替换。
- 粘贴图片：**保留外链**。不配置 customUpload，图片 src 原样保留；已有媒体库插入能力不受影响。
- 安全：**信任管理员**，不做 XSS 清洗（管理后台场景，展示端沿用现有 v-html 渲染逻辑）。

## 组件设计

新建 `frontend/src/components/RichTextEditor.vue`（与 `MarkdownEditor.vue` 同级、同风格）：

```
props:  modelValue: string  （HTML 字符串）
        placeholder?: string
        minHeight?: string
emit:   update:modelValue
```

内部结构：

- **工具栏 + 编辑区**：`@wangeditor/editor-for-vue@next` 的 `<Toolbar>` + `<Editor>` 组件
- **v-model 双向同步**：`onChange` 时 emit；外部 `modelValue` 变化且与当前 HTML 不同时 `editor.setHtml()`（参考 MarkdownEditor 的防回写循环做法：silent 标志 / 值比对）
- **源码模式**：工具栏右侧自定义「源码」按钮，用 v-if 切换 wangEditor 与源码 `<textarea>`（等宽字体）。切回 WYSIWYG 时把 textarea 内容 `setHtml()` 回编辑器
- **粘贴**：wangEditor 内置保留格式粘贴，零额外代码
- **卸载**：销毁编辑器实例，防内存泄漏

## 页面接入（ContentsPage.vue）

内容编辑区（约 924-977 行）按格式分流：

```
v-if formData.content_format === 'html'  → <RichTextEditor v-model="formData.content" />
v-else                                   → 现有 textarea + 预览逻辑不变
```

- 图片/文件插入按钮、预览切换按钮对 HTML 格式隐藏（wangEditor 自带图片能力与实时预览）
- 提示文字按格式显示：「支持 Markdown 格式」/「富文本编辑，可粘贴网页内容，支持源码模式」

## 依赖

```bash
npm i @wangeditor/editor @wangeditor/editor-for-vue@next
```

## 边界与错误处理

- 编辑已有 HTML 内容回填：`setHtml` 兼容不完整 HTML，wangEditor 自动规范化
- `content_format` 下拉切换（Markdown ⇄ HTML）时内容原样保留，不做自动转换（与现状一致）
- 源码模式下用户输入非法 HTML：setHtml 时由 wangEditor 规范化，不报错

## 不做的事（YAGNI）

- 不做 XSS 清洗
- 不做图片自动转存
- 不替换 Markdown 编辑器（Milkdown 保留）

## 测试要点

- HTML 格式：从网页复制一段带标题/加粗/表格/图片的内容粘贴，格式保留
- WYSIWYG ⇄ 源码切换，内容一致、双向不丢失
- 编辑已有 HTML 内容，回填正常
- Markdown 格式编辑不受影响（回归）
