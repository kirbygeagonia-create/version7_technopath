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
          <p>Ask me about SEAIT campus</p>
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
          <div class="chatbot-message-time">{{ formatTime(msg.timestamp) }}</div>
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
          placeholder="Type your question..."
          type="text"
          ref="inputField"
        />
        <button class="chatbot-send-btn" @click="sendMessage" :disabled="!userInput.trim()">
          <span class="material-icons">send</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const messages = ref([
  { 
    type: 'bot', 
    text: 'Hello! I\'m your SEAIT Campus Assistant. I can help you find buildings, rooms, and answer common questions about our campus. What would you like to know?',
    timestamp: new Date()
  }
])
const userInput = ref('')
const isTyping = ref(false)
const showFAQ = ref(true)
const messagesContainer = ref(null)
const inputField = ref(null)

const goBack = () => router.back()

// FAQ Data from Flutter archive
const faqList = ref([
  { question: 'Where is the MST Building?', answer: 'The MST (Main Science and Technology) Building is located at the center of the campus. It houses computer labs CL1, CL2 on the 1st floor and CL5, CL6 on the 2nd floor, as well as lecture rooms and administrative offices.' },
  { question: 'Where is the comfort room?', answer: 'Comfort rooms are available in all campus buildings. The main restrooms are located on each floor of MST, JST, and RST buildings, near the stairwells.' },
  { question: 'How do I navigate the campus?', answer: 'You can use the Navigate tab in this app to find routes between buildings and rooms. The campus has 3 main buildings: MST, JST, and RST arranged in a central layout.' },
  { question: 'Where is the CICT office?', answer: 'The CICT (College of Information and Communications Technology) office is located in the MST Building, 2nd floor, near the computer labs.' },
  { question: 'What are the library hours?', answer: 'The library is open Monday to Friday from 8:00 AM to 6:00 PM, and Saturday from 8:00 AM to 12:00 PM. It\'s closed on Sundays and holidays.' },
  { question: 'Where is the cafeteria?', answer: 'The cafeteria is located near the main entrance of the campus, between the MST Building and the Gymnasium. It serves meals from 7:00 AM to 6:00 PM.' },
  { question: 'What rooms are in JST Building?', answer: 'JST (Junior Science and Technology) Building contains lecture rooms JST101-JST102 on the 1st floor, laboratories JST201-JST202 on the 2nd floor, and seminar rooms on the 3rd floor.' },
  { question: 'Where is the Registrar Office?', answer: 'The Registrar Office is located on the ground floor of the MST Building, near the main entrance. Office hours are 8:00 AM to 5:00 PM, Monday to Friday.' }
])

