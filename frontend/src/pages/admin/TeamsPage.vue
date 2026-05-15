<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import Dialog from '@/components/Dialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useNotification } from '@/composables/useNotification'

const authStore = useAuthStore()
const { success, error } = useNotification()

const teams = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 20
const statusFilter = ref('')
const keyword = ref('')
const themes = ref<any[]>([])
const currentUser = ref<any>(null)
const userHasTeam = ref(false)
const userTeamId = ref<number | null>(null)

// 多选状态
const selectedTeams = ref<Set<number>>(new Set())

const showDialog = ref(false)
const dialogType = ref<'detail' | 'create' | 'edit'>('detail')
const editingTeam = ref<any>(null)
const teamMembers = ref<any[]>([])
const formData = ref({
  name: '',
  description: '',
  members: [{ student_id: '', name: '', is_leader: true }]
})

// Confirm dialog state
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)

const canAudit = computed(() => authStore.isAdmin || authStore.isReviewer)
const selectedCount = computed(() => selectedTeams.value.size)
const allSelected = computed(() => teams.value.length > 0 && selectedTeams.value.size === teams.value.length)

onMounted(async () => {
  // 获取当前用户信息
  currentUser.value = authStore.user
  await fetchUserTeamStatus()
  await fetchTeams()
  await fetchThemes()
})

function toggleSelectAll() {
  if (allSelected.value) {
    selectedTeams.value.clear()
  } else {
    selectedTeams.value = new Set(teams.value.map(t => t.id))
  }
}

function toggleSelect(teamId: number) {
  if (selectedTeams.value.has(teamId)) {
    selectedTeams.value.delete(teamId)
  } else {
    selectedTeams.value.add(teamId)
  }
  selectedTeams.value = new Set(selectedTeams.value)
}

function clearSelection() {
  selectedTeams.value.clear()
}

async function fetchUserTeamStatus() {
  try {
    const res = await api.get('/teams/my/team')
    if (res.data) {
      userHasTeam.value = true
      userTeamId.value = res.data.id
    }
  } catch (e) {
    userHasTeam.value = false
    userTeamId.value = null
  }
}

