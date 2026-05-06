<template>
  <div class="adminfaq-section">
    <!-- Header -->
    <div class="section-header">
      <div>
        <h1>FAQ / Chatbot Management</h1>
        <p class="subtitle">Manage chatbot knowledge base and FAQ entries</p>
      </div>
      <button v-if="activeTab === 'manual'" class="btn-primary" @click="showCreateModal = true">
        <span class="material-icons">add</span>
        Add FAQ
      </button>
      <button v-else class="btn-primary" @click="runAnalysis" :disabled="isAnalyzing">
        <span class="material-icons">auto_fix_high</span>
        {{ isAnalyzing ? 'Analyzing...' : 'Run AI Analysis' }}
      </button>
    </div>

    <!-- Main Tabs -->
    <div class="main-tabs">
      <button 
        :class="['tab-btn', { active: activeTab === 'manual' }]"
        @click="activeTab = 'manual'"
      >
        <span class="material-icons">list</span>
        Manual FAQs
        <span class="tab-badge">{{ faqs.length }}</span>
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'ai' }]"
        @click="activeTab = 'ai'"
      >
        <span class="material-icons">psychology</span>
        AI Suggestions
        <span class="tab-badge warning">{{ suggestionCounts.pending }}</span>
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'analytics' }]"
        @click="activeTab = 'analytics'"
      >
        <span class="material-icons">analytics</span>
        Analytics
      </button>
    </div>

    <!-- Manual FAQs Tab -->
    <div v-if="activeTab === 'manual'">
      <!-- Stats -->
      <div class="stats-row">
        <div class="stat-box">
          <span class="stat-number">{{ faqs.length }}</span>
          <span class="stat-label">Total FAQs</span>
        </div>
        <div class="stat-box">
          <span class="stat-number">{{ categories.length }}</span>
          <span class="stat-label">Categories</span>
        </div>
        <div class="stat-box">
          <span class="stat-number">{{ faqs.filter(f => f.is_active).length }}</span>
          <span class="stat-label">Active</span>
        </div>
      </div>

    <!-- Category Filter -->
    <div class="category-filter">
      <button 
        :class="['category-btn', { active: selectedCategory === '' }]"
        @click="selectedCategory = ''"
      >
        All
      </button>
      <button 
        v-for="cat in categories" 
        :key="cat"
        :class="['category-btn', { active: selectedCategory === cat }]"
        @click="selectedCategory = cat"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Search -->
    <div class="search-bar">
      <span class="material-icons">search</span>
      <input v-model="searchQuery" type="text" placeholder="Search questions or answers..." />
    </div>

    <!-- FAQ List -->
    <div class="faq-list">
      <div v-for="faq in filteredFaqs" :key="faq.id" class="faq-card">
        <div class="faq-header">
          <span class="category-tag">{{ faq.category }}</span>
          <div class="faq-actions">
            <button class="btn-icon" @click="toggleActive(faq)" :title="faq.is_active ? 'Deactivate' : 'Activate'">
              <span class="material-icons">{{ faq.is_active ? 'visibility' : 'visibility_off' }}</span>
            </button>
            <button class="btn-icon" @click="editFaq(faq)" title="Edit">
              <span class="material-icons">edit</span>
            </button>
            <button class="btn-icon btn-danger" @click="confirmDelete(faq)" title="Delete">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
        <div class="faq-content">
          <h3 class="faq-question">{{ faq.question }}</h3>
          <p class="faq-answer">{{ faq.answer }}</p>
        </div>
        <div class="faq-footer">
          <span :class="['status-badge', faq.is_active ? 'status-active' : 'status-inactive']">
            {{ faq.is_active ? 'Active' : 'Inactive' }}
          </span>
          <span class="updated-at">Updated {{ formatDate(faq.updated_at) }}</span>
        </div>
      </div>
    </div>

    <div v-if="filteredFaqs.length === 0" class="empty-state">
      <span class="material-icons">help_outline</span>
      <p>No FAQs found</p>
    </div>
    </div><!-- End Manual FAQs Tab -->

    <!-- AI Suggestions Tab -->
    <div v-else-if="activeTab === 'ai'" class="ai-suggestions-tab">
      <!-- Analysis Controls -->
      <div class="analysis-controls">
        <div class="control-group">
          <label>Analysis Period (days)</label>
          <input type="number" v-model.number="analyzeDays" min="1" max="90" class="admin-input" />
        </div>
        <div class="control-group">
          <label>Min Query Count</label>
          <input type="number" v-model.number="minQueryCount" min="1" max="10" class="admin-input" />
        </div>
        <div class="control-group">
          <label>Similarity Threshold</label>
          <input type="number" v-model.number="similarityThreshold" min="0.1" max="1.0" step="0.1" class="admin-input" />
        </div>
      </div>

      <div v-if="analysisResult" class="analysis-result" :class="analysisResult.type">
        <span class="material-icons">{{ analysisResult.type === 'success' ? 'check_circle' : 'info' }}</span>
        {{ analysisResult.message }}
      </div>

      <!-- Suggestion Status Tabs -->
      <div class="suggestion-tabs">
        <button 
          :class="['suggestion-tab', { active: suggestionTab === 'pending' }]"
          @click="suggestionTab = 'pending'"
        >
          Pending ({{ suggestionCounts.pending }})
        </button>
        <button 
          :class="['suggestion-tab', { active: suggestionTab === 'approved' }]"
          @click="suggestionTab = 'approved'"
        >
          Approved ({{ suggestionCounts.approved }})
        </button>
        <button 
          :class="['suggestion-tab', { active: suggestionTab === 'rejected' }]"
          @click="suggestionTab = 'rejected'"
        >
          Rejected ({{ suggestionCounts.rejected }})
        </button>
      </div>

      <!-- Suggestions List -->
      <div v-if="loadingSuggestions" class="loading-state">
        <div class="spinner"></div>
        <p>Loading suggestions...</p>
      </div>

      <div v-else-if="filteredSuggestions.length === 0" class="empty-state">
        <span class="material-icons">inbox</span>
        <p>No {{ suggestionTab }} suggestions found</p>
        <p v-if="suggestionTab === 'pending'" class="hint">
          Click "Run AI Analysis" to generate new FAQ suggestions from chat logs
        </p>
      </div>

      <div v-else class="suggestions-list">
        <div 
          v-for="suggestion in filteredSuggestions" 
          :key="suggestion.id"
          class="suggestion-card"
          :class="{ expanded: expandedSuggestion === suggestion.id }"
        >
          <div class="suggestion-header" @click="toggleExpand(suggestion.id)">
            <div class="suggestion-info">
              <span class="category-badge" :class="suggestion.category">{{ suggestion.category }}</span>
              <h4>{{ suggestion.suggested_question }}</h4>
              <div class="suggestion-meta">
                <span><span class="material-icons">repeat</span> {{ suggestion.query_count }} similar queries</span>
                <span><span class="material-icons">psychology</span> {{ Math.round(suggestion.confidence_score * 100) }}% confidence</span>
                <span><span class="material-icons">calendar_today</span> {{ formatDate(suggestion.created_at) }}</span>
              </div>
            </div>
            <div v-if="suggestion.status === 'pending'" class="suggestion-actions">
              <button class="btn-icon success" @click.stop="approveSuggestion(suggestion)" title="Approve">
                <span class="material-icons">check</span>
              </button>
              <button class="btn-icon btn-danger" @click.stop="showRejectDialog(suggestion)" title="Reject">
                <span class="material-icons">close</span>
              </button>
            </div>
            <span v-else class="status-badge" :class="suggestion.status">{{ suggestion.status }}</span>
          </div>

          <div v-if="expandedSuggestion === suggestion.id" class="suggestion-details">
            <div class="detail-section">
              <label>Suggested Answer:</label>
              <textarea 
                v-if="suggestion.status === 'pending'"
                v-model="suggestion.editAnswer"
                class="admin-textarea"
                rows="4"
              ></textarea>
              <p v-else class="answer-text">{{ suggestion.suggested_answer }}</p>
            </div>
            <div class="detail-row">
              <div class="detail-section">
                <label>Keywords:</label>
                <input v-if="suggestion.status === 'pending'" v-model="suggestion.editKeywords" type="text" class="admin-input" />
                <span v-else>{{ suggestion.keywords }}</span>
              </div>
              <div class="detail-section">
                <label>Category:</label>
                <select v-if="suggestion.status === 'pending'" v-model="suggestion.editCategory" class="admin-select">
                  <option value="location">Location</option>
                  <option value="schedule">Schedule</option>
                  <option value="academic">Academic</option>
                  <option value="services">Services</option>
                  <option value="general">General</option>
                </select>
                <span v-else>{{ suggestion.category }}</span>
              </div>
            </div>
            <div class="detail-section" v-if="suggestion.source_queries?.length">
              <label>Sample Queries:</label>
              <ul class="source-queries">
                <li v-for="(query, idx) in suggestion.source_queries.slice(0, 5)" :key="idx">"{{ query }}"</li>
              </ul>
            </div>
            <div v-if="suggestion.status === 'pending'" class="detail-actions">
              <button class="btn-secondary" @click="saveSuggestionEdits(suggestion)">Save Changes</button>
              <button class="btn-primary" @click="approveSuggestion(suggestion)">Approve & Create FAQ</button>
            </div>
          </div>
        </div>
      </div>
    </div><!-- End AI Suggestions Tab -->

    <!-- Analytics Tab -->
    <div v-else-if="activeTab === 'analytics'" class="analytics-tab">
      <div class="analytics-header">
        <div class="analytics-filters">
          <select v-model="analyticsDays" @change="loadAnalytics" class="admin-select">
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          <button class="btn-secondary" @click="loadAnalytics">
            <span class="material-icons">refresh</span>
            Refresh
          </button>
        </div>
      </div>

      <div v-if="analytics" class="analytics-content">
        <!-- Key Metrics -->
        <div class="analytics-grid">
          <div class="metric-card">
            <div class="metric-value">{{ analytics.total_queries }}</div>
            <div class="metric-label">Total Queries</div>
          </div>
          <div class="metric-card success">
            <div class="metric-value">{{ analytics.successful_queries }}</div>
            <div class="metric-label">Successful</div>
            <div class="metric-sub">{{ analytics.success_rate }}% rate</div>
          </div>
          <div class="metric-card danger">
            <div class="metric-value">{{ analytics.failed_queries }}</div>
            <div class="metric-label">Failed/Unanswered</div>
          </div>
          <div class="metric-card warning">
            <div class="metric-value">{{ analytics.suggestions?.pending || 0 }}</div>
            <div class="metric-label">Pending Suggestions</div>
          </div>
        </div>

        <!-- Mode Breakdown -->
        <div class="analytics-section">
          <h4>Query Mode Breakdown</h4>
          <div class="mode-breakdown">
            <div class="mode-item">
              <span class="mode-label">Online AI:</span>
              <span class="mode-value">{{ analytics.mode_breakdown?.online || 0 }}</span>
            </div>
            <div class="mode-item">
              <span class="mode-label">Offline FAQ:</span>
              <span class="mode-value">{{ analytics.mode_breakdown?.offline || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Top Unanswered Queries -->
        <div class="analytics-section" v-if="analytics.top_unanswered_queries?.length">
          <h4>Top Unanswered Queries</h4>
          <div class="unanswered-list">
            <div v-for="(query, idx) in analytics.top_unanswered_queries" :key="idx" class="unanswered-item">
              <span class="query-rank">#{{ idx + 1 }}</span>
              <span class="query-text">{{ query.user_query }}</span>
              <span class="query-count">{{ query.count }} times</span>
            </div>
          </div>
        </div>

        <!-- Top FAQs -->
        <div class="analytics-section" v-if="analytics.top_faqs?.length">
          <h4>Most Used FAQs</h4>
          <div class="top-faqs-list">
            <div v-for="(faq, idx) in analytics.top_faqs" :key="idx" class="top-faq-item">
              <span class="faq-rank">#{{ idx + 1 }}</span>
              <span class="faq-question-text">{{ faq.question }}</span>
              <span class="faq-usage">{{ faq.usage_count }} uses</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="loading-state">
        <div class="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    </div><!-- End Analytics Tab -->

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-dialog">
        <div class="modal-header">
          <h2>{{ showEditModal ? 'Edit FAQ' : 'Add New FAQ' }}</h2>
          <button class="btn-close" @click="closeModal">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Category</label>
            <select v-model="form.category">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              <option value="_new">+ Add New Category</option>
            </select>
            <input v-if="form.category === '_new'" v-model="newCategory" type="text" placeholder="Enter new category name" class="new-category-input" />
          </div>
          <div class="form-group">
            <label>Question</label>
            <input v-model="form.question" type="text" placeholder="Enter the question" />
          </div>
          <div class="form-group">
            <label>Answer</label>
            <div class="ai-generate-wrapper">
              <textarea v-model="form.answer" rows="5" placeholder="Enter the answer or click AI Generate"></textarea>
              <button 
                v-if="form.question && !showEditModal" 
                class="btn-ai-generate" 
                @click="generateAiAnswer"
                :disabled="isGeneratingAnswer"
              >
                <span class="material-icons">auto_fix_high</span>
                {{ isGeneratingAnswer ? 'Generating...' : 'AI Generate Answer' }}
              </button>
            </div>
          </div>
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input v-model="form.is_active" type="checkbox" />
              <span>Active (visible to users)</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn-primary" @click="saveFaq">
            {{ showEditModal ? 'Save Changes' : 'Create FAQ' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-dialog modal-sm">
        <div class="modal-header">
          <span class="material-icons modal-icon">warning</span>
          <h2>Delete FAQ</h2>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this FAQ?</p>
          <p class="text-muted">"{{ faqToDelete?.question }}"</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancel</button>
          <button class="btn-danger" @click="deleteFaq">Delete</button>
        </div>
      </div>
    </div>

    <!-- Reject Suggestion Dialog -->
    <div v-if="showRejectDialog" class="modal-overlay" @click.self="showRejectDialog = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <span class="material-icons modal-icon">help_outline</span>
          <h2>Reject Suggestion</h2>
        </div>
        <div class="modal-body">
          <p>Add an optional note explaining why this suggestion is being rejected:</p>
          <textarea 
            v-model="rejectNote" 
            placeholder="Review note (optional)..."
            rows="3"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showRejectDialog = false">Cancel</button>
          <button class="btn-danger" @click="confirmReject">
            <span class="material-icons">close</span>
            Reject Suggestion
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'
import { normalizePaginated } from '../../utils/pagination.js'

// Tab state
const activeTab = ref('manual')
const suggestionTab = ref('pending')

// FAQ data
const faqs = ref([])
const searchQuery = ref('')
const selectedCategory = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const faqToDelete = ref(null)
const newCategory = ref('')

// FAQ Maker AI state
const suggestions = ref([])
const analytics = ref(null)
const analyticsDays = ref(7)
const loadingSuggestions = ref(false)
const isAnalyzing = ref(false)
const expandedSuggestion = ref(null)
const analysisResult = ref(null)
const isGeneratingAnswer = ref(false)

// Analysis controls
const analyzeDays = ref(7)
const minQueryCount = ref(2)
const similarityThreshold = ref(0.7)

const form = ref({
  id: null,
  category: '',
  question: '',
  answer: '',
  is_active: true
})

// Reject dialog
const showRejectDialog = ref(false)
const rejectSuggestion = ref(null)
const rejectNote = ref('')

const categories = computed(() => {
  const cats = [...new Set(faqs.value.map(f => f.category))]
  return cats.sort()
})

const filteredFaqs = computed(() => {
  return faqs.value.filter(faq => {
    const matchesCategory = !selectedCategory.value || faq.category === selectedCategory.value
    const matchesSearch = !searchQuery.value ||
      faq.question.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCategory && matchesSearch
  })
})

const filteredSuggestions = computed(() => {
  return suggestions.value.filter(s => s.status === suggestionTab.value)
})

const suggestionCounts = computed(() => {
  const pending = suggestions.value.filter(s => s.status === 'pending').length
  const approved = suggestions.value.filter(s => s.status === 'approved').length
  const rejected = suggestions.value.filter(s => s.status === 'rejected').length
  return { pending, approved, rejected }
})

function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function editFaq(faq) {
  form.value = { ...faq }
  showEditModal.value = true
}

function closeModal() {
  showCreateModal.value = false
  showEditModal.value = false
  newCategory.value = ''
  form.value = { id: null, category: categories.value[0] || '', question: '', answer: '', is_active: true }
}

function confirmDelete(faq) {
  faqToDelete.value = faq
  showDeleteModal.value = true
}

async function loadFaqs() {
  try {
    const response = await api.get('/faq/?page_size=1000')
    faqs.value = normalizePaginated(response.data).items
  } catch (e) {
    console.error('Failed to load FAQs:', e)
    // Mock data
    faqs.value = [
      { id: 1, category: 'General', question: 'What are the campus operating hours?', answer: 'The campus is open from 6:00 AM to 9:00 PM on weekdays, and 7:00 AM to 6:00 PM on weekends.', is_active: true, updated_at: new Date().toISOString() },
      { id: 2, category: 'General', question: 'Where can I find the registrar\'s office?', answer: 'The registrar\'s office is located on the 2nd floor of the Administration Building, Room 201.', is_active: true, updated_at: new Date(Date.now() - 86400000).toISOString() },
      { id: 3, category: 'Facilities', question: 'How do I book a meeting room?', answer: 'You can book meeting rooms through the student portal or by visiting the facilities office in the Main Building.', is_active: true, updated_at: new Date(Date.now() - 172800000).toISOString() },
      { id: 4, category: 'Navigation', question: 'Where is the library?', answer: 'The University Library is located in Building C, accessible from the main campus entrance.', is_active: true, updated_at: new Date(Date.now() - 259200000).toISOString() },
      { id: 5, category: 'IT Support', question: 'How do I connect to campus WiFi?', answer: 'Connect to "CampusNet" network using your student ID as username and your password.', is_active: false, updated_at: new Date(Date.now() - 345600000).toISOString() }
    ]
  }
}

async function saveFaq() {
  try {
    const category = form.value.category === '_new' ? newCategory.value : form.value.category
    const data = { ...form.value, category }
    
    if (showEditModal.value) {
      await api.put(`/faq/${form.value.id}/`, data)
    } else {
      await api.post('/faq/', data)
    }
    closeModal()
    loadFaqs()
  } catch (e) {
    console.error('Failed to save FAQ:', e)
    showToast('Failed to save FAQ', 'error')
  }
}

async function toggleActive(faq) {
  try {
    await api.patch(`/faq/${faq.id}/`, { is_active: !faq.is_active })
    faq.is_active = !faq.is_active
  } catch (e) {
    console.error('Failed to toggle status:', e)
  }
}

async function deleteFaq() {
  try {
    await api.delete(`/faq/${faqToDelete.value.id}/`)
    showDeleteModal.value = false
    loadFaqs()
  } catch (e) {
    console.error('Failed to delete FAQ:', e)
  }
}

onMounted(() => {
  loadFaqs()
  loadSuggestions()
  loadAnalytics()
})

// FAQ Maker AI Methods
async function loadSuggestions() {
  loadingSuggestions.value = true
  try {
    const res = await api.get(`/chatbot/faq-suggestions/?status=${suggestionTab.value}`)
    suggestions.value = res.data.map(s => ({
      ...s,
      editAnswer: s.suggested_answer,
      editKeywords: s.keywords,
      editCategory: s.category
    }))
  } catch (error) {
    console.error('Error loading suggestions:', error)
  } finally {
    loadingSuggestions.value = false
  }
}

async function loadAnalytics() {
  try {
    // Use Django backend for analytics (reliable)
    const res = await api.get(`/chatbot/analytics/?days=${analyticsDays.value}`)
    analytics.value = res.data
  } catch (error) {
    console.error('Error loading analytics:', error)
    analytics.value = null
  }
}

async function runAnalysis() {
  isAnalyzing.value = true
  analysisResult.value = null
  
  try {
    const res = await api.post('/chatbot/faq-maker/analyze/', {
      days: analyzeDays.value,
      min_query_count: minQueryCount.value,
      similarity_threshold: similarityThreshold.value
    })
    
    analysisResult.value = {
      type: res.data.suggestions_created > 0 ? 'success' : 'info',
      message: res.data.message
    }
    
    await Promise.all([
      loadSuggestions(),
      loadAnalytics()
    ])
  } catch (error) {
    analysisResult.value = {
      type: 'error',
      message: error.response?.data?.error || 'Analysis failed. Please try again.'
    }
  } finally {
    isAnalyzing.value = false
  }
}

function toggleExpand(id) {
  expandedSuggestion.value = expandedSuggestion.value === id ? null : id
}

async function saveSuggestionEdits(suggestion) {
  try {
    await api.put(`/chatbot/faq-suggestions/${suggestion.id}/`, {
      suggested_answer: suggestion.editAnswer,
      keywords: suggestion.editKeywords,
      category: suggestion.editCategory
    })
    suggestion.suggested_answer = suggestion.editAnswer
    suggestion.keywords = suggestion.editKeywords
    suggestion.category = suggestion.editCategory
    showToast('Changes saved', 'success')
  } catch (error) {
    console.error('Error saving edits:', error)
    showToast('Failed to save changes', 'error')
  }
}

async function approveSuggestion(suggestion) {
  try {
    // Save any pending edits first
    if (suggestion.editAnswer !== suggestion.suggested_answer ||
        suggestion.editKeywords !== suggestion.keywords ||
        suggestion.editCategory !== suggestion.category) {
      await saveSuggestionEdits(suggestion)
    }
    
    await api.post(`/chatbot/faq-suggestions/${suggestion.id}/approve/`, {
      action: 'approve'
    })
    
    suggestions.value = suggestions.value.filter(s => s.id !== suggestion.id)
    await Promise.all([loadFaqs(), loadAnalytics()])
    showToast('FAQ created successfully!', 'success')
  } catch (error) {
    console.error('Error approving suggestion:', error)
    showToast('Failed to approve suggestion', 'error')
  }
}

function showRejectDialogFn(suggestion) {
  rejectSuggestion.value = suggestion
  rejectNote.value = ''
  showRejectDialog.value = true
}

async function confirmReject() {
  if (!rejectSuggestion.value) return
  
  try {
    await api.post(`/chatbot/faq-suggestions/${rejectSuggestion.value.id}/approve/`, {
      action: 'reject',
      review_note: rejectNote.value
    })
    
    suggestions.value = suggestions.value.filter(s => s.id !== rejectSuggestion.value.id)
    showRejectDialog.value = false
    rejectSuggestion.value = null
    await loadAnalytics()
    showToast('Suggestion rejected', 'success')
  } catch (error) {
    console.error('Error rejecting suggestion:', error)
    showToast('Failed to reject suggestion', 'error')
  }
}

// AI Generate Answer for new FAQs
async function generateAiAnswer() {
  if (!form.value.question) {
    showToast('Please enter a question first', 'error')
    return
  }
  
  isGeneratingAnswer.value = true
  
  try {
    // Call the chatbot API to generate an answer
    const res = await fetch('/chatbot-api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: form.value.question,
        campus_context: true,
        system_prompt: 'You are a helpful SEAIT campus guide. Provide a clear, concise, and accurate answer. Keep it under 150 words and be friendly.'
      })
    })
    
    if (!res.ok) throw new Error('Failed to generate answer')
    
    const data = await res.json()
    form.value.answer = data.reply || data.response || 'Could not generate answer. Please try again.'
    
    showToast('✨ AI answer generated! I learn from campus data to give you the best responses.', 'success')
  } catch (error) {
    console.error('Error generating AI answer:', error)
    showToast('Failed to generate AI answer. Please try again.', 'error')
  } finally {
    isGeneratingAnswer.value = false
  }
}

// Watch for tab changes
watch(suggestionTab, () => {
  loadSuggestions()
})

watch(activeTab, (newTab) => {
  if (newTab === 'ai') {
    loadSuggestions()
  } else if (newTab === 'analytics') {
    loadAnalytics()
  }
})

// Load data on mount
onMounted(() => {
  loadFaqs()
  loadSuggestions()
  loadAnalytics()
})
</script>

<style scoped>
.adminfaq-section { padding: 0; font-family: var(--font-primary); max-width: 1400px; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  padding: 14px 20px;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  min-width: 100px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary);
}

