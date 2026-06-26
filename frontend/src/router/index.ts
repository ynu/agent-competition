import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/layouts/MainLayout.vue'

// 扩展路由元数据类型
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresAdmin?: boolean
    requiresReviewer?: boolean
    requiresPermission?: string[]
    guest?: boolean
    title?: string
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/pages/HomePage.vue')
        },
        {
          path: 'agent-center',
          name: 'agent-center',
          component: () => import('@/pages/AgentCenterPage.vue')
        },
        {
          path: 'news',
          name: 'news-list',
          component: () => import('@/pages/NewsListPage.vue')
        },
        {
          path: 'news/:id',
          name: 'news-detail',
          component: () => import('@/pages/NewsDetailPage.vue')
        },
        {
          path: 'materials',
          name: 'materials',
          component: () => import('@/pages/MaterialsListPage.vue')
        },
        {
          path: 'materials/:id',
          name: 'materials-detail',
          component: () => import('@/pages/MaterialsDetailPage.vue')
        },
        {
          path: 'works',
          name: 'works',
          component: () => import('@/pages/WorksPage.vue')
        },
        {
          path: 'works/:id',
          name: 'work-detail',
          component: () => import('@/pages/WorkDetailPage.vue')
        },
        {
          path: 'page/:slug',
          name: 'page',
          component: () => import('@/pages/PagePage.vue')
        },
        {
          path: 'contact',
          name: 'contact',
          component: () => import('@/pages/ContactPage.vue')
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
      meta: { guest: true }
    },
    {
      path: '/unauthorized',
      name: 'unauthorized',
      component: () => import('@/pages/UnauthorizedPage.vue')
    },
    {
      path: '/admin',
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('@/pages/admin/DashboardPage.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/pages/admin/UsersPage.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'teams',
          name: 'admin-teams',
          component: () => import('@/pages/admin/TeamsPage.vue'),
          meta: { requiresPermission: ['team:read', 'team:create', 'team:update', 'team:delete', 'team:audit'] }
        },
        {
          path: 'teams/:id',
          name: 'admin-team-detail',
          component: () => import('@/pages/admin/TeamDetailPage.vue'),
          meta: { requiresPermission: ['team:read'] }
        },
        {
          path: 'works',
          name: 'admin-works',
          component: () => import('@/pages/admin/WorksPage.vue'),
          meta: { requiresPermission: ['work:read', 'work:create', 'work:update', 'work:delete', 'work:audit'] }
        },
        {
          path: 'reviews',
          name: 'admin-reviews',
          component: () => import('@/pages/admin/ReviewsPage.vue'),
          meta: { requiresPermission: ['review:read', 'review:create', 'review:update'] }
        },
        {
          path: 'votes',
          name: 'admin-votes',
          component: () => import('@/pages/admin/VotesPage.vue'),
          meta: { requiresPermission: ['vote:read', 'vote:manage'] }
        },
        {
          path: 'contents',
          name: 'admin-contents',
          component: () => import('@/pages/admin/ContentsPage.vue'),
          meta: { requiresPermission: ['content:read', 'content:create', 'content:update', 'content:delete'] }
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('@/pages/admin/SettingsPage.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'permissions',
          name: 'admin-permissions',
          component: () => import('@/pages/admin/PermissionsPage.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'logs',
          name: 'admin-logs',
          component: () => import('@/pages/admin/LogsPage.vue'),
          meta: { requiresPermission: ['log:read'] }
        },
        {
          path: 'webhooks',
          name: 'admin-webhooks',
          component: () => import('@/pages/admin/WebhookPage.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'event-channels',
          name: 'admin-event-channels',
          component: () => import('@/pages/admin/EventChannelsPage.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'messages',
          name: 'admin-messages',
          component: () => import('@/pages/admin/MessagesPage.vue'),
          meta: { requiresPermission: [] }  // 所有登录用户都可以访问消息
        },
        {
          path: 'copyright-agreements',
          name: 'admin-copyright-agreements',
          component: () => import('@/pages/admin/CopyrightAgreementsPage.vue'),
          meta: { requiresAdmin: true }
        }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Try to fetch user if token exists but user is not loaded
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn) {
      next({ name: 'unauthorized' })
      return
    }
    next()
    return
  }

  // Check if route requires admin role
  if (to.meta.requiresAdmin) {
    if (!authStore.isAdmin) {
      next({ name: 'unauthorized' })
      return
    }
  }

  // Check if route requires specific permissions
  if (to.meta.requiresPermission) {
    const requiredPerms = to.meta.requiresPermission as string[]
    // 空权限数组表示所有登录用户都可访问
    if (requiredPerms.length > 0 && !authStore.isAdmin) {
      const hasAnyPermission = requiredPerms.some(p => authStore.hasPermission(p))
      if (!hasAnyPermission) {
        next({ name: 'unauthorized' })
        return
      }
    }
  }

  // Check if route requires reviewer role (legacy, now use requiresPermission)
  if (to.meta.requiresReviewer && !authStore.isReviewer && !authStore.isAdmin) {
    next({ name: 'unauthorized' })
    return
  }

  // Redirect to dashboard if already logged in and trying to access login
  if (to.meta.guest && authStore.isLoggedIn) {
    next({ name: 'admin-dashboard' })
    return
  }

  next()
})

export default router