const quickActions = ref([
  'Find CL1',
  'MST Building',
  'Library hours',
  'Registrar location'
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

function askQuestion(question) {
  userInput.value = question
  sendMessage()
  showFAQ.value = false
}

function sendMessage() {
  if (!userInput.value.trim()) return

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

  // Simulate bot thinking and response
  setTimeout(() => {
    isTyping.value = false
    const response = generateResponse(userMessage)
    messages.value.push({ 
      type: 'bot', 
      text: response,
      timestamp: new Date()
    })
    scrollToBottom()
  }, 1000 + Math.random() * 1000)
}

function generateResponse(userMessage) {
  const lowerMsg = userMessage.toLowerCase()
  
  // Check FAQ first
  for (const faq of faqList.value) {
    if (lowerMsg.includes(faq.question.toLowerCase().substring(0, 10))) {
      return faq.answer
    }
  }
  
  // Building queries
  if (lowerMsg.includes('mst') || lowerMsg.includes('main science')) {
    return 'The MST Building is our main academic building with 4 floors. It houses Computer Labs CL1-CL2 on the 1st floor, CL5-CL6 on the 2nd floor, Classroom CR1-CR2, and various administrative offices including the Registrar.'
  }
  
  if (lowerMsg.includes('jst') || lowerMsg.includes('junior science')) {
    return 'JST Building has 4 floors with lecture rooms on the 1st floor (JST101-JST102), laboratories on the 2nd floor (JST201-JST202), and seminar rooms on the 3rd floor.'
  }
  
  if (lowerMsg.includes('rst') || lowerMsg.includes('research')) {
    return 'RST Building is our Research Science and Technology building with 3 floors. It contains research labs, graduate studies areas, specialized equipment, and conference rooms.'
  }
  
  // Room queries
  if (lowerMsg.includes('cl1') || lowerMsg.includes('cl2') || lowerMsg.includes('cl5') || lowerMsg.includes('cl6')) {
    return 'Computer Labs CL1 and CL2 are on the 1st floor of MST Building. CL5 and CL6 are on the 2nd floor. Each lab has 30 PCs available for student use.'
  }
  
  if (lowerMsg.includes('cr1') || lowerMsg.includes('cr2')) {
    return 'Classrooms CR1 and CR2 are located on the 1st floor of MST Building, each with a capacity of 35 seats.'
  }
  
  if (lowerMsg.includes('library')) {
    return 'The Library is located near the main campus entrance. It has 2 floors with book lending, study areas, digital resources, and reading rooms. Open Mon-Fri 8AM-6PM, Sat 8AM-12PM.'
  }
  
  if (lowerMsg.includes('registrar')) {
    return 'The Registrar Office is on the ground floor of MST Building. They handle enrollment services, academic records, and transcript requests. Office hours: Mon-Fri 8AM-5PM.'
  }
  
  if (lowerMsg.includes('canteen') || lowerMsg.includes('cafeteria')) {
    return 'Our Cafeteria is located between MST Building and the Gymnasium. It serves meals, snacks, and beverages from 7:00 AM to 6:00 PM daily.'
  }
  
  if (lowerMsg.includes('gym') || lowerMsg.includes('gymnasium')) {
    return 'The Gymnasium features a basketball court, volleyball court, fitness equipment, locker rooms, and hosts various sports events. It\'s located near the cafeteria.'
  }
  
  if (lowerMsg.includes('comfort room') || lowerMsg.includes('restroom') || lowerMsg.includes('cr') || lowerMsg.includes('bathroom')) {
    return 'Comfort rooms are available on every floor of all campus buildings (MST, JST, RST). They\'re typically located near the stairwells for easy access.'
  }
  
  if (lowerMsg.includes('cict') || lowerMsg.includes('office')) {
    return 'The CICT (College of Information and Communications Technology) office is on the 2nd floor of MST Building, near the computer labs area.'
  }
  
  // Greetings
  if (lowerMsg.includes('hello') || lowerMsg.includes('hi') || lowerMsg.includes('hey')) {
    return 'Hello! Welcome to SEAIT Campus. I can help you find buildings, rooms, and answer questions about our facilities. What would you like to know?'
  }
  
  // Navigation help
  if (lowerMsg.includes('navigate') || lowerMsg.includes('direction') || lowerMsg.includes('map') || lowerMsg.includes('where')) {
    return 'I can help you navigate! Use the Navigate tab for detailed routes. Our campus has 3 main buildings: MST (center), JST (east), and RST (west). What specific location are you looking for?'
  }
  
  // Thank you
  if (lowerMsg.includes('thank')) {
    return 'You\'re welcome! Feel free to ask if you need any other help navigating the campus.'
  }
  
  // Default response
  return "I'm not sure about that specific question. Try asking about:\n• Building locations (MST, JST, RST)\n• Computer Labs (CL1-CL6) or Classrooms (CR1-CR2)\n• Library or Registrar Office\n• Cafeteria or Gymnasium\n• Or tap the FAQ button for common questions!"
}

onMounted(() => {
  inputField.value?.focus()
})
</script>

<style>
/* Styles moved to external file: src/assets/chatbot.css */
@import '../assets/chatbot.css';
</style>
