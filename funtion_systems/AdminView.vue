<template>
  <!-- ── Desktop & Mobile admin shell ── -->
  <div class="tp-admin-shell" :style="secondaryColorStyles" :class="{'mobile-layout': isMobile}">

    <!-- Sidebar -->
    <aside class="tp-sidebar">

      <div class="tp-sidebar-brand">
        <span class="tp-brand-icon">T</span>
        <div>
          <div class="tp-brand-name">TechnoPath</div>
          <div class="tp-brand-sub">Admin Panel</div>
        </div>
      </div>

      <nav class="tp-sidebar-nav">

        <!-- Dashboard — all roles -->
        <button :class="navCls('dashboard')" @click="go('dashboard')">
          <span class="material-icons tp-nav-icon">dashboard</span>
          <span>Dashboard</span>
        </button>

        <!-- ── Map management group ─────────────── -->
        <div v-if="!isMobile && (auth.canManageFacilities || auth.canManageAllRooms || auth.canManageNavigation || auth.canManageFAQ)"
             class="tp-nav-group-label">MAP MANAGEMENT</div>

        <button v-if="!isMobile && auth.canManageFacilities"
                :class="navCls('facilities')" @click="go('facilities')">
          <span class="material-icons tp-nav-icon">business</span>
          <span>Facilities</span>
        </button>

        <button v-if="!isMobile && (auth.canManageAllRooms || auth.canManageOwnRooms)"
                :class="navCls('rooms')" @click="go('rooms')">
          <span class="material-icons tp-nav-icon">meeting_room</span>
          <span>Rooms</span>
          <span v-if="!auth.canManageAllRooms" class="tp-nav-scope">own dept</span>
        </button>

        <button v-if="!isMobile && auth.canManageNavigation"
                :class="navCls('paths')" @click="go('paths')">
          <span class="material-icons tp-nav-icon">route</span>
          <span>SVG Paths</span>
        </button>

        <button v-if="!isMobile && auth.canManageFAQ"
                :class="navCls('faq')" @click="go('faq')">
          <span class="material-icons tp-nav-icon">smart_toy</span>
          <span>FAQ / Chatbot</span>
        </button>

        <!-- ── Communications group ──────────────── -->
        <div class="tp-nav-group-label">COMMUNICATIONS</div>

        <button v-if="auth.canPostAnnouncement"
                :class="navCls('announcements')" @click="go('announcements')">
          <span class="material-icons tp-nav-icon">campaign</span>
          <span>Announcements</span>
          <span v-if="myPendingCount > 0" class="tp-nav-badge">{{ myPendingCount }}</span>
        </button>

        <button v-if="auth.canApproveAnnouncements"
                :class="navCls('pending')" @click="go('pending')">
          <span class="material-icons tp-nav-icon">pending_actions</span>
          <span>Pending Approvals</span>
          <span v-if="pendingCount > 0" class="tp-nav-badge tp-badge-urgent">{{ pendingCount }}</span>
        </button>

        <button v-if="auth.canSendCampusNotification"
                :class="navCls('notifications')" @click="go('notifications')">
          <span class="material-icons tp-nav-icon">notifications_active</span>
          <span>Send Notification</span>
        </button>

        <!-- ── Administration group ──────────────── -->
        <div v-if="!isMobile && (auth.canManageAdminAccounts || auth.canViewAllFeedback || auth.canViewAuditLog || auth.canViewDeptFeedback || auth.canViewDeptAuditLog)"
             class="tp-nav-group-label">ADMINISTRATION</div>

        <button v-if="!isMobile && auth.canManageAdminAccounts"
                :class="navCls('admins')" @click="go('admins')">
          <span class="material-icons tp-nav-icon">admin_panel_settings</span>
          <span>Admin Accounts</span>
        </button>

        <button v-if="!isMobile && (auth.canViewAllFeedback || auth.canViewDeptFeedback)"
                :class="navCls('feedback')" @click="go('feedback')">
          <span class="material-icons tp-nav-icon">star</span>
          <span>Feedback & Ratings</span>
        </button>

        <button v-if="!isMobile && (auth.canViewAuditLog || auth.canViewDeptAuditLog)"
                :class="navCls('auditlog')" @click="go('auditlog')">
          <span class="material-icons tp-nav-icon">assignment</span>
          <span>Audit Log</span>
        </button>

        <!-- ── System group ──────────────── -->
        <div v-if="!isMobile" class="tp-nav-group-label">SYSTEM</div>

        <button v-if="!isMobile" class="tp-sidebar-nav-item" @click="goToFrontend">
          <span class="material-icons tp-nav-icon">open_in_new</span>
          <span>View Site</span>
        </button>

      </nav>

      <!-- Sidebar footer: current user info + logout -->
      <div class="tp-sidebar-footer">
        <div class="tp-footer-avatar">
          <span class="material-icons">account_circle</span>
        </div>
        <div class="tp-footer-info">
          <div class="tp-footer-name">{{ auth.displayName }}</div>
          <div class="tp-footer-role">{{ auth.roleLabel }}</div>
          <div class="tp-footer-dept">{{ auth.departmentLabel }}</div>
        </div>
        <button class="tp-logout-btn" @click="showLogoutConfirm = true">
          <span class="material-icons">logout</span>
          <span>Sign out</span>
        </button>
      </div>

    </aside>

    <!-- Main content area -->
    <main class="tp-admin-main">

      <AdminDashboard        v-if="section === 'dashboard'" />
      
      <div v-else-if="isMobile && blockedOnMobile(section)" class="tp-access-denied">
        <span class="material-icons">computer</span>
        <h2>Desktop Required</h2>
        <p>This feature requires a desktop screen to manage effectively.</p>
      </div>

      <AdminFacilities       v-else-if="section === 'facilities'  && auth.canManageFacilities" />
      <AdminRooms            v-else-if="section === 'rooms'       && (auth.canManageAllRooms || auth.canManageOwnRooms)"
                             :own-only="!auth.canManageAllRooms"
                             :dept="auth.department" />
      <AdminPathManager      v-else-if="section === 'paths'       && auth.canManageNavigation" />
      <AdminFAQ              v-else-if="section === 'faq'         && auth.canManageFAQ" />
      <AdminAnnouncements    v-else-if="section === 'announcements' && auth.canPostAnnouncement"
                             @my-pending="myPendingCount = $event" />
      <AdminPendingApprovals v-else-if="section === 'pending'     && auth.canApproveAnnouncements"
                             @count="pendingCount = $event" />
      <AdminSendNotification v-else-if="section === 'notifications' && auth.canSendCampusNotification" />
      <AdminAccounts         v-else-if="section === 'admins'      && auth.canManageAdminAccounts" />
      <AdminFeedback         v-else-if="section === 'feedback'    && (auth.canViewAllFeedback || auth.canViewDeptFeedback)" />
      <AdminAuditLog         v-else-if="section === 'auditlog'    && auth.canViewAuditLog" />

      <div v-else class="tp-access-denied">
        <span class="material-icons">lock</span>
        <p>You do not have permission to access this section.</p>
      </div>

    </main>

    <!-- Sign-out Confirmation Modal -->
    <div v-if="showLogoutConfirm" class="tp-modal-overlay" @click.self="showLogoutConfirm = false">
      <div class="tp-modal-dialog">
        <div class="tp-modal-header">
          <span class="material-icons tp-modal-icon">logout</span>
          <h3>Sign Out</h3>
        </div>
        <p class="tp-modal-text">Are you sure you want to log out?</p>
        <div class="tp-modal-actions">
          <button class="tp-btn-secondary" @click="showLogoutConfirm = false">Cancel</button>
          <button class="tp-btn-danger" @click="confirmLogout">Sign Out</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import api from '../services/api.js'

