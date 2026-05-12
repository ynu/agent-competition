<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import Dialog from '@/components/Dialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import Notification from '@/components/Notification.vue'

const users = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 20
const roleFilter = ref('')
const keyword = ref('')

const showDialog = ref(false)
const dialogType = ref<'create' | 'edit' | 'reset'>('create')
const resettingUser = ref<any>(null)
const newPassword = ref('')
const editingUser = ref<any>(null)
const formData = ref({
  username: '',
  nickname: '',
  email: '',
  password: '',
  role: 'user'
})

// Confirm dialog state
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref<(() => void) | null>(null)

const notify = ref<InstanceType<typeof Notification> | null>(null)

function showNotification(type: 'success' | 'error' | 'warning' | 'info', title: string, message?: string) {
  if (notify.value) {
    notify.value[type](title, message)
  } else if (typeof window !== 'undefined') {
    ;(window as any).$notify?.[type]?.(title, message)
  }
}

onMounted(() => {
  fetchUsers()
})

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/users', {
      params: {
        page: page.value,
        page_width: pageSize,
        role: roleFilter.value || undefined,
        keyword: keyword.value || undefined
      }
    })
    users.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openDialog(type: 'create' | 'edit' | 'reset', user?: any) {
  dialogType.value = type
  if (type === 'create') {
    editingUser.value = null
    formData.value = { username: '', nickname: '', email: '', password: '', role: 'user' }
  } else if (type === 'edit') {
    editingUser.value = user
    formData.value = {
      username: user.username,
      nickname: user.nickname || '',
      email: user.email || '',
      password: '',
      role: user.role
    }
  } else if (type === 'reset') {
    resettingUser.value = user
    newPassword.value = ''
  }
  showDialog.value = true
}

async function handleSave() {
  try {
    if (editingUser.value) {
      await api.put(`/users/${editingUser.value.id}`, {
        nickname: formData.value.nickname,
        email: formData.value.email,
        role: formData.value.role
      })
      showNotification('success', '更新成功')
    } else {
      await api.post('/users', formData.value)
      showNotification('success', '创建成功')
    }
    showDialog.value = false
    await fetchUsers()
  } catch (e: any) {
    showNotification('error', '操作失败', e.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(user: any) {
  confirmMessage.value = `确定删除用户 "${user.username}" 吗？此操作不可恢复。`
  showConfirm.value = true
  confirmCallback.value = async () => {
    try {
      await api.delete(`/users/${user.id}`)
      showNotification('success', '删除成功')
      await fetchUsers()
    } catch (e: any) {
      showNotification('error', '删除失败', e.response?.data?.detail || '删除失败')
    }
  }
}

async function handleResetPassword() {
  if (!newPassword.value) {
    showNotification('warning', '请输入新密码')
    return
  }
  try {
    await api.post(`/users/${resettingUser.value.id}/reset-password`, {
      new_password: newPassword.value
    })
    showDialog.value = false
    showNotification('success', '密码重置成功')
  } catch (e: any) {
    showNotification('error', '重置密码失败', e.response?.data?.detail || '重置密码失败')
  }
}

function handlePageChange(newPage: number) {
  page.value = newPage
  fetchUsers()
}

function handleSearch() {
  page.value = 1
  fetchUsers()
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">用户管理</h1>
          <p class="text-sm text-gray-500 mt-1">管理系统用户账号与权限</p>
        </div>
        <button
          @click="openDialog('create')"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          添加用户
        </button>
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
            placeholder="搜索用户名 / 昵称 / 邮箱"
            class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            @keyup.enter="handleSearch"
          />
        </div>
        <select
          v-model="roleFilter"
          class="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white min-w-[140px]"
          @change="handleSearch"
        >
          <option value="">全部角色</option>
          <option value="user">普通用户</option>
          <option value="reviewer">评审用户</option>
          <option value="admin">超级用户</option>
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
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">ID</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">用户名</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">昵称</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">邮箱</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">角色</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="user in users"
            :key="user.id"
            class="hover:bg-blue-50/50 transition-colors"
          >
            <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ user.id }}</td>
            <td class="px-6 py-4 text-sm text-gray-800 font-medium">{{ user.username }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ user.nickname || '-' }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ user.email || '-' }}</td>
            <td class="px-6 py-4 text-sm">
              <span
                class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium"
                :class="{
                  'bg-blue-100 text-blue-700': user.role === 'user',
                  'bg-amber-100 text-amber-700': user.role === 'reviewer',
                  'bg-red-100 text-red-700': user.role === 'admin'
                }"
              >
                <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="{
                  'bg-blue-500': user.role === 'user',
                  'bg-amber-500': user.role === 'reviewer',
                  'bg-red-500': user.role === 'admin'
                }"></span>
                {{ user.role === 'user' ? '普通用户' : user.role === 'reviewer' ? '评审用户' : '超级用户' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm">
              <span
                class="inline-flex items-center gap-1.5"
                :class="user.is_active ? 'text-green-600' : 'text-red-600'"
              >
                <span class="w-2 h-2 rounded-full" :class="user.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
                {{ user.is_active ? '正常' : '禁用' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm">
              <div class="flex items-center gap-2">
                <button @click="openDialog('edit', user)" class="text-blue-600 hover:text-blue-700 font-medium transition-colors">编辑</button>
                <span class="text-gray-300">|</span>
                <button @click="openDialog('reset', user)" class="text-amber-600 hover:text-amber-700 font-medium transition-colors">重置密码</button>
                <span class="text-gray-300">|</span>
                <button @click="handleDelete(user)" class="text-red-600 hover:text-red-700 font-medium transition-colors">删除</button>
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
      <div v-else-if="users.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        暂无数据
      </div>

      <!-- Pagination -->
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

    <!-- Create/Edit Dialog -->
    <Dialog
      :show="showDialog && (dialogType === 'create' || dialogType === 'edit')"
      :title="dialogType === 'create' ? '添加用户' : '编辑用户'"
      :subtitle="dialogType === 'create' ? '创建新用户账号' : '修改用户信息'"
      width="md"
      @close="showDialog = false"
    >
      <form @submit.prevent="handleSave" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">用户名</label>
          <input
            v-model="formData.username"
            type="text"
            :disabled="!!editingUser"
            required
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl disabled:bg-gray-100 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">昵称</label>
          <input
            v-model="formData.nickname"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">邮箱</label>
          <input
            v-model="formData.email"
            type="email"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <div v-if="!editingUser">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">密码</label>
          <input
            v-model="formData.password"
            type="password"
            required
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">角色</label>
          <select
            v-model="formData.role"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white"
          >
            <option value="user">普通用户</option>
            <option value="reviewer">评审用户</option>
            <option value="admin">超级用户</option>
          </select>
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
            class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-600/20 font-medium"
          >
            保存
          </button>
        </div>
      </form>
    </Dialog>

    <!-- Reset Password Dialog -->
    <Dialog
      :show="showDialog && dialogType === 'reset'"
      title="重置密码"
      :subtitle="`为用户 ${resettingUser?.username} 重置密码`"
      width="sm"
      @close="showDialog = false"
    >
      <form @submit.prevent="handleResetPassword" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">新密码</label>
          <input
            v-model="newPassword"
            type="password"
            required
            placeholder="请输入新密码"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition-all"
          />
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
            class="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl hover:from-amber-600 hover:to-orange-700 transition-all shadow-lg shadow-amber-500/20 font-medium"
          >
            重置密码
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

    <!-- Notification -->
    <Notification ref="notify" />
  </div>
</template>