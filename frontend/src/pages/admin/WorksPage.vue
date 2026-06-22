<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { workApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import Dialog from '@/components/Dialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import CopyrightAgreementDialog from '@/components/CopyrightAgreementDialog.vue'
import { useNotification } from '@/composables/useNotification'

const authStore = useAuthStore()
const { success, error } = useNotification()

const works = ref<any[]>([])
const loading = ref(true)
const uploading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 20
const statusFilter = ref('')
const keyword = ref('')
const teamFilter = ref('')
const themes = ref<any[]>([])
const teams = ref<any[]>([])
const userTeam = ref<any>(null)

const showDialog = ref(false)
const dialogType = ref<'detail' | 'create' | 'edit'>('detail')
const showPdfModal = ref(false)
const showVideoModal = ref(false)
const showCopyrightDialog = ref(false)
const copyrightAgreementStatus = ref<{ has_agreed: boolean } | null>(null)
const editingWork = ref<any>(null)
const formData = ref({
  name: '',
  description: '',
  theme_id: null as number | null,
  team_id: null as number | null,
  agent_url: '',
  agent_editor_url: '',
  pdf_file: null as File | null,
  video_file: null as File | null,
  status: 'pending'
})

// 字段错误提示
const fieldErrors = ref<Record<string, string>>({
  name: '',
  theme_id: '',
  agent_url: '',
  agent_editor_url: '',
  pdf_file: '',
  video_file: ''
})

// 多选状态
const selectedWorks = ref<Set<number>>(new Set())

const canAudit = computed(() => authStore.isAdmin || authStore.isReviewer)
const hasTeam = computed(() => !!userTeam.value)
const canAddWork = computed(() => canAudit.value || hasTeam.value)
// 只有已提交过作品但未签署版权协议的用户才需要签署
const needsCopyrightAgreement = computed(() => {
  if (canAudit.value) return false
  if (copyrightAgreementStatus.value?.has_agreed) return false
  // 检查是否有已提交的作品
  const hasWorks = works.value.length > 0
  return hasWorks
})
const selectedCount = computed(() => selectedWorks.value.size)
const allSelected = computed(() => works.value.length > 0 && selectedWorks.value.size === works.value.length)

function toggleSelectAll() {
  if (allSelected.value) {
    selectedWorks.value.clear()
  } else {
    selectedWorks.value = new Set(works.value.map(w => w.id))
  }
  selectedWorks.value = new Set(selectedWorks.value)
}

function toggleSelect(workId: number) {
  if (selectedWorks.value.has(workId)) {
    selectedWorks.value.delete(workId)
  } else {
    selectedWorks.value.add(workId)
  }
  selectedWorks.value = new Set(selectedWorks.value)
}

function clearSelection() {
  selectedWorks.value.clear()
}

// 批量删除
async function handleBatchDelete() {
  if (selectedWorks.value.size === 0) return
  confirmMessage.value = `确定删除选中的 ${selectedWorks.value.size} 个作品吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    let successCount = 0
    let failCount = 0
    for (const workId of selectedWorks.value) {
      try {
        await api.delete(`/works/${workId}`)
        successCount++
      } catch (e: any) {
        failCount++
      }
    }
    clearSelection()
    await fetchWorks()
    if (failCount === 0) {
      success(`成功删除 ${successCount} 个作品`)
    } else {
      error(`删除完成`, `成功 ${successCount} 个，失败 ${failCount} 个`)
    }
  }
}

// 批量审核
async function handleBatchAudit(status: string) {
  if (selectedWorks.value.size === 0) return
  confirmMessage.value = `确定将选中的 ${selectedWorks.value.size} 个作品审核${status === 'approved' ? '通过' : '拒绝'}吗？`
  showConfirm.value = true
  confirmCallback.value = async () => {
    let successCount = 0
    let failCount = 0
    for (const workId of selectedWorks.value) {
      try {
        await api.put(`/works/${workId}`, { status })
        successCount++
      } catch (e: any) {
        failCount++
      }
    }
    clearSelection()
    await fetchWorks()
    if (failCount === 0) {
      success(`成功审核 ${successCount} 个作品`)
    } else {
      error(`审核完成`, `成功 ${successCount} 个，失败 ${failCount} 个`)
    }
  }
}

// 校验规则
const urlPatterns = {
  agent: /^https:\/\/agent\.ynu\.edu\.cn\/product\/llm\/chat\/.+$/,
  editor: /^https:\/\/agent\.ynu\.edu\.cn\/product\/llm\/(?:personal|workspace)\/.+\/application\/.+\/.+(?:\?.*)?$/
}

function validateField(field: string, value: any): string {
  switch (field) {
    case 'name':
      if (!value || !String(value).trim()) return '请输入作品名称'
      if (String(value).trim().length > 100) return '作品名称不能超过100个字符'
      return ''
    case 'theme_id':
      if (!value) return '请选择主题方向'
      return ''
    case 'agent_url':
      if (!value) return '请输入智能体URL'
      if (!urlPatterns.agent.test(value)) return '智能体URL格式错误，应为 https://agent.ynu.edu.cn/product/llm/chat/<publish_id>'
      return ''
    case 'agent_editor_url':
      if (!value) return '请输入编排URL'
      if (!urlPatterns.editor.test(value)) return '编排URL格式错误，应为 https://agent.ynu.edu.cn/product/llm/(personal|workspace)/<space_id>/application/<app_id>/...'
      return ''
    case 'pdf_file':
      if (!value) return '请上传PDF文档'
      return ''
    case 'video_file':
      if (!value) return '请上传演示视频'
      return ''
    default:
      return ''
  }
}

function validateAllFields(): boolean {
  const errors: Record<string, string> = {}
  let isValid = true

  if (dialogType.value === 'create' || dialogType.value === 'edit') {
    for (const key of ['name', 'theme_id', 'agent_url', 'agent_editor_url']) {
      const err = validateField(key, formData.value[key as keyof typeof formData.value])
      if (err) {
        errors[key] = err
        isValid = false
      }
    }
    if (dialogType.value === 'create') {
      if (!formData.value.pdf_file) errors['pdf_file'] = '请上传PDF文档'
      if (!formData.value.video_file) errors['video_file'] = '请上传演示视频'
      if (!formData.value.pdf_file || !formData.value.video_file) isValid = false
    }
  }

  fieldErrors.value = errors
  return isValid
}

function handleBlur(field: string) {
  const value = formData.value[field as keyof typeof formData.value]
  if (dialogType.value === 'create' || dialogType.value === 'edit') {
    if (field === 'pdf_file' || field === 'video_file') return
    fieldErrors.value[field] = validateField(field, value)
  }
}

// Confirm dialog state
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)

onMounted(async () => {
  if (!canAudit.value) {
    await fetchUserTeam()
    await checkCopyrightAgreementStatus()
  } else {
    await fetchTeams()
  }
  await fetchWorks()
  await fetchThemes()
})

async function checkCopyrightAgreementStatus() {
  try {
    const res = await workApi.checkCopyrightAgreement()
    copyrightAgreementStatus.value = res.data
  } catch (e) {
    copyrightAgreementStatus.value = null
  }
}

async function fetchUserTeam() {
  try {
    const res = await api.get('/teams/my/team')
    if (res.data) {
      userTeam.value = res.data
    }
  } catch (e) {
    userTeam.value = null
  }
}

const availableThemes = computed(() => {
  if (canAudit.value) return themes.value
  // 创建模式下，获取当前队伍已使用的主题
  const usedThemeIds = userTeam.value?.used_theme_ids || []
  return themes.value.filter((t: any) => !usedThemeIds.includes(t.id))
})

// 编辑模式下显示所有主题（包括已使用的）
const editAvailableThemes = computed(() => {
  return themes.value
})

async function fetchWorks() {
  loading.value = true
  try {
    const res = await api.get('/works/admin/list', {
      params: {
        page: page.value,
        page_size: pageSize,
        status: statusFilter.value || undefined,
        keyword: keyword.value || undefined,
        team_name: teamFilter.value || undefined
      }
    })
    works.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchThemes() {
  try {
    const res = await api.get('/settings/competition-themes', { params: { page_size: 100 } })
    themes.value = res.data.items?.filter((t: any) => t.is_active) || []
    // 如果有用户队伍，获取已使用的主题
    if (userTeam.value) {
      await fetchTeamUsedThemes()
    }
  } catch (e) {
    themes.value = []
  }
}

async function fetchTeamUsedThemes() {
  try {
    const res = await api.get('/works/my/works', { params: { page_size: 100 } })
    const usedThemeIds = (res.data.items || []).map((w: any) => w.theme_id).filter(Boolean)
    if (userTeam.value) {
      userTeam.value.used_theme_ids = usedThemeIds
    }
  } catch (e) {
    // 忽略错误
  }
}

async function fetchTeams() {
  try {
    const res = await api.get('/teams', { params: { status: 'approved', page_size: 100 } })
    teams.value = res.data.items || []
  } catch (e) {
    teams.value = []
  }
}

function openDetail(work: any) {
  editingWork.value = work
  dialogType.value = 'detail'
  showDialog.value = true
}

function openCreate() {
  // 检查是否有已审核通过的队伍
  if (!canAudit.value && userTeam.value && userTeam.value.status !== 'approved') {
    error('创建失败', '您的队伍尚未通过审核，无法提交作品')
    return
  }

  // 管理员不需要签署协议
  if (canAudit.value) {
    editingWork.value = null
    formData.value = {
      name: '',
      description: '',
      theme_id: null,
      team_id: userTeam.value?.id || null,
      agent_url: '',
      agent_editor_url: '' as any,
      pdf_file: null,
      video_file: null,
      status: 'pending'
    }
    dialogType.value = 'create'
    showDialog.value = true
    return
  }

  // 检查是否已签署版权协议
  workApi.checkCopyrightAgreement().then(res => {
    if (res.data.has_agreed) {
      // 已签署，打开创建对话框
      editingWork.value = null
      formData.value = {
        name: '',
        description: '',
        theme_id: null,
        team_id: userTeam.value?.id || null,
        agent_url: '',
        agent_editor_url: '' as any,
        pdf_file: null,
        video_file: null,
        status: 'pending'
      }
      dialogType.value = 'create'
      showDialog.value = true
    } else {
      // 未签署，显示签署协议对话框
      showCopyrightDialog.value = true
    }
  }).catch(() => {
    // API错误，默认显示签署对话框
    showCopyrightDialog.value = true
  })
}

function openCreateAfterAgreement() {
  // 协议签署完成后，打开创建对话框，并更新协议签署状态
  if (copyrightAgreementStatus.value) {
    copyrightAgreementStatus.value.has_agreed = true
  }
  editingWork.value = null
  formData.value = {
    name: '',
    description: '',
    theme_id: null,
    team_id: userTeam.value?.id || null,
    agent_url: '',
    agent_editor_url: '' as any,
    pdf_file: null,
    video_file: null,
    status: 'pending'
  }
  dialogType.value = 'create'
  showDialog.value = true
}

function openEdit(work: any) {
  editingWork.value = work
  formData.value = {
    name: work.name,
    description: work.description || '',
    theme_id: work.theme_id || null,
    team_id: work.team_id || null,
    agent_url: work.agent_url || '',
    agent_editor_url: work.agent_editor_url || '' as any,
    pdf_file: null,
    video_file: null,
    status: work.status
  }
  dialogType.value = 'edit'
  showDialog.value = true
}

async function handleSave() {
  // 校验所有字段
  if (!validateAllFields()) {
    error('创建失败', '请检查表单中的错误')
    return
  }

  if (dialogType.value === 'create') {
    uploading.value = true
    const form = new FormData()
    form.append('name', formData.value.name)
    if (formData.value.description) form.append('description', formData.value.description)
    form.append('theme_id', String(formData.value.theme_id))
    if (formData.value.team_id) form.append('team_id', String(formData.value.team_id))
    form.append('agent_url', formData.value.agent_url)
    form.append('agent_editor_url', formData.value.agent_editor_url)
    if (formData.value.pdf_file) form.append('pdf_file', formData.value.pdf_file)
    if (formData.value.video_file) form.append('video_file', formData.value.video_file)

    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/works', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: form
      })
      const data = await res.json()
      if (!res.ok) throw { response: { data } }
      showDialog.value = false
      success('创建成功')
      await fetchWorks()
    } catch (e: any) {
      error('创建失败', e.response?.data?.detail)
    } finally {
      uploading.value = false
    }
  } else {
    try {
      await api.put(`/works/${editingWork.value.id}`, {
        name: formData.value.name,
        description: formData.value.description,
        theme_id: formData.value.theme_id,
        agent_url: formData.value.agent_url,
        agent_editor_url: formData.value.agent_editor_url,
        status: canAudit.value ? formData.value.status : undefined
      })
      showDialog.value = false
      success('更新成功')
      await fetchWorks()
    } catch (e: any) {
      error('操作失败', e.response?.data?.detail)
    }
  }
}

async function handleAudit(status: string) {
  if (!editingWork.value) return
  try {
    await api.put(`/works/${editingWork.value.id}`, { status })
    showDialog.value = false
    success('审核成功')
    await fetchWorks()
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function handleDelete(work: any) {
  confirmMessage.value = `确定删除作品 "${work.name}" 吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    try {
      await api.delete(`/works/${work.id}`)
      success('删除成功')
      await fetchWorks()
    } catch (e: any) {
      error('删除失败', e.response?.data?.detail)
    }
  }
}

