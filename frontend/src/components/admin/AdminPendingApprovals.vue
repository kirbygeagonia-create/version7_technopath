<template>
  <div class="adminpendingapprovals-section">
    <h1>Notifications</h1>
    
    <div v-if="pending.length === 0" class="tp-empty">
      No notifications to approve.
    </div>
    
    <div v-for="a in pending" :key="a.id" class="adminpendingapprovals-card">
      <div class="adminpendingapprovals-header">
        <span :class="['adminpendingapprovals-source-chip', 'adminpendingapprovals-chip-' + a.source_color]">{{ a.source_label }}</span>
        <span class="adminpendingapprovals-submitter">by {{ a.created_by }} ({{ a.department }})</span>
        <span class="adminpendingapprovals-time">{{ formatTime(a.created_at) }}</span>
      </div>
      <h3>{{ a.title }}</h3>
      <p>{{ a.content }}</p>
      <div class="adminpendingapprovals-scope">Scope: {{ formatScope(a.scope) }}</div>
      <div class="adminpendingapprovals-actions">
        <button @click="approve(a.id)" class="adminpendingapprovals-btn-success">Approve & Publish</button>
        <button @click="showRejectDialog(a.id)" class="adminpendingapprovals-btn-danger">Reject</button>
      </div>
    </div>

    <!-- Reject Dialog -->
    <div v-if="rejectingId" class="adminpendingapprovals-reject-dialog">
      <h3>Reject Announcement</h3>
      <textarea v-model="rejectNote" placeholder="Reason for rejection (optional)" rows="3" class="tp-textarea"></textarea>
      <div class="adminpendingapprovals-dialog-actions">
        <button @click="cancelReject" class="adminpendingapprovals-btn-secondary">Cancel</button>
        <button @click="confirmReject" class="adminpendingapprovals-btn-danger">Confirm Reject</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'

const emit = defineEmits(['count'])
const pending = ref([])
const rejectingId = ref(null)
const rejectNote = ref('')

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleString()
}

function formatScope(scope) {
  const labels = {
    'campus_wide': 'Entire Campus',
    'all_college': 'All College Students',
    'basic_ed_only': 'Basic Education Only',
    'department': 'Specific Department'
  }
  return labels[scope] || scope
}

async function loadPending() {
  try {
    const r = await api.get('/announcements/pending/')
    pending.value = r.data
    emit('count', r.data.length)
  } catch (e) {
    console.error('Failed to load pending:', e)
  }
}

async function approve(id) {
  try {
    await api.post(`/announcements/${id}/approve/`)
    await loadPending()
  } catch (e) {
    console.error('Failed to approve:', e)
    showToast('Failed to approve announcement', 'error')
  }
}

function showRejectDialog(id) {
  rejectingId.value = id
  rejectNote.value = ''
}

function cancelReject() {
  rejectingId.value = null
  rejectNote.value = ''
}

async function confirmReject() {
  try {
    await api.post(`/announcements/${rejectingId.value}/reject/`, { note: rejectNote.value })
    rejectingId.value = null
    rejectNote.value = ''
    await loadPending()
  } catch (e) {
    console.error('Failed to reject:', e)
    showToast('Failed to reject announcement', 'error')
  }
}

onMounted(loadPending)
</script>

<style scoped>
.adminpendingapprovals-section { padding: 20px; font-family: var(--font-primary); }
.tp-empty { color: var(--color-text-hint); padding: 40px; text-align: center; }
.adminpendingapprovals-card { 
  background: var(--color-bg); border: 1px solid var(--color-border); 
  padding: 20px; border-radius: var(--radius-md); margin-bottom: 16px; 
}
.adminpendingapprovals-header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.adminpendingapprovals-source-chip { 
  display: inline-block; font-size: var(--text-xs); font-weight: 600;
  padding: 2px 8px; border-radius: var(--radius-full);
}
.adminpendingapprovals-chip-red        { background: #FFEBEE; color: #B71C1C; }
.adminpendingapprovals-chip-dark_blue  { background: #E8EAF6; color: #1A237E; }
.adminpendingapprovals-chip-green      { background: #E8F5E9; color: #1B5E20; }
.adminpendingapprovals-chip-charcoal   { background: #ECEFF1; color: #263238; }
.adminpendingapprovals-chip-purple     { background: #F3E5F5; color: #4A148C; }
.adminpendingapprovals-chip-teal       { background: #E0F2F1; color: #004D40; }
.adminpendingapprovals-chip-amber      { background: #FFF8E1; color: #E65100; }
.adminpendingapprovals-chip-blue       { background: #E3F2FD; color: #0D47A1; }
.adminpendingapprovals-chip-dark_green { background: #E8F5E9; color: #33691E; }
.adminpendingapprovals-chip-indigo     { background: #E8EAF6; color: #283593; }
.adminpendingapprovals-chip-brown      { background: #EFEBE9; color: #4E342E; }
.adminpendingapprovals-chip-orange     { background: #FFF3E0; color: #E65100; }
.adminpendingapprovals-submitter { font-size: var(--text-sm); color: var(--color-text-secondary); }
.adminpendingapprovals-time { font-size: var(--text-xs); color: var(--color-text-hint); margin-left: auto; }
.adminpendingapprovals-scope { font-size: var(--text-sm); color: var(--color-text-secondary); margin-top: 8px; }
.adminpendingapprovals-actions { display: flex; gap: 12px; margin-top: 16px; }
.adminpendingapprovals-btn-success, .adminpendingapprovals-btn-danger, .adminpendingapprovals-btn-secondary {
  padding: 10px 20px; border: none; border-radius: var(--radius-md);
  font-family: var(--font-primary); font-size: var(--text-sm);
  cursor: pointer; min-height: 44px;
}
.adminpendingapprovals-btn-success { background: #4CAF50; color: white; }
.adminpendingapprovals-btn-danger { background: #F44336; color: white; }
.adminpendingapprovals-btn-secondary { background: var(--color-surface); color: var(--color-text-primary); border: 1px solid var(--color-border); }
.adminpendingapprovals-reject-dialog {
  background: var(--color-bg); border: 1px solid var(--color-border);
  padding: 20px; border-radius: var(--radius-md); margin-top: 20px;
}
.adminpendingapprovals-textarea { 
  width: 100%; padding: 10px; border: 1px solid var(--color-border); 
  border-radius: var(--radius-sm); font-family: var(--font-primary);
  margin: 12px 0;
}
.adminpendingapprovals-dialog-actions { display: flex; gap: 12px; justify-content: flex-end; }
</style>