import AdminDashboard        from '../components/admin/AdminDashboard.vue'
import AdminFacilities       from '../components/admin/AdminFacilities.vue'
import AdminRooms            from '../components/admin/AdminRooms.vue'
import AdminPathManager      from '../components/admin/AdminPathManager.vue'
import AdminFAQ              from '../components/admin/AdminFAQ.vue'
import AdminAnnouncements    from '../components/admin/AdminAnnouncements.vue'
import AdminPendingApprovals from '../components/admin/AdminPendingApprovals.vue'
import AdminSendNotification from '../components/admin/AdminSendNotification.vue'
import AdminAccounts         from '../components/admin/AdminAccounts.vue'
import AdminFeedback         from '../components/admin/AdminFeedback.vue'
import AdminAuditLog         from '../components/admin/AdminAuditLog.vue'

const router        = useRouter()
const auth          = useAuthStore()
const section       = ref('dashboard')
const pendingCount  = ref(0)
const myPendingCount= ref(0)
const showLogoutConfirm = ref(false)

const isMobile = ref(window.innerWidth < 1024)

onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 1024
    if (isMobile.value && blockedOnMobile(section.value)) {
      section.value = 'dashboard'
    }
  })
})

function blockedOnMobile(sec) {
  return !['dashboard', 'announcements', 'notifications'].includes(sec)
}

// Department-based secondary color theming
const departmentColors = {
  orange: '#FF9800',
  blue: '#1976D2',
  green: '#388E3C',
  purple: '#7B1FA2',
  red: '#D32F2F',
  teal: '#00796B',
  indigo: '#303F9F',
  pink: '#C2185B',
  amber: '#F57C00',
  cyan: '#0097A7'
}

