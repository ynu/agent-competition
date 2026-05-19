<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import Dialog from '@/components/Dialog.vue'
import { useNotification } from '@/composables/useNotification'
import markdownIt from 'markdown-it'

// 创建 markdown 渲染器
const md = markdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// 渲染 markdown 内容
function renderMarkdown(content: string): string {
  if (!content) return ''
  return md.render(content)
}

const authStore = useAuthStore()
const { success, error } = useNotification()

const messages = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 20
const filter = ref<'all' | 'unread'>('all')
const showDetail = ref(false)
const showSendDialog = ref(false)
const selectedMessage = ref<any>(null)
const receivers = ref<any[]>([])
const selectedReceiverIds = ref<number[]>([])
const receiverSearch = ref('')
const showReceiverDropdown = ref(false)
const selectedRole = ref<string>('')
const sendForm = ref({
  title: '',
  content: ''
})
const sendLoading = ref(false)
const contentPreview = ref('')
const editorMode = ref<'edit' | 'preview'>('edit')
const receiverInputRef = ref<HTMLInputElement | null>(null)

const isAdmin = computed(() => authStore.isAdmin)
const unreadMessages = computed(() => messages.value.filter(m => !m.is_read).slice(0, 10))
const unreadCount = computed(() => messages.value.filter(m => !m.is_read).length)
const filteredMessages = computed(() => {
  let msgs = messages.value
  if (filter.value === 'unread') {
    msgs = msgs.filter(m => !m.is_read)
  }
  return msgs
})

// 选中的用户详情
const selectedReceivers = computed(() => {
  return receivers.value.filter(u => selectedReceiverIds.value.includes(u.id))
})

// 角色选项
const roleOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'reviewer', label: '评审' },
  { value: 'user', label: '普通用户' }
]

// 过滤后的用户列表（搜索匹配，排除已选的）
const filteredReceivers = computed(() => {
  let users = receivers.value
  if (receiverSearch.value) {
    const search = receiverSearch.value.toLowerCase()
    users = users.filter(u =>
      u.username.toLowerCase().includes(search) ||
      (u.nickname && u.nickname.toLowerCase().includes(search))
    )
  }
  return users.slice(0, 50)
})

// 根据角色获取用户
watch(selectedRole, async (role) => {
  if (role && isAdmin.value) {
    try {
      const res = await api.get('/messages/receivers', { params: { role } })
      for (const user of res.data) {
        if (!selectedReceiverIds.value.includes(user.id)) {
          selectedReceiverIds.value.push(user.id)
        }
      }
      selectedRole.value = ''
      success('已添加所有 ' + roleOptions.find(r => r.value === role)?.label)
    } catch (e) {
      error('获取用户失败')
    }
  }
})

