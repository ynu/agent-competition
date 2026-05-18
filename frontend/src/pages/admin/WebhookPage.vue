<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import Dialog from '@/components/Dialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useNotification } from '@/composables/useNotification'

const { success, error } = useNotification()

const webhooks = ref<any[]>([])
const loading = ref(true)
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingWebhook = ref<any>(null)

const form = ref({
  name: '',
  url: '',
  secret: '',
  events: [] as string[],
  description: '',
  headers: {} as Record<string, string>,
  is_active: true
})

const eventTypes = ref<Record<string, { name: string; description: string }[]>>({})
const headersList = ref<{ key: string; value: string }[]>([])

const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)

const showDeliveries = ref(false)
const currentWebhook = ref<any>(null)
const deliveries = ref<any[]>([])
const deliveriesLoading = ref(false)
const deliveryPage = ref(1)
const deliveryTotal = ref(0)
const testingWebhook = ref<number | null>(null)

onMounted(async () => {
  await Promise.all([fetchWebhooks(), fetchEventTypes()])
})

async function fetchWebhooks() {
  loading.value = true
  try {
    const res = await api.get('/webhooks', { params: { page_size: 100 } })
    webhooks.value = res.data.items || []
  } catch (e: any) {
    console.error(e)
    error('加载失败', e.response?.data?.detail || '请确认是否有权限')
  } finally {
    loading.value = false
  }
}

async function fetchEventTypes() {
  try {
    const res = await api.get('/webhooks/event-types')
    eventTypes.value = res.data || {}
  } catch (e: any) {
    console.error(e)
  }
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingWebhook.value = null
  form.value = {
    name: '',
    url: '',
    secret: '',
    events: [],
    description: '',
    headers: {},
    is_active: true
  }
  headersList.value = []
  showDialog.value = true
}

function openEditDialog(webhook: any) {
  dialogMode.value = 'edit'
  editingWebhook.value = webhook
  form.value = {
    name: webhook.name,
    url: webhook.url,
    secret: '',
    events: webhook.events || [],
    description: webhook.description || '',
    headers: webhook.headers || {},
    is_active: webhook.is_active
  }
  headersList.value = Object.entries(webhook.headers || {}).map(([key, value]) => ({
    key,
    value: value as string
  }))
  showDialog.value = true
}

function addHeader() {
  headersList.value.push({ key: '', value: '' })
}

function removeHeader(index: number) {
  headersList.value.splice(index, 1)
}

async function handleSave() {
  if (!form.value.name || !form.value.url) {
    error('保存失败', '请填写名称和URL')
    return
  }

  if (!form.value.url.startsWith('http://') && !form.value.url.startsWith('https://')) {
    error('保存失败', 'URL必须以 http:// 或 https:// 开头')
    return
  }

  form.value.headers = {}
  headersList.value.forEach(h => {
    if (h.key && h.value) {
      form.value.headers[h.key] = h.value
    }
  })

  try {
    if (dialogMode.value === 'create') {
      await api.post('/webhooks', form.value)
      success('创建成功')
    } else {
      const data = { ...form.value }
      if (!data.secret) {
        delete data.secret
      }
      await api.put(`/webhooks/${editingWebhook.value.id}`, data)
      success('更新成功')
    }
    showDialog.value = false
    await fetchWebhooks()
  } catch (e: any) {
    error('保存失败', e.response?.data?.detail)
  }
}

function confirmDelete(webhook: any) {
  confirmMessage.value = `确定要删除 Webhook "${webhook.name}" 吗？`
  confirmCallback.value = async () => {
    try {
      await api.delete(`/webhooks/${webhook.id}`)
      success('删除成功')
      await fetchWebhooks()
    } catch (e: any) {
      error('删除失败', e.response?.data?.detail)
    }
  }
  showConfirm.value = true
}

async function testWebhook(webhook: any) {
  testingWebhook.value = webhook.id
  try {
    const res = await api.post(`/webhooks/${webhook.id}/test`)
    if (res.data.success) {
      success('测试成功', `状态码: ${res.data.status}`)
    } else {
      error('测试失败', `状态码: ${res.data.status || 'N/A'}`)
    }
  } catch (e: any) {
    error('测试失败', e.response?.data?.detail || '请求失败')
  } finally {
    testingWebhook.value = null
  }
}

async function viewDeliveries(webhook: any) {
  currentWebhook.value = webhook
  showDeliveries.value = true
  deliveryPage.value = 1
  await fetchDeliveries()
}

async function fetchDeliveries() {
  if (!currentWebhook.value) return
  deliveriesLoading.value = true
  try {
    const res = await api.get(`/webhooks/${currentWebhook.value.id}/deliveries`, {
      params: { page: deliveryPage.value, page_size: 20 }
    })
    deliveries.value = res.data.items || []
    deliveryTotal.value = res.data.total || 0
  } catch (e: any) {
    console.error(e)
    error('加载失败', e.response?.data?.detail)
  } finally {
    deliveriesLoading.value = false
  }
}

