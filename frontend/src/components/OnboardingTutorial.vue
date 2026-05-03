<template>
  <div v-if="isVisible" class="onboarding-overlay">
    <!-- Backdrop with cutout for highlighted element -->
    <div class="onboarding-backdrop" @click="skipTutorial"></div>
    
    <!-- Tutorial Card -->
    <div class="onboarding-card" :class="`step-${currentStep}`">
      <!-- Progress dots -->
      <div class="onboarding-progress">
        <div
          v-for="(_, index) in steps"
          :key="index"
          class="onboarding-dot"
          :class="{ active: index === currentStep }"
        ></div>
      </div>

      <!-- Step Content -->
      <div class="onboarding-content-wrapper">
        <Transition :name="transitionName" mode="out-in">
          <div :key="currentStep" class="onboarding-content">
            <div class="onboarding-icon">
              <span class="material-icons">{{ steps[currentStep].icon }}</span>
            </div>
            <h2 class="onboarding-title">{{ steps[currentStep].title }}</h2>
            <p class="onboarding-description">{{ steps[currentStep].description }}</p>
          </div>
        </Transition>
      </div>

      <!-- Actions -->
      <div class="onboarding-actions">
        <button v-if="currentStep > 0" class="onboarding-btn-secondary" @click="prevStep">
          Back
        </button>
        <button class="onboarding-btn-primary" @click="nextStep">
          {{ isLastStep ? 'Get Started' : 'Next' }}
        </button>
      </div>

      <!-- Skip option -->
      <button class="onboarding-skip" @click="skipTutorial">
        Skip tutorial
      </button>
    </div>

    <!-- Feature highlights (positioned absolutely based on step) -->
    <div
      v-if="steps[currentStep].highlight"
      class="onboarding-highlight"
      :style="getHighlightStyle()"
    >
      <div class="highlight-pulse"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'

const emit = defineEmits(['complete', 'skip'])

const currentStep = ref(0)
const isVisible = ref(false)
const transitionName = ref('slide-left')

const steps = [
  {
    icon: 'map',
    title: 'Welcome to TechnoPath',
    description: 'Your interactive SEAIT campus guide. Navigate buildings, find rooms, and explore the campus with ease.',
    highlight: null
  },
  {
    icon: 'search',
    title: 'Quick Search',
    description: 'Type any building, room, or facility name in the search bar above to find it instantly.',
    highlight: 'search'
  },
  {
    icon: 'explore',
    title: 'Interactive Map',
    description: 'The embedded map lets you zoom and pan across the full SEAIT campus. Tap a marker to get details.',
    highlight: 'map'
  },
  {
    icon: 'directions',
    title: 'Turn-by-Turn Navigation',
    description: 'Use the Navigate tab in the bottom bar to get step-by-step directions between any two campus points.',
    highlight: 'navigate'
  },
  {
    icon: 'chat',
    title: 'AI Campus Assistant',
    description: 'Have a question about campus? Tap the chatbot button to ask our AI assistant — it works offline too.',
    highlight: 'chatbot'
  },
  {
    icon: 'campaign',
    title: 'Campus Announcements',
    description: 'Stay updated with announcements from departments and administrators right on your home screen.',
    highlight: null
  }
]

const isLastStep = computed(() => currentStep.value === steps.length - 1)

// Re-calculate highlight position after DOM settles on step change
watch(currentStep, async () => {
  await nextTick()
  // Force re-render of highlight by touching a reactive value
  // (getHighlightStyle is called reactively in the template)
})

const getHighlightStyle = () => {
  const key = steps[currentStep.value].highlight
  if (!key) return {}

  // Map each step key to a CSS selector that targets the actual DOM element
  const selectors = {
    search:    '.home-search-input-wrapper, .unified-search-input-wrapper',
    map:       '.seait-embedded-map, .map-container',
    favorites: '.desktop-fab-btn.desktop-ratings-btn, .favorites-view, [href="/favorites"]',
    chatbot:   '.desktop-fab-btn.desktop-chatbot-btn, [href="/chatbot"]',
    navigate:  '[href="/navigate"], .app-nav-item[to="/navigate"]',
  }

  const selector = selectors[key]
  if (!selector) return {}

  // Try each comma-separated selector until one matches
  const candidates = selector.split(',').map(s => s.trim())
  let el = null
  for (const s of candidates) {
    el = document.querySelector(s)
    if (el) break
  }

  if (!el) {
    // Element not found: hide the highlight gracefully instead of misplacing it
    return { display: 'none' }
  }

  const rect = el.getBoundingClientRect()
  const padding = 8

  return {
    position: 'fixed',
    top:    `${rect.top    - padding}px`,
    left:   `${rect.left   - padding}px`,
    width:  `${rect.width  + padding * 2}px`,
    height: `${rect.height + padding * 2}px`,
  }
}

const nextStep = () => {
  if (isLastStep.value) {
    completeTutorial()
  } else {
    transitionName.value = 'slide-left'
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    transitionName.value = 'slide-right'
    currentStep.value--
  }
}

const skipTutorial = () => {
  localStorage.setItem('tp_onboarding_completed', 'true')
  localStorage.setItem('tp_onboarding_skipped', 'true')
  isVisible.value = false
  emit('skip')
}

const completeTutorial = () => {
  localStorage.setItem('tp_onboarding_completed', 'true')
  isVisible.value = false
  emit('complete')
}

// Check if should show onboarding
onMounted(() => {
  const completed = localStorage.getItem('tp_onboarding_completed')
  const skipped = localStorage.getItem('tp_onboarding_skipped')
  
  if (!completed && !skipped) {
    // Small delay to let the app render first
    setTimeout(() => {
      isVisible.value = true
    }, 500)
  }
})

// Expose methods for manual triggering
defineExpose({
  start: () => {
    currentStep.value = 0
    isVisible.value = true
  },
  reset: () => {
    localStorage.removeItem('tp_onboarding_completed')
    localStorage.removeItem('tp_onboarding_skipped')
    currentStep.value = 0
    isVisible.value = true
  }
})
</script>

<style>
@import '../assets/onboarding.css';
</style>
