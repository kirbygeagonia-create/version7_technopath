import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // Public mobile routes
  { path: '/', component: () => import('../views/HomeView.vue') },
  { path: '/map', component: () => import('../views/MapView.vue') },
  { path: '/navigate', component: () => import('../views/NavigateView.vue') },
  { path: '/chatbot', component: () => import('../views/ChatbotView.vue') },
  { path: '/notifications', component: () => import('../views/NotificationsView.vue') },
  { path: '/settings', component: () => import('../views/SettingsView.vue') },
  
  // QR Scanner
  { path: '/qr-scanner', component: () => import('../views/QRScannerView.vue') },

  // Feedback
  { path: '/feedback', component: () => import('../views/FeedbackView.vue') },

  // Info pages (Building, Rooms, Instructors, Employees)
  { path: '/building-info', component: () => import('../views/InfoView.vue'), props: { type: 'buildings' } },
  { path: '/rooms-info', component: () => import('../views/InfoView.vue'), props: { type: 'rooms' } },
  { path: '/instructor-info', component: () => import('../views/InfoView.vue'), props: { type: 'instructors' } },
  { path: '/employees', component: () => import('../views/InfoView.vue'), props: { type: 'employees' } },
  { path: '/info/:type', component: () => import('../views/InfoView.vue'), props: true },

  // Admin routes — require login
  { path: '/admin/login', component: () => import('../views/AdminLoginView.vue') },
  {
    path: '/admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard — redirect to login if not authenticated
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('technopath_token')
    if (!token) {
      next('/admin/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
