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
      { label: '大赛方案', path: '/competition-plan' },
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
  <header class="sticky top-0 z-50">
    <!-- 毛玻璃悬浮导航 -->
    <div class="glass shadow-[0_1px_0_rgba(0,0,0,0.05),0_8px_32px_rgba(29,42,68,0.08)]">
      <div class="mx-auto max-w-[1200px] lg:h-[76px] flex items-center justify-between px-[16px] h-[60px]">
        <RouterLink to="/" class="flex items-center shrink-0" @click="mobileOpen = false">
          <img :src="logoTop" alt="云南大学" class="h-[48px] w-auto lg:block hidden drop-shadow-sm" />
          <img :src="logoTop" alt="云南大学" class="h-[36px] w-auto lg:hidden" />
        </RouterLink>

        <!-- 桌面端导航 -->
        <nav class="hidden lg:flex h-full items-center gap-[6px]">
          <div
            v-for="item in navItems"
            :key="item.label"
            class="relative h-full"
            @mouseenter="hasChildren(item) && openDropdown(item.label)"
            @mouseleave="hasChildren(item) && openDropdown(null)"
          >
            <button
              type="button"
              class="nav-btn group h-full border-0 bg-transparent px-[14px] flex flex-col items-center justify-center text-[18px] text-[#1d1d1f] font-[400] tracking-[0.2px] cursor-pointer transition-colors duration-300 hover:text-[#0071e3]"
              :class="{ 'text-[#0071e3]': isActive(item) }"
              @click="item.children ? openDropdown(activeDropdown === item.label ? null : item.label) : goTo(item)"
            >
              <span class="nav-btn-label flex items-center gap-[4px]">
                {{ item.label }}
                <svg
                  v-if="hasChildren(item)"
                  class="w-[14px] h-[14px] transition-transform duration-300"
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
                class="nav-btn-dot w-[20px] h-[3px] rounded-full transition-all duration-300"
                :class="isActive(item) ? 'bg-gradient-to-r from-[#0090ff] to-[#6a5cff] scale-x-100' : 'bg-gradient-to-r from-[#0090ff] to-[#6a5cff] scale-x-0'"
              ></p>
            </button>

            <!-- 下拉子菜单：毛玻璃圆角面板 -->
            <Transition name="dropdown">
              <div
                v-if="hasChildren(item) && activeDropdown === item.label"
                class="dropdown-panel absolute left-1/2 -translate-x-1/2 top-full min-w-[180px] whitespace-nowrap glass rounded-[20px] shadow-[0_20px_60px_rgba(29,42,68,0.18)] p-[8px]"
              >
                <button
                  v-for="child in item.children"
                  :key="child.label"
                  type="button"
                  class="w-full border-0 bg-transparent px-[16px] py-[10px] flex items-center justify-between text-[15px] text-[#1d1d1f] transition-all duration-200 cursor-pointer rounded-[14px] hover:text-[#0071e3] hover:bg-[#0071e3]/8"
                  :class="{ 'text-[#0071e3] bg-[#0071e3]/8': child.path && isActivePath(child.path) }"
                  @click="goTo(child); openDropdown(null)"
                >
                  {{ child.label }}
                  <svg
                    v-if="child.externalUrl && child.externalUrl.startsWith('http')"
                    class="w-[13px] h-[13px] text-[#a1a1a6]"
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
            <div class="flex items-center gap-[16px]">
              <RouterLink
                to="/admin"
                class="flex items-center gap-[8px] text-[15px] text-[#1d1d1f] hover:text-[#0071e3] transition-colors duration-300"
              >
                <div
                  class="w-[36px] h-[36px] bg-gradient-to-br from-[#0090ff] via-[#6a5cff] to-[#ff5ca8] rounded-full flex items-center justify-center text-white text-[14px] font-semibold shadow-[0_4px_14px_rgba(106,92,255,0.35)] transition-transform duration-300 hover:scale-110"
                >
                  {{ userInitial }}
                </div>
                <span class="font-medium">{{ userName }}</span>
              </RouterLink>
              <button @click="handleLogout" class="text-[14px] text-[#86868b] hover:text-[#ff3b30] transition-colors duration-300">
                退出
              </button>
            </div>
          </template>
          <template v-else>
            <el-button
              type="primary"
              round
              size="large"
              class="!h-[38px] !px-0 !w-[104px] !text-[15px] !font-[600] anim-gradient !bg-gradient-to-r !from-[#0090ff] !via-[#6a5cff] !to-[#ff5ca8] !border-0"
              @click="router.push('/login')"
            >
              立即报名
            </el-button>
          </template>
        </div>

        <!-- 移动端汉堡按钮 -->
        <button
          type="button"
          class="lg:hidden border-0 bg-transparent p-[8px] cursor-pointer text-[#1d1d1f] transition-transform duration-300 active:scale-90"
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
    </div>

    <!-- 移动端抽屉菜单 -->
    <Transition name="drawer">
      <div v-if="mobileOpen" class="lg:hidden glass border-t border-white/40 max-h-[calc(100vh-60px)] overflow-y-auto">
        <div class="px-[16px] py-[8px]">
          <template v-for="item in navItems" :key="item.label">
            <!-- 有子菜单的项：手风琴 -->
            <div v-if="hasChildren(item)">
              <button
                type="button"
                class="w-full border-0 bg-transparent py-[14px] flex items-center justify-between text-[16px] text-[#1d1d1f] font-[500] cursor-pointer"
                :class="{ 'text-[#0071e3]': isActive(item) }"
                @click="toggleMobileExpand(item.label)"
              >
                {{ item.label }}
                <svg
                  class="w-[16px] h-[16px] transition-transform duration-300"
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
                  class="w-full border-0 bg-transparent py-[12px] pl-[16px] flex items-center justify-between text-[15px] text-[#515154] transition-colors cursor-pointer hover:text-[#0071e3]"
                  :class="{ 'text-[#0071e3]': child.path && isActivePath(child.path) }"
                  @click="handleMobileChildClick(child)"
                >
                  {{ child.label }}
                  <svg
                    v-if="child.externalUrl && child.externalUrl.startsWith('http')"
                    class="w-[13px] h-[13px] text-[#a1a1a6]"
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
              class="w-full border-0 bg-transparent py-[14px] flex items-center justify-between text-[16px] text-[#1d1d1f] font-[500] transition-colors cursor-pointer hover:text-[#0071e3]"
              :class="{ 'text-[#0071e3]': isActive(item) }"
              @click="handleMobileClick(item)"
            >
              {{ item.label }}
              <svg
                v-if="item.externalUrl && item.externalUrl.startsWith('http')"
                class="w-[14px] h-[14px] text-[#a1a1a6]"
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
          <div class="border-t border-black/5 mt-[8px] pt-[12px] pb-[16px]">
            <template v-if="authStore.isLoggedIn">
              <RouterLink to="/admin" class="flex items-center gap-[10px] text-[16px] text-[#1d1d1f]" @click="mobileOpen = false">
                <div
                  class="w-[34px] h-[34px] bg-gradient-to-br from-[#0090ff] via-[#6a5cff] to-[#ff5ca8] rounded-full flex items-center justify-center text-white text-[14px] font-semibold"
                >
                  {{ userInitial }}
                </div>
                <span class="font-medium">{{ userName }}</span>
              </RouterLink>
              <button
                @click="handleLogout"
                class="mt-[12px] w-full border border-black/8 rounded-full py-[8px] text-[14px] text-[#86868b] hover:text-[#ff3b30] hover:border-[#ff3b30]/30 transition-colors duration-300 bg-transparent cursor-pointer"
              >
                退出登录
              </button>
            </template>
            <template v-else>
              <button
                type="button"
                class="w-full border-0 rounded-full py-[11px] text-[16px] font-[600] text-white cursor-pointer anim-gradient bg-gradient-to-r from-[#0090ff] via-[#6a5cff] to-[#ff5ca8] shadow-[0_8px_24px_rgba(106,92,255,0.35)] active:scale-[0.98] transition-transform"
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
/* 子菜单面板：完全不透明，避免文字与页面内容重叠 */
.dropdown-panel {
  background: #ffffff;
}

