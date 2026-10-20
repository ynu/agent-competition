<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import logoTop from '@/assets/images/logo.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const externalLinks = {
  createAgent: 'https://agent.ynu.edu.cn/',
  submitWork: '/admin/teams',
  agentPlaza: '/agent-center',
  llmPlatform: 'https://new-api-itc.ynu.edu.cn/',
  contact: '/contact',
  signup: '/login',
}

interface NavLeaf {
  label: string
  path?: string
  externalUrl?: string
}

interface NavItem extends NavLeaf {
  children?: NavLeaf[]
}

const navItems: NavItem[] = [
  { label: '首页', path: '/' },
  { label: '创建智能体', externalUrl: externalLinks.createAgent },
  {
    label: '智能体大赛',
    children: [
      { label: '作品提交', externalUrl: externalLinks.submitWork },
      { label: '参赛作品', path: '/works' },
      { label: '课程资料', path: '/materials' },
    ],
  },
  { label: '智能体广场', externalUrl: externalLinks.agentPlaza },
  { label: '大模型服务平台', externalUrl: externalLinks.llmPlatform },
  { label: '联系我们', path: '/page/contact' },
]

const openExternal = (url: string) => {
  if (url.startsWith('http')) {
    window.open(url, '_blank', 'noopener,noreferrer')
  } else {
    router.push(url)
  }
}

const goTo = (item: NavLeaf) => {
  if (item.externalUrl) {
    openExternal(item.externalUrl)
    return
  }
  if (item.path && route.path !== item.path) {
    router.push(item.path)
  }
}

const activeDropdown = ref<string | null>(null)
const openDropdown = (label: string | null) => {
  activeDropdown.value = label
}

// 桌面端：子菜单命中当前路由时，父项高亮
const isChildActive = (item: NavItem) => {
  if (!item.children) return false
  return item.children.some((child) => child.path && isActivePath(child.path))
}

const isActivePath = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const isActive = (item: NavItem) => {
  if (item.children) return isChildActive(item)
  if (!item.path) return false
  return isActivePath(item.path)
}

// 移动端抽屉
const mobileOpen = ref(false)
const mobileExpanded = ref<string | null>(null)

const toggleMobileExpand = (label: string) => {
  mobileExpanded.value = mobileExpanded.value === label ? null : label
}

const handleMobileClick = (item: NavItem) => {
  if (item.children) {
    toggleMobileExpand(item.label)
    return
  }
  goTo(item)
  mobileOpen.value = false
}

const handleMobileChildClick = (child: NavLeaf) => {
  goTo(child)
  mobileOpen.value = false
}

// 路由变化时关闭抽屉
watch(
  () => route.path,
  () => {
    mobileOpen.value = false
    activeDropdown.value = null
  }
)

const hasChildren = (item: NavItem) => !!item.children?.length

const userInitial = computed(
  () => (authStore.user?.nickname || authStore.user?.username || 'U')[0].toUpperCase()
)
const userName = computed(() => authStore.user?.nickname || authStore.user?.username)

const handleLogout = () => {
  authStore.logout()
  mobileOpen.value = false
  router.push('/')
}
</script>

<template>
  <header class="sticky top-0 z-50 bg-white shadow-[0_2px_10px_rgba(0,0,0,0.16)]">
    <div class="mx-auto max-w-[1200px] lg:h-[80px] flex items-center justify-between px-[16px] h-[60px]">
      <RouterLink to="/" class="flex items-center shrink-0" @click="mobileOpen = false">
        <img :src="logoTop" alt="云南大学" class="h-[51px] w-auto lg:block hidden" />
        <img :src="logoTop" alt="云南大学" class="h-[38px] w-auto lg:hidden" />
      </RouterLink>

      <!-- 桌面端导航 -->
      <nav class="hidden lg:flex h-full items-center gap-[12px]">
        <div
          v-for="item in navItems"
          :key="item.label"
          class="relative h-full"
          @mouseenter="hasChildren(item) && openDropdown(item.label)"
          @mouseleave="hasChildren(item) && openDropdown(null)"
        >
          <button
            type="button"
            class="h-full border-0 bg-transparent px-[10px] flex flex-col items-center justify-center text-[18px] text-[#1f1f1f] font-[500] transition-colors cursor-pointer hover:text-[#1f73ff]"
            :class="{ 'text-[#1f73ff]': isActive(item) }"
            @click="item.children ? openDropdown(activeDropdown === item.label ? null : item.label) : goTo(item)"
          >
            <span class="flex items-center gap-[4px]">
              {{ item.label }}
              <svg
                v-if="hasChildren(item)"
                class="w-[14px] h-[14px] transition-transform duration-200"
                :class="{ 'rotate-180': activeDropdown === item.label }"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M6 9l6 6 6-6" />
              </svg>
            </span>
            <p
              class="w-[30px] h-[4px] rounded-[2px]"
              :class="{ 'bg-[linear-gradient(90deg,#047eff_18%,#0052ff_87%)]': isActive(item) }"
            ></p>
          </button>

          <!-- 下拉子菜单 -->
          <Transition name="dropdown">
            <div
              v-if="hasChildren(item) && activeDropdown === item.label"
              class="absolute left-1/2 -translate-x-1/2 top-full min-w-[160px] whitespace-nowrap bg-white rounded-[8px] shadow-[0_8px_24px_rgba(0,0,0,0.12)] py-[6px]"
            >
              <button
                v-for="child in item.children"
                :key="child.label"
                type="button"
                class="w-full border-0 bg-transparent px-[20px] py-[12px] flex items-center justify-between text-[16px] text-[#1f1f1f] transition-colors cursor-pointer hover:text-[#1f73ff] hover:bg-[#f0f6ff]"
                :class="{ 'text-[#1f73ff] bg-[#f0f6ff]': child.path && isActivePath(child.path) }"
                @click="goTo(child); openDropdown(null)"
              >
                {{ child.label }}
                <svg
                  v-if="child.externalUrl && child.externalUrl.startsWith('http')"
                  class="w-[13px] h-[13px] text-[#999]"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <path d="M15 3h6v6" />
                  <path d="M10 14L21 3" />
                </svg>
              </button>
            </div>
          </Transition>
        </div>
      </nav>

      <!-- 桌面端用户区 -->
      <div class="hidden items-center lg:flex">
        <template v-if="authStore.isLoggedIn">
          <div class="flex items-center gap-[20px]">
            <RouterLink
              to="/admin"
              class="flex items-center gap-[8px] text-[16px] text-[#1f1f1f] hover:text-[#1f73ff] transition-colors"
            >
              <div
                class="w-[36px] h-[36px] bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white text-[14px] font-medium"
              >
                {{ userInitial }}
              </div>
              <span class="font-medium">{{ userName }}</span>
            </RouterLink>
            <button @click="handleLogout" class="text-[14px] text-gray-500 hover:text-red-500 transition-colors">
              退出
            </button>
          </div>
        </template>
        <template v-else>
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

      <!-- 移动端汉堡按钮 -->
      <button
        type="button"
        class="lg:hidden border-0 bg-transparent p-[8px] cursor-pointer text-[#1f1f1f]"
        :aria-expanded="mobileOpen"
        aria-label="打开菜单"
        @click="mobileOpen = !mobileOpen"
      >
        <svg v-if="!mobileOpen" class="w-[24px] h-[24px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M3 6h18M3 12h18M3 18h18" />
        </svg>
        <svg v-else class="w-[24px] h-[24px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 移动端抽屉菜单 -->
    <Transition name="drawer">
      <div v-if="mobileOpen" class="lg:hidden border-t border-[#eee] bg-white max-h-[calc(100vh-60px)] overflow-y-auto">
        <div class="px-[16px] py-[8px]">
          <template v-for="item in navItems" :key="item.label">
            <!-- 有子菜单的项：手风琴 -->
            <div v-if="hasChildren(item)">
              <button
                type="button"
                class="w-full border-0 bg-transparent py-[14px] flex items-center justify-between text-[16px] text-[#1f1f1f] font-[500] cursor-pointer"
                :class="{ 'text-[#1f73ff]': isActive(item) }"
                @click="toggleMobileExpand(item.label)"
              >
                {{ item.label }}
                <svg
                  class="w-[16px] h-[16px] transition-transform duration-200"
                  :class="{ 'rotate-180': mobileExpanded === item.label }"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              <div v-if="mobileExpanded === item.label" class="pb-[8px]">
                <button
                  v-for="child in item.children"
                  :key="child.label"
                  type="button"
                  class="w-full border-0 bg-transparent py-[12px] pl-[16px] flex items-center justify-between text-[15px] text-[#555] transition-colors cursor-pointer hover:text-[#1f73ff]"
                  :class="{ 'text-[#1f73ff]': child.path && isActivePath(child.path) }"
                  @click="handleMobileChildClick(child)"
                >
                  {{ child.label }}
                  <svg
                    v-if="child.externalUrl && child.externalUrl.startsWith('http')"
                    class="w-[13px] h-[13px] text-[#999]"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <path d="M15 3h6v6" />
                    <path d="M10 14L21 3" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 普通项 -->
            <button
              v-else
              type="button"
              class="w-full border-0 bg-transparent py-[14px] flex items-center justify-between text-[16px] text-[#1f1f1f] font-[500] transition-colors cursor-pointer hover:text-[#1f73ff]"
              :class="{ 'text-[#1f73ff]': isActive(item) }"
              @click="handleMobileClick(item)"
            >
              {{ item.label }}
              <svg
                v-if="item.externalUrl && item.externalUrl.startsWith('http')"
                class="w-[14px] h-[14px] text-[#999]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <path d="M15 3h6v6" />
                <path d="M10 14L21 3" />
              </svg>
            </button>
          </template>

          <!-- 移动端用户区 -->
          <div class="border-t border-[#eee] mt-[8px] pt-[12px] pb-[16px]">
            <template v-if="authStore.isLoggedIn">
              <RouterLink to="/admin" class="flex items-center gap-[10px] text-[16px] text-[#1f1f1f]" @click="mobileOpen = false">
                <div
                  class="w-[34px] h-[34px] bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white text-[14px] font-medium"
                >
                  {{ userInitial }}
                </div>
                <span class="font-medium">{{ userName }}</span>
              </RouterLink>
              <button
                @click="handleLogout"
                class="mt-[12px] w-full border border-[#eee] rounded-full py-[8px] text-[14px] text-gray-500 hover:text-red-500 transition-colors bg-transparent cursor-pointer"
              >
                退出登录
              </button>
            </template>
            <template v-else>
              <button
                type="button"
                class="w-full border-0 rounded-full py-[10px] text-[16px] font-[500] text-white cursor-pointer bg-[linear-gradient(90deg,#248fff_15%,#3777ff_73%)]"
                @click="mobileOpen = false; router.push('/login')"
              >
                立即报名
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
