<template>
  <div class="adminsendnotif-section">
    <div class="section-header">
      <div>
        <h1>Send Notification</h1>
        <p class="subtitle">Send push notifications and announcements to users</p>
      </div>
    </div>

    <div class="content-grid">
      <!-- Send Form -->
      <div class="form-panel">
        <h2>Compose Notification</h2>
        <form @submit.prevent="sendNotification">
          <div class="form-group">
            <label>Notification Title</label>
            <input v-model="form.title" type="text" placeholder="Enter title" maxlength="100" required />
          </div>
          <div class="form-group">
            <label>Message Body</label>
            <textarea v-model="form.body" rows="4" placeholder="Enter message body" maxlength="500" required></textarea>
            <span class="char-count">{{ form.body.length }}/500</span>
          </div>
          <div class="form-group">
            <label>Target Audience</label>
            <select v-model="form.target">
              <option value="all">All Users</option>
              <option value="students">Students Only</option>
              <option value="faculty">Faculty Only</option>
              <option value="department">My Department Only</option>
            </select>
          </div>
          <div class="form-group">
            <label>Priority</label>
            <div class="priority-options">
              <label class="priority-option">
                <input v-model="form.priority" type="radio" value="low" />
                <span class="priority-label low">Low</span>
              </label>
              <label class="priority-option">
                <input v-model="form.priority" type="radio" value="normal" />
                <span class="priority-label normal">Normal</span>
              </label>
              <label class="priority-option">
                <input v-model="form.priority" type="radio" value="high" />
                <span class="priority-label high">High</span>
              </label>
            </div>
          </div>
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input v-model="form.schedule" type="checkbox" />
              <span>Schedule for later</span>
            </label>
          </div>
          <div v-if="form.schedule" class="form-group">
            <label>Schedule Time</label>
            <input v-model="form.scheduledTime" type="datetime-local" />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="previewNotification">
              <span class="material-icons">visibility</span>
              Preview
            </button>
            <button type="submit" class="btn-primary" :disabled="sending">
              <span class="material-icons">send</span>
              {{ sending ? 'Sending...' : 'Send Now' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Preview Panel -->
      <div class="preview-panel">
        <h2>Live Preview</h2>
        <div class="device-mockup">
          <div class="notification-preview">
            <div class="notification-header">
              <span class="app-icon">TP</span>
              <span class="app-name">TechnoPath</span>
              <span class="time">Now</span>
            </div>
            <h3 class="preview-title">{{ form.title || 'Notification Title' }}</h3>
            <p class="preview-body">{{ form.body || 'Notification message body will appear here...' }}</p>
          </div>
        </div>
        <div class="target-preview">
          <span class="material-icons">people</span>
          <span>Will be sent to: <strong>{{ getTargetLabel(form.target) }}</strong></span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'

const sending = ref(false)
const form = ref({
  title: '',
  body: '',
  target: 'all',
  priority: 'normal',
  schedule: false,
  scheduledTime: ''
})

function getTargetLabel(target) {
  const labels = { all: 'All Users', students: 'Students', faculty: 'Faculty', department: 'My Department' }
  return labels[target] || target
}

function previewNotification() {
  showToast('Preview: ' + form.value.title, 'info')
}

async function sendNotification() {
  sending.value = true
  try {
    await api.post('/notifications/send/', form.value)
    form.value = { title: '', body: '', target: 'all', priority: 'normal', schedule: false, scheduledTime: '' }
  } catch (e) {
    console.error('Failed to send notification:', e)
    showToast('Failed to send notification', 'error')
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.adminsendnotif-section { padding: 0; font-family: var(--font-primary); max-width: 1400px; }

.section-header { margin-bottom: 24px; }
.section-header h1 { font-size: var(--text-2xl); font-weight: 700; color: var(--color-text-primary); margin: 0 0 4px 0; }
.subtitle { font-size: var(--text-base); color: var(--color-text-secondary); margin: 0; }

.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-box { display: flex; flex-direction: column; padding: 14px 20px; background: var(--color-bg); border-radius: var(--radius-lg); border: 1px solid var(--color-border); min-width: 100px; }
.stat-number { font-size: 24px; font-weight: 700; color: var(--color-primary); }
.stat-label { font-size: var(--text-xs); color: var(--color-text-secondary); }

.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }

.form-panel, .preview-panel { background: var(--color-bg); border-radius: var(--radius-lg); border: 1px solid var(--color-border); padding: 24px; }
.form-panel h2, .preview-panel h2 { font-size: var(--text-lg); font-weight: 600; color: var(--color-text-primary); margin: 0 0 20px 0; }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: var(--text-sm); font-weight: 500; color: var(--color-text-secondary); margin-bottom: 8px; }
.form-group input[type="text"],
.form-group textarea,
.form-group select,
.form-group input[type="datetime-local"] {
  width: 100%; padding: 12px 14px; background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); font-family: var(--font-primary); font-size: var(--text-base); color: var(--color-text-primary); outline: none;
}
.form-group input:focus, .form-group textarea:focus, .form-group select:focus { border-color: var(--color-primary); }
.char-count { float: right; font-size: var(--text-xs); color: var(--color-text-hint); margin-top: 4px; }

.priority-options { display: flex; gap: 12px; }
.priority-option { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.priority-option input { width: 18px; height: 18px; accent-color: var(--color-primary); }
.priority-label { padding: 6px 14px; border-radius: var(--radius-full); font-size: var(--text-sm); font-weight: 500; }
.priority-label.low { background: var(--color-surface-2); color: var(--color-text-secondary); }
.priority-label.normal { background: var(--color-primary-light); color: var(--color-primary); }
.priority-label.high { background: var(--color-danger-bg); color: var(--color-danger); }

.checkbox-group { display: flex; align-items: center; }
.checkbox-label { display: flex; align-items: center; gap: 10px; cursor: pointer; font-size: var(--text-base); color: var(--color-text-primary); }
.checkbox-label input { width: 18px; height: 18px; accent-color: var(--color-primary); }

.form-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }
.btn-primary, .btn-secondary { display: flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: var(--radius-md); font-family: var(--font-primary); font-size: var(--text-sm); font-weight: 500; cursor: pointer; transition: all 0.2s ease; }
.btn-primary { background: var(--color-primary); color: white; border: none; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-dark); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: var(--color-surface); color: var(--color-text-primary); border: 1px solid var(--color-border); }
.btn-secondary:hover { background: var(--color-surface-2); }

