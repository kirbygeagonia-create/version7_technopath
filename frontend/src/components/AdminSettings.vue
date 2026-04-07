<template>
  <div class="admin-settings">
    <!-- Profile Section -->
    <div class="settings-section">
      <div class="section-header">
        <span class="material-icons">person_outline</span>
        <h3>Admin Profile</h3>
      </div>
      <div class="settings-card">
        <div class="profile-card">
          <div class="profile-avatar">
            <span class="material-icons">admin_panel_settings</span>
          </div>
          <div class="profile-info">
            <div class="profile-name">{{ authStore.user?.username || 'Administrator' }}</div>
            <div class="profile-email">{{ authStore.user?.email || 'admin@seait.edu.ph' }}</div>
            <div class="profile-role">{{ authStore.user?.user_type_display || 'Super Admin' }}</div>
          </div>
          <button class="btn-edit" @click="showEditProfile = true">Edit</button>
        </div>
      </div>
    </div>

    <!-- General Settings Section -->
    <div class="settings-section">
      <div class="section-header">
        <span class="material-icons">tune</span>
        <h3>General Settings</h3>
      </div>
      <div class="settings-card">
        <div class="setting-row">
          <div class="setting-info">
            <span class="material-icons setting-icon">dark_mode</span>
            <div class="setting-text">
              <div class="setting-title">Dark Mode</div>
              <div class="setting-desc">Enable dark theme for admin panel</div>
            </div>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="settings.darkMode" @change="toggleDarkMode">
            <span class="slider"></span>
          </label>
        </div>
        <div class="divider"></div>
        <div class="setting-row">
          <div class="setting-info">
            <span class="material-icons setting-icon">notifications</span>
            <div class="setting-text">
              <div class="setting-title">Notifications</div>
              <div class="setting-desc">Receive system notifications</div>
            </div>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="settings.notifications">
            <span class="slider"></span>
          </label>
        </div>
        <div class="divider"></div>
        <div class="setting-row">
          <div class="setting-info">
            <span class="material-icons setting-icon">save</span>
            <div class="setting-text">
              <div class="setting-title">Auto Save</div>
              <div class="setting-desc">Automatically save changes</div>
            </div>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="settings.autoSave">
            <span class="slider"></span>
          </label>
        </div>
      </div>
    </div>

    <!-- Campus Settings Section -->
    <div class="settings-section">
      <div class="section-header">
        <span class="material-icons">school</span>
        <h3>Campus Settings</h3>
      </div>
      <div class="settings-card">
        <div class="setting-row clickable" @click="editCampusName">
          <div class="setting-info">
            <span class="material-icons setting-icon">business</span>
            <div class="setting-text">
              <div class="setting-title">Campus Name</div>
              <div class="setting-desc">{{ settings.campusName }}</div>
            </div>
          </div>
          <span class="material-icons chevron">chevron_right</span>
        </div>
        <div class="divider"></div>
        <div class="setting-row clickable" @click="showLanguageDialog = true">
          <div class="setting-info">
            <span class="material-icons setting-icon">language</span>
            <div class="setting-text">
              <div class="setting-title">Language</div>
              <div class="setting-desc">{{ settings.language }}</div>
            </div>
          </div>
          <span class="material-icons chevron">chevron_right</span>
        </div>
      </div>
    </div>

    <!-- Data Management Section -->
    <div class="settings-section">
      <div class="section-header">
        <span class="material-icons">storage</span>
        <h3>Data Management</h3>
      </div>
      <div class="settings-card">
        <div class="setting-row clickable" @click="backupData">
          <div class="setting-info">
            <span class="material-icons setting-icon" style="color: #2196F3;">backup</span>
            <div class="setting-text">
              <div class="setting-title">Backup Data</div>
              <div class="setting-desc">Export database backup</div>
            </div>
          </div>
          <span class="material-icons chevron">chevron_right</span>
        </div>
        <div class="divider"></div>
        <div class="setting-row clickable" @click="restoreData">
          <div class="setting-info">
            <span class="material-icons setting-icon" style="color: #4CAF50;">restore</span>
            <div class="setting-text">
              <div class="setting-title">Restore Data</div>
              <div class="setting-desc">Import from backup file</div>
            </div>
          </div>
          <span class="material-icons chevron">chevron_right</span>
        </div>
        <div class="divider"></div>
        <div class="setting-row clickable" @click="showClearCacheDialog = true">
          <div class="setting-info">
            <span class="material-icons setting-icon" style="color: #F44336;">delete_sweep</span>
            <div class="setting-text">
              <div class="setting-title">Clear Cache</div>
              <div class="setting-desc">Remove temporary files</div>
            </div>
          </div>
          <span class="material-icons chevron">chevron_right</span>
        </div>
      </div>
    </div>

    <!-- About Section -->
    <div class="settings-section">
      <div class="section-header">
        <span class="material-icons">info_outline</span>
        <h3>About</h3>
      </div>
      <div class="settings-card">
        <div class="setting-row">
          <div class="setting-info">
            <span class="material-icons setting-icon">app_shortcut</span>
            <div class="setting-text">
              <div class="setting-title">App Version</div>
              <div class="setting-desc">v4.0.1</div>
            </div>
          </div>
        </div>
        <div class="divider"></div>
        <div class="setting-row">
          <div class="setting-info">
            <span class="material-icons setting-icon">code</span>
            <div class="setting-text">
              <div class="setting-title">Build Number</div>
              <div class="setting-desc">20250327</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Logout Button -->
    <div class="logout-section">
      <button class="btn-logout" @click="logout">
        <span class="material-icons">logout</span>
        Logout from Admin
      </button>
    </div>

    <!-- Edit Profile Dialog -->
    <div v-if="showEditProfile" class="modal-overlay" @click.self="showEditProfile = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>Edit Profile</h3>
          <button class="btn-close" @click="showEditProfile = false">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Username</label>
            <input v-model="editProfile.username" type="text">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="editProfile.email" type="email">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditProfile = false">Cancel</button>
          <button class="btn-primary" @click="saveProfile">Save</button>
        </div>
      </div>
    </div>

    <!-- Language Dialog -->
    <div v-if="showLanguageDialog" class="modal-overlay" @click.self="showLanguageDialog = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>Select Language</h3>
          <button class="btn-close" @click="showLanguageDialog = false">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="language-list">
            <div 
              v-for="lang in languages" 
              :key="lang" 
              class="language-option"
              :class="{ active: settings.language === lang }"
              @click="selectLanguage(lang)"
            >
              <span class="language-name">{{ lang }}</span>
              <span v-if="settings.language === lang" class="material-icons check">check</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Clear Cache Confirmation -->
    <div v-if="showClearCacheDialog" class="modal-overlay" @click.self="showClearCacheDialog = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>Clear Cache</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to clear the cache? This will remove temporary files but not affect your data.</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showClearCacheDialog = false">Cancel</button>
          <button class="btn-danger" @click="clearCache">Clear</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = useRouter()
