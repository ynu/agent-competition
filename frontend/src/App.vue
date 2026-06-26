<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Notification from '@/components/Notification.vue'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isAdminPage = computed(() => route.path.startsWith('/admin'))
const unreadMessageCount = ref(0)

const menuItems = computed(() => [
  { path: '/admin', name: '仪表盘', icon: 'dashboard', permissions: [] },
  { path: '/admin/users', name: '用户管理', icon: 'users', permissions: ['user:read', 'user:create', 'user:update', 'user:delete'] },
  { path: '/admin/teams', name: '队伍管理', icon: 'team', permissions: ['team:read', 'team:create', 'team:update', 'team:delete', 'team:audit'] },
  { path: '/admin/works', name: '作品管理', icon: 'works', permissions: ['work:read', 'work:create', 'work:update', 'work:delete', 'work:audit'] },
  { path: '/admin/reviews', name: '评审管理', icon: 'review', permissions: ['review:read', 'review:create', 'review:update'] },
  { path: '/admin/votes', name: '投票管理', icon: 'votes', permissions: ['vote:read', 'vote:manage'] },
  { path: '/admin/contents', name: '内容管理', icon: 'content', permissions: ['content:read', 'content:create', 'content:update', 'content:delete'] },
  { path: '/admin/messages', name: '消息管理', icon: 'message', permissions: [] },
  { path: '/admin/permissions', name: '权限管理', icon: 'permission', permissions: ['user:read'] },
  { path: '/admin/settings', name: '配置管理', icon: 'settings', permissions: ['setting:read', 'setting:update'] },
  { path: '/admin/webhooks', name: 'Webhook', icon: 'webhook', permissions: ['setting:read'] },
  { path: '/admin/event-channels', name: '事件通知', icon: 'notification', permissions: ['setting:read'] },
  { path: '/admin/logs', name: '日志管理', icon: 'logs', permissions: ['log:read', 'log:export'] },
])

const filteredMenuItems = computed(() => {
  if (!authStore.user) return []
  return menuItems.value.filter(item => {
    // 管理员拥有所有权限
    if (authStore.isAdmin) return true
    // 如果没有定义权限要求（空数组），则允许访问
    if (item.permissions.length === 0) return true
    // 检查是否拥有任意一个所需权限
    return item.permissions.some(perm => authStore.hasPermission(perm))
  })
})

const sidebarCollapsed = ref(false)

async function fetchUnreadMessageCount() {
  if (!authStore.isLoggedIn) return
  try {
    const res = await api.get('/messages/unread-count')
    unreadMessageCount.value = res.data.unread_count || 0
  } catch (e) {
    console.error('Failed to fetch unread message count', e)
  }
}

async function fetchUnreadMessages() {
  if (!authStore.isLoggedIn) return []
  try {
    const res = await api.get('/messages', { params: { page: 1, page_size: 10, is_read: false } })
    return res.data.items || []
  } catch (e) {
    console.error('Failed to fetch unread messages', e)
    return []
  }
}

const unreadDropdownMessages = ref<any[]>([])
const showUnreadDropdown = ref(false)

async function toggleUnreadDropdown() {
  showUnreadDropdown.value = !showUnreadDropdown.value
  if (showUnreadDropdown.value && unreadDropdownMessages.value.length === 0) {
    unreadDropdownMessages.value = await fetchUnreadMessages()
  }
}

function viewUnreadMessage(msg: any) {
  showUnreadDropdown.value = false
  router.push('/admin/messages')
  // 标记为已读
  if (!msg.is_read) {
    api.put(`/messages/${msg.id}/read`).then(() => {
      msg.is_read = true
      if (unreadMessageCount.value > 0) {
        unreadMessageCount.value--
      }
    })
  }
}

function formatDateShort(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.unread-dropdown-container')) {
    showUnreadDropdown.value = false
  }
}

