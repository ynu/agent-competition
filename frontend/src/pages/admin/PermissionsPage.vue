<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useNotification } from '@/composables/useNotification'

const { success, error } = useNotification()

const permissions = ref<any[]>([])
const roles = ref<any[]>([])
const loading = ref(true)
const activeTab = ref('roles')

const showRoleModal = ref(false)
const editingRole = ref<any>(null)
const roleForm = ref({
  name: '',
  description: '',
  permission_ids: [] as number[]
})

// Confirm dialog state
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)

const categories = [
  { code: 'user', name: '用户管理' },
  { code: 'team', name: '队伍管理' },
  { code: 'work', name: '作品管理' },
  { code: 'review', name: '评审管理' },
  { code: 'content', name: '内容管理' },
  { code: 'setting', name: '配置管理' },
  { code: 'log', name: '日志管理' },
  { code: 'message', name: '消息管理' },
  { code: 'webhook', name: 'Webhook管理' },
  { code: 'event', name: '事件通知' },
]

const permissionsByCategory = computed(() => {
  const grouped: Record<string, any[]> = {}
  categories.forEach(c => grouped[c.code] = [])
  permissions.value.forEach(p => {
    if (grouped[p.category]) {
      grouped[p.category].push(p)
    }
  })
  return grouped
})

onMounted(async () => {
  await fetchPermissions()
  await fetchRoles()
})

async function fetchPermissions() {
  try {
    const res = await api.get('/permissions', { params: { page_size: 100 } })
    permissions.value = res.data.items || []
  } catch (e) {
    console.error(e)
  }
}

async function fetchRoles() {
  loading.value = true
  try {
    const res = await api.get('/permissions/roles', { params: { page_size: 50 } })
    roles.value = res.data.items || []
  } finally {
    loading.value = false
  }
}

function openRoleModal(role?: any) {
  if (role) {
    editingRole.value = role
    roleForm.value = {
      name: role.name,
      description: role.description || '',
      permission_ids: role.permissions?.map((p: any) => p.id) || []
    }
  } else {
    editingRole.value = null
    roleForm.value = { name: '', description: '', permission_ids: [] }
  }
  showRoleModal.value = true
}

function togglePermission(permId: number) {
  const idx = roleForm.value.permission_ids.indexOf(permId)
  if (idx > -1) {
    roleForm.value.permission_ids.splice(idx, 1)
  } else {
    roleForm.value.permission_ids.push(permId)
  }
}

async function saveRole() {
  try {
    if (editingRole.value) {
      await api.put(`/permissions/roles/${editingRole.value.id}`, {
        name: roleForm.value.name,
        description: roleForm.value.description,
        permission_ids: roleForm.value.permission_ids
      })
    } else {
      await api.post('/permissions/roles', roleForm.value)
    }
    showRoleModal.value = false
    success('保存成功')
    await fetchRoles()
  } catch (e: any) {
    error('操作失败', e.response?.data?.detail)
  }
}