const authStore = useAuthStore()

const settings = reactive({
  darkMode: false,
  notifications: true,
  autoSave: true,
  campusName: 'SEAIT Campus',
  language: 'English'
})

const showEditProfile = ref(false)
const showLanguageDialog = ref(false)
const showClearCacheDialog = ref(false)

const editProfile = reactive({
  username: '',
  email: ''
})

const languages = ['English', 'Filipino', 'Cebuano']

onMounted(() => {
  editProfile.username = authStore.user?.username || 'Administrator'
  editProfile.email = authStore.user?.email || 'admin@seait.edu.ph'
})

function toggleDarkMode() {
  document.documentElement.classList.toggle('dark-mode', settings.darkMode)
}

function editCampusName() {
  const newName = prompt('Enter campus name:', settings.campusName)
  if (newName && newName.trim()) {
    settings.campusName = newName.trim()
  }
}

function selectLanguage(lang) {
  settings.language = lang
  showLanguageDialog.value = false
}

function saveProfile() {
  showEditProfile.value = false
  // TODO: Save profile to backend
  alert('Profile updated!')
}

function backupData() {
  alert('Backup feature - Downloading database backup...')
  // TODO: Implement actual backup
}

function restoreData() {
  alert('Restore feature - Select backup file to import...')
  // TODO: Implement actual restore
}

function clearCache() {
  showClearCacheDialog.value = false
  // Clear localStorage and IndexedDB cache
  localStorage.clear()
  alert('Cache cleared successfully!')
}

function logout() {
  authStore.logout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-settings {
  padding: 24px;
  max-width: 900px;
}

.settings-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-left: 8px;
}

.section-header .material-icons {
  font-size: 18px;
  color: #666;
}

.section-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin: 0;
}

.settings-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}

/* Profile Card */
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #FF9800;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.profile-avatar .material-icons {
  font-size: 28px;
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.profile-email {
  font-size: 13px;
  color: #888;
  margin-bottom: 4px;
}

.profile-role {
  font-size: 11px;
  color: #FF9800;
  background: #FFF3E0;
  padding: 2px 10px;
  border-radius: 12px;
  display: inline-block;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-edit {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 8px;
  color: #666;
  font-size: 13px;
  cursor: pointer;
}

.btn-edit:hover {
  background: #f5f5f5;
}

/* Setting Row */
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
}

.setting-row.clickable {
  cursor: pointer;
  transition: background 0.15s;
}

.setting-row.clickable:hover {
  background: #f8f9fa;
}

.setting-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.setting-icon {
  font-size: 24px;
  color: #666;
}

.setting-text {
  flex: 1;
}

.setting-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
}

.setting-desc {
  font-size: 13px;
  color: #888;
}

.chevron {
  color: #bbb;
  font-size: 20px;
}

.divider {
  height: 1px;
  background: #f0f0f0;
  margin: 0 24px;
}

/* Switch */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .3s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #FF9800;
}

input:checked + .slider:before {
  transform: translateX(22px);
}

/* Logout Section */
.logout-section {
  padding: 24px;
  text-align: center;
}

.btn-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px 24px;
  background: #F44336;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-logout:hover {
  background: #D32F2F;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  overflow: hidden;
  animation: modalSlideIn 0.2s ease;
}

@keyframes modalSlideIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.modal-body {
  padding: 24px;
}

.modal-body p {
  margin: 0;
  color: #555;
  font-size: 14px;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #555;
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #FF9800;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #f8f9fa;
}

.btn-secondary {
  padding: 10px 20px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
}

.btn-primary {
  padding: 10px 20px;
  background: #FF9800;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: white;
  font-weight: 500;
  cursor: pointer;
}

.btn-danger {
  padding: 10px 20px;
  background: #F44336;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: white;
  font-weight: 500;
  cursor: pointer;
}

/* Language List */
.language-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.language-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.language-option:hover {
  background: #f5f5f5;
}

.language-option.active {
  background: #FFF3E0;
}

.language-name {
  font-size: 14px;
  color: #333;
}

.language-option.active .language-name {
  color: #FF9800;
  font-weight: 500;
}

.language-option .check {
  color: #FF9800;
  font-size: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-settings {
    padding: 12px;
  }
  
  .profile-card {
    padding: 16px;
    flex-direction: column;
    text-align: center;
  }
  
  .setting-row {
    padding: 14px 16px;
  }
  
  .setting-info {
    gap: 12px;
  }
  
  .modal-dialog {
    width: 95%;
  }
}
</style>