.device-mockup { background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%); border-radius: var(--radius-xl); padding: 24px; max-width: 320px; margin: 0 auto; }
.notification-preview { background: rgba(255,255,255,0.95); border-radius: var(--radius-lg); padding: 16px; }
.notification-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.app-icon { width: 24px; height: 24px; background: var(--color-primary); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: white; }
.app-name { font-size: var(--text-xs); color: var(--color-text-secondary); font-weight: 600; }
.time { margin-left: auto; font-size: var(--text-xs); color: var(--color-text-hint); }
.preview-title { font-size: var(--text-base); font-weight: 600; color: var(--color-text-primary); margin: 0 0 6px 0; }
.preview-body { font-size: var(--text-sm); color: var(--color-text-secondary); margin: 0; line-height: 1.4; }

.target-preview { display: flex; align-items: center; gap: 8px; margin-top: 16px; padding: 12px; background: var(--color-surface); border-radius: var(--radius-md); font-size: var(--text-sm); color: var(--color-text-secondary); }
.target-preview .material-icons { font-size: 18px; color: var(--color-primary); }

.history-section h2 { font-size: var(--text-lg); font-weight: 600; color: var(--color-text-primary); margin: 0 0 16px 0; }
.history-list { display: flex; flex-direction: column; gap: 12px; }
.history-item { display: flex; align-items: flex-start; gap: 16px; padding: 16px; background: var(--color-bg); border-radius: var(--radius-lg); border: 1px solid var(--color-border); }
.history-icon { width: 40px; height: 40px; background: var(--color-primary-light); border-radius: var(--radius-full); display: flex; align-items: center; justify-content: center; }
.history-icon .material-icons { color: var(--color-primary); }
.history-content { flex: 1; }
.history-content h4 { font-size: var(--text-base); font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px 0; }
.history-content p { font-size: var(--text-sm); color: var(--color-text-secondary); margin: 0 0 8px 0; }
.history-meta { display: flex; gap: 12px; }
.history-meta span { font-size: var(--text-xs); padding: 2px 8px; border-radius: var(--radius-full); }
.history-meta .target { background: var(--color-info-bg); color: var(--color-info); }
.history-meta .priority { text-transform: uppercase; font-weight: 600; }
.history-meta .priority.low { background: var(--color-surface-2); color: var(--color-text-secondary); }
.history-meta .priority.normal { background: var(--color-primary-light); color: var(--color-primary); }
.history-meta .priority.high { background: var(--color-danger-bg); color: var(--color-danger); }
.history-meta .time { color: var(--color-text-hint); background: var(--color-surface); }
.history-stats { display: flex; align-items: center; }
.history-stats .stat { display: flex; align-items: center; gap: 4px; font-size: var(--text-sm); color: var(--color-success); }
.history-stats .stat .material-icons { font-size: 16px; }

@media (max-width: 768px) {
  .content-grid { grid-template-columns: 1fr; }
}
</style>
