<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Notification from '@/components/Notification.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isAdminPage = computed(() => route.path.startsWith('/admin'))

const menuItems = computed(() => [
  { path: '/admin', name: '仪表盘', icon: 'dashboard', roles: ['user', 'reviewer', 'admin'] },
  { path: '/admin/users', name: '用户管理', icon: 'users', roles: ['admin'] },
  { path: '/admin/teams', name: '队伍管理', icon: 'team', roles: ['user', 'reviewer', 'admin'] },
  { path: '/admin/works', name: '作品管理', icon: 'works', roles: ['user', 'reviewer', 'admin'] },
  { path: '/admin/reviews', name: '评审管理', icon: 'review', roles: ['reviewer', 'admin'] },
  { path: '/admin/votes', name: '投票管理', icon: 'votes', roles: ['reviewer', 'admin'] },
  { path: '/admin/contents', name: '内容管理', icon: 'content', roles: ['reviewer', 'admin'] },
  { path: '/admin/permissions', name: '权限管理', icon: 'permission', roles: ['admin'] },
  { path: '/admin/settings', name: '配置管理', icon: 'settings', roles: ['admin'] },
  { path: '/admin/logs', name: '日志管理', icon: 'logs', roles: ['reviewer', 'admin'] },
])

const filteredMenuItems = computed(() => {
  if (!authStore.user) return []
  return menuItems.value.filter(item => item.roles.includes(authStore.user!.role))
})

const sidebarCollapsed = ref(false)
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
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