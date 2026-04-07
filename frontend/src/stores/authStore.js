import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('technopath_user') || 'null'),
    token: localStorage.getItem('technopath_token') || null,
    refreshToken: localStorage.getItem('technopath_refresh') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => !!state.user,
    isSuperAdmin: (state) => state.user?.user_type === 'super_admin',
  },

  actions: {
    async login(username, password) {
      const response = await api.post('/auth/login/', { username, password })
      const { access, refresh } = response.data

      this.token = access
      this.refreshToken = refresh
      localStorage.setItem('technopath_token', access)
      localStorage.setItem('technopath_refresh', refresh)

      // Fetch user profile
      const userRes = await api.get('/users/me/')
      this.user = userRes.data
      localStorage.setItem('technopath_user', JSON.stringify(userRes.data))
    },

    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('technopath_token')
      localStorage.removeItem('technopath_refresh')
      localStorage.removeItem('technopath_user')
    }
  }
})
