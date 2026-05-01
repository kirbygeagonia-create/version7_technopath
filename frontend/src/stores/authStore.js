import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user:         JSON.parse(sessionStorage.getItem('tp_user')  || 'null'),
    token:        sessionStorage.getItem('tp_token')            || null,
    refreshToken: sessionStorage.getItem('tp_refresh')          || null,
  }),

  getters: {
    isLoggedIn:                 (s) => !!s.token,
    isAdmin:                    (s) => !!s.token && ['super_admin', 'dean', 'program_head', 'basic_ed_head'].includes(s.user?.role),
    isSuperAdmin:               (s) => s.user?.role === 'super_admin',
    isDean:                     (s) => s.user?.role === 'dean',
    isProgramHead:              (s) => s.user?.role === 'program_head',
    isBasicEdHead:              (s) => s.user?.role === 'basic_ed_head',
    displayName:                (s) => s.user?.display_name || s.user?.username || '',
    roleLabel:                  (s) => s.user?.role_label || '',
    departmentLabel:            (s) => s.user?.department_label || '',
    departmentColor:            (s) => s.user?.department_color || 'orange',
    department:                 (s) => s.user?.department || '',

    // Permission getters — sourced directly from login response flags
    canManageFacilities:        (s) => s.user?.can_manage_facilities        || false,
    canManageAllRooms:          (s) => s.user?.can_manage_all_rooms         || false,
    canManageOwnRooms:          (s) => s.user?.can_manage_own_rooms         || false,
    canManageNavigation:        (s) => s.user?.can_manage_navigation        || false,
    canManageFAQ:               (s) => s.user?.can_manage_faq               || false,
    canManageAdminAccounts:     (s) => s.user?.can_manage_admin_accounts    || false,
    canViewAuditLog:            (s) => s.user?.can_view_audit_log           || false,
    canViewDeptAuditLog:        (s) => s.user?.can_view_dept_audit_log       || false,
    canViewAllFeedback:         (s) => s.user?.can_view_all_feedback        || false,
    canViewDeptFeedback:        (s) => s.user?.can_view_dept_feedback       || false,
    canApproveAnnouncements:    (s) => s.user?.can_approve_announcements    || false,
    canPublishDirectly:         (s) => s.user?.can_publish_directly         || false,
    canPostAnnouncement:        (s) => s.user?.can_post_announcement        || false,
    canPostDeptAnnouncement:    (s) => s.user?.can_post_dept_announcement    || false,
    canPostCampusAnnouncement:  (s) => s.user?.can_post_campus_announcement  || false,
    canSendCampusNotification:  (s) => s.user?.can_send_campus_notification || false,
  },

  actions: {
    async login(username, password) {
      try {
        const res = await api.post('/users/login/', { username, password })
        const { access, refresh, user } = res.data
        this.token        = access
        this.refreshToken = refresh
        this.user         = user
        // SECURITY: sessionStorage clears on tab close (reduces XSS exposure window)
        sessionStorage.setItem('tp_token',   access)
        sessionStorage.setItem('tp_refresh', refresh)
        sessionStorage.setItem('tp_user',    JSON.stringify(user))
        return { success: true, user }
      } catch (error) {
        const message = error.response?.data?.detail 
          || error.response?.data?.message 
          || error.response?.data?.error
          || 'Invalid username or password'
        return { success: false, error: message }
      }
    },

    logout(router = null, redirectPath = '/') {
      api.post('/users/logout/').catch(() => {})
      this.token = this.refreshToken = this.user = null
      sessionStorage.removeItem('tp_token')
      sessionStorage.removeItem('tp_refresh')
      sessionStorage.removeItem('tp_user')
      
      // Redirect if router provided
      if (router) {
        router.push(redirectPath)
      }
    },
    
    clearTokens() {
      this.token = this.refreshToken = this.user = null
      sessionStorage.removeItem('tp_token')
      sessionStorage.removeItem('tp_refresh')
      sessionStorage.removeItem('tp_user')
    }
  },
})