const secondaryColorStyles = computed(() => {
  const deptColor = auth.departmentColor || 'orange'
  const color = departmentColors[deptColor] || departmentColors.orange
  return {
    '--color-secondary': color,
    '--color-secondary-light': color + '20',
    '--color-secondary-dark': color
  }
})

function navCls(name) {
  return ['tp-sidebar-nav-item', section.value === name ? 'active' : '']
}

function go(name) { section.value = name }

function goToFrontend() {
  router.push('/')
}

async function loadPendingCount() {
  if (!auth.canApproveAnnouncements) return
  try {
    const r = await api.get('/announcements/pending/')
    pendingCount.value = r.data.length
  } catch { pendingCount.value = 0 }
}

function confirmLogout() {
  showLogoutConfirm.value = false
  auth.logout(router, '/admin/login')
}

onMounted(() => {
  if (!auth.isLoggedIn) { router.push('/admin/login'); return }
  loadPendingCount()
  
  // Handle query parameters for direct section navigation
  const routeSection = router.currentRoute.value.query.section
  if (routeSection && ['dashboard', 'facilities', 'rooms', 'navigation', 'paths', 'faq', 'announcements', 'pending', 'notifications', 'admins', 'feedback', 'auditlog'].includes(routeSection)) {
    section.value = routeSection
  }
  
  // Listen for navigation events from Quick Actions in AdminDashboard
  window.addEventListener('admin-navigate', handleAdminNavigate)
})

onUnmounted(() => {
  window.removeEventListener('admin-navigate', handleAdminNavigate)
})

function handleAdminNavigate(e) {
  if (e.detail) {
    section.value = e.detail
  }
}
</script>

<style scoped>
/* Mobile block */
.tp-mobile-block {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  padding: var(--space-6);
}
.tp-mobile-card {
  background: var(--color-bg);
  border-radius: var(--radius-xl);
  padding: 40px 32px;
  max-width: 420px;
  text-align: center;
  box-shadow: var(--shadow-md);
}
.tp-mobile-icon { 
  font-size: 56px; 
  display: block; 
  margin-bottom: 16px; 
  color: var(--color-primary);
}
.tp-mobile-card h2 { font-size: var(--text-xl); font-weight: 700; font-family: var(--font-primary); margin-bottom: 12px; }
.tp-mobile-card p { font-size: var(--text-base); font-family: var(--font-primary); color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 8px; }

/* Admin shell */
.tp-admin-shell { 
  display: flex; 
  height: 100vh; 
  overflow: hidden; 
  background: var(--color-surface); 
  font-family: var(--font-primary); 
}

/* Sidebar */
.tp-sidebar {
  width: 260px;
  min-width: 260px;
  max-width: 260px;
  background: var(--color-bg);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}
.tp-sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  border-bottom: 1px solid var(--color-border);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-bg) 100%);
}
.tp-brand-icon {
  width: 40px; height: 40px;
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700;
  font-family: var(--font-primary);
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}
.tp-brand-name { font-size: var(--text-base); font-weight: 700; font-family: var(--font-primary); color: var(--color-text-primary); line-height: 1.2; }
.tp-brand-sub  { font-size: var(--text-xs); font-family: var(--font-primary); color: var(--color-text-hint); font-weight: 500; }

.tp-sidebar-nav { flex: 1; padding: 8px 0; display: flex; flex-direction: column; }

.tp-nav-group-label {
  font-size: 10px;
  font-family: var(--font-primary);
  font-weight: 700;
  color: var(--color-text-hint);
  letter-spacing: 0.8px;
  text-transform: uppercase;
  padding: 16px 18px 6px;
  margin-top: 4px;
}

.tp-sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 11px 18px;
  min-height: 44px;
  border: none;
  background: transparent;
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  margin: 2px 0;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}
.tp-sidebar-nav-item:hover { 
  background: var(--color-surface); 
  color: var(--color-text-primary);
  transform: translateX(2px);
}
.tp-sidebar-nav-item.active {
  background: linear-gradient(90deg, var(--color-primary-light) 0%, rgba(255,152,0,0.05) 100%);
  color: var(--color-primary-dark);
  font-weight: 600;
  border-left-color: var(--color-primary);
}
.tp-sidebar-nav-item.active .tp-nav-icon {
  color: var(--color-primary);
}
.tp-nav-icon { 
  font-size: 20px; 
  width: 24px; 
  text-align: center; 
  flex-shrink: 0;
  color: var(--color-text-hint);
  transition: color 0.2s ease;
}
.tp-sidebar-nav-item:hover .tp-nav-icon {
  color: var(--color-text-secondary);
}
.tp-nav-scope {
  margin-left: auto;
  font-size: 10px;
  background: var(--color-surface-2);
  color: var(--color-text-hint);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-family: var(--font-primary);
  font-weight: 500;
}
.tp-nav-badge {
  margin-left: auto;
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-primary);
  min-width: 20px; height: 20px;
  padding: 0 6px;
  display: inline-flex; align-items: center; justify-content: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.tp-badge-urgent { background: var(--color-danger); }