.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.category-btn {
  padding: 8px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-btn:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.category-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 500px;
  padding: 12px 16px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 20px;
}

.search-bar .material-icons {
  font-size: 20px;
  color: var(--color-text-hint);
}

.search-bar input {
  flex: 1;
  border: none;
  background: transparent;
  font-family: var(--font-primary);
  font-size: var(--text-base);
  color: var(--color-text-primary);
  outline: none;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.faq-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 20px;
  transition: all 0.2s ease;
}

.faq-card:hover {
  box-shadow: var(--shadow-sm);
}

.faq-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-tag {
  padding: 4px 12px;
  background: var(--color-primary-light);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-primary);
}

.faq-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-icon.btn-danger:hover {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.btn-icon .material-icons {
  font-size: 18px;
}

.faq-question {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.faq-answer {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
}

.faq-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

/* AI Generate Button Styles */
.ai-generate-wrapper {
  position: relative;
}

.btn-ai-generate {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark, #f57c00) 100%);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ai-generate:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.btn-ai-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ai-generate .material-icons {
  font-size: 18px;
}

.status-badge {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
}

.status-active { background: var(--color-success-bg); color: var(--color-success); }
.status-inactive { background: var(--color-surface-2); color: var(--color-text-hint); }

.updated-at {
  font-size: var(--text-xs);
  color: var(--color-text-hint);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  color: var(--color-text-hint);
}

.empty-state .material-icons {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-dialog {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-dialog.modal-sm {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-icon {
  font-size: 32px;
  color: var(--color-warning);
}

.btn-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-hint);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  outline: none;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--color-primary);
}

.new-category-input {
  margin-top: 8px;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.btn-secondary {
  padding: 10px 20px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--color-surface);
}

.btn-danger {
  padding: 10px 20px;
  background: var(--color-danger);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: #B71C1C;
}

.text-muted {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin-top: 8px;
}

/* Main Tabs */
.main-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: var(--color-surface-2);
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.tab-badge.warning {
  background: var(--color-primary);
  color: white;
}

/* AI Suggestions Tab */
.ai-suggestions-tab {
  animation: fadeIn 0.3s ease;
}

.analysis-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-group label {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.control-group input {
  width: 100px;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.analysis-result {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  margin-bottom: 20px;
}

.analysis-result.success {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.analysis-result.info {
  background: var(--color-info-bg);
  color: var(--color-info);
}

.analysis-result.error {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

/* Suggestion Tabs */
.suggestion-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.suggestion-tab {
  padding: 8px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-tab:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.suggestion-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

/* Suggestions List */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.2s ease;
}

.suggestion-card:hover {
  border-color: var(--color-primary);
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  cursor: pointer;
  background: var(--color-surface);
}

.suggestion-info {
  flex: 1;
}

.suggestion-info h4 {
  margin: 8px 0;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.suggestion-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.suggestion-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.suggestion-meta .material-icons {
  font-size: 14px;
}

.suggestion-actions {
  display: flex;
  gap: 8px;
}

.suggestion-details {
  padding: 16px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg);
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section label {
  display: block;
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.detail-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.answer-text {
  padding: 12px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  white-space: pre-wrap;
  font-size: var(--text-sm);
}

.source-queries {
  list-style: none;
  padding: 0;
  margin: 0;
}

.source-queries li {
  padding: 8px 12px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  font-style: italic;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.btn-icon.success {
  color: var(--color-success);
}

.btn-icon.success:hover {
  background: var(--color-success-bg);
  border-color: var(--color-success);
}

/* Analytics Tab */
.analytics-tab {
  animation: fadeIn 0.3s ease;
}

.analytics-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.analytics-filters {
  display: flex;
  gap: 8px;
}

.analytics-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.metric-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 16px;
  text-align: center;
  border-left: 4px solid var(--color-border);
}

.metric-card.success {
  border-left-color: var(--color-success);
}

.metric-card.danger {
  border-left-color: var(--color-danger);
}

.metric-card.warning {
  border-left-color: var(--color-warning);
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.metric-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.metric-sub {
  font-size: var(--text-xs);
  color: var(--color-success);
  margin-top: 4px;
}

.analytics-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 16px;
}

.analytics-section h4 {
  margin: 0 0 12px 0;
  font-size: var(--text-base);
  color: var(--color-text-primary);
}

.mode-breakdown {
  display: flex;
  gap: 24px;
}

.mode-item {
  display: flex;
  gap: 8px;
  font-size: var(--text-sm);
}

.mode-label {
  color: var(--color-text-secondary);
}

.mode-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.unanswered-list, .top-faqs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.unanswered-item, .top-faq-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.query-rank, .faq-rank {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
}

.query-text, .faq-question-text {
  flex: 1;
  font-size: var(--text-sm);
}

.query-count, .faq-usage {
  font-size: var(--text-xs);
  color: var(--color-text-hint);
}

/* Loading & Empty States */
.loading-state {
  text-align: center;
  padding: 40px;
  color: var(--color-text-hint);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-surface-2);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.empty-state .hint {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: 8px;
}

/* Category Badge */
.category-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
}

.category-badge.location { background: #e3f2fd; color: #1976d2; }
.category-badge.schedule { background: #f3e5f5; color: #7b1fa2; }
.category-badge.academic { background: #e8f5e9; color: #388e3c; }
.category-badge.services { background: #fff3e0; color: #f57c00; }
.category-badge.general { background: #f5f5f5; color: #616161; }

/* Reject Dialog */
.reject-dialog textarea {
  width: 100%;
  margin-top: 12px;
}

/* Form Elements */
.admin-input, .admin-select, .admin-textarea {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  background: var(--color-bg);
  color: var(--color-text-primary);
}

.admin-input:focus, .admin-select:focus, .admin-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.admin-textarea {
  width: 100%;
  resize: vertical;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-faq-section {
    padding: 12px;
    min-width: auto;
  }
  
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .admin-header h1 {
    font-size: var(--text-lg);
  }
  
  .admin-actions {
    width: 100%;
  }
  
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
  
  .faq-header {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .faq-actions {
    margin-left: auto;
  }
  
  .faq-card {
    padding: 12px;
  }
  
  .faq-question {
    font-size: var(--text-sm);
  }
  
  .faq-answer {
    font-size: var(--text-xs);
  }
  
  .modal-overlay {
    padding: 16px;
  }
  
  .modal-content {
    max-height: 90vh;
    width: 100%;
    max-width: 100%;
    margin: 0;
  }
  
  .main-tabs {
    flex-wrap: wrap;
  }
  
  .analysis-controls {
    flex-direction: column;
  }
  
  .control-group input {
    width: 100%;
  }
  
  .detail-row {
    grid-template-columns: 1fr;
  }
  
  .suggestion-header {
    flex-direction: column;
  }
  
  .suggestion-actions {
    margin-top: 12px;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .search-bar input {
    font-size: 16px; /* Prevent iOS zoom */
  }
  
  .admin-textarea,
  .admin-input,
  .admin-select {
    font-size: 16px; /* Prevent iOS zoom */
  }
}
</style>
