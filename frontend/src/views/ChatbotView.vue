<template>
  <div class="chatbot-view">
    <!-- Header -->
    <header class="chatbot-header">
      <button class="chatbot-back-btn" @click="goBack">
        <span class="material-icons">arrow_back</span>
      </button>
      <div class="chatbot-header-content">
        <div class="chatbot-header-icon">
          <span class="material-icons">smart_toy</span>
        </div>
        <div class="chatbot-header-text">
          <h1>Campus Assistant</h1>
          <p class="chatbot-status">
            <span v-if="isOffline" class="status-offline">
              <span class="material-icons">wifi_off</span> Offline Mode
            </span>
            <span v-else-if="flaskConnected" class="status-ai">
              <span class="material-icons">psychology</span> AI Powered (GPT)
            </span>
            <span v-else class="status-basic">
              <span class="material-icons">chat</span> Connecting...
            </span>
          </p>
        </div>
      </div>
    </header>

    <!-- FAQ Section -->
    <div class="chatbot-faq-section" v-if="showFAQ">
      <h3 class="chatbot-faq-title">
        <span class="material-icons">help_outline</span>
        Frequently Asked Questions
      </h3>
      <div class="chatbot-faq-list">
        <button 
          v-for="faq in faqList" 
          :key="faq.question"
          class="chatbot-faq-item"
          @click="askQuestion(faq.question)"
        >
          <span class="material-icons">chat_bubble_outline</span>
          <span class="chatbot-faq-question-text">{{ faq.question }}</span>
        </button>
      </div>
    </div>

    <!-- Chat Messages -->
    <div class="chatbot-messages-container" ref="messagesContainer">
      <div v-for="(msg, index) in messages" :key="index" :class="['chatbot-message-wrapper', msg.type]">
        <div class="chatbot-message-avatar">
          <span class="material-icons">{{ msg.type === 'bot' ? 'smart_toy' : 'person' }}</span>
        </div>
        <div :class="['chatbot-message', msg.type]">
          <div class="chatbot-message-content">{{ msg.text }}</div>
          <div class="chatbot-message-meta">
            <span class="chatbot-message-time">{{ formatTime(msg.timestamp) }}</span>
            <span v-if="msg.source" class="chatbot-message-source">{{ msg.source }}</span>
          </div>
        </div>
      </div>
      <div v-if="isTyping" class="chatbot-message-wrapper bot typing">
        <div class="chatbot-message-avatar">
          <span class="material-icons">smart_toy</span>
        </div>
        <div class="chatbot-typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
      <div v-if="error" class="chatbot-error">
        <span class="material-icons">error_outline</span>
        {{ error }}
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="chatbot-quick-actions" v-if="showQuickActions">
      <button 
        v-for="action in quickActions" 
        :key="action"
        class="chatbot-quick-action-btn"
        @click="askQuestion(action)"
      >
        {{ action }}
      </button>
    </div>

    <!-- Input Area -->
    <div class="chatbot-input-area">
      <div class="chatbot-input-container">
        <button class="chatbot-attach-btn" @click="toggleFAQ">
          <span class="material-icons">{{ showFAQ ? 'close' : 'help_outline' }}</span>
        </button>
        <input 
          v-model="userInput" 
          @keyup.enter="sendMessage"
          :placeholder="isOffline ? 'Offline mode - using cached responses' : 'Ask me anything about SEAIT...'"
          type="text"
          ref="inputField"
          :disabled="isTyping"
        />
        <button class="chatbot-send-btn" @click="sendMessage" :disabled="!userInput.trim() || isTyping">
          <span class="material-icons">{{ isTyping ? 'hourglass_top' : 'send' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import aiChatbot from '../services/aiChatbot.js'
import { isOnline } from '../services/sync.js'
import { getFAQEntries } from '../services/offlineData.js'

const router = useRouter()

const messages = ref([
  { 
    type: 'bot', 
    text: "Hello! I'm your SEAIT Campus Assistant. I can help you find buildings, rooms, navigate the campus, and answer questions about SEAIT. What would you like to know?",
    timestamp: new Date(),
    source: ''
  }
])
const userInput = ref('')
const isTyping = ref(false)
const showFAQ = ref(true)
const messagesContainer = ref(null)
const inputField = ref(null)
const error = ref('')
const faqList = ref([])

const isOffline = computed(() => !isOnline())
const flaskConnected = ref(false)
const isAIEnabled = computed(() => {
  const status = aiChatbot.getStatus()
  return status.isAIEnabled
})

// Check Flask connection on mount
async function checkFlaskConnection() {
  try {
    const response = await fetch(`${import.meta.env.VITE_FLASK_CHATBOT_URL || 'http://localhost:5000'}/health`, {
      method: 'GET',
      mode: 'cors'
    })
    flaskConnected.value = response.ok
  } catch {
    flaskConnected.value = false
  }
}

const quickActions = ref([
  'Where is CL1?',
  'MST Building info',
  'Library hours',
  'How do I get to the Registrar?'
])

const showQuickActions = ref(true)

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function toggleFAQ() {
  showFAQ.value = !showFAQ.value
}

function goBack() {
  router.back()
}

function askQuestion(question) {
  userInput.value = question
  sendMessage()
  showFAQ.value = false
}

async function loadFAQ() {
  try {
    const faqData = await getFAQEntries()
    if (faqData.data && faqData.data.length > 0) {
      faqList.value = faqData.data.slice(0, 8).map(f => ({
        question: f.question,
        answer: f.answer
      }))
    } else {
      // Fallback FAQ
      faqList.value = [
        { question: 'Where is the MST Building?', answer: 'Center of campus, 4 floors with classrooms and computer labs' },
        { question: 'Where is the comfort room?', answer: 'Available on every floor near stairwells in all buildings' },
        { question: 'How do I navigate the campus?', answer: 'Use the Navigate tab for turn-by-turn directions' },
        { question: 'Where is the CICT office?', answer: '2nd floor MST Building, near computer labs' },
        { question: 'What are the library hours?', answer: 'Mon-Fri 8AM-6PM, Sat 8AM-12PM' },
        { question: 'Where is the cafeteria?', answer: 'Between MST Building and Gymnasium, open 7AM-6PM' },
        { question: 'What rooms are in JST Building?', answer: 'Lecture rooms (1F), labs (2F), seminar rooms (3F)' },
        { question: 'Where is the Registrar Office?', answer: '1st floor RST Building, Mon-Fri 8AM-5PM' }
      ]
    }
  } catch (err) {
    console.log('[Chatbot] Using fallback FAQ')
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || isTyping.value) return

  error.value = ''
  
  // Add user message
  const userMessage = userInput.value.trim()
  messages.value.push({ 
    type: 'user', 
    text: userMessage,
    timestamp: new Date()
  })
  
  userInput.value = ''
  isTyping.value = true
  showQuickActions.value = false
  scrollToBottom()

  try {
    // Get AI response
    const result = await aiChatbot.sendMessage(userMessage)
    
    isTyping.value = false
    
    // Determine source label
    let sourceLabel = ''
    if (result.isOffline) {
      sourceLabel = 'Offline'
    } else if (result.source === 'ai') {
      sourceLabel = 'AI'
    } else if (result.source === 'fallback') {
      sourceLabel = 'Cached'
    }
    
    messages.value.push({ 
      type: 'bot', 
      text: result.reply,
      timestamp: new Date(),
      source: sourceLabel
    })
  } catch (err) {
    isTyping.value = false
    error.value = 'Sorry, I had trouble processing that. Please try again.'
    console.error('[Chatbot] Error:', err)
    
    // Add fallback message
    messages.value.push({ 
      type: 'bot', 
      text: "I'm having trouble connecting right now. For campus info, try the Map and Navigate tabs, or check the FAQ section above.",
      timestamp: new Date(),
      source: 'Error'
    })
  }
  
  scrollToBottom()
}

onMounted(async () => {
  inputField.value?.focus()
  await checkFlaskConnection()
  await loadFAQ()
  await aiChatbot.initChatHistory()
})
</script>

<style>
@import '../assets/chatbot.css';
</style>
