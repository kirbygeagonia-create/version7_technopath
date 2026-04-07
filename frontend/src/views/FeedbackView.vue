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
          ></textarea>
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

const categories = ['General', 'Map Accuracy', 'Navigation', 'AI Chatbot', 'Bug Report']

const ratingText = computed(() => {
  const texts = ['', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
  return texts[rating.value] || ''
})

// Methods
const goBack = () => {
  router.push('/')
}

const submitFeedback = async () => {
  if (!rating.value) return

  isSubmitting.value = true
  error.value = ''

  const feedbackData = {
    rating: rating.value,
    category: category.value,
    comment: comment.value,
    created_at: new Date().toISOString()
  }

  try {
    // Try to submit online first
    await api.post('/feedback/', feedbackData)
    submitted.value = true
  } catch (err) {
    // If offline, save to IndexedDB for later sync
    try {
      await db.feedback.add({
        ...feedbackData,
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
</script>

<style>
/* Styles moved to external file: src/assets/feedback.css */
@import '../assets/feedback.css';
</style>
