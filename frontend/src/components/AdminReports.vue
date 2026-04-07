<template>
  <div class="admin-reports">
    <!-- Most Picked FAQs Section -->
    <div class="report-card">
      <div class="card-header">
        <div class="header-title">
          <span class="material-icons" style="color: #3F51B5;">question_answer</span>
          <h3>Most Picked FAQs</h3>
        </div>
      </div>
      <div class="faq-list">
        <div v-for="(faq, index) in sortedFaqs" :key="index" class="faq-item">
          <div class="faq-rank">{{ index + 1 }}</div>
          <div class="faq-content">
            <div class="faq-question">{{ faq.question }}</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getFaqPercentage(faq.count) + '%', background: getProgressColor(index) }"></div>
            </div>
          </div>
          <div class="faq-count">
            <span class="count-badge">{{ faq.count }} ({{ getFaqPercentage(faq.count) }}%)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- User Ratings & Comments Section -->
    <div class="report-card">
      <div class="card-header">
        <div class="header-title">
          <span class="material-icons" style="color: #FFC107;">star</span>
          <h3>User Ratings & Comments ({{ ratings.length }})</h3>
        </div>
      </div>
      <div class="ratings-summary">
        <div class="average-rating">
          <div class="big-rating">{{ averageRating.toFixed(1) }}</div>
          <div class="stars">
            <span v-for="n in 5" :key="n" class="material-icons">
              {{ n <= Math.round(averageRating) ? 'star' : 'star_border' }}
            </span>
          </div>
          <div class="rating-count">{{ ratings.length }} reviews</div>
        </div>
        <div class="rating-breakdown">
          <div v-for="n in 5" :key="n" class="breakdown-row">
            <span class="star-label">{{ 6 - n }} star</span>
            <div class="breakdown-bar">
              <div class="breakdown-fill" :style="{ width: getStarPercentage(6 - n) + '%' }"></div>
            </div>
            <span class="breakdown-count">{{ getStarCount(6 - n) }}</span>
          </div>
        </div>
      </div>
      <div class="ratings-list">
        <div v-if="ratings.length === 0" class="empty-state">No ratings yet</div>
        <div v-for="rating in displayedRatings" :key="rating.id" class="rating-item">
          <div class="rating-avatar">
            <span class="material-icons">person</span>
          </div>
          <div class="rating-content">
            <div class="rating-stars">
              <span v-for="n in 5" :key="n" class="material-icons star-icon">
                {{ n <= rating.rating ? 'star' : 'star_border' }}
              </span>
            </div>
            <div class="rating-comment">{{ rating.comment || 'No comment' }}</div>
            <div class="rating-category" v-if="rating.category">Category: {{ rating.category }}</div>
          </div>
          <div class="rating-date">{{ formatDate(rating.created_at) }}</div>
        </div>
      </div>
      <div v-if="ratings.length > 10" class="show-more">
        <span class="more-text">+ {{ ratings.length - 10 }} more ratings</span>
      </div>
    </div>

    <!-- Usage Statistics -->
    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-icon blue">
          <span class="material-icons">chat</span>
        </div>
        <div class="stat-data">
          <div class="stat-number">{{ stats.chatbotQueries }}</div>
          <div class="stat-label">Chatbot Queries</div>
        </div>
      </div>
      <div class="stat-box">
        <div class="stat-icon green">
          <span class="material-icons">navigation</span>
        </div>
        <div class="stat-data">
          <div class="stat-number">{{ stats.navigationUses }}</div>
          <div class="stat-label">Navigation Uses</div>
        </div>
      </div>
      <div class="stat-box">
        <div class="stat-icon orange">
          <span class="material-icons">qr_code_scanner</span>
        </div>
        <div class="stat-data">
          <div class="stat-number">{{ stats.qrScans }}</div>
          <div class="stat-label">QR Scans</div>
        </div>
      </div>
      <div class="stat-box">
        <div class="stat-icon purple">
          <span class="material-icons">map</span>
        </div>
        <div class="stat-data">
          <div class="stat-number">{{ stats.mapViews }}</div>
          <div class="stat-label">Map Views</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api.js'

const ratings = ref([])
const faqCounts = ref({
  'Where is the library?': 45,
  'How do I navigate to CL1?': 38,
  'What time does the cafeteria open?': 32,
  'Where is the registrar office?': 28,
  'How many floors in MST Building?': 24,
  'Where can I find CR1?': 20,
  'Is there WiFi in the campus?': 18,
  'Where is the parking area?': 15,
})

const stats = ref({
  chatbotQueries: 1247,
  navigationUses: 856,
  qrScans: 432,
  mapViews: 2103
})

const sortedFaqs = computed(() => {
  return Object.entries(faqCounts.value)
    .map(([question, count]) => ({ question, count }))
    .sort((a, b) => b.count - a.count)
})

const averageRating = computed(() => {
  if (ratings.value.length === 0) return 0
  return ratings.value.reduce((sum, r) => sum + (r.rating || 0), 0) / ratings.value.length
})

const displayedRatings = computed(() => {
  return ratings.value.slice(0, 10)
})

