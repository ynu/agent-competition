<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import Dialog from '@/components/Dialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useNotification } from '@/composables/useNotification'

const { success, error } = useNotification()

const channels = ref<any[]>([])
const loading = ref(true)
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingChannel = ref<any>(null)

interface ChannelForm {
  name: string
  channel_type: string
  config: Record<string, string>
  events: string[]
  description: string
  is_active: boolean
}

const form = ref<ChannelForm>({
  name: '',
  channel_type: '',
  config: {},
  events: [],
  description: '',
  is_active: true
})

const channelTypes = ref<{ type: string; name: string; description: string }[]>([])
const eventTypes = ref<Record<string, { name: string; description: string }[]>>({})
const webhookUrl = ref('')

const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)

const testingChannel = ref<number | null>(null)

onMounted(async () => {
  await Promise.all([fetchChannels(), fetchChannelTypes(), fetchEventTypes()])
})

async function fetchChannels() {
  loading.value = true
  try {
    const res = await api.get('/event-channels', { params: { page_size: 100 } })
    channels.value = res.data.items || []
  } catch (e: any) {
    console.error(e)
    error('加载失败', e.response?.data?.detail || '请确认是否有权限')
  } finally {
    loading.value = false
  }
}

async function fetchChannelTypes() {
  try {
    const res = await api.get('/event-channels/types')
    channelTypes.value = res.data || []
  } catch (e: any) {
    console.error(e)
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

function selectChannelType(type: string) {
  form.value.channel_type = type
  if (type === 'wecom-bot') {
    form.value.config = { webhook_url: '' }
    webhookUrl.value = ''
  }
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingChannel.value = null
  form.value = {
    name: '',
    channel_type: '',
    config: {},
    events: [],
    description: '',
    is_active: true
  }
  webhookUrl.value = ''
  showDialog.value = true
}

function openEditDialog(channel: any) {
  dialogMode.value = 'edit'
  editingChannel.value = channel
  form.value = {
    name: channel.name,
    channel_type: channel.channel_type,
    config: channel.config || {},
    events: channel.events || [],
    description: channel.description || '',
    is_active: channel.is_active
  }
  webhookUrl.value = channel.config?.webhook_url || ''
  showDialog.value = true
}

async function handleSave() {
  if (!form.value.name) {
    error('保存失败', '请填写渠道名称')
    return
  }

  if (!form.value.channel_type) {
    error('保存失败', '请选择渠道类型')
    return
  }

  // 验证配置
  if (form.value.channel_type === 'wecom-bot') {
    if (!webhookUrl.value) {
      error('保存失败', '请填写企微机器人 Webhook 地址')
      return
    }
    if (!webhookUrl.value.startsWith('https://qyapi.weixin.qq.com/')) {
      error('保存失败', 'Webhook 地址必须以 https://qyapi.weixin.qq.com/ 开头')
      return
    }
    form.value.config = { webhook_url: webhookUrl.value }
  }

  try {
    if (dialogMode.value === 'create') {
      await api.post('/event-channels', form.value)
      success('创建成功')
    } else {
      await api.put(`/event-channels/${editingChannel.value.id}`, form.value)
      success('更新成功')
    }
    showDialog.value = false
    await fetchChannels()
  } catch (e: any) {
    error('保存失败', e.response?.data?.detail)
  }
}

function confirmDelete(channel: any) {
  confirmMessage.value = `确定要删除通知渠道 "${channel.name}" 吗？`
  confirmCallback.value = async () => {
    try {
      await api.delete(`/event-channels/${channel.id}`)
      success('删除成功')
      await fetchChannels()
    } catch (e: any) {
      error('删除失败', e.response?.data?.detail)
    }
  }
  showConfirm.value = true
}

async function toggleChannel(channel: any) {
  try {
    const res = await api.post(`/event-channels/${channel.id}/toggle`)
    channel.is_active = res.data.is_active
    success(res.data.message)
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function testChannel(channel: any) {
  testingChannel.value = channel.id
  try {
    const res = await api.post(`/event-channels/${channel.id}/test`)
    if (res.data.success) {
      success('测试成功', res.data.message)
    } else {
      error('测试失败', res.data.error)
    }
    // 刷新状态
    await fetchChannels()
  } catch (e: any) {
    error('测试失败', e.response?.data?.detail || '请求失败')
  } finally {
    testingChannel.value = null
  }
}

function formatTime(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function getChannelTypeName(type: string): string {
  const found = channelTypes.value.find(t => t.type === type)
  return found?.name || type
}

function getChannelTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    'wecom-bot': '企'
  }
  return icons[type] || '?'
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '创建通知渠道' : '编辑通知渠道')
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">事件通知渠道</h1>
        <p class="text-gray-500 text-sm mt-1">配置系统事件通知渠道，支持企微机器人等多渠道推送</p>
      </div>
      <button
        @click="openCreateDialog"
        class="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
        </svg>
        创建渠道
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-2xl shadow-sm p-12 text-center">
      <div class="inline-block w-10 h-10 border-4 border-orange-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-4 text-gray-500">加载中...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="channels.length === 0" class="bg-white rounded-2xl shadow-sm p-12 text-center">
      <div class="w-16 h-16 mx-auto bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-700 mb-2">暂无通知渠道</h3>
      <p class="text-gray-500 mb-6">创建您的第一个通知渠道来接收系统事件通知</p>
      <button
        @click="openCreateDialog"
        class="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
      >
        创建第一个渠道
      </button>
    </div>

    <!-- List -->
    <div v-else class="grid gap-4">
      <div
        v-for="channel in channels"
        :key="channel.id"
        class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-lg transition-all"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-lg"
                   :class="{
                     'bg-gradient-to-br from-green-500 to-green-600': channel.channel_type === 'wecom-bot',
                     'bg-gray-400': channel.channel_type !== 'wecom-bot'
                   }">
                {{ getChannelTypeIcon(channel.channel_type) }}
              </div>
              <h3 class="text-lg font-semibold text-gray-800">{{ channel.name }}</h3>
              <span class="px-2.5 py-0.5 text-xs rounded-full font-medium"
                    :class="channel.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                {{ channel.is_active ? '启用' : '禁用' }}
              </span>
              <span class="px-2.5 py-0.5 text-xs bg-blue-100 text-blue-600 rounded-full font-medium">
                {{ getChannelTypeName(channel.channel_type) }}
              </span>
            </div>

            <!-- Config URL -->
            <p v-if="channel.config?.webhook_url" class="text-sm text-blue-600 font-mono truncate">
              {{ channel.config.webhook_url }}
            </p>

            <p v-if="channel.description" class="mt-2 text-sm text-gray-500">{{ channel.description }}</p>

            <!-- Events -->
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="event in channel.events"
                :key="event"
                class="px-2 py-1 text-xs bg-orange-50 text-orange-600 rounded-md font-medium"
              >
                {{ event }}
              </span>
              <span v-if="!channel.events?.length" class="text-xs text-gray-400">未订阅事件</span>
            </div>

            <!-- Last triggered -->
            <div class="mt-3 flex items-center gap-4 text-xs">
              <span class="text-gray-400" v-if="channel.last_triggered_at">
                最后触发: {{ formatTime(channel.last_triggered_at) }}
              </span>
              <span v-else class="text-gray-400">从未触发</span>

              <span v-if="channel.last_trigger_status === true"
                    class="px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                成功
              </span>
              <span v-else-if="channel.last_trigger_status === false"
                    class="px-2 py-0.5 rounded-full bg-red-100 text-red-700">
                失败
              </span>

              <span v-if="channel.last_error" class="text-red-500 max-w-xs truncate" :title="channel.last_error">
                {{ channel.last_error }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-wrap items-center gap-2">
            <button
              @click="testChannel(channel)"
              :disabled="testingChannel === channel.id"
              class="px-3 py-1.5 text-xs bg-purple-100 text-purple-600 rounded-lg hover:bg-purple-200 transition-colors disabled:opacity-50"
            >
              {{ testingChannel === channel.id ? '测试中...' : '测试' }}
            </button>
            <button
              @click="toggleChannel(channel)"
              class="px-3 py-1.5 text-xs rounded-lg transition-colors"
              :class="channel.is_active ? 'bg-yellow-100 text-yellow-600 hover:bg-yellow-200' : 'bg-green-100 text-green-600 hover:bg-green-200'"
            >
              {{ channel.is_active ? '禁用' : '启用' }}
            </button>
            <button
              @click="openEditDialog(channel)"
              class="px-3 py-1.5 text-xs bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
            >
              编辑
            </button>
            <button
              @click="confirmDelete(channel)"
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
      width="xl"
      @close="showDialog = false"
    >
      <div class="p-6 space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">渠道名称 *</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="例如：大赛通知群"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all"
          />
        </div>

        <!-- Channel Type Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">渠道类型 *</label>
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="ct in channelTypes"
              :key="ct.type"
              @click="selectChannelType(ct.type)"
              class="p-4 rounded-xl border-2 text-left transition-all"
              :class="form.channel_type === ct.type
                ? 'border-orange-500 bg-orange-50'
                : 'border-gray-200 bg-white hover:border-gray-300'"
            >
              <div class="flex items-center gap-2 mb-1">
                <span class="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                      :class="{
                        'bg-gradient-to-br from-green-500 to-green-600': ct.type === 'wecom-bot',
                        'bg-gray-400': ct.type !== 'wecom-bot'
                      }">
                  {{ getChannelTypeIcon(ct.type) }}
                </span>
                <span class="font-medium text-gray-800">{{ ct.name }}</span>
              </div>
              <p class="text-xs text-gray-500">{{ ct.description }}</p>
            </button>
          </div>
        </div>

        <!-- WeCom Bot Config -->
        <div v-if="form.channel_type === 'wecom-bot'">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">企微机器人 Webhook 地址 *</label>
          <input
            v-model="webhookUrl"
            type="url"
            placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all font-mono text-sm"
          />
          <p class="text-xs text-gray-400 mt-1">
            在企微群机器人设置中获取 Webhook 地址，格式：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
          </p>
        </div>

        <!-- Events Subscription -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">订阅事件</label>
          <div class="space-y-3 max-h-48 overflow-y-auto pr-2">
            <div v-for="(events, group) in eventTypes" :key="group" class="border border-gray-100 rounded-xl p-3">
              <h4 class="text-sm font-medium text-gray-600 mb-2 flex items-center gap-2">
                <span class="w-2 h-2 bg-orange-500 rounded-full"></span>
                {{ group }}
              </h4>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="evt in events"
                  :key="evt.name"
                  class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border cursor-pointer transition-all"
                  :class="form.events.includes(evt.name) ? 'bg-orange-50 border-orange-300 text-orange-700' : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'"
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
          <label class="block text-sm font-medium text-gray-700 mb-1.5">描述</label>
          <textarea
            v-model="form.description"
            rows="2"
            placeholder="渠道描述..."
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all resize-none"
          ></textarea>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="form.is_active = !form.is_active"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
            :class="form.is_active ? 'bg-orange-500' : 'bg-gray-300'"
          >
            <span
              class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
              :class="form.is_active ? 'translate-x-6' : 'translate-x-1'"
            />
          </button>
          <span class="text-sm text-gray-700">启用此渠道</span>
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
          class="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
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
  </div>
</template>