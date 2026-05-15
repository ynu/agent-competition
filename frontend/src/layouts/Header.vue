<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import logoTop from '@/assets/images/logo.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const defaultGuideUrl = '/admin/teams'

const externalLinks = {
  createAgent: 'https://agent.ynu.edu.cn/',
  submitWork: '/admin/teams',
  agentPlaza: '/agent-center',
  contact: '/contact',
  signup: '/login',
}

const navItems = [
  { label: '首页', path: '/' },
  { label: '创建智能体', externalUrl: externalLinks.createAgent },
  { label: '作品提交', externalUrl: externalLinks.submitWork },
  { label: '参赛作品', path: '/works' },
  { label: '课程资料', path: '/materials' },
  { label: '智能体广场', externalUrl: externalLinks.agentPlaza },
  { label: '联系我们', path: '/page/contact' },
]

const openExternal = (url: string) => {
  if (url.startsWith('http')) {
    window.open(url, '_blank', 'noopener,noreferrer')
  } else {
    router.push(url)
  }
}

const goTo = (item: any) => {
  if (item.externalUrl) {
    openExternal(item.externalUrl)
    return
  }
  if (item.path) {
    if (route.path !== item.path) {
      router.push(item.path)
    }
  }
}

const isActive = (item: any) => {
  if (!item.path) return false
  if (item.path === '/') return route.path === '/'
  return route.path.startsWith(item.path)
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="sticky top-0 z-50 h-[80px] bg-white shadow-[0_2px_10px_rgba(0,0,0,0.16)]">
    <div class="mx-auto h-full max-w-[1200px] flex items-center justify-between px-[16px]">
      <RouterLink to="/" class="flex items-center">
        <img :src="logoTop" alt="云南大学" class="h-[51px] w-auto" />
      </RouterLink>

      <nav class="hidden h-full items-center gap-[18px] lg:flex">
        <button
          v-for="item in navItems"
          :key="item.label"
          type="button"
          class="h-full border-0 bg-transparent px-[10px] flex flex-col items-center justify-center text-[18px] text-[#1f1f1f] font-[500] transition-colors cursor-pointer hover:text-[#1f73ff]"
          :class="{ 'text-[#1f73ff]': isActive(item) }"
          @click="goTo(item)"
        >
          {{ item.label }}
          <p class="w-[30px] h-[4px] rounded-[2px]" :class="{ 'bg-[linear-gradient(90deg,#047eff_18%,#0052ff_87%)]': isActive(item) }"></p>
        </button>
      </nav>

      <div class="hidden items-center lg:flex">
        <template v-if="authStore.isLoggedIn">
          <!-- Logged in state -->
          <div class="flex items-center gap-[20px]">
            <RouterLink to="/admin" class="flex items-center gap-[8px] text-[16px] text-[#1f1f1f] hover:text-[#1f73ff] transition-colors">
              <div class="w-[36px] h-[36px] bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white text-[14px] font-medium">
                {{ (authStore.user?.nickname || authStore.user?.username || 'U')[0].toUpperCase() }}
              </div>
              <span class="font-medium">{{ authStore.user?.nickname || authStore.user?.username }}</span>
            </RouterLink>
            <button
              @click="handleLogout"
              class="text-[14px] text-gray-500 hover:text-red-500 transition-colors"
            >
              退出
            </button>
          </div>
        </template>
        <template v-else>
          <!-- Logged out state -->
          <el-button
            type="primary"
            round
            size="large"
            class="!h-[38px] !px-0 !w-[100px] !text-[16px] !font-[500] !bg-[linear-gradient(90deg,#248fff_15%,#3777ff_73%)]!"
            @click="router.push('/login')"
          >
            立即报名
          </el-button>
        </template>
      </div>
    </div>
  </header>
</template>