<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import Dialog from '@/components/Dialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useNotification } from '@/composables/useNotification'
import MarkdownIt from 'markdown-it'

const { success, error } = useNotification()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true
})

const settings = ref<any[]>([])
const themes = ref<any[]>([])
const dragIndex = ref(-1)
const loading = ref(true)
const saving = ref<false | string>(false)
const showDialog = ref(false)
const dialogType = ref<'theme' | 'detail'>('theme')
const editingTheme = ref<any>(null)
const themeForm = ref({
  name: '',
  description: '',
  is_active: true
})

// Confirm dialog state
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)
const detailWork = ref<any>(null)
const showDetailDialog = ref(false)
const clearingData = ref(false)

const formData = ref<Record<string, string>>({})

// 检查是否为版权协议配置
const isCopyrightAgreement = (key: string) => key === 'copyright_agreement'

// 渲染 Markdown 内容预览
const previewCopyrightAgreement = computed(() => {
  const content = formData.value['copyright_agreement'] || ''
  return md.render(content)
})

const settingDescriptions: Record<string, { label: string; desc: string; type: string; placeholder?: string }> = {
  // ========== 基础限制 ==========
  max_votes: { label: 'Max Votes Per User', desc: 'Maximum votes per user (0 = unlimited)', type: 'number', placeholder: '5' },
  max_team_members: { label: 'Max Team Members', desc: 'Maximum members allowed per team', type: 'number', placeholder: '5' },
  max_works_per_team: { label: 'Max Works Per Team', desc: 'Maximum works allowed per team', type: 'number', placeholder: '5' },
  // ========== 报名时间 ==========
  registration_start: { label: 'Registration Start', desc: 'Registration start time (ISO format, empty = no limit)', type: 'datetime-local', placeholder: '2024-01-01T00:00' },
  registration_end: { label: 'Registration End', desc: 'Registration end time (ISO format, empty = no limit)', type: 'datetime-local', placeholder: '2024-12-31T23:59' },
  // ========== 作品提交时间 ==========
  submission_start: { label: 'Submission Start', desc: 'Work submission start time (ISO format, empty = no limit)', type: 'datetime-local', placeholder: '2024-01-01T00:00' },
  submission_end: { label: 'Submission End', desc: 'Work submission end time (ISO format, empty = no limit)', type: 'datetime-local', placeholder: '2024-12-31T23:59' },
  // ========== 投票时间 ==========
  voting_start: { label: 'Voting Start', desc: 'Voting start time (ISO format, empty = no limit)', type: 'datetime-local', placeholder: '2024-01-01T00:00' },
  voting_end: { label: 'Voting End', desc: 'Voting end time (ISO format, empty = no limit)', type: 'datetime-local', placeholder: '2024-12-31T23:59' },
  // ========== 大赛信息 ==========
  competition_theme: { label: 'Competition Theme', desc: 'Competition theme name', type: 'text', placeholder: '智能体创新大赛' },
  competition_description: { label: 'Competition Description', desc: 'Competition theme description', type: 'text', placeholder: 'Competition description...' },
  themes: { label: 'Work Themes', desc: 'Work themes (comma-separated)', type: 'text', placeholder: '智能问答,Agent工作流...' },
  // ========== 统一身份认证 ==========
  cas_enabled: { label: 'Enable CAS', desc: 'Enable CAS 2.0 unified authentication (true/false)', type: 'text', placeholder: 'true/false' },
  cas_base_url: { label: 'CAS Server URL', desc: 'CAS server address', type: 'text', placeholder: 'https://ids.ynu.edu.cn/authserver' },
  base_url: { label: 'Application Base URL', desc: 'For CAS callback, must be publicly accessible in production', type: 'text', placeholder: 'https://your-domain.com' },
  // ========== 版权协议 ==========
  copyright_agreement: { label: 'Copyright Agreement', desc: 'Copyright agreement content (Markdown format)', type: 'textarea', placeholder: 'Enter Markdown content...' },
}

onMounted(async () => {
  await Promise.all([fetchSettings(), fetchThemes()])
})