async function handleStatusChange(work: any, newStatus: string) {
  try {
    await api.put(`/works/${work.id}`, { status: newStatus })
    success('状态更新成功')
    work.status = newStatus
  } catch (e: any) {
    error('状态更新失败', e.response?.data?.detail)
    await fetchWorks()
  }
}

function openUrl(url: string) {
  if (url) window.open(url, '_blank')
}

function getPdfUrl(path: string) {
  if (!path) return ''
  // 确保正确的URL路径
  const cleanPath = path.replace(/^\.\//, '').replace(/^\//, '')
  return '/' + cleanPath
}

function getVideoUrl(path: string) {
  if (!path) return ''
  const cleanPath = path.replace(/^\.\//, '').replace(/^\//, '')
  return '/' + cleanPath
}

function openPdfViewer() {
  if (editingWork.value?.pdf_file) {
    showPdfModal.value = true
  }
}

function openVideoPlayer() {
  if (editingWork.value?.video_file) {
    showVideoModal.value = true
  }
}

function handlePageChange(newPage: number) {
  page.value = newPage
  clearSelection()
  fetchWorks()
}

function handleSearch() {
  page.value = 1
  clearSelection()
  fetchWorks()
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">作品管理</h1>
          <p class="text-sm text-gray-500 mt-1">管理参赛作品与审核状态</p>
        </div>
        <div class="flex items-center gap-3">
          <!-- 批量操作 -->
          <div v-if="canAudit && selectedCount > 0" class="flex items-center gap-2 mr-2">
            <span class="text-sm text-gray-500">已选 {{ selectedCount }} 项</span>
            <button
              @click="handleBatchAudit('approved')"
              class="px-3 py-1.5 text-sm font-medium text-emerald-600 bg-emerald-50 rounded-lg hover:bg-emerald-100 transition-colors"
            >
              批量通过
            </button>
            <button
              @click="handleBatchAudit('rejected')"
              class="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
            >
              批量拒绝
            </button>
            <button
              @click="handleBatchDelete"
              class="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
            >
              批量删除
            </button>
            <button @click="clearSelection" class="px-3 py-1.5 text-sm font-medium text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
              取消选择
            </button>
          </div>
          <!-- 版权协议签署按钮 -->
          <button
            v-if="needsCopyrightAgreement"
            @click="showCopyrightDialog = true"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-xl hover:from-amber-600 hover:to-amber-700 transition-all shadow-lg shadow-amber-500/20 font-medium"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            版权协议签署
          </button>
          <button
            v-if="canAddWork"
            @click="openCreate"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
            </svg>
            添加作品
          </button>
          <div
            v-else-if="!needsCopyrightAgreement"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-gray-100 text-gray-400 rounded-xl cursor-not-allowed font-medium"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
            </svg>
            请先创建队伍
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-1 relative">
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索作品名"
            class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="flex-1 relative">
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <input
            v-model="teamFilter"
            type="text"
            placeholder="搜索队伍名"
            class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            @keyup.enter="handleSearch"
          />
        </div>
        <select
          v-model="statusFilter"
          class="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white min-w-[140px]"
          @change="handleSearch"
        >
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">已拒绝</option>
        </select>
        <button
          @click="handleSearch"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
        >
          搜索
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
            <th class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider w-10">
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="selectedCount > 0 && !allSelected"
                @change="toggleSelectAll"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </th>
            <th class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">作品名</th>
            <th class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">队伍</th>
            <th class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">主题</th>
            <th class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">投票</th>
            <th v-if="authStore.isAdmin" class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">版权协议</th>
            <th class="px-4 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="work in works"
            :key="work.id"
            :class="selectedWorks.has(work.id) ? 'bg-blue-50/50' : 'hover:bg-blue-50/50'"
            class="transition-colors"
          >
            <td class="px-4 py-4">
              <input
                type="checkbox"
                :checked="selectedWorks.has(work.id)"
                @change="toggleSelect(work.id)"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </td>
            <td class="px-4 py-4">
              <button @click="openEdit(work)" class="text-sm text-gray-800 font-medium hover:text-blue-600 hover:underline text-left">
                {{ work.name }}
              </button>
            </td>
            <td class="px-4 py-4 text-sm text-gray-600">{{ work.team_name || '-' }}</td>
            <td class="px-4 py-4 text-sm text-gray-600">{{ work.theme_name || '-' }}</td>
            <td class="px-4 py-4 text-sm">
              <div class="flex items-center gap-1 text-gray-600">
                <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                </svg>
                {{ work.vote_count }}
              </div>
            </td>
            <td v-if="authStore.isAdmin" class="px-4 py-4 text-sm">
              <span
                v-if="work.leader_has_copyright_agreement !== undefined"
                :class="work.leader_has_copyright_agreement ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
              >
                <svg v-if="work.leader_has_copyright_agreement" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
                {{ work.leader_has_copyright_agreement ? '已签署' : '未签署' }}
              </span>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="px-4 py-4 text-sm">
              <div class="flex items-center gap-2">
                <button @click="openDetail(work)" class="text-blue-600 hover:text-blue-700 font-medium transition-colors">详情</button>
                <span class="text-gray-300">|</span>
                <button
                  v-if="canAudit || work.team_leader_id === authStore.user?.id"
                  @click="openEdit(work)"
                  class="text-green-600 hover:text-green-700 font-medium transition-colors"
                >
                  编辑
                </button>
                <template v-if="canAudit || work.team_leader_id === authStore.user?.id">
                  <span class="text-gray-300">|</span>
                  <button @click="handleDelete(work)" class="text-red-600 hover:text-red-700 font-medium transition-colors">删除</button>
                </template>
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
      <div v-else-if="works.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
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

    <!-- Detail Dialog -->
    <Dialog
      :show="showDialog && dialogType === 'detail'"
      :title="editingWork?.name || '作品详情'"
      subtitle="作品详细信息"
      width="3xl"
      @close="showDialog = false"
    >
      <div class="p-6 space-y-5">
        <div class="grid md:grid-cols-2 gap-5">
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">队伍</label>
            <p class="text-gray-800 font-medium mt-1">{{ editingWork?.team_name }}</p>
          </div>
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">主题</label>
            <p class="text-gray-800 font-medium mt-1">{{ editingWork?.theme || '未设置' }}</p>
          </div>
        </div>

        <div class="bg-gray-50 rounded-xl p-4">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">描述</label>
          <p class="text-gray-800 mt-1 whitespace-pre-wrap">{{ editingWork?.description || '暂无描述' }}</p>
        </div>

        <div class="grid md:grid-cols-2 gap-5">
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">智能体URL</label>
            <button
              v-if="editingWork?.agent_url"
              @click="openUrl(editingWork.agent_url)"
              class="mt-2 inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
              打开链接
            </button>
            <span v-else class="text-gray-400 mt-2 block">-</span>
          </div>
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">编排URL</label>
            <button
              v-if="editingWork?.agent_editor_url"
              @click="openUrl(editingWork.agent_editor_url)"
              class="mt-2 inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
              打开链接
            </button>
            <span v-else class="text-gray-400 mt-2 block">-</span>
          </div>
        </div>

        <div class="grid md:grid-cols-2 gap-5">
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">PDF文档</label>
            <div v-if="editingWork?.pdf_file" class="mt-2">
              <p class="text-blue-600 font-medium text-sm">{{ editingWork.pdf_file.split('/').pop() }}</p>
              <button @click="openPdfViewer" class="inline-flex items-center gap-1 mt-2 text-blue-600 hover:text-blue-700 font-medium text-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                在线预览
              </button>
            </div>
            <span v-else class="text-gray-400 mt-1 block">-</span>
          </div>
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">演示视频</label>
            <div v-if="editingWork?.video_file" class="mt-2">
              <p class="text-blue-600 font-medium text-sm">{{ editingWork.video_file.split('/').pop() }}</p>
              <button @click="openVideoPlayer" class="inline-flex items-center gap-1 mt-2 text-blue-600 hover:text-blue-700 font-medium text-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                在线播放
              </button>
            </div>
            <span v-else class="text-gray-400 mt-1 block">-</span>
          </div>
        </div>

        <div class="grid md:grid-cols-2 gap-5">
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">投票数</label>
            <p class="text-gray-800 font-medium mt-1">{{ editingWork?.vote_count }}</p>
          </div>
          <div class="bg-gray-50 rounded-xl p-4">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">评分</label>
            <p class="text-gray-800 font-medium mt-1">{{ editingWork?.score?.toFixed(1) || '暂无' }}</p>
          </div>
        </div>

        <div v-if="canAudit && editingWork?.status === 'pending'" class="flex gap-3 pt-2">
          <button
            @click="handleAudit('approved')"
            class="flex-1 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 transition-all shadow-lg shadow-green-500/20 font-medium"
          >
            通过审核
          </button>
          <button
            @click="handleAudit('rejected')"
            class="flex-1 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:from-red-600 hover:to-red-700 transition-all shadow-lg shadow-red-500/20 font-medium"
          >
            拒绝
          </button>
        </div>
      </div>
    </Dialog>

    <!-- Create/Edit Dialog -->
    <Dialog
      :show="showDialog && (dialogType === 'create' || dialogType === 'edit')"
      :title="dialogType === 'create' ? '添加作品' : '编辑作品'"
      :subtitle="dialogType === 'create' ? '创建新作品' : '修改作品信息'"
      width="3xl"
      maxHeight="90vh"
      @close="showDialog = false"
    >
      <form @submit.prevent="handleSave" class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">作品名称 <span class="text-red-500">*</span></label>
          <input
            v-model="formData.name"
            type="text"
            required
            :class="fieldErrors.name ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20' : ''"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="请输入作品名称"
            @blur="handleBlur('name')"
          />
          <p v-if="fieldErrors.name" class="mt-1 text-xs text-red-500">{{ fieldErrors.name }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">描述</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="请输入作品描述"
          ></textarea>
        </div>
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">所属队伍</label>
            <div v-if="canAudit">
              <select
                v-model="formData.team_id"
                class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white"
              >
                <option :value="null">请选择队伍</option>
                <option v-for="team in teams" :key="team.id" :value="team.id">{{ team.name }}</option>
              </select>
            </div>
            <div v-else class="px-4 py-2.5 bg-gray-100 border border-gray-200 rounded-xl text-gray-600">
              {{ userTeam?.name || '未加入队伍' }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">主题方向 <span class="text-red-500">*</span></label>
            <select
              v-model="formData.theme_id"
              :disabled="!canAudit && (!userTeam || (dialogType === 'create' ? availableThemes.length === 0 : editAvailableThemes.length === 0))"
              required
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white disabled:bg-gray-100 disabled:text-gray-500"
            >
              <option :value="null">{{ dialogType === 'create' && !canAudit && availableThemes.length === 0 ? '所有主题已使用' : '请选择主题' }}</option>
              <option v-for="theme in (dialogType === 'edit' ? editAvailableThemes : availableThemes)" :key="theme.id" :value="theme.id">{{ theme.name }}</option>
            </select>
          </div>
          <div v-if="(canAudit || hasTeam) && dialogType === 'edit'">
            <label class="block text-sm font-medium text-gray-700 mb-1.5">状态</label>
            <select
              v-model="formData.status"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white"
            >
              <option value="pending">待审核</option>
              <option value="approved">已通过</option>
              <option value="rejected">已拒绝</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            智能体URL <span class="text-red-500">*</span>
            <span class="text-gray-400 font-normal text-xs ml-1" title="发布后的智能体访问URL，格式：https://agent.ynu.edu.cn/product/llm/chat/<publish_id>">ⓘ</span>
          </label>
          <input
            v-model="formData.agent_url"
            type="url"
            required
            :class="fieldErrors.agent_url ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20' : ''"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="https://agent.ynu.edu.cn/product/llm/chat/<publish_id>"
            @blur="handleBlur('agent_url')"
          />
          <p v-if="fieldErrors.agent_url" class="mt-1 text-xs text-red-500">{{ fieldErrors.agent_url }}</p>
          <p v-else class="mt-1 text-xs text-gray-400">发布后的智能体访问URL，如 https://agent.ynu.edu.cn/product/llm/chat/d4oku4car5es72sj05d0</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            编排URL <span class="text-red-500">*</span>
            <span class="text-gray-400 font-normal text-xs ml-1" title="智能体编排页面的URL，格式：https://agent.ynu.edu.cn/product/llm/(personal|workspace)/<space_id>/application/<app_id>/...">ⓘ</span>
          </label>
          <input
            v-model="formData.agent_editor_url"
            type="url"
            required
            :class="fieldErrors.agent_editor_url ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20' : ''"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="https://agent.ynu.edu.cn/product/llm/(personal|workspace)/<space_id>/application/<app_id>/..."
            @blur="handleBlur('agent_editor_url')"
          />
          <p v-if="fieldErrors.agent_editor_url" class="mt-1 text-xs text-red-500">{{ fieldErrors.agent_editor_url }}</p>
          <p v-else class="mt-1 text-xs text-gray-400">智能体编排页面URL，如 https://agent.ynu.edu.cn/product/llm/(personal|workspace)/d356fl226fac72o35sfg/application/d4oknpsar5es72sj04gg/arrange</p>
        </div>
        <div v-if="dialogType === 'create' || dialogType === 'edit'">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            PDF文档 <span class="text-red-500">*</span>
            <span class="text-gray-400 font-normal text-xs ml-1" title="作品设计文档，支持PDF格式，大小不超过10MB">ⓘ</span>
          </label>
          <div :class="fieldErrors.pdf_file ? 'border-red-400' : ''" class="border-2 border-dashed border-gray-200 rounded-xl p-4 text-center hover:border-blue-400 transition-colors">
            <input
              @change="(e: any) => { formData.pdf_file = e.target.files[0]; fieldErrors.pdf_file = '' }"
              type="file"
              accept=".pdf"
              class="hidden"
              id="pdf-upload"
            />
            <label for="pdf-upload" class="cursor-pointer">
              <svg class="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
              </svg>
              <span class="text-sm text-gray-500">{{ formData.pdf_file?.name || '点击上传PDF文件' }}</span>
              <p class="text-xs text-gray-400 mt-1">支持PDF格式，大小不超过10MB</p>
            </label>
          </div>
          <p v-if="fieldErrors.pdf_file" class="mt-1 text-xs text-red-500">{{ fieldErrors.pdf_file }}</p>
        </div>
        <div v-if="dialogType === 'create' || dialogType === 'edit'">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            演示视频 <span class="text-red-500">*</span>
            <span class="text-gray-400 font-normal text-xs ml-1" title="作品演示视频，支持MP4格式，大小不超过50MB">ⓘ</span>
          </label>
          <div :class="fieldErrors.video_file ? 'border-red-400' : ''" class="border-2 border-dashed border-gray-200 rounded-xl p-4 text-center hover:border-blue-400 transition-colors">
            <input
              @change="(e: any) => { formData.video_file = e.target.files[0]; fieldErrors.video_file = '' }"
              type="file"
              accept="video/mp4"
              class="hidden"
              id="video-upload"
            />
            <label for="video-upload" class="cursor-pointer">
              <svg class="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
              </svg>
              <span class="text-sm text-gray-500">{{ formData.video_file?.name || '点击上传MP4视频' }}</span>
              <p class="text-xs text-gray-400 mt-1">支持MP4格式，大小不超过50MB</p>
            </label>
          </div>
          <p v-if="fieldErrors.video_file" class="mt-1 text-xs text-red-500">{{ fieldErrors.video_file }}</p>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="showDialog = false"
            :disabled="uploading"
            class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 font-medium text-gray-700 transition-colors disabled:opacity-50"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="uploading"
            class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium disabled:opacity-50 flex items-center gap-2"
          >
            <svg v-if="uploading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            {{ uploading ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
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

    <!-- PDF Viewer Dialog -->
    <Dialog
      :show="showPdfModal"
      title="PDF文档预览"
      :subtitle="editingWork?.name"
      width="6xl"
      @close="showPdfModal = false"
    >
      <div class="h-[70vh]">
        <iframe :src="getPdfUrl(editingWork?.pdf_file)" class="w-full h-full" frameborder="0"></iframe>
      </div>
    </Dialog>

    <!-- Video Player Dialog -->
    <Dialog
      :show="showVideoModal"
      title="演示视频播放"
      :subtitle="editingWork?.name"
      width="lg"
      @close="showVideoModal = false"
    >
      <div class="p-4 bg-black">
        <video :src="getVideoUrl(editingWork?.video_file)" controls class="w-full rounded-lg" preload="metadata">
          您的浏览器不支持视频播放
        </video>
      </div>
    </Dialog>

    <!-- Copyright Agreement Dialog -->
    <CopyrightAgreementDialog
      :visible="showCopyrightDialog"
      @update:visible="showCopyrightDialog = $event"
      @agreed="openCreateAfterAgreement"
    />
  </div>
</template>