async function fetchMessages() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize }
    if (filter.value === 'unread') {
      params.is_read = false
    }
    const res = await api.get('/messages', { params })
    messages.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchReceivers() {
  try {
    const res = await api.get('/messages/receivers')
    receivers.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

function viewMessage(msg: any) {
  selectedMessage.value = msg
  showDetail.value = true
  if (!msg.is_read) {
    api.put(`/messages/${msg.id}/read`).then(() => {
      msg.is_read = true
    })
  }
}

async function markAsRead(msg: any) {
  try {
    await api.put(`/messages/${msg.id}/read`)
    msg.is_read = true
    success('已标记为已读')
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function markAllAsRead() {
  try {
    await api.put('/messages/read-all')
    messages.value.forEach(m => m.is_read = true)
    success('所有消息已标记为已读')
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function sendMessage() {
  if (selectedReceiverIds.value.length === 0) {
    error('发送失败', '请选择接收者')
    return
  }
  if (!sendForm.value.title.trim() || !sendForm.value.content.trim()) {
    error('发送失败', '请填写标题和内容')
    return
  }
  sendLoading.value = true
  try {
    await api.post('/messages', {
      receiver_ids: selectedReceiverIds.value,
      title: sendForm.value.title,
      content: sendForm.value.content
    })
    success('发送成功')
    showSendDialog.value = false
    sendForm.value = { title: '', content: '' }
    selectedReceiverIds.value = []
    receiverSearch.value = ''
    contentPreview.value = ''
    editorMode.value = 'edit'
  } catch (e: any) {
    error('发送失败', e.response?.data?.detail)
  } finally {
    sendLoading.value = false
  }
}

function handlePageChange(newPage: number) {
  page.value = newPage
  fetchMessages()
}

function toggleReceiver(user: any) {
  const index = selectedReceiverIds.value.indexOf(user.id)
  if (index !== -1) {
    selectedReceiverIds.value.splice(index, 1)
  } else {
    selectedReceiverIds.value.push(user.id)
  }
}

function removeReceiver(id: number) {
  const index = selectedReceiverIds.value.indexOf(id)
  if (index !== -1) {
    selectedReceiverIds.value.splice(index, 1)
  }
}

function clearAllReceivers() {
  selectedReceiverIds.value = []
}

function isReceiverSelected(id: number): boolean {
  return selectedReceiverIds.value.includes(id)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Markdown 预览（发送时的实时预览）
function updatePreview() {
  contentPreview.value = renderMarkdown(sendForm.value.content)
}

watch(() => sendForm.value.content, () => {
  if (editorMode.value === 'preview') {
    updatePreview()
  }
})

// 点击外部关闭下拉
let blurTimeout: ReturnType<typeof setTimeout> | null = null

function handleReceiverFocus() {
  showReceiverDropdown.value = true
  if (blurTimeout) {
    clearTimeout(blurTimeout)
    blurTimeout = null
  }
}

function handleReceiverBlur() {
  blurTimeout = setTimeout(() => {
    showReceiverDropdown.value = false
    blurTimeout = null
  }, 200)
}

function handleDropdownClick() {
  if (blurTimeout) {
    clearTimeout(blurTimeout)
    blurTimeout = null
  }
}

onMounted(async () => {
  await fetchMessages()
  if (isAdmin.value) {
    await fetchReceivers()
  }
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">消息管理</h1>
        <p class="text-sm text-gray-500 mt-1">查看和管理站内消息</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          v-if="unreadCount > 0"
          @click="markAllAsRead"
          class="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors"
        >
          全部标为已读
        </button>
        <button
          v-if="isAdmin"
          @click="showSendDialog = true"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          发送消息
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex gap-4">
        <button
          @click="filter = 'all'; fetchMessages()"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
            filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          全部消息
        </button>
        <button
          @click="filter = 'unread'; fetchMessages()"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2',
            filter === 'unread' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          未读消息
          <span v-if="unreadCount > 0" class="px-1.5 py-0.5 text-xs bg-red-500 text-white rounded-full">
            {{ unreadCount }}
          </span>
        </button>
      </div>
    </div>

    <!-- Messages List -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-16">
        <div class="inline-flex items-center gap-3 text-gray-500">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          加载中...
        </div>
      </div>
      <div v-else-if="filteredMessages.length === 0" class="text-center py-16">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
          </svg>
        </div>
        <p class="text-gray-500">暂无消息</p>
      </div>
      <div v-else class="divide-y divide-gray-100">
        <div
          v-for="msg in filteredMessages"
          :key="msg.id"
          @click="viewMessage(msg)"
          :class="[
            'p-4 cursor-pointer transition-all hover:bg-blue-50/50',
            !msg.is_read ? 'bg-blue-50/30' : ''
          ]"
        >
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 pt-1">
              <div v-if="!msg.is_read" class="w-2.5 h-2.5 bg-blue-600 rounded-full"></div>
              <div v-else class="w-2.5 h-2.5 bg-gray-200 rounded-full"></div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <h3 :class="['font-medium truncate', !msg.is_read ? 'text-gray-900' : 'text-gray-700']">
                  {{ msg.title }}
                </h3>
                <span class="text-xs text-gray-400 ml-2 flex-shrink-0">
                  {{ formatDate(msg.created_at) }}
                </span>
              </div>
              <p class="text-sm text-gray-500 mt-1 line-clamp-2">{{ msg.content.replace(/[#*`\[\]]/g, '').substring(0, 100) }}</p>
              <p class="text-xs text-gray-400 mt-2">
                来自: {{ msg.sender_nickname || msg.sender_username }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > pageSize" class="px-6 py-4 border-t border-gray-100 flex justify-center gap-2">
        <button
          @click="handlePageChange(page - 1)"
          :disabled="page === 1"
          class="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          上一页
        </button>
        <span class="px-4 py-2 text-sm text-gray-600">
          第 <span class="font-medium">{{ page }}</span> / <span class="font-medium">{{ Math.ceil(total / pageSize) }}</span> 页
        </span>
        <button
          @click="handlePageChange(page + 1)"
          :disabled="page * pageSize >= total"
          class="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- Message Detail Dialog -->
    <Dialog
      :show="showDetail"
      title="消息详情"
      width="md"
      @close="showDetail = false"
    >
      <div v-if="selectedMessage" class="p-6 space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-500">标题</label>
          <p class="mt-1 text-gray-900 font-medium">{{ selectedMessage.title }}</p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-500">发送者</label>
          <p class="mt-1 text-gray-900">{{ selectedMessage.sender_nickname || selectedMessage.sender_username }}</p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-500">时间</label>
          <p class="mt-1 text-gray-500 text-sm">{{ formatDate(selectedMessage.created_at) }}</p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-500">内容</label>
          <div class="mt-1 text-gray-700 prose prose-sm max-w-none" v-html="renderMarkdown(selectedMessage.content)"></div>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
        <button
          @click="showDetail = false"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
        >
          关闭
        </button>
      </div>
    </Dialog>

    <!-- Send Message Dialog -->
    <Dialog
      :show="showSendDialog"
      title="发送消息"
      width="xl"
      @close="showSendDialog = false"
    >
      <div class="p-6 space-y-4">
        <!-- 角色快速选择 -->
        <div v-if="isAdmin">
          <label class="block text-sm font-medium text-gray-700 mb-2">快速添加（按角色）</label>
          <div class="flex gap-2">
            <button
              v-for="role in roleOptions"
              :key="role.value"
              @click="selectedRole = role.value"
              class="px-3 py-1.5 text-sm font-medium bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
            >
              {{ role.label }}
            </button>
          </div>
        </div>

        <!-- 接收者选择 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            接收者 <span class="text-red-500">*</span>
            <span class="text-gray-400 font-normal">(已选 {{ selectedReceiverIds.length }} 人)</span>
          </label>

          <!-- 搜索输入框 -->
          <div class="relative receiver-dropdown-container">
            <div class="relative">
              <input
                ref="receiverInputRef"
                v-model="receiverSearch"
                @focus="handleReceiverFocus"
                @blur="handleReceiverBlur"
                type="text"
                class="w-full px-4 py-2.5 pr-16 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                placeholder="搜索用户名或昵称..."
              />
              <!-- 清除按钮 -->
              <button
                v-if="selectedReceiverIds.length > 0"
                @click.stop="clearAllReceivers"
                class="absolute right-12 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                title="清除全部"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
              <!-- 下拉箭头 -->
              <div class="absolute right-3 top-1/2 -translate-y-1/2">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
            </div>

            <!-- 下拉列表 -->
            <Transition name="dropdown">
              <div
                v-if="showReceiverDropdown"
                @mousedown="handleDropdownClick"
                class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto"
              >
                <div v-if="filteredReceivers.length === 0" class="px-4 py-6 text-center text-gray-400 text-sm">
                  未找到匹配的用户
                </div>
                <div
                  v-else
                  v-for="user in filteredReceivers"
                  :key="user.id"
                  @click="toggleReceiver(user)"
                  class="px-4 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center gap-3 border-b border-gray-50 last:border-b-0"
                >
                  <!-- 选择框 -->
                  <div :class="[
                    'w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors',
                    isReceiverSelected(user.id)
                      ? 'bg-blue-600 border-blue-600'
                      : 'border-gray-300 bg-white'
                  ]">
                    <svg v-if="isReceiverSelected(user.id)" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                    </svg>
                  </div>
                  <!-- 用户信息 -->
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <div class="w-7 h-7 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {{ (user.nickname || user.username).charAt(0).toUpperCase() }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ user.nickname || user.username }}</p>
                      <p class="text-xs text-gray-500 truncate">{{ user.username }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- 已选择的用户标签 -->
          <div v-if="selectedReceivers.length > 0" class="mt-3 flex flex-wrap gap-2">
            <div
              v-for="user in selectedReceivers"
              :key="user.id"
              class="group inline-flex items-center gap-1.5 pl-2 pr-1 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium"
            >
              <span>{{ user.nickname || user.username }}</span>
              <button
                @click="removeReceiver(user.id)"
                class="p-0.5 rounded hover:bg-blue-200 transition-colors"
                title="移除"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 标题 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">标题 <span class="text-red-500">*</span></label>
          <input
            v-model="sendForm.title"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="请输入消息标题"
          />
        </div>

        <!-- 内容编辑器 -->
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="text-sm font-medium text-gray-700">内容 <span class="text-red-500">*</span></label>
            <!-- 编辑/预览切换 -->
            <div class="flex rounded-lg border border-gray-200 overflow-hidden">
              <button
                @click="editorMode = 'edit'"
                :class="[
                  'px-3 py-1.5 text-xs font-medium transition-colors',
                  editorMode === 'edit' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
                ]"
              >
                编辑
              </button>
              <button
                @click="editorMode = 'preview'; updatePreview()"
                :class="[
                  'px-3 py-1.5 text-xs font-medium transition-colors',
                  editorMode === 'preview' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
                ]"
              >
                预览
              </button>
            </div>
          </div>
          <!-- 编辑模式 -->
          <textarea
            v-if="editorMode === 'edit'"
            v-model="sendForm.content"
            rows="12"
            class="w-full h-[calc(8*1.5rem+2.5rem)] px-4 py-2.5 border border-gray-200 rounded-xl font-mono text-sm resize-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="支持 Markdown 语法：&#10;# 标题&#10;**粗体** *斜体*&#10;- 列表项&#10;[链接](url)&#10;`代码`"
          ></textarea>
          <!-- 预览模式 -->
          <div
            v-else
            class="w-full h-[calc(8*1.5rem+2.5rem)] px-4 py-2.5 border border-gray-200 rounded-xl font-mono text-sm resize-none overflow-y-auto bg-gray-50"
          >
            <div v-if="sendForm.content" v-html="contentPreview" class="prose prose-sm max-w-none"></div>
            <div v-else class="text-gray-400">暂无内容</div>
          </div>
          <p class="text-xs text-gray-400 mt-1">支持 Markdown 语法：# 标题、**粗体**、*斜体*、- 列表、[链接](url)、`代码`</p>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
        <button
          @click="showSendDialog = false"
          class="px-6 py-2.5 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-all"
        >
          取消
        </button>
        <button
          @click="sendMessage"
          :disabled="sendLoading || selectedReceiverIds.length === 0"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ sendLoading ? '发送中...' : '发送' }}
        </button>
      </div>
    </Dialog>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
/* Markdown content styles */
.prose {
  color: #374151;
  line-height: 1.6;
}
.prose :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 1rem 0 0.5rem;
  color: #111827;
}
.prose :deep(h2) {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 1rem 0 0.5rem;
  color: #1f2937;
}
.prose :deep(h3) {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0.75rem 0 0.375rem;
  color: #374151;
}
.prose :deep(p) {
  margin: 0.5rem 0;
}
.prose :deep(ul),
.prose :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}
.prose :deep(li) {
  margin: 0.25rem 0;
}
.prose :deep(code) {
  background: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
  font-family: ui-monospace, monospace;
}
.prose :deep(pre) {
  background: #1f2937;
  color: #e5e7eb;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0.75rem 0;
}
.prose :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}
.prose :deep(blockquote) {
  border-left: 4px solid #d1d5db;
  padding-left: 1rem;
  margin: 0.75rem 0;
  color: #6b7280;
  font-style: italic;
}
.prose :deep(a) {
  color: #2563eb;
  text-decoration: underline;
}
.prose :deep(a:hover) {
  color: #1d4ed8;
}
.prose :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1rem 0;
}
.prose :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.75rem 0;
}
.prose :deep(th),
.prose :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.5rem 0.75rem;
  text-align: left;
}
.prose :deep(th) {
  background: #f9fafb;
  font-weight: 600;
}
.prose :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 0.5rem 0;
}
.prose :deep(strong) {
  font-weight: 600;
}
.prose :deep(em) {
  font-style: italic;
}
/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>