onMounted(() => {
  if (authStore.isLoggedIn) {
    fetchUnreadMessageCount()
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div @click="handleClickOutside" class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Admin Layout -->
    <template v-if="isAdminPage">
      <div class="flex h-screen overflow-hidden">
        <aside :class="['relative flex flex-col transition-all duration-500', sidebarCollapsed ? 'w-20' : 'w-72']">
          <div class="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"></div>
          <div class="absolute inset-0 bg-gradient-to-tr from-blue-600/20 via-transparent to-purple-600/20 animate-pulse"></div>

          <div class="relative h-20 flex items-center px-4 border-b border-white/10 backdrop-blur-sm">
            <RouterLink to="/" class="flex items-center gap-3 group">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-500 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-purple-500/30 group-hover:scale-110 transition-transform duration-300">
                <span class="text-white font-bold text-xl">🤖</span>
              </div>
              <div v-if="!sidebarCollapsed" class="flex flex-col">
                <span class="text-white font-bold text-lg whitespace-nowrap bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
                  智能体大赛
                </span>
                <span class="text-xs text-blue-300/70 whitespace-nowrap">管理后台</span>
              </div>
            </RouterLink>
          </div>

          <nav class="relative flex-1 py-6 overflow-y-auto">
            <ul class="space-y-2 px-3">
              <li v-for="(item, index) in filteredMenuItems" :key="item.path">
                <RouterLink
                  :to="item.path"
                  :class="[
                    'group relative flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all duration-300',
                    route.path === item.path || (item.path !== '/admin' && route.path.startsWith(item.path))
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'text-slate-300 hover:bg-white/10 hover:text-white'
                  ]"
                >
                  <div :class="[
                    'relative z-10 w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0',
                    route.path === item.path || (item.path !== '/admin' && route.path.startsWith(item.path))
                      ? 'bg-white/20'
                      : 'bg-white/5 group-hover:bg-white/10'
                  ]">
                    <svg v-if="item.icon === 'dashboard'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'users'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'team'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'works'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                    </svg>
                    <svg v-else-if="item.icon === 'review'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'content'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'permission'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'settings'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'logs'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
                    </svg>
                    <svg v-else-if="item.icon === 'votes'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                    </svg>
                    <svg v-else-if="item.icon === 'webhook'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                    </svg>
                    <svg v-else-if="item.icon === 'notification'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                    </svg>
                    <svg v-else-if="item.icon === 'message'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                    </svg>
                  </div>
                  <span v-if="!sidebarCollapsed" class="whitespace-nowrap font-medium">{{ item.name }}</span>
                </RouterLink>
              </li>
            </ul>
          </nav>

          <div class="relative p-4 border-t border-white/10">
            <button
              @click="sidebarCollapsed = !sidebarCollapsed"
              class="w-full flex items-center justify-center gap-2 px-4 py-3 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300"
            >
              <svg :class="['w-5 h-5 transition-transform duration-300', sidebarCollapsed ? 'rotate-180' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
              </svg>
              <span v-if="!sidebarCollapsed" class="text-sm">收起</span>
            </button>
          </div>
        </aside>

        <div class="flex-1 flex flex-col overflow-hidden">
          <header class="bg-white shadow-sm border-b h-16 flex items-center justify-between px-6">
            <h1 class="text-lg font-semibold text-gray-800">{{ route.meta?.title || '管理后台' }}</h1>
            <div class="flex items-center gap-4">
              <!-- Messages Dropdown -->
              <div class="relative unread-dropdown-container">
                <button
                  @click="toggleUnreadDropdown"
                  class="relative p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                  </svg>
                  <span
                    v-if="unreadMessageCount > 0"
                    class="absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center px-1 bg-red-500 text-white text-xs font-medium rounded-full"
                  >
                    {{ unreadMessageCount > 99 ? '99+' : unreadMessageCount }}
                  </span>
                </button>

                <!-- Unread Messages Dropdown -->
                <Transition name="dropdown">
                  <div
                    v-if="showUnreadDropdown"
                    class="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden z-50"
                  >
                    <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-700">未读消息</span>
                      <RouterLink
                        to="/admin/messages"
                        @click="showUnreadDropdown = false"
                        class="text-xs text-blue-600 hover:text-blue-700"
                      >
                        查看全部
                      </RouterLink>
                    </div>
                    <div class="max-h-96 overflow-y-auto">
                      <div v-if="unreadDropdownMessages.length === 0" class="px-4 py-8 text-center text-gray-400 text-sm">
                        暂无未读消息
                      </div>
                      <div
                        v-else
                        v-for="msg in unreadDropdownMessages"
                        :key="msg.id"
                        @click="viewUnreadMessage(msg)"
                        class="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-50 last:border-b-0"
                      >
                        <div class="flex items-start gap-3">
                          <div class="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                          <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-gray-900 truncate">{{ msg.title }}</p>
                            <p class="text-xs text-gray-500 truncate mt-0.5">{{ msg.sender_nickname || msg.sender_username }}</p>
                            <p class="text-xs text-gray-400 mt-0.5">{{ formatDateShort(msg.created_at) }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
              <!-- Theme toggle -->
              <button
                @click="themeStore.toggleDark()"
                class="relative w-14 h-8 rounded-full transition-all duration-300"
                :class="themeStore.isDark ? 'bg-indigo-600' : 'bg-gray-300'"
              >
                <span
                  class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full shadow-md flex items-center justify-center transition-all duration-300"
                  :class="themeStore.isDark ? 'translate-x-6' : 'translate-x-0'"
                >
                  <svg v-if="themeStore.isDark" class="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
                  </svg>
                  <svg v-else class="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
                  </svg>
                </span>
              </button>
              <RouterLink to="/" class="text-sm text-gray-500 hover:text-blue-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
                前台
              </RouterLink>
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {{ (authStore.user?.nickname || authStore.user?.username || 'U')[0].toUpperCase() }}
                </div>
                <span class="text-sm text-gray-700">{{ authStore.user?.nickname || authStore.user?.username }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="{
                  'bg-blue-100 text-blue-700': authStore.isAdmin,
                  'bg-purple-100 text-purple-700': authStore.isReviewer,
                  'bg-gray-100 text-gray-700': !authStore.isAdmin && !authStore.isReviewer
                }">
                  {{ authStore.isAdmin ? '管理员' : authStore.isReviewer ? '评审' : '用户' }}
                </span>
              </div>
              <button @click="() => { authStore.logout(); router.push('/') }" class="text-sm text-red-500 hover:text-red-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
                退出
              </button>
            </div>
          </header>

          <main class="flex-1 overflow-y-auto p-6 bg-gray-50">
            <RouterView />
          </main>
        </div>
      </div>
    </template>

    <!-- Non-admin pages (will be wrapped by MainLayout in router) -->
    <template v-else>
      <RouterView />
    </template>
  </div>

  <Notification />
</template>

<style scoped>
/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>