onMounted(async () => {
  try {
    const res = await api.get('/feedback/')
    ratings.value = res.data || []
  } catch (err) {
    console.log('Using mock ratings data')
    ratings.value = [
      { id: 1, rating: 5, comment: 'Great app! Very helpful for navigating campus.', category: 'General', created_at: '2024-03-25' },
      { id: 2, rating: 4, comment: 'Good but could use more building details.', category: 'Map Accuracy', created_at: '2024-03-24' },
      { id: 3, rating: 5, comment: 'The chatbot is amazing! Answered all my questions.', category: 'AI Chatbot', created_at: '2024-03-23' },
      { id: 4, rating: 5, comment: 'Navigation feature saved me so much time!', category: 'Navigation', created_at: '2024-03-22' },
      { id: 5, rating: 3, comment: 'App is good but sometimes slow to load.', category: 'Bug Report', created_at: '2024-03-21' },
      { id: 6, rating: 5, comment: 'Love the QR scanner feature!', category: 'General', created_at: '2024-03-20' },
      { id: 7, rating: 4, comment: 'Very useful for new students.', category: 'General', created_at: '2024-03-19' },
      { id: 8, rating: 5, comment: 'Perfect campus guide!', category: 'General', created_at: '2024-03-18' },
    ]
  }
})

function getFaqPercentage(count) {
  const total = Object.values(faqCounts.value).reduce((a, b) => a + b, 0)
  return Math.round((count / total) * 100)
}

function getProgressColor(index) {
  const colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']
  return colors[index % colors.length]
}

function getStarCount(star) {
  return ratings.value.filter(r => r.rating === star).length
}

function getStarPercentage(star) {
  if (ratings.value.length === 0) return 0
  return Math.round((getStarCount(star) / ratings.value.length) * 100)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.substring(0, 10)
}
</script>

<style scoped>
.admin-reports {
  padding: 24px;
  max-width: 1400px;
}

.report-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 24px;
  overflow: hidden;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.header-title .material-icons {
  font-size: 28px;
}

/* FAQ List */
.faq-list {
  padding: 16px 24px;
}

.faq-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #E8EAF6;
  color: #3F51B5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.faq-content {
  flex: 1;
  min-width: 0;
}

.faq-question {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.progress-bar {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.faq-count {
  flex-shrink: 0;
}

.count-badge {
  padding: 4px 12px;
  background: #E8EAF6;
  color: #3F51B5;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* Ratings Summary */
.ratings-summary {
  display: flex;
  gap: 32px;
  padding: 24px;
  border-bottom: 1px solid #f5f5f5;
}

.average-rating {
  text-align: center;
  min-width: 120px;
}

.big-rating {
  font-size: 48px;
  font-weight: 700;
  color: #FFC107;
  line-height: 1;
}

.stars {
  display: flex;
  justify-content: center;
  gap: 2px;
  margin: 8px 0;
  color: #FFC107;
}

.stars .material-icons {
  font-size: 20px;
}

.rating-count {
  font-size: 13px;
  color: #888;
}

.rating-breakdown {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breakdown-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.star-label {
  width: 50px;
  font-size: 12px;
  color: #666;
  flex-shrink: 0;
}

.breakdown-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.breakdown-fill {
  height: 100%;
  background: #FFC107;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.breakdown-count {
  width: 30px;
  font-size: 12px;
  color: #666;
  text-align: right;
  flex-shrink: 0;
}

/* Ratings List */
.ratings-list {
  padding: 16px 24px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #888;
  font-size: 14px;
}

.rating-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 12px;
}

.rating-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #E3F2FD;
  color: #2196F3;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rating-avatar .material-icons {
  font-size: 20px;
}

.rating-content {
  flex: 1;
  min-width: 0;
}

.rating-stars {
  display: flex;
  gap: 2px;
  margin-bottom: 6px;
  color: #FFC107;
}

.star-icon {
  font-size: 16px;
}

.rating-comment {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.rating-category {
  font-size: 12px;
  color: #FF9800;
  background: #FFF3E0;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.rating-date {
  font-size: 11px;
  color: #888;
  flex-shrink: 0;
}

.show-more {
  text-align: center;
  padding: 12px;
  border-top: 1px solid #f5f5f5;
}

.more-text {
  font-size: 12px;
  color: #888;
  font-style: italic;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue { background: #E3F2FD; color: #2196F3; }
.stat-icon.green { background: #E8F5E9; color: #4CAF50; }
.stat-icon.orange { background: #FFF3E0; color: #FF9800; }
.stat-icon.purple { background: #F3E5F5; color: #9C27B0; }

.stat-icon .material-icons {
  font-size: 24px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-reports {
    padding: 12px;
  }
  
  .card-header,
  .faq-list,
  .ratings-list {
    padding: 16px;
  }
  
  .faq-item {
    gap: 12px;
  }
  
  .faq-question {
    font-size: 13px;
  }
  
  .ratings-summary {
    flex-direction: column;
    gap: 24px;
  }
  
  .average-rating {
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
  }
  
  .big-rating {
    font-size: 36px;
  }
  
  .rating-item {
    flex-direction: column;
    gap: 8px;
  }
  
  .rating-date {
    align-self: flex-end;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-box {
    padding: 16px;
  }
  
  .stat-number {
    font-size: 20px;
  }
}
</style>