function formatTime(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function getStatusClass(status: number | null): string {
  if (status === 200) return 'bg-green-100 text-green-700'
  if (status && status >= 200 && status < 300) return 'bg-green-100 text-green-700'
  if (status === 0) return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

function getStatusText(status: number | null): string {
  if (status === 200) return '成功'
  if (status && status >= 200 && status < 300) return '成功'
  if (status === 0) return '失败'
  return status ? `HTTP ${status}` : '超时'
}

function parsePayload(payload: string): string {
  try {
    const obj = JSON.parse(payload)
    return JSON.stringify(obj, null, 2)
  } catch {
    return payload
  }
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '创建 Webhook' : '编辑 Webhook')
const deliveryDialogTitle = computed(() => `投递记录 - ${currentWebhook.value?.name || ''}`)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Webhook 管理</h1>
        <p class="text-gray-500 text-sm mt-1">配置和管理系统 Webhook 回调</p>
      </div>
      <button
        @click="openCreateDialog"
        class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
        </svg>
        创建 Webhook
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-2xl shadow-sm p-12 text-center">
      <div class="inline-block w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-4 text-gray-500">加载中...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="webhooks.length === 0" class="bg-white rounded-2xl shadow-sm p-12 text-center">
      <div class="w-16 h-16 mx-auto bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-700 mb-2">暂无 Webhook</h3>
      <p class="text-gray-500 mb-6">创建您的第一个 Webhook 来接收系统事件通知</p>
      <button
        @click="openCreateDialog"
        class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
      >
        创建第一个 Webhook
      </button>
    </div>

    <!-- List -->
    <div v-else class="grid gap-4">
      <div
        v-for="webhook in webhooks"
        :key="webhook.id"
        class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-lg transition-all"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-800">{{ webhook.name }}</h3>
              <span
                :class="webhook.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                class="px-2.5 py-0.5 text-xs rounded-full font-medium"
              >
                {{ webhook.is_active ? '启用' : '禁用' }}
              </span>
            </div>
            <p class="text-sm text-blue-600 font-mono truncate">{{ webhook.url }}</p>
            <p v-if="webhook.description" class="mt-2 text-sm text-gray-500">{{ webhook.description }}</p>

            <!-- Secret -->
            <div class="mt-3 flex items-center gap-2">
              <span class="text-xs text-gray-400">Secret:</span>
              <code class="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                {{ webhook.secret || '未设置' }}
              </code>
            </div>

            <!-- Events -->
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="event in webhook.events"
                :key="event"
                class="px-2 py-1 text-xs bg-blue-50 text-blue-600 rounded-md font-medium"
              >
                {{ event }}
              </span>
              <span v-if="!webhook.events?.length" class="text-xs text-gray-400">未订阅事件</span>
            </div>

            <!-- Last triggered -->
            <div class="mt-3 flex items-center gap-4 text-xs text-gray-400">
              <span v-if="webhook.last_triggered_at">
                最后触发: {{ formatTime(webhook.last_triggered_at) }}
              </span>
              <span v-else>从未触发</span>
              <span v-if="webhook.last_trigger_status" :class="getStatusClass(webhook.last_trigger_status)" class="px-2 py-0.5 rounded-full">
                {{ getStatusText(webhook.last_trigger_status) }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-wrap items-center gap-2">
            <button
              @click="viewDeliveries(webhook)"
              class="px-3 py-1.5 text-xs bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
            >
              历史
            </button>
            <button
              @click="testWebhook(webhook)"
              :disabled="testingWebhook === webhook.id"
              class="px-3 py-1.5 text-xs bg-purple-100 text-purple-600 rounded-lg hover:bg-purple-200 transition-colors disabled:opacity-50"
            >
              {{ testingWebhook === webhook.id ? '测试中...' : '测试' }}
            </button>
            <button
              @click="openEditDialog(webhook)"
              class="px-3 py-1.5 text-xs bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
            >
              编辑
            </button>
            <button
              @click="confirmDelete(webhook)"
              class="px-3 py-1.5 text-xs bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog
      :show="showDialog"
      :title="dialogTitle"
      width="3xl"
      @close="showDialog = false"
    >
      <div class="p-6 space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">名称 *</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Webhook 名称"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">URL *</label>
          <input
            v-model="form.url"
            type="url"
            placeholder="https://example.com/webhook"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Secret (可选)</label>
          <input
            v-model="form.secret"
            type="password"
            placeholder="留空则不更新，用于签名验证"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          />
          <p class="text-xs text-gray-400 mt-1">用于生成 HMAC-SHA256 签名，接收方可通过 X-Hub-Signature-256 验证</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">订阅事件</label>
          <div class="space-y-3 max-h-48 overflow-y-auto pr-2">
            <div v-for="(events, group) in eventTypes" :key="group" class="border border-gray-100 rounded-xl p-3">
              <h4 class="text-sm font-medium text-gray-600 mb-2 flex items-center gap-2">
                <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                {{ group }}
              </h4>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="evt in events"
                  :key="evt.name"
                  class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border cursor-pointer transition-all"
                  :class="form.events.includes(evt.name) ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'"
                >
                  <input
                    type="checkbox"
                    :value="evt.name"
                    v-model="form.events"
                    class="hidden"
                  />
                  <span class="text-xs font-medium">{{ evt.description }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">自定义请求头</label>
          <div class="space-y-2">
            <div v-for="(header, index) in headersList" :key="index" class="flex gap-2 items-center">
              <input
                v-model="header.key"
                placeholder="Header名称"
                class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
              <input
                v-model="header.value"
                placeholder="Header值"
                class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
              <button
                @click="removeHeader(index)"
                class="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
          <button
            @click="addHeader"
            class="mt-2 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            + 添加请求头
          </button>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">描述</label>
          <textarea
            v-model="form.description"
            rows="2"
            placeholder="Webhook 描述..."
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none"
          ></textarea>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="form.is_active = !form.is_active"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
            :class="form.is_active ? 'bg-blue-600' : 'bg-gray-300'"
          >
            <span
              class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
              :class="form.is_active ? 'translate-x-6' : 'translate-x-1'"
            />
          </button>
          <span class="text-sm text-gray-700">启用此 Webhook</span>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3 border-t">
        <button
          @click="showDialog = false"
          class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-100 font-medium text-gray-700 transition-colors"
        >
          取消
        </button>
        <button
          @click="handleSave"
          class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
        >
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </button>
      </div>
    </Dialog>

    <!-- Delete Confirm -->
    <ConfirmDialog
      v-model="showConfirm"
      :message="confirmMessage"
      type="danger"
      confirm-text="删除"
      @confirm="confirmCallback?.()"
    />

    <!-- Deliveries Dialog -->
    <Dialog
      v-model="showDeliveries"
      :title="deliveryDialogTitle"
      width="4xl"
      max-height="80vh"
    >
      <div class="p-6">
        <div v-if="deliveriesLoading" class="text-center py-8">
          <div class="inline-block w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p class="mt-3 text-gray-500">加载中...</p>
        </div>
        <div v-else-if="deliveries.length === 0" class="text-center py-8 text-gray-500">暂无投递记录</div>
        <div v-else class="space-y-3 max-h-[60vh] overflow-y-auto">
          <div
            v-for="delivery in deliveries"
            :key="delivery.id"
            class="border border-gray-200 rounded-xl p-4 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <span
                  :class="getStatusClass(delivery.response_status)"
                  class="px-2.5 py-0.5 text-xs rounded-full font-medium"
                >
                  {{ getStatusText(delivery.response_status) }}
                </span>
                <span class="text-sm font-medium text-gray-700">{{ delivery.event }}</span>
                <span class="text-xs text-gray-400">#{{ delivery.id }}</span>
              </div>
              <span class="text-xs text-gray-400">{{ formatTime(delivery.created_at) }}</span>
            </div>

            <details class="text-sm">
              <summary class="cursor-pointer text-blue-600 hover:text-blue-700 font-medium">查看载荷</summary>
              <pre class="mt-2 p-3 bg-gray-900 text-gray-100 rounded-lg text-xs overflow-auto max-h-40 font-mono">{{ parsePayload(delivery.payload) }}</pre>
            </details>

            <details v-if="delivery.response_body" class="mt-2 text-sm">
              <summary class="cursor-pointer text-gray-500 hover:text-gray-600">查看响应</summary>
              <pre class="mt-2 p-3 bg-gray-100 rounded-lg text-xs overflow-auto max-h-32 font-mono">{{ delivery.response_body }}</pre>
            </details>

            <div v-if="delivery.error_message" class="mt-2 text-xs text-red-500 bg-red-50 px-3 py-2 rounded-lg">
              错误: {{ delivery.error_message }}
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="deliveryTotal > 20" class="flex justify-center pt-4">
            <div class="flex items-center gap-2">
              <button
                @click="deliveryPage--; fetchDeliveries()"
                :disabled="deliveryPage === 1"
                class="px-3 py-1 rounded-lg border disabled:opacity-50"
              >
                上一页
              </button>
              <span class="text-sm text-gray-500">{{ deliveryPage }} / {{ Math.ceil(deliveryTotal / 20) }}</span>
              <button
                @click="deliveryPage++; fetchDeliveries()"
                :disabled="deliveryPage >= Math.ceil(deliveryTotal / 20)"
                class="px-3 py-1 rounded-lg border disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>