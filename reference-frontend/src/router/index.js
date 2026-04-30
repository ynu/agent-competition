import { createRouter, createWebHashHistory } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = createRouter({
  history: createWebHashHistory(''),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: false },
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('@/views/home/index.vue'),
          meta: { title: '首页', requiresAuth: false },
        },
        {
          path: 'content',
          name: 'ContentPage',
          component: () => import('@/views/home/contentpage.vue'),
          meta: { title: '内容页', requiresAuth: false },
        },
        {
          path: 'articlecontent',
          name: 'ArticleContent',
          component: () => import('@/views/home/articlecontent.vue'),
          meta: { title: '内容页', requiresAuth: false },
        },
        {
          path: 'articlelist',
          name: 'ArticleList',
          component: () => import('@/views/home/articlelist.vue'),
          meta: { title: '新闻列表', requiresAuth: false },
        },
        {
          path: 'works',
          name: 'Works',
          component: () => import('@/views/home/works.vue'),
          meta: { title: '参赛作品', requiresAuth: false },
        },
        {
          path: 'materials',
          name: 'Materials',
          component: () => import('@/views/home/materials.vue'),
          meta: { title: '课程资料', requiresAuth: false },
        },
      ],
    },
  ],
});

const appTitle = import.meta.env.VITE_APP_TITLE;

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore();

  document.title = to.meta.title ? `${to.meta.title} - ${appTitle}` : appTitle;

  if (to.meta.requiresAuth) {
    if (userStore.isLogin) {
      next();
    } else {
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      });
    }
  } else {
    next();
  }
});

export default router;
