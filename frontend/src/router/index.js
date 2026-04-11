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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  // Show splash on first session visit to /
  if (to.path === '/' && !sessionStorage.getItem('tp_splash_shown') && from.path !== '/splash') {
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
