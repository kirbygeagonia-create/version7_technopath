import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const routes = [
  // Splash screen
  { path: '/splash', component: () => import('../views/SplashScreen.vue') },

  // Public mobile routes
  { path: '/',             component: () => import('../views/HomeView.vue') },
  { path: '/map',          component: () => import('../views/MapView.vue') },
  { path: '/navigate',     component: () => import('../views/NavigateView.vue') },
  { path: '/chatbot',      component: () => import('../views/ChatbotView.vue') },
  { path: '/notifications',component: () => import('../views/NotificationsView.vue') },
  { path: '/settings',     component: () => import('../views/SettingsView.vue') },
  { path: '/profile',      component: () => import('../views/ProfileView.vue') },
  { path: '/favorites',    component: () => import('../views/FavoritesView.vue') },
  { path: '/feedback',     component: () => import('../views/FeedbackView.vue') },


  // Info pages
  { path: '/building-info',   component: () => import('../views/InfoView.vue'), props: { type: 'buildings' } },
  { path: '/rooms-info',      component: () => import('../views/InfoView.vue'), props: { type: 'rooms' } },
  { path: '/instructor-info', component: () => import('../views/InfoView.vue'), props: { type: 'instructors' } },
  { path: '/employees',       component: () => import('../views/InfoView.vue'), props: { type: 'employees' } },
  { path: '/info/:type',      component: () => import('../views/InfoView.vue'), props: true },

  // Admin routes
  { path: '/admin/login', component: () => import('../views/AdminLoginView.vue') },
  {
    path: '/admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true },
  },

  // 404 catch-all — redirect unknown routes to home
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    beforeEnter: (to, from, next) => {
      console.warn(`[Router] No route matched: ${to.fullPath} — redirecting to home`)
      next('/')
    }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  // Show splash on first session visit to /
  const isInitialLoad = from.matched.length === 0
  const hasSeenSplash = sessionStorage.getItem('tp_splash_seen')
  if (to.path === '/' && isInitialLoad && !hasSeenSplash) {
    sessionStorage.setItem('tp_splash_seen', '1')
    next('/splash')
    return
  }

  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    if (!authStore.isLoggedIn) {
      next('/admin/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
