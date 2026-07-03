<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const countdown = ref(3)
const isLoggedIn = authStore.isLoggedIn

onMounted(() => {
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      if (isLoggedIn) {
        router.push('/admin')
      } else {
        router.push('/login')
      }
    }
  }, 1000)
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="text-center">
      <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-800 mb-2">{{ isLoggedIn ? '权限不足' : '未登录' }}</h1>
      <p class="text-gray-500 mb-4">{{ isLoggedIn ? '您没有权限访问该页面' : '请先登录后再访问' }}</p>
      <p class="text-sm text-gray-400">
        <span class="text-blue-600 font-medium">{{ countdown }}</span> 秒后{{ isLoggedIn ? '返回首页' : '跳转登录页' }}...
      </p>
    </div>
  </div>
</template>