async function fetchTeams() {
  loading.value = true
  try {
    const res = await api.get('/teams', {
      params: {
        page: page.value,
        page_width: pageSize,
        status: statusFilter.value || undefined,
        keyword: keyword.value || undefined
      }
    })
    teams.value = res.data.items || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchThemes() {
  try {
    const res = await api.get('/settings/competition-themes')
    themes.value = res.data.items || []
  } catch (e) {
    themes.value = []
  }
}

async function openDetail(team: any) {
  try {
    const res = await api.get(`/teams/${team.id}`)
    editingTeam.value = res.data
    teamMembers.value = res.data.members || []
    dialogType.value = 'detail'
    showDialog.value = true
  } catch (e: any) {
    error('加载失败')
  }
}

async function openEdit(team: any) {
  // 只有队长可以编辑
  if (team.leader_id !== authStore.user?.id) {
    error('操作失败', '只有队长可以编辑队伍')
    return
  }
  try {
    const res = await api.get(`/teams/${team.id}`)
    editingTeam.value = res.data
    teamMembers.value = res.data.members || []
    // Populate form data for editing (只允许编辑名称和描述)
    formData.value = {
      name: res.data.name,
      description: res.data.description || '',
      members: res.data.members?.filter((m: any) => !m.is_leader).map((m: any) => ({
        student_id: m.student_id,
        name: m.name,
        is_leader: false
      })) || []
    }
    dialogType.value = 'edit'
    showDialog.value = true
  } catch (e: any) {
    error('加载失败')
  }
}

async function handleAudit(status: string) {
  if (!editingTeam.value) return
  try {
    await api.put(`/teams/${editingTeam.value.id}/audit`, { status })
    showDialog.value = false
    await fetchTeams()
    success('操作成功')
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function handleDelete(team: any) {
  confirmMessage.value = `确定删除队伍 "${team.name}" 吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    try {
      await api.delete(`/teams/${team.id}`)
      success('删除成功')
      await fetchTeams()
    } catch (e: any) {
      error('删除失败', e.response?.data?.detail)
    }
  }
}

function openCreateTeam() {
  if (!canAudit.value && userHasTeam.value) {
    error('创建失败', '您已经创建或加入了队伍，不能再创建新队伍')
    return
  }
  editingTeam.value = null
  // 默认使用当前用户作为队长
  formData.value = {
    name: '',
    description: '',
    members: [{
      student_id: currentUser.value?.username || '',
      name: currentUser.value?.nickname || currentUser.value?.username || '',
      is_leader: true
    }]
  }
  dialogType.value = 'create'
  showDialog.value = true
}

function addMember() {
  formData.value.members.push({ student_id: '', name: '', is_leader: false })
}

function removeMember(index: number) {
  // 队长不能删除
  if (formData.value.members[index].is_leader) {
    error('操作失败', '队长不能删除')
    return
  }
  if (formData.value.members.length > 1) {
    formData.value.members.splice(index, 1)
  }
}

async function handleSaveTeam() {
  try {
    const data = { ...formData.value }
    // Remove is_leader from members as it's set server-side
    data.members = data.members.map((m: any) => ({
      student_id: m.student_id,
      name: m.name,
      is_leader: m.is_leader
    }))
    if (editingTeam.value) {
      await api.put(`/teams/${editingTeam.value.id}`, data)
      success('更新成功')
    } else {
      await api.post('/teams', data)
      success('创建成功')
    }
    showDialog.value = false
    await fetchTeams()
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

// 批量删除
async function handleBatchDelete() {
  if (selectedTeams.value.size === 0) return
  confirmMessage.value = `确定删除选中的 ${selectedTeams.value.size} 个队伍吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    let successCount = 0
    let failCount = 0
    for (const teamId of selectedTeams.value) {
      try {
        await api.delete(`/teams/${teamId}`)
        successCount++
      } catch (e: any) {
        failCount++
      }
    }
    clearSelection()
    await fetchTeams()
    if (failCount === 0) {
      success(`成功删除 ${successCount} 个队伍`)
    } else {
      error(`删除完成`, `成功 ${successCount} 个，失败 ${failCount} 个`)
    }
  }
}

// 批量审核通过
async function handleBatchAudit(status: string) {
  if (selectedTeams.value.size === 0) return
  confirmMessage.value = `确定将选中的 ${selectedTeams.value.size} 个队伍审核${status === 'approved' ? '通过' : '拒绝'}吗？`
  showConfirm.value = true
  confirmCallback.value = async () => {
    let successCount = 0
    let failCount = 0
    for (const teamId of selectedTeams.value) {
      try {
        await api.put(`/teams/${teamId}/audit`, { status })
        successCount++
      } catch (e: any) {
        failCount++
      }
    }
    clearSelection()
    await fetchTeams()
    if (failCount === 0) {
      success(`成功审核 ${successCount} 个队伍`)
    } else {
      error(`审核完成`, `成功 ${successCount} 个，失败 ${failCount} 个`)
    }
  }
}

function handlePageChange(newPage: number) {
  page.value = newPage
  clearSelection()
  fetchTeams()
}

function handleSearch() {
  page.value = 1
  clearSelection()
  fetchTeams()
}

function getStatusClass(status: string) {
  switch (status) {
    case 'pending': return 'bg-amber-100 text-amber-700 border-amber-200'
    case 'approved': return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    case 'rejected': return 'bg-red-100 text-red-700 border-red-200'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'pending': return '待审核'
    case 'approved': return '已通过'
    case 'rejected': return '已拒绝'
    default: return status
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">队伍管理</h1>
        <p class="text-sm text-gray-500 mt-1">管理参赛队伍和成员信息</p>
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
        <div v-if="!canAudit && userHasTeam" class="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-100 text-gray-400 rounded-xl cursor-not-allowed font-medium">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          已有队伍
        </div>
        <button
          v-else
          @click="openCreateTeam"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          创建队伍
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex flex-col lg:flex-row gap-4">
        <div class="flex-1">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input
              v-model="keyword"
              type="text"
              placeholder="搜索队伍名..."
              class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              @keyup.enter="handleSearch"
            />
          </div>
        </div>
        <select
          v-model="statusFilter"
          class="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white"
          @change="handleSearch"
        >
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">已拒绝</option>
        </select>
        <button
          @click="handleSearch"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
        >
          搜索
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
              <th class="px-4 py-4 text-left text-sm font-semibold text-gray-700 w-10">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  :indeterminate="selectedCount > 0 && !allSelected"
                  @change="toggleSelectAll"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </th>
              <th class="px-4 py-4 text-left text-sm font-semibold text-gray-700">ID</th>
              <th class="px-4 py-4 text-left text-sm font-semibold text-gray-700">队名</th>
              <th class="px-4 py-4 text-left text-sm font-semibold text-gray-700">成员数</th>
              <th class="px-4 py-4 text-left text-sm font-semibold text-gray-700">创建时间</th>
              <th class="px-4 py-4 text-left text-sm font-semibold text-gray-700">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="team in teams"
              :key="team.id"
              :class="selectedTeams.has(team.id) ? 'bg-blue-50/50' : 'hover:bg-blue-50/50'"
              class="transition-colors"
            >
              <td class="px-4 py-4">
                <input
                  type="checkbox"
                  :checked="selectedTeams.has(team.id)"
                  @change="toggleSelect(team.id)"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">#{{ team.id }}</td>
              <td class="px-4 py-4">
                <button @click="openEdit(team)" class="font-medium text-gray-900 hover:text-blue-600 hover:underline text-left">
                  {{ team.name }}
                </button>
              </td>
              <td class="px-4 py-4">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  {{ team.members?.length || 0 }} 人
                </span>
              </td>
              <td class="px-4 py-4 text-sm text-gray-500">
                {{ new Date(team.created_at).toLocaleDateString('zh-CN') }}
              </td>
              <td class="px-4 py-4">
                <div class="flex items-center gap-2">
                  <button
                    @click="openDetail(team)"
                    class="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                  >
                    详情
                  </button>
                  <button
                    v-if="team.leader_id === authStore.user?.id"
                    @click="openEdit(team)"
                    class="px-3 py-1.5 text-sm font-medium text-green-600 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                  >
                    编辑
                  </button>
                  <button
                    v-if="team.leader_id === authStore.user?.id || canAudit"
                    @click="handleDelete(team)"
                    class="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Loading / Empty -->
      <div v-if="loading" class="text-center py-16">
        <div class="inline-flex items-center gap-3 text-gray-500">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          加载中...
        </div>
      </div>
      <div v-else-if="teams.length === 0" class="text-center py-16">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <p class="text-gray-500">暂无队伍数据</p>
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

    <!-- Team Detail Dialog -->
    <Dialog
      :show="showDialog && dialogType === 'detail'"
      :title="editingTeam?.name || '队伍详情'"
      subtitle="队伍成员信息"
      width="lg"
      @close="showDialog = false"
    >
      <div class="p-6 space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-500">描述</label>
          <p class="mt-1 text-gray-900">{{ editingTeam?.description || '暂无描述' }}</p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-500">状态</label>
          <p class="mt-1">
            <span
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border"
              :class="getStatusClass(editingTeam?.status)"
            >
              {{ getStatusText(editingTeam?.status) }}
            </span>
          </p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-500 mb-2">成员列表</label>
          <div class="bg-gray-50 rounded-xl overflow-hidden">
            <table class="w-full">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">姓名</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">学工号</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">角色</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="member in teamMembers" :key="member.id">
                  <td class="px-4 py-2.5 text-sm text-gray-900">{{ member.name }}</td>
                  <td class="px-4 py-2.5 text-sm text-gray-600">{{ member.student_id }}</td>
                  <td class="px-4 py-2.5">
                    <span v-if="member.is_leader" class="px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs font-medium">队长</span>
                    <span v-else class="text-gray-500 text-xs">成员</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-100 flex gap-3">
        <template v-if="canAudit && editingTeam?.status === 'pending'">
          <button
            @click="handleAudit('approved')"
            class="flex-1 py-2.5 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-emerald-500/25 transition-all"
          >
            通过
          </button>
          <button
            @click="handleAudit('rejected')"
            class="flex-1 py-2.5 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-red-500/25 transition-all"
          >
            拒绝
          </button>
        </template>
        <button
          v-else
          @click="showDialog = false"
          class="w-full py-2.5 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-all"
        >
          关闭
        </button>
      </div>
    </Dialog>

    <!-- Create/Edit Team Dialog -->
    <Dialog
      :show="showDialog && (dialogType === 'create' || dialogType === 'edit')"
      :title="dialogType === 'edit' ? '编辑队伍' : '创建队伍'"
      :subtitle="dialogType === 'edit' ? '修改队伍信息' : '创建新的参赛队伍'"
      width="lg"
      @close="showDialog = false"
    >
      <form @submit.prevent="handleSaveTeam" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">队名 <span class="text-red-500">*</span></label>
          <input
            v-model="formData.name"
            type="text"
            required
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="请输入队名"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">描述</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            placeholder="请输入队伍描述"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">成员 <span class="text-xs text-gray-400">(创建后队长不可修改)</span></label>
          <div class="space-y-2">
            <div v-for="(member, index) in formData.members" :key="index" class="flex gap-2 items-center">
              <!-- 队长信息（只读） -->
              <template v-if="member.is_leader">
                <input
                  v-model="member.name"
                  type="text"
                  readonly
                  disabled
                  class="flex-1 px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 text-gray-600 text-sm cursor-not-allowed"
                  placeholder="队长姓名"
                />
                <input
                  v-model="member.student_id"
                  type="text"
                  readonly
                  disabled
                  class="flex-1 px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 text-gray-600 text-sm cursor-not-allowed"
                  placeholder="队长学工号"
                />
                <div class="px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg text-amber-600 text-xs font-medium">
                  队长
                </div>
              </template>
              <!-- 普通成员 -->
              <template v-else>
                <input
                  v-model="member.name"
                  type="text"
                  placeholder="姓名"
                  required
                  class="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm"
                />
                <input
                  v-model="member.student_id"
                  type="text"
                  placeholder="学工号"
                  required
                  class="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm"
                />
                <button
                  type="button"
                  @click="removeMember(index)"
                  class="px-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </template>
            </div>
          </div>
          <button
            type="button"
            @click="addMember"
            class="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            + 添加成员
          </button>
        </div>
        <div class="flex gap-3 pt-4">
          <button
            type="button"
            @click="showDialog = false"
            class="flex-1 py-2.5 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-all"
          >
            取消
          </button>
          <button
            type="submit"
            class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all"
          >
            {{ dialogType === 'edit' ? '保存修改' : '创建' }}
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
  </div>
</template>