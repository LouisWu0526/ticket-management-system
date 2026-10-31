import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../layout/Layout.vue'),
    redirect: '/tickets',
    children: [
      {
        path: 'tickets',
        name: 'TicketList',
        component: () => import('../views/TicketList.vue'),
      },
      {
        path: 'tickets/create',
        name: 'TicketCreate',
        component: () => import('../views/TicketCreate.vue'),
      },
      {
        path: 'tickets/:id',
        name: 'TicketDetail',
        component: () => import('../views/TicketDetail.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局前置守卫：未登录跳登录页；登录后刷新页面时拉取最新用户信息（含角色）
router.beforeEach(async (to) => {
  const userStore = useUserStore()

  if (!userStore.token) {
    return to.meta.public ? true : '/login'
  }

  if (!userStore.user) {
    try {
      await userStore.fetchMe()
    } catch {
      userStore.clearAuth()
      return '/login'
    }
  }

  if (to.path === '/login') return '/'
  return true
})

export default router
