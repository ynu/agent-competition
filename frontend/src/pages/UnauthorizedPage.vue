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
  <div class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0b0b14]">
    <!-- 绚丽极光背景 -->
    <div class="absolute inset-0" style="background: radial-gradient(at 20% 30%, rgba(0,144,255,0.35) 0px, transparent 50%), radial-gradient(at 80% 70%, rgba(255,92,168,0.3) 0px, transparent 50%), radial-gradient(at 60% 20%, rgba(106,92,255,0.3) 0px, transparent 50%)"></div>

    <div class="anim-fade-up relative text-center">
      <div class="anim-float mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-[24px] bg-gradient-to-br from-[#ff5ca8] to-[#ff3b30] shadow-[0_16px_48px_rgba(255,59,48,0.4)]">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <h1 class="mb-2 text-[28px] font-[700] text-white">{{ isLoggedIn ? '权限不足' : '未登录' }}</h1>
      <p class="mb-4 text-white/70">{{ isLoggedIn ? '您没有权限访问该页面' : '请先登录后再访问' }}</p>
      <p class="text-sm text-white/50">
        <span class="font-[600] text-[#4d9df0]">{{ countdown }}</span> 秒后{{ isLoggedIn ? '返回首页' : '跳转登录页' }}...
      </p>
    </div>
  </div>
</template>