/* Sidebar footer */
.tp-sidebar-footer {
  padding: 16px 18px;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-surface) 100%);
}
.tp-footer-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--color-secondary-light, var(--color-primary-light));
  border-radius: var(--radius-full);
  margin-bottom: 4px;
}
.tp-footer-avatar .material-icons {
  font-size: 32px;
  color: var(--color-secondary, var(--color-primary));
}
.tp-footer-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.tp-footer-name { font-size: var(--text-sm); font-weight: 600; font-family: var(--font-primary); color: var(--color-text-primary); }
.tp-footer-role { font-size: var(--text-xs); font-family: var(--font-primary); color: var(--color-secondary, var(--color-primary)); font-weight: 600; }
.tp-footer-dept { font-size: var(--text-xs); font-family: var(--font-primary); color: var(--color-text-hint); }
.tp-logout-btn {
  margin-top: 4px;
  width: 100%;
  padding: 10px 0;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-danger);
  cursor: pointer;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.tp-logout-btn:hover { 
  background: var(--color-danger-bg); 
  border-color: var(--color-danger);
  transform: translateY(-1px);
}
.tp-logout-btn .material-icons {
  font-size: 18px;
}

/* Main content */
.tp-admin-main { flex: 1; overflow-y: auto; padding: 28px 32px; }

.tp-access-denied {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 12px;
  color: var(--color-text-hint);
  font-family: var(--font-primary);
  font-size: var(--text-base);
}
.tp-access-denied .material-icons { font-size: 48px; color: var(--color-text-hint); }

/* Modal Styles */
.tp-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}
.tp-modal-dialog {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: 24px 28px;
  min-width: 360px;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
  animation: slideUp 0.3s ease;
}
.tp-modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.tp-modal-icon {
  font-size: 28px;
  color: var(--color-danger);
}
.tp-modal-header h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  font-family: var(--font-primary);
  color: var(--color-text-primary);
  margin: 0;
}
.tp-modal-text {
  font-size: var(--text-base);
  font-family: var(--font-primary);
  color: var(--color-text-secondary);
  margin-bottom: 24px;
  line-height: 1.5;
}
.tp-modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.tp-btn-secondary {
  padding: 10px 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}
.tp-btn-secondary:hover {
  background: var(--color-surface-2);
}
.tp-btn-danger {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-danger);
  color: #fff;
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}
.tp-btn-danger:hover {
  background: #B71C1C;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(211, 47, 47, 0.3);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mobile Responsive Admin Shell */
@media (max-width: 1023px) {
  .tp-admin-shell.mobile-layout {
    flex-direction: column;
  }
  .mobile-layout .tp-sidebar {
    width: 100%;
    min-width: 100%;
    max-width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
    height: auto;
    flex-shrink: 0;
  }
  .mobile-layout .tp-sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: flex-start;
    padding: 8px;
    max-height: 200px;
    overflow-y: auto;
  }
  .mobile-layout .tp-nav-group-label {
    display: none;
  }
  .mobile-layout .tp-sidebar-nav-item {
    width: auto;
    border-radius: var(--radius-full);
    border-left: none;
    padding: 8px 16px;
    margin: 4px;
    background: var(--color-surface-2);
    min-height: auto;
  }
  .mobile-layout .tp-sidebar-nav-item span:not(.tp-nav-icon) {
    font-size: var(--text-sm);
  }
  .mobile-layout .tp-sidebar-nav-item.active {
    background: var(--color-primary);
    color: white;
  }
  .mobile-layout .tp-sidebar-nav-item.active .tp-nav-icon {
    color: white;
  }
  .mobile-layout .tp-sidebar-footer {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
  }
  .mobile-layout .tp-footer-avatar {
    width: 32px;
    height: 32px;
    margin-bottom: 0;
  }
  .mobile-layout .tp-footer-avatar .material-icons {
    font-size: 20px;
  }
  .mobile-layout .tp-footer-info {
    flex: 1;
    margin-left: 12px;
  }
  .mobile-layout .tp-logout-btn {
    width: auto;
    margin-top: 0;
    padding: 6px 12px;
    min-height: auto;
  }
  .mobile-layout .tp-admin-main {
    padding: 20px 16px;
  }
}
</style>