async function deleteRole(role: any) {
  confirmMessage.value = `确定删除角色 "${role.name}" 吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    try {
      await api.delete(`/permissions/roles/${role.id}`)
      success('删除成功')
      await fetchRoles()
    } catch (e: any) {
      error('删除失败', e.response?.data?.detail)
    }
  }
}

async function initData() {
  try {
    await api.get('/permissions/init')
    await fetchPermissions()
    await fetchRoles()
    success('初始化成功')
  } catch (e: any) {
    error('初始化失败', e.response?.data?.detail)
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">权限管理</h1>
          <p class="text-sm text-gray-500 mt-1">管理系统角色和权限配置</p>
        </div>
        <button
          @click="initData"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all shadow-lg shadow-gray-600/20 font-medium text-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          初始化数据
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 mb-6">
      <div class="flex border-b border-gray-100">
        <button
          @click="activeTab = 'roles'"
          :class="[
            'px-6 py-4 text-sm font-medium transition relative',
            activeTab === 'roles'
              ? 'text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          <span class="relative z-10">角色管理</span>
          <div v-if="activeTab === 'roles'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"></div>
        </button>
        <button
          @click="activeTab = 'permissions'"
          :class="[
            'px-6 py-4 text-sm font-medium transition relative',
            activeTab === 'permissions'
              ? 'text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          <span class="relative z-10">权限列表</span>
          <div v-if="activeTab === 'permissions'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"></div>
        </button>
      </div>
    </div>

    <!-- Roles Tab -->
    <div v-if="activeTab === 'roles'" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="font-semibold text-gray-800">角色列表</h2>
        <button
          @click="openRoleModal()"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium text-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          新建角色
        </button>
      </div>
      <table class="w-full">
        <thead>
          <tr class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">角色名称</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">描述</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">权限数量</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">系统角色</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="role in roles" :key="role.id" class="hover:bg-blue-50/50 transition-colors">
            <td class="px-6 py-4 text-sm text-gray-900 font-medium">{{ role.name }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ role.description || '-' }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ role.permissions?.length || 0 }}</td>
            <td class="px-6 py-4 text-sm">
              <span v-if="role.is_system" class="inline-flex items-center px-2.5 py-1 bg-gray-100 text-gray-600 rounded-lg text-xs font-medium">系统角色</span>
              <span v-else class="inline-flex items-center px-2.5 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium">自定义</span>
            </td>
            <td class="px-6 py-4 text-sm">
              <div class="flex items-center gap-3">
                <button @click="openRoleModal(role)" class="text-blue-600 hover:text-blue-700 font-medium transition-colors">编辑</button>
                <button v-if="!role.is_system" @click="deleteRole(role)" class="text-red-600 hover:text-red-700 font-medium transition-colors">删除</button>
                <span v-else class="text-gray-400 text-xs">不可操作</span>
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
      <div v-else-if="roles.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        暂无角色
      </div>
    </div>

    <!-- Permissions Tab -->
    <div v-if="activeTab === 'permissions'" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div class="p-4 border-b border-gray-100 mb-6">
        <h2 class="font-semibold text-gray-800">权限列表</h2>
      </div>
      <div class="space-y-6">
        <div v-for="cat in categories" :key="cat.code">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ cat.name }}
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 pl-6">
            <div
              v-for="perm in permissionsByCategory[cat.code]"
              :key="perm.id"
              class="flex items-center gap-2 p-3 rounded-xl bg-gray-50 text-sm hover:bg-blue-50 transition-colors"
            >
              <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              <span class="text-gray-700">{{ perm.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Role Modal -->
    <div v-if="showRoleModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
          <h3 class="text-lg font-semibold text-white">{{ editingRole ? '编辑角色' : '新建角色' }}</h3>
          <p class="text-blue-100 text-sm">{{ editingRole ? '修改角色信息' : '创建新角色' }}</p>
        </div>
        <div class="p-6 overflow-y-auto flex-1 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">角色名称 <span class="text-red-500">*</span></label>
            <input
              v-model="roleForm.name"
              type="text"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              placeholder="请输入角色名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">描述</label>
            <textarea
              v-model="roleForm.description"
              rows="2"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              placeholder="请输入角色描述"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">权限配置</label>
            <div class="space-y-4 max-h-80 overflow-y-auto border border-gray-200 rounded-xl p-4">
              <div v-for="cat in categories" :key="cat.code">
                <h4 class="font-medium text-gray-600 text-sm mb-2 flex items-center gap-2">
                  <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                  </svg>
                  {{ cat.name }}
                </h4>
                <div class="grid grid-cols-2 gap-2 pl-6">
                  <label
                    v-for="perm in permissionsByCategory[cat.code]"
                    :key="perm.id"
                    class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors"
                  >
                    <input
                      type="checkbox"
                      :checked="roleForm.permission_ids.includes(perm.id)"
                      @change="togglePermission(perm.id)"
                      class="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <span class="text-sm text-gray-700">{{ perm.name }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="p-6 border-t border-gray-100 flex justify-end gap-3">
          <button
            @click="showRoleModal = false"
            class="px-5 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 font-medium text-gray-700 transition-colors"
          >
            取消
          </button>
          <button
            @click="saveRole"
            class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
          >
            保存
          </button>
        </div>
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