async function fetchSettings() {
  loading.value = true
  try {
    const res = await api.get('/settings', { params: { page_width: 100 } })
    settings.value = res.data.items || []
    settings.value.forEach((s: any) => {
      formData.value[s.key] = s.value || ''
    })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchThemes() {
  try {
    const res = await api.get('/settings/competition-themes', { params: { page_width: 100 } })
    themes.value = res.data.items || []
  } catch (e: any) {
    console.error(e)
    error('加载主题失败', e.response?.data?.detail || '请确认是否有权限')
  }
}

async function handleSave(key: string) {
  saving.value = key
  try {
    await api.put(`/settings/${key}`, { value: formData.value[key] })
    success('保存成功')
  } catch (e: any) {
    error('保存失败', e.response?.data?.detail)
  } finally {
    saving.value = false
  }
}

function openThemeDialog(theme?: any) {
  if (theme) {
    editingTheme.value = theme
    themeForm.value = {
      name: theme.name,
      description: theme.description || '',
      is_active: theme.is_active
    }
  } else {
    editingTheme.value = null
    themeForm.value = { name: '', description: '', is_active: true }
  }
  dialogType.value = 'theme'
  showDialog.value = true
}

async function handleSaveTheme() {
  try {
    if (editingTheme.value) {
      await api.put(`/settings/competition-themes/${editingTheme.value.id}`, themeForm.value)
    } else {
      await api.post('/settings/competition-themes', themeForm.value)
    }
    showDialog.value = false
    success('保存成功')
    await fetchThemes()
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function handleDeleteTheme(theme: any) {
  confirmMessage.value = `确定删除主题 "${theme.name}" 吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    try {
      await api.delete(`/settings/competition-themes/${theme.id}`)
      success('删除成功')
      await fetchThemes()
    } catch (e: any) {
      error('删除失败', e.response?.data?.detail)
    }
  }
}

async function toggleThemeStatus(theme: any) {
  try {
    await api.put(`/settings/competition-themes/${theme.id}`, {
      is_active: !theme.is_active
    })
    success('操作成功')
    await fetchThemes()
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function handleSortThemes(fromIndex: number, toIndex: number) {
  const item = themes.value.splice(fromIndex, 1)[0]
  themes.value.splice(toIndex, 0, item)

  // Update order in backend
  try {
    await api.put(`/settings/reorder-themes`, {
      theme_ids: themes.value.map((t: any) => t.id)
    })
    success('排序已更新')
  } catch (e: any) {
    console.error('Failed to save order:', e)
    error('保存排序失败', e.response?.data?.detail)
    // Revert on failure
    const reverted = themes.value.splice(toIndex, 1)[0]
    themes.value.splice(fromIndex, 0, reverted)
    await fetchThemes()
  }
}

async function viewThemeWorks(theme: any) {
  try {
    const res = await api.get('/works', { params: { theme_id: theme.id, page_width: 100 } })
    detailWork.value = { ...theme, works: res.data.items || [] }
    showDetailDialog.value = true
  } catch (e: any) {
    error('加载失败')
  }
}

function getSettingInfo(key: string) {
  return settingDescriptions[key] || { label: key, desc: key, type: 'text', placeholder: '' }
}

function onDragStart(index: number) {
  dragIndex.value = index
}

function onDragOver(e: DragEvent, index: number) {
  e.preventDefault()
  // Highlight the drop target
  if (dragIndex.value !== index && dragIndex.value !== -1) {
    const items = document.querySelectorAll('[draggable="true"]')
    items.forEach((item, i) => {
      if (i === index) {
        item.classList.add('bg-blue-50', 'border-blue-300')
      } else {
        item.classList.remove('bg-blue-50', 'border-blue-300')
      }
    })
  }
}

function onDrop(index: number) {
  if (dragIndex.value !== -1 && dragIndex.value !== index) {
    handleSortThemes(dragIndex.value, index)
  }
  dragIndex.value = -1
}

function onDragEnd() {
  dragIndex.value = -1
}

async function handleClearData() {
  confirmMessage.value = '确定要清空所有数据吗？此操作将删除所有用户、队伍、作品、投票、评审和日志，仅保留admin账号、角色/权限和系统配置。此操作不可恢复！'
  showConfirm.value = true
  confirmCallback.value = async () => {
    clearingData.value = true
    try {
      await api.post('/settings/clear-data')
      success('数据清空成功')
    } catch (e: any) {
      error('清空失败', e.response?.data?.detail)
    } finally {
      clearingData.value = false
    }
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">配置管理</h1>
          <p class="text-sm text-gray-500 mt-1">系统参数与大赛配置</p>
        </div>
        <button
          @click="handleClearData"
          :disabled="clearingData"
          class="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-all font-medium text-sm disabled:opacity-50"
        >
          <svg v-if="!clearingData" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
          <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ clearingData ? '清空中...' : '清空数据' }}
        </button>
      </div>
    </div>

    <!-- System Settings -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        系统配置
      </h2>

      <div v-if="loading" class="text-center py-8">
        <div class="inline-flex items-center gap-2 text-gray-500">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          加载中...
        </div>
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="setting in settings.filter(s => s.key !== 'themes' && !s.key.endsWith('_themes'))"
          :key="setting.id"
          class="flex flex-col md:flex-row md:items-center gap-4 p-4 bg-gray-50 rounded-xl hover:shadow-sm transition-shadow"
        >
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-gray-800">{{ getSettingInfo(setting.key).label }}</span>
              <code class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">{{ setting.key }}</code>
            </div>
            <div class="text-sm text-gray-500 mt-1">{{ getSettingInfo(setting.key).desc }}</div>
          </div>
          <!-- 版权协议特殊处理：使用 textarea + 实时预览 -->
          <template v-if="isCopyrightAgreement(setting.key)">
            <div class="flex-1 flex flex-col gap-2">
              <textarea
                v-model="formData[setting.key]"
                :placeholder="getSettingInfo(setting.key).placeholder"
                rows="8"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-mono text-sm resize-y"
              ></textarea>
              <div class="text-xs text-gray-500">
                支持 Markdown 格式，保存后可在协议签署对话框中预览渲染效果
              </div>
            </div>
          </template>
          <template v-else>
            <div class="flex-1">
              <input
                v-model="formData[setting.key]"
                :type="getSettingInfo(setting.key).type"
                :placeholder="getSettingInfo(setting.key).placeholder"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              />
            </div>
          </template>
          <button
            @click="handleSave(setting.key)"
            :disabled="saving === setting.key"
            class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            <span v-if="saving === setting.key">保存中...</span>
            <span v-else>保存</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Competition Themes -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
          </svg>
          智能体主题方向
        </h2>
        <button
          @click="openThemeDialog()"
          class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg shadow-purple-600/20 font-medium text-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          添加主题
        </button>
      </div>

      <p class="text-sm text-gray-500 mb-4">智能体的主题方向，支持拖拽排序</p>

      <div v-if="themes.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
        </svg>
        暂无主题，请添加
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="(theme, index) in themes"
          :key="theme.id"
          class="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-move"
          :class="[theme.is_active ? '' : 'opacity-60', { 'bg-blue-50 border-blue-300': dragIndex === index }]"
          draggable="true"
          @dragstart="onDragStart(index)"
          @dragover="onDragOver($event, index)"
          @drop="onDrop(index)"
          @dragend="onDragEnd"
        >
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-3">
              <div class="text-gray-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"/>
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-800">{{ theme.name }}</h3>
                <span
                  class="inline-flex items-center gap-1 text-xs mt-1"
                  :class="theme.is_active ? 'text-green-600' : 'text-gray-400'"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="theme.is_active ? 'bg-green-500' : 'bg-gray-400'"></span>
                  {{ theme.is_active ? '启用' : '禁用' }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1">
              <button
                @click="toggleThemeStatus(theme)"
                class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                :title="theme.is_active ? '禁用' : '启用'"
              >
                <svg v-if="theme.is_active" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </button>
              <button
                @click="viewThemeWorks(theme)"
                class="p-1.5 text-green-500 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors"
                title="查看作品"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </button>
              <button
                @click="openThemeDialog(theme)"
                class="p-1.5 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                title="编辑"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button
                @click="handleDeleteTheme(theme)"
                class="p-1.5 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                title="删除"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
          <p class="text-sm text-gray-500 line-clamp-2 ml-8">{{ theme.description || '暂无描述' }}</p>
        </div>
      </div>
    </div>

    <!-- Theme Dialog -->
    <Dialog
      :show="showDialog && dialogType === 'theme'"
      :title="editingTheme ? '编辑主题' : '添加主题'"
      :subtitle="editingTheme ? '修改主题信息' : '创建新大赛主题'"
      width="md"
      @close="showDialog = false"
    >
      <form @submit.prevent="handleSaveTheme" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">主题名称 <span class="text-red-500">*</span></label>
          <input
            v-model="themeForm.name"
            type="text"
            required
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
            placeholder="请输入主题名称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">主题描述</label>
          <textarea
            v-model="themeForm.description"
            rows="3"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
            placeholder="请输入主题描述..."
          ></textarea>
        </div>
        <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="themeForm.is_active" type="checkbox" class="rounded text-purple-600 focus:ring-purple-500" />
            <span class="text-sm font-medium text-gray-700">启用此主题</span>
          </label>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="showDialog = false"
            class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 font-medium text-gray-700 transition-colors"
          >
            取消
          </button>
          <button
            type="submit"
            class="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg shadow-purple-600/20 font-medium"
          >
            保存
          </button>
        </div>
      </form>
    </Dialog>

    <!-- Theme Works Detail Dialog -->
    <Dialog
      :show="showDetailDialog"
      :title="`主题作品 - ${detailWork?.name}`"
      :subtitle="`共 ${detailWork?.works?.length || 0} 个作品`"
      width="lg"
      @close="showDetailDialog = false"
    >
      <div class="p-6">
        <div v-if="!detailWork?.works?.length" class="text-center py-8 text-gray-500">
          暂无作品
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="work in detailWork.works"
            :key="work.id"
            class="p-4 bg-gray-50 rounded-xl"
          >
            <div class="flex justify-between items-start">
              <div>
                <h4 class="font-medium text-gray-800">{{ work.name }}</h4>
                <p class="text-sm text-gray-500 mt-1">{{ work.description || '暂无描述' }}</p>
              </div>
              <span
                class="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium"
                :class="{
                  'bg-amber-100 text-amber-700': work.status === 'pending',
                  'bg-green-100 text-green-700': work.status === 'approved',
                  'bg-red-100 text-red-700': work.status === 'rejected'
                }"
              >
                {{ work.status === 'pending' ? '待审核' : work.status === 'approved' ? '已通过' : '已拒绝' }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-100">
        <button
          @click="showDetailDialog = false"
          class="w-full py-2.5 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-all"
        >
          关闭
        </button>
      </div>
    </Dialog>

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