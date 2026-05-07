<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useNotification } from '@/composables/useNotification'
import markdownIt from 'markdown-it'

const { success, error } = useNotification()

const contents = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 20
const typeFilter = ref('')
const keyword = ref('')
const publishedFilter = ref('')
const dragIndex = ref(-1)

const showModal = ref(false)
const previewMode = ref(false)

const md = markdownIt()
const renderMarkdown = (content: string) => {
  if (!content) return ''
  return md.render(content)
}

const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)
const editingContent = ref<any>(null)
const formData = ref({
  title: '',
  slug: '',
  type: 'page',
  content: '',
  content_format: 'markdown',
  is_published: false,
  order: 0,
  summary: '',
  author: '',
  cover_image: ''
})

const typeOptions = [
  { value: '', label: '全部类型' },
  { value: 'page', label: '页面' },
  { value: 'category', label: '栏目' },
  { value: 'article', label: '文章' }
]

const publishedOptions = [
  { value: '', label: '全部状态' },
  { value: 'true', label: '已发布' },
  { value: 'false', label: '草稿' }
]

const formTypeOptions = [
  { value: 'page', label: '页面' },
  { value: 'category', label: '栏目' },
  { value: 'article', label: '文章' }
]

onMounted(() => {
  fetchContents()
})

async function fetchContents() {
  loading.value = true
  try {
    const res = await api.get('/contents', {
      params: {
        page: page.value,
        page_size: pageSize,
        type: typeFilter.value || undefined,
        keyword: keyword.value || undefined,
        is_published: publishedFilter.value === '' ? undefined : publishedFilter.value === 'true'
      }
    })
    contents.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingContent.value = null
  formData.value = {
    title: '',
    slug: '',
    type: 'article',
    content: '',
    content_format: 'markdown',
    is_published: false,
    order: contents.value.length,
    summary: '',
    author: '',
    cover_image: ''
  }
  previewMode.value = false
  showModal.value = true
}

function openEdit(content: any) {
  editingContent.value = content
  formData.value = {
    title: content.title,
    slug: content.slug,
    type: content.type,
    content: content.content || '',
    content_format: content.content_format,
    is_published: content.is_published,
    order: content.order || 0,
    summary: content.summary || '',
    author: content.author || '',
    cover_image: content.cover_image || ''
  }
  previewMode.value = false
  showModal.value = true
}

async function handleSave() {
  try {
    const data = { ...formData.value }
    if (editingContent.value) {
      await api.put(`/contents/${editingContent.value.id}`, data)
    } else {
      await api.post('/contents', data)
    }
    showModal.value = false
    success('保存成功')
    await fetchContents()
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function handleDelete(content: any) {
  confirmMessage.value = `确定删除内容 "${content.title}" 吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    try {
      await api.delete(`/contents/${content.id}`)
      success('删除成功')
      await fetchContents()
    } catch (e: any) {
      error('删除失败', e.response?.data?.detail)
    }
  }
}

async function handleGenerateStatic(content: any) {
  try {
    const res = await api.post(`/contents/${content.id}/generate-static`)
    success('生成成功', `静态页面已生成: ${res.data.path}`)
  } catch (e: any) {
    error('生成失败', e.response?.data?.detail)
  }
}

function handlePageChange(newPage: number) {
  page.value = newPage
  fetchContents()
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = { page: '页面', category: '栏目', article: '文章' }
  return map[type] || type
}

function getTypeClass(type: string) {
  const map: Record<string, string> = {
    page: 'bg-blue-100 text-blue-700',
    category: 'bg-purple-100 text-purple-700',
    article: 'bg-green-100 text-green-700'
  }
  return map[type] || 'bg-gray-100 text-gray-700'
}

// Drag and drop sorting
function onDragStart(index: number) {
  dragIndex.value = index
}

function onDragOver(e: DragEvent, index: number) {
  e.preventDefault()
  if (dragIndex.value !== index && dragIndex.value !== -1) {
    const items = document.querySelectorAll('[data-draggable="true"]')
    items.forEach((item, i) => {
      if (i === index) {
        item.classList.add('bg-blue-50', 'border-blue-300')
      } else {
        item.classList.remove('bg-blue-50', 'border-blue-300')
      }
    })
  }
}

async function onDrop(index: number) {
  if (dragIndex.value !== -1 && dragIndex.value !== index) {
    const item = contents.value.splice(dragIndex.value, 1)[0]
    contents.value.splice(index, 0, item)
    // Save new order to backend
    try {
      await api.put('/contents/reorder', {
        content_ids: contents.value.map((c: any) => c.id)
      })
      success('排序已更新')
    } catch (e: any) {
      error('保存排序失败', e.response?.data?.detail)
      await fetchContents()
    }
  }
  dragIndex.value = -1
}

function onDragEnd() {
  dragIndex.value = -1
}

async function updateContentOrder(content: any, newOrder: number) {
  try {
    await api.put(`/contents/${content.id}`, { order: newOrder })
    success('排序已更新')
    await fetchContents()
  } catch (e: any) {
    error('更新失败', e.response?.data?.detail)
  }
}

function moveUp(content: any, index: number) {
  if (index > 0) {
    const newOrder = contents.value[index - 1].order + 1
    updateContentOrder(content, newOrder)
  }
}

function moveDown(content: any, index: number) {
  if (index < contents.value.length - 1) {
    const newOrder = contents.value[index + 1].order - 1
    updateContentOrder(content, newOrder)
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">内容管理</h1>
          <p class="text-sm text-gray-500 mt-1">管理页面、栏目与文章</p>
        </div>
        <button
          @click="openCreate"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          创建内容
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <input
          v-model="keyword"
          @keyup.enter="fetchContents"
          type="text"
          placeholder="搜索标题/slug..."
          class="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all min-w-[200px]"
        />
        <select
          v-model="typeFilter"
          class="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white min-w-[140px]"
          @change="fetchContents"
        >
          <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
        <select
          v-model="publishedFilter"
          class="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white min-w-[140px]"
          @change="fetchContents"
        >
          <option v-for="opt in publishedOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
        <button
          @click="fetchContents"
          class="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all font-medium"
        >
          搜索
        </button>
        <button
          v-if="keyword || typeFilter || publishedFilter"
          @click="keyword = ''; typeFilter = ''; publishedFilter = ''; fetchContents()"
          class="px-4 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all font-medium text-gray-600"
        >
          重置
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider w-20">排序</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">ID</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">标题</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Slug</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">类型</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="(content, index) in contents"
            :key="content.id"
            class="hover:bg-blue-50/50 transition-colors"
            data-draggable="true"
            :class="{ 'bg-blue-50 border-blue-300': dragIndex === index }"
            draggable="true"
            @dragstart="onDragStart(index)"
            @dragover="onDragOver($event, index)"
            @drop="onDrop(index)"
            @dragend="onDragEnd"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-1">
                <button @click="moveUp(content, index)" :disabled="index === 0" class="p-1 text-gray-400 hover:text-blue-600 disabled:opacity-30 disabled:cursor-not-allowed">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                  </svg>
                </button>
                <span class="text-xs text-gray-400 w-6 text-center">{{ index + 1 }}</span>
                <button @click="moveDown(content, index)" :disabled="index === contents.length - 1" class="p-1 text-gray-400 hover:text-blue-600 disabled:opacity-30 disabled:cursor-not-allowed">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </button>
              </div>
            </td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ content.id }}</td>
            <td class="px-6 py-4 text-sm text-gray-800 font-medium">{{ content.title }}</td>
            <td class="px-6 py-4 text-sm text-gray-600 font-mono text-xs">{{ content.slug }}</td>
            <td class="px-6 py-4 text-sm">
              <span
                class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium"
                :class="getTypeClass(content.type)"
              >
                {{ getTypeLabel(content.type) }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm">
              <span
                class="inline-flex items-center gap-1.5"
                :class="content.is_published ? 'text-green-600' : 'text-gray-400'"
              >
                <span class="w-2 h-2 rounded-full" :class="content.is_published ? 'bg-green-500' : 'bg-gray-400'"></span>
                {{ content.is_published ? '已发布' : '草稿' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm">
              <div class="flex items-center gap-2">
                <button @click="openEdit(content)" class="text-blue-600 hover:text-blue-700 font-medium transition-colors">编辑</button>
                <span class="text-gray-300">|</span>
                <button @click="handleGenerateStatic(content)" class="text-green-600 hover:text-green-700 font-medium transition-colors">生成静态</button>
                <span class="text-gray-300">|</span>
                <button @click="handleDelete(content)" class="text-red-600 hover:text-red-700 font-medium transition-colors">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-flex items-center gap-2 text-gray-500">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          加载中...
        </div>
      </div>
      <div v-else-if="contents.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        暂无数据
      </div>

      <div v-if="total > pageSize" class="px-6 py-4 border-t border-gray-100 flex justify-center">
        <div class="flex items-center gap-1">
          <button
            @click="handlePageChange(page - 1)"
            :disabled="page === 1"
            class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>
          <div class="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg text-sm font-medium shadow-md">
            {{ page }} / {{ Math.ceil(total / pageSize) }}
          </div>
          <button
            @click="handlePageChange(page + 1)"
            :disabled="page * pageSize >= total"
            class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex justify-between items-center">
          <div>
            <h3 class="text-lg font-semibold text-white">{{ editingContent ? '编辑内容' : '创建内容' }}</h3>
            <p class="text-blue-100 text-sm">{{ editingContent ? '修改内容信息' : '创建新的页面或栏目' }}</p>
          </div>
          <button @click="showModal = false" class="text-white hover:bg-white/20 rounded-lg p-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <form @submit.prevent="handleSave" class="p-6 space-y-5 overflow-y-auto flex-1">
          <div class="grid md:grid-cols-2 gap-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">标题 <span class="text-red-500">*</span></label>
              <input
                v-model="formData.title"
                type="text"
                required
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Slug <span class="text-red-500">*</span></label>
              <input
                v-model="formData.slug"
                type="text"
                required
                placeholder="url-slug"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-mono text-sm"
              />
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">类型</label>
              <select
                v-model="formData.type"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white"
              >
                <option v-for="opt in formTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">排序</label>
              <input
                v-model.number="formData.order"
                type="number"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              />
            </div>
          </div>

          <!-- Article fields -->
          <div v-if="formData.type === 'article'" class="grid md:grid-cols-3 gap-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">作者</label>
              <input
                v-model="formData.author"
                type="text"
                placeholder="作者名称"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">封面图片URL</label>
              <input
                v-model="formData.cover_image"
                type="url"
                placeholder="https://..."
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              />
            </div>
          </div>

          <!-- Article summary -->
          <div v-if="formData.type === 'article'">
            <label class="block text-sm font-medium text-gray-700 mb-1.5">摘要</label>
            <textarea
              v-model="formData.summary"
              rows="2"
              placeholder="文章摘要（显示在列表中）"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            ></textarea>
          </div>

          <div class="grid md:grid-cols-2 gap-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">内容格式</label>
              <select
                v-model="formData.content_format"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white"
              >
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
            </div>
            <div class="flex items-center pt-5">
              <label class="flex items-center gap-3 cursor-pointer">
                <div class="relative">
                  <input v-model="formData.is_published" type="checkbox" class="sr-only peer" />
                  <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-blue-600 transition-colors"></div>
                  <div class="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow peer-checked:translate-x-5 transition-transform"></div>
                </div>
                <span class="text-sm font-medium text-gray-700">立即发布</span>
              </label>
            </div>
          </div>

          <!-- Content editor with preview -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-sm font-medium text-gray-700">内容</label>
              <button
                type="button"
                @click="previewMode = !previewMode"
                class="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                {{ previewMode ? '编辑' : '预览' }}
              </button>
            </div>
            <div class="border border-gray-200 rounded-xl overflow-hidden">
              <textarea
                v-if="!previewMode"
                v-model="formData.content"
                rows="15"
                placeholder="支持 Markdown 格式..."
                class="w-full px-4 py-3 border-0 focus:ring-0 resize-none font-mono text-sm"
              ></textarea>
              <div
                v-else
                class="p-4 min-h-[300px] prose prose-sm max-w-none"
                v-html="renderMarkdown(formData.content)"
              ></div>
            </div>
            <p class="text-xs text-gray-500 mt-1.5">
              支持 Markdown 格式。切换到预览模式查看效果。
            </p>
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button
              type="button"
              @click="showModal = false"
              class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 font-medium text-gray-700 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
            >
              保存
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <ConfirmDialog
      :show="showConfirm"
      title="确认删除"
      :message="confirmMessage"
      confirm-text="删除"
      cancel-text="取消"
      type="danger"
      @confirm="() => { if (confirmCallback) confirmCallback(); showConfirm = false }"
      @cancel="showConfirm = false"
      @close="showConfirm = false"
    />
  </div>
</template>

<style scoped>
.prose :deep(h1) { font-size: 1.5rem; font-weight: 700; margin: 1rem 0 0.75rem; }
.prose :deep(h2) { font-size: 1.25rem; font-weight: 600; margin: 0.875rem 0 0.625rem; }
.prose :deep(h3) { font-size: 1.125rem; font-weight: 600; margin: 0.75rem 0 0.5rem; }
.prose :deep(p) { margin: 0.5rem 0; line-height: 1.7; }
.prose :deep(ul), .prose :deep(ol) { padding-left: 1.5rem; margin: 0.5rem 0; }
.prose :deep(li) { margin: 0.25rem 0; }
.prose :deep(code) { background: #f3f4f6; padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-family: monospace; }
.prose :deep(pre) { background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }
.prose :deep(blockquote) { border-left: 4px solid #3b82f6; padding-left: 1rem; margin: 1rem 0; color: #6b7280; }
.prose :deep(img) { max-width: 100%; height: auto; border-radius: 0.5rem; }
.prose :deep(a) { color: #3b82f6; text-decoration: none; }
.prose :deep(a:hover) { text-decoration: underline; }
</style>