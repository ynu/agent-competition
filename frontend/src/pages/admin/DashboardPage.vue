<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const stats = ref<any>({
  users: 0,
  teams: 0,
  works: 0,
  votes: 0
})
const recentLogs = ref<any[]>([])
const loading = ref(true)

const statsCards = computed(() => {
  const cards = []

  // 普通用户只显示本队伍相关的统计
  if (!authStore.isAdmin && !authStore.isReviewer) {
    cards.push(
      {
        title: '队伍成员',
        value: stats.value.teams,
        icon: 'team',
        color: 'purple',
        bg: 'from-purple-500 to-purple-600'
      },
      {
        title: '作品数量',
        value: stats.value.works,
        icon: 'works',
        color: 'green',
        bg: 'from-green-500 to-green-600'
      },
      {
        title: '投票数',
        value: stats.value.votes,
        icon: 'votes',
        color: 'red',
        bg: 'from-red-500 to-red-600'
      }
    )
  } else {
    // 管理员/评审可以看到全局统计
    cards.push(
      {
        title: '队伍总数',
        value: stats.value.teams,
        icon: 'team',
        color: 'purple',
        bg: 'from-purple-500 to-purple-600'
      },
      {
        title: '作品总数',
        value: stats.value.works,
        icon: 'works',
        color: 'green',
        bg: 'from-green-500 to-green-600'
      },
      {
        title: '投票总数',
        value: stats.value.votes,
        icon: 'votes',
        color: 'red',
        bg: 'from-red-500 to-red-600'
      }
    )
    // 管理员可以看到用户总数
    if (authStore.isAdmin) {
      cards.unshift({
        title: '用户总数',
        value: stats.value.users,
        icon: 'users',
        color: 'blue',
        bg: 'from-blue-500 to-blue-600'
      })
    }
  }

  return cards
})

onMounted(async () => {
  await fetchStats()
  await fetchRecentLogs()
})

async function fetchStats() {
  try {
    // 普通用户获取本队伍的统计
    if (!authStore.isAdmin && !authStore.isReviewer) {
      try {
        const res = await api.get('/teams/my/team')
        if (res.data) {
          const team = res.data
          stats.value = {
            teams: team.members?.length || 0,
            works: 0,
            votes: 0
          }
          // 获取本队伍的作品数
          try {
            const worksRes = await api.get('/works/my/works')
            stats.value.works = worksRes.data.total || 0
          } catch (e) {}
          // 获取本队伍的投票数
          try {
            const myReviewsRes = await api.get('/reviews/my-reviews')
            stats.value.votes = myReviewsRes.data.total || 0
          } catch (e) {}
        }
      } catch (e) {
        // 用户没有队伍
        stats.value = { users: 0, teams: 0, works: 0, votes: 0 }
      }
    } else {
      // 管理员/评审获取全局统计
      const res = await api.get('/logs/dashboard-stats', { params: { days: 7 } })
      stats.value = {
        users: res.data.users || 0,
        teams: res.data.teams || 0,
        works: res.data.works || 0,
        votes: res.data.votes || 0
      }
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchRecentLogs() {
  try {
    // 管理员/评审可以查看所有日志，普通用户只能查看自己的
    const endpoint = authStore.isAdmin || authStore.isReviewer ? '/logs' : '/logs/my'
    const res = await api.get(endpoint, { params: { page_size: 10 } })
    recentLogs.value = res.data.items || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatTime(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div>
    <!-- Welcome Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-800">欢迎回来，{{ authStore.user?.nickname || authStore.user?.username }} 👋</h1>
      <p class="text-gray-500 mt-1">这里是系统概览和数据统计</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div
        v-for="(card, index) in statsCards"
        :key="index"
        class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-lg transition-shadow duration-300"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 mb-1">{{ card.title }}</p>
            <p class="text-3xl font-bold text-gray-800">{{ card.value }}</p>
          </div>
          <div :class="['w-14 h-14 rounded-2xl bg-gradient-to-br flex items-center justify-center shadow-lg', card.bg]">
            <svg v-if="card.icon === 'users'" class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <svg v-else-if="card.icon === 'team'" class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <svg v-else-if="card.icon === 'works'" class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
            <svg v-else-if="card.icon === 'votes'" class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions & Recent Logs -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Quick Actions -->
      <div class="lg:col-span-1 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-semibold text-gray-800 mb-4">快捷操作</h3>
        <div class="space-y-3">
          <RouterLink
            to="/admin/teams"
            class="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 transition"
          >
            <div class="w-10 h-10 rounded-xl bg-blue-500 flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-800">创建队伍</p>
              <p class="text-xs text-gray-500">组建参赛团队</p>
            </div>
          </RouterLink>
          <RouterLink
            v-if="authStore.isReviewer"
            to="/admin/reviews"
            class="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 transition"
          >
            <div class="w-10 h-10 rounded-xl bg-purple-500 flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-800">作品评审</p>
              <p class="text-xs text-gray-500">评审参赛作品</p>
            </div>
          </RouterLink>
          <RouterLink
            v-if="authStore.isAdmin"
            to="/admin/contents"
            class="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-green-50 to-teal-50 hover:from-green-100 hover:to-teal-100 transition"
          >
            <div class="w-10 h-10 rounded-xl bg-green-500 flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-800">内容管理</p>
              <p class="text-xs text-gray-500">发布赛事资讯</p>
            </div>
          </RouterLink>
          <RouterLink
            v-if="authStore.isAdmin"
            to="/admin/copyright-agreements"
            class="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-orange-50 to-red-50 hover:from-orange-100 hover:to-red-100 transition"
          >
            <div class="w-10 h-10 rounded-xl bg-orange-500 flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-800">版权协议</p>
              <p class="text-xs text-gray-500">管理签署记录</p>
            </div>
          </RouterLink>
        </div>
      </div>

      <!-- Recent Logs -->
      <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-semibold text-gray-800">最近操作</h3>
          <RouterLink to="/admin/logs" class="text-sm text-blue-600 hover:text-blue-700">查看全部 →</RouterLink>
        </div>
        <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
        <div v-else-if="recentLogs.length === 0" class="text-center py-8 text-gray-500">暂无操作记录</div>
        <div v-else class="space-y-3">
          <div
            v-for="log in recentLogs"
            :key="log.id"
            class="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50 transition"
          >
            <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="{
              'bg-blue-100 text-blue-600': log.action === 'login',
              'bg-green-100 text-green-600': log.action === 'create',
              'bg-yellow-100 text-yellow-600': log.action === 'update',
              'bg-red-100 text-red-600': log.action === 'delete',
              'bg-gray-100 text-gray-600': !['login', 'create', 'update', 'delete'].includes(log.action)
            }">
              <svg v-if="log.action === 'login'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
              </svg>
              <svg v-else-if="log.action === 'create'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
              </svg>
              <svg v-else-if="log.action === 'update'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              <svg v-else-if="log.action === 'delete'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-800 truncate">{{ log.details || log.action }}</p>
              <p class="text-xs text-gray-500">{{ log.user?.username || '系统' }} · {{ log.resource }}</p>
            </div>
            <div class="text-xs text-gray-400 whitespace-nowrap">{{ formatTime(log.created_at) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>