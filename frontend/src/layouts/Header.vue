<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import logoTop from '@/assets/images/logo_top.png'

const router = useRouter()
const route = useRoute()

const defaultGuideUrl = 'https://itc.ynu.edu.cn/info/1013/1799.htm'

const externalLinks = {
  createAgent: defaultGuideUrl,
  submitWork: defaultGuideUrl,
  agentPlaza: 'https://agent.ynu.edu.cn',
  contact: 'https://www.ynu.edu.cn/',
  signup: defaultGuideUrl,
}

const navItems = [
  { label: '首页', path: '/' },
  { label: '智能体中心', path: '/agent-center' },
  { label: '参赛作品', path: '/works' },
  { label: '新闻资讯', path: '/news' },
]

const openExternal = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

const goTo = (item: any) => {
  if (item.externalUrl) {
    openExternal(item.externalUrl)
    return
  }
  if (route.path !== item.path) {
    router.push(item.path)
  }
}

const isActive = (item: any) => {
  if (!item.path) return false
  if (item.path === '/') return route.path === '/'
  return route.path.startsWith(item.path)
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
          <p class="w-[30px] h-[4px] rounded-[2px] mt-4" :class="{ 'bg-[linear-gradient(90deg,#047eff_18%,#0052ff_87%)]': isActive(item) }"></p>
        </button>
      </nav>

      <div class="hidden items-center lg:flex">
        <el-button
          type="primary"
          round
          size="large"
          class="!h-[38px] !px-0 !w-[100px] !text-[16px] !font-[500] !bg-[linear-gradient(90deg,#248fff_15%,#3777ff_73%)]!"
          @click="openExternal(externalLinks.signup)"
        >
          立即报名
        </el-button>
      </div>
    </div>
  </header>
</template>