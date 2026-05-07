<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPasswordTab = ref(false)
const error = ref('')
const loading = ref(false)

// Default: show only unified auth, show both when ?localAccount=true
const showBothTabs = computed(() => route.query.localAccount === 'true')

onMounted(() => {
  // Check if there's a token in URL (from CAS callback)
  const token = route.query.token as string
  if (token) {
    console.log('CAS callback: got token', token.substring(0, 20) + '...')
    localStorage.setItem('token', token)
    // Use window.location to force full page reload
    const redirect = route.query.redirect as string || '/admin'
    window.location.href = redirect
  }

  // Default to unified auth if not showing both tabs
  if (!showBothTabs.value) {
    showPasswordTab.value = false
  }
})

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    await authStore.login(username.value, password.value)
    const redirect = route.query.redirect as string || '/admin'
    router.push(redirect)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}

function handleCasLogin() {
  // Redirect to CAS login (backend will handle service URL)
  window.location.href = '/api/auth/cas/login'
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 py-12 px-4 relative overflow-hidden">
    <!-- Background decorations -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl"></div>
    </div>

    <div class="relative max-w-md w-full">
      <!-- Logo & Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4">
          <span class="text-3xl">🤖</span>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">智能体创新大赛</h1>
        <p class="text-white/80">登录到管理系统</p>
      </div>

      <!-- Login Card -->
      <div class="bg-white rounded-2xl shadow-2xl p-8">
        <!-- Login Mode Toggle (only show if showBothTabs) -->
        <div v-if="showBothTabs" class="flex bg-gray-100 rounded-xl p-1 mb-6">
          <button
            @click="showPasswordTab = true"
            class="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
            :class="showPasswordTab ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          >
            账号密码登录
          </button>
          <button
            @click="showPasswordTab = false"
            class="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
            :class="!showPasswordTab ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          >
            统一身份认证
          </button>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Password Login -->
          <template v-if="showBothTabs && showPasswordTab">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">用户名/学工号</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                </div>
                <input
                  v-model="username"
                  type="text"
                  required
                  class="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  placeholder="请输入用户名"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                </div>
                <input
                  v-model="password"
                  type="password"
                  required
                  class="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  placeholder="请输入密码"
                />
              </div>
            </div>
          </template>

          <!-- Unified Auth / Default content -->
          <template v-else>
            <div v-if="!showBothTabs" class="text-center py-4 mb-2">
              <p class="text-sm text-gray-500 mb-6">使用学校统一身份认证账号登录，首次登录将自动创建用户</p>
            </div>

            <!-- Unified Auth Button -->
            <button
              type="button"
              @click="handleCasLogin"
              class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3.5 rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200 flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
              </svg>
              使用统一身份认证登录
            </button>
          </template>

          <!-- Error Message -->
          <div v-if="error" class="flex items-center gap-2 text-red-500 text-sm bg-red-50 p-3 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ error }}
          </div>

          <!-- Submit Button (password login) -->
          <button
            v-if="showPasswordTab"
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3.5 rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <RouterLink to="/" class="text-sm text-gray-500 hover:text-blue-600 transition">
            ← 返回首页
          </RouterLink>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center mt-6 text-white/60 text-sm">
        <p>如有问题请联系管理员</p>
      </div>
    </div>
  </div>
</template>