/* 导航项 hover 特效：文字轻微上浮 + 渐变光点浮现 */
.nav-btn {
  overflow: visible;
}

.nav-btn-label {
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.nav-btn:hover .nav-btn-label {
  transform: translateY(-2px);
}

/* 底部渐变指示条：hover 时从中间展开 */
.nav-btn-dot {
  transform: scaleX(0);
  transform-origin: center;
  opacity: 0;
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.35s ease;
}

.nav-btn:hover .nav-btn-dot {
  transform: scaleX(0.6);
  opacity: 0.55;
}

.nav-btn-dot.scale-x-100 {
  transform: scaleX(1);
  opacity: 1;
}

.nav-btn:hover .nav-btn-dot.scale-x-100 {
  transform: scaleX(1);
  opacity: 1;
}

/* 柔光扫过效果 */
.nav-btn-label::after {
  content: '';
  position: absolute;
  inset: -8px -12px;
  border-radius: 12px;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 113, 227, 0.1) 0%,
    transparent 70%
  );
  opacity: 0;
  transform: scale(0.7);
  transition: opacity 0.3s ease, transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
  pointer-events: none;
  z-index: -1;
}

.nav-btn:hover .nav-btn-label::after {
  opacity: 1;
  transform: scale(1);
}

.nav-btn-label {
  position: relative;
}

/* 子菜单抽屉式展开动画：从导航栏下滑出 */
.dropdown-enter-active {
  transition: opacity 0.32s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}
.dropdown-leave-active {
  transition: opacity 0.22s cubic-bezier(0.4, 0, 1, 1),
    transform 0.22s cubic-bezier(0.4, 0, 1, 1);
}
.dropdown-enter-from {
  opacity: 0;
  transform: translate(-50%, -14px);
}
.dropdown-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}

/* 抽屉内部条目错峰滑入 */
.dropdown-enter-active :deep(button) {
  animation: drawer-item-in 0.36s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.dropdown-enter-active :deep(button:nth-child(1)) { animation-delay: 0.04s; }
.dropdown-enter-active :deep(button:nth-child(2)) { animation-delay: 0.09s; }
.dropdown-enter-active :deep(button:nth-child(3)) { animation-delay: 0.14s; }
.dropdown-enter-active :deep(button:nth-child(4)) { animation-delay: 0.19s; }

@keyframes drawer-item-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
