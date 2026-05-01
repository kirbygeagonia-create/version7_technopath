import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

let isRefreshing = false
let refreshSubscribers = []

// Attach JWT token to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tp_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token expiry — auto-refresh then retry
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    
    // If error is not 401 or already retried, reject immediately
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }
    
    original._retry = true
    
    // If already refreshing, wait for it
    if (isRefreshing) {
      return new Promise((resolve) => {
        refreshSubscribers.push((token) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(api(original))
        })
      })
    }
    
    isRefreshing = true
    
    try {
      const refresh = localStorage.getItem('tp_refresh')
      if (!refresh) {
        throw new Error('No refresh token')
      }
      
      const res = await axios.post('/api/auth/refresh/', { refresh })
      const newToken = res.data.access
      localStorage.setItem('tp_token', newToken)
      
      // Notify subscribers
      refreshSubscribers.forEach((callback) => callback(newToken))
      refreshSubscribers = []
      
      original.headers.Authorization = `Bearer ${newToken}`
      return api(original)
    } catch (refreshError) {
      // Clear tokens but don't redirect on public pages
      localStorage.removeItem('tp_token')
      localStorage.removeItem('tp_refresh')
      
      // Only redirect to login if on admin page
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/admin/login'
      }
      
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default api
