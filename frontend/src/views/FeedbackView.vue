<template>
  <div class="feedback-view">
    <!-- Top Bar -->
    <div class="feedback-top-bar">
      <button class="feedback-top-bar-icon-btn" @click="goBack">
        <span class="material-icons">arrow_back</span>
      </button>
      <div class="feedback-top-bar-title">Submit Feedback</div>
      <div style="width: 44px"></div>
    </div>

    <!-- Main Content -->
    <div class="feedback-main-content" v-if="!submitted">
      <div class="feedback-form">
        <!-- Star Rating -->
        <div class="feedback-rating-section">
          <h3 class="feedback-section-label">How would you rate your experience?</h3>
          <div class="feedback-star-rating">
            <button
              v-for="n in 5"
              :key="n"
              class="feedback-star-btn"
              :class="{ 'feedback-filled': n <= rating }"
              @click="rating = n"
            >
              <span class="material-icons">{{ n <= rating ? 'star' : 'star_border' }}</span>
            </button>
          </div>
          <p class="feedback-rating-text">{{ ratingText }}</p>
        </div>

        <!-- Category Chips -->
        <div class="feedback-category-section">
          <h3 class="feedback-section-label">What is this about?</h3>
          <div class="feedback-category-chips">
            <button
              v-for="cat in categories"
              :key="cat"
              class="feedback-chip"
              :class="{ 'feedback-selected': category === cat }"
              @click="category = cat"
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <!-- Comment Textarea -->
        <div class="feedback-comment-section">
          <h3 class="feedback-section-label">Additional comments (optional)</h3>
          <textarea
            v-model="comment"
            class="feedback-input-field feedback-comment-field"
            placeholder="Tell us more about your experience..."
            rows="4"
            @focus="scrollIntoView"
          ></textarea>
        </div>

        <!-- Location Selector -->
        <div class="feedback-location-section" v-if="category === 'Map Accuracy' || category === 'Navigation'">
          <h3 class="feedback-section-label">Related Facility/Room (Optional)</h3>
          <div class="feedback-select-wrapper">
            <select v-model="selectedLocation" class="feedback-input-field">
              <option value="">Select a location (optional)</option>
              <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
            </select>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="feedback-submit-section">
          <button
            class="feedback-btn feedback-btn-primary"
            :disabled="!rating"
            @click="submitFeedback"
          >
            <span v-if="isSubmitting" class="feedback-spinner"></span>
            <span v-else>Submit Feedback</span>
          </button>
          <p v-if="error" class="feedback-error-message">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Success Screen -->
    <div class="feedback-main-content" v-else>
      <div class="feedback-success-screen">
        <div class="feedback-success-icon">
          <span class="material-icons">check_circle</span>
        </div>
        <h2 class="feedback-success-title">Thank You!</h2>
        <p class="feedback-success-text">Your feedback helps us improve TechnoPath for everyone.</p>
        <button class="feedback-btn feedback-btn-primary" @click="goBack">
          Back to Home
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'
import db from '../services/db.js'

const router = useRouter()

// State
const rating = ref(0)
const category = ref('General')
const comment = ref('')
const isSubmitting = ref(false)
const submitted = ref(false)
const error = ref('')
const selectedLocation = ref('')

const locations = ['Main Gate', 'MST Building', 'JST Building', 'RST Building', 'Library', 'Registrar Office', 'Cafeteria', 'Gymnasium', 'CL1', 'CL2', 'CL3', 'CL4', 'CL5', 'CL6', 'CR1', 'CR2', 'CR3', 'CR4']

const categories = ['General', 'Map Accuracy', 'Navigation', 'AI Chatbot', 'Bug Report']

const ratingText = computed(() => {
  const texts = ['', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
  return texts[rating.value] || ''
})

// Methods
const goBack = () => {
  router.replace('/')
}

// Category mapping from UI display names to backend values
const categoryMap = {
  'General': 'general',
  'Map Accuracy': 'map_accuracy',
  'Navigation': 'navigation',
  'AI Chatbot': 'ai_chatbot',
  'Bug Report': 'bug_report'
}

const submitFeedback = async () => {
  if (!rating.value) return

  isSubmitting.value = true
  error.value = ''

  // API payload - only valid backend fields
  const apiPayload = {
    rating: rating.value,
    category: categoryMap[category.value] || 'general',
    comment: comment.value
  }

  // Local storage payload (includes UI-only fields)
  const localPayload = {
    rating: rating.value,
    category: category.value,
    comment: comment.value,
    location: selectedLocation.value,
    created_at: new Date().toISOString()
  }

  try {
    // Try to submit online first
    await api.post('/feedback/', apiPayload)
    submitted.value = true
  } catch (err) {
    // If offline, save to IndexedDB for later sync
    try {
      await db.feedback.add({
        ...localPayload,
        synced: 0
      })
      submitted.value = true
    } catch (dbErr) {
      error.value = 'Unable to submit feedback. Please try again.'
      console.error('Feedback submission failed:', dbErr)
    }
  } finally {
    isSubmitting.value = false
  }
}

// Fix keyboard overlap (Discrepancy E9)
const scrollIntoView = (e) => {
  setTimeout(() => {
    e.target.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 300) // Wait for keyboard to appear
}
</script>

<style>
/* Styles moved to external file: src/assets/feedback.css */
@import '../assets/feedback.css';
</style>
