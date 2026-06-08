import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'

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
    } catch {
      logout()
    }
  }

  async function updateUser(data: Partial<User>) {
    if (!user.value) return
    const response = await userApi.update(user.value.id, data)
    user.value = response.data
    return response.data
  }

  async function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    loading.value = true
    try {
      const response = await authApi.logout()
      // 如果是CAS登录，跳转到CAS logout页面
      if (response.data.cas_logout_url) {
        window.location.href = response.data.cas_logout_url
        return
      }
    } catch (e) {
      console.log('Logout API error:', e)
    } finally {
      loading.value = false
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
    isLoggedIn,
    isAdmin,
    isReviewer,
    login,
    unifiedAuthLogin,
    fetchUser,
    updateUser,
    logout
  }
})