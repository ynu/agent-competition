import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'
import api from '@/api'

export interface User {
  id: number
  username: string
  nickname?: string
  email?: string
  role: 'user' | 'reviewer' | 'admin'
  auth_source: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const permissions = ref<string[]>([])

  // Initialize token from localStorage
  const initToken = () => {
    token.value = localStorage.getItem('token')
  }

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isReviewer = computed(() => user.value?.role === 'reviewer' || user.value?.role === 'admin')

  async function login(username: string, password: string) {
    loading.value = true
    try {
      const response = await authApi.login({ username, password })
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      user.value = response.data.user
      await fetchPermissions()
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function unifiedAuthLogin(code: string) {
    loading.value = true
    try {
      const response = await authApi.unifiedAuth({ code })
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      user.value = response.data.user
      await fetchPermissions()
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await authApi.me()
      user.value = response.data
      await fetchPermissions()
    } catch {
      logout()
    }
  }

  async function fetchPermissions() {
    if (!token.value) return
    try {
      const response = await api.get('/permissions/my-permissions')
      permissions.value = response.data.permissions || []
    } catch {
      permissions.value = []
    }
  }

  function hasPermission(permissionCode: string): boolean {
    // 如果用户是admin，拥有所有权限
    if (user.value?.role === 'admin') return true
    return permissions.value.includes(permissionCode)
  }

  async function updateUser(data: Partial<User>) {
    if (!user.value) return
    const response = await userApi.update(user.value.id, data)
    user.value = response.data
    return response.data
  }

  async function logout() {
    // 关键：先获取token，再清除本地状态，但请求时要带上token
    const currentToken = token.value

    // 立即清除本地状态，防止后续请求带token
    token.value = null
    user.value = null
    localStorage.removeItem('token')

    // 如果有token，调用后端登出API（带上token）
    if (currentToken) {
      try {
        const response = await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        })

        // 如果返回的是HTML页面（含CAS登出按钮），用 document.write 替换当前页面
        const contentType = response.headers.get('content-type') || ''
        if (contentType.includes('text/html')) {
          const html = await response.text()
          document.open()
          document.write(html)
          document.close()
          return
        }

        // 如果是纯JSON响应，检查是否有 cas_logout_url
        const data = await response.json()
        if (data.cas_logout_url) {
          window.location.href = data.cas_logout_url
          return
        }
      } catch (e) {
        console.log('Logout error:', e)
      }
    }
  }

  // Initialize on store creation
  initToken()
  if (token.value) {
    fetchUser()
  }

  return {
    user,
    token,
    loading,
    permissions,
    isLoggedIn,
    isAdmin,
    isReviewer,
    login,
    unifiedAuthLogin,
    fetchUser,
    fetchPermissions,
    hasPermission,
    updateUser,
    logout
  }
})