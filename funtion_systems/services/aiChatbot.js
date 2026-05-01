import { isOnline } from './sync.js'
import { getFAQEntries } from './offlineData.js'
import db from './db.js'

/**
 * AI-Powered Chatbot Service for TechnoPath
 *
 * Priority chain:
 * 1. Flask chatbot API (handles AI internally — key stays server-side)
 * 2. Rule-based fallback (always works offline)
 *
 * NOTE: OpenAI API key is NEVER in the frontend.
 * All AI calls go through the Flask backend which holds the key securely.
 */

const FLASK_CHATBOT_URL = import.meta.env.VITE_FLASK_CHATBOT_URL || '/chatbot-api'

const CAMPUS_CONTEXT_SUMMARY = `
SEAIT Campus — TechnoPath guide app for South East Asian Institute of Technology, Tupi, South Cotabato.
Buildings: MST (4F, center), JST (4F, back), RST (3F, left-bottom from gate).
Key rooms: CL1-CL10 on MST 3F. Registrar on RST 1F. Library left wing.
Cafeteria between MST and Gymnasium. Comfort rooms near stairwells on every floor.
`

// Conversation history (in-memory per session)
const conversationHistory = []
const MAX_HISTORY = 10

export async function initChatHistory() {
  if (!isOnline()) return
  try {
    const history = await db.ai_chat_logs.limit(MAX_HISTORY).toArray()
    conversationHistory.push(...history.map(h => ({
      role: h.mode === 'user' ? 'user' : 'assistant',
      content: h.message
    })))
  } catch { /* silent fail — start fresh */ }
}

async function saveToHistory(mode, message) {
  try {
    await db.ai_chat_logs.add({ mode, message, created_at: new Date().toISOString() })
  } catch { /* silent fail */ }
}

/**
 * Call Flask chatbot — Flask handles OpenAI internally (key never in frontend)
 */
async function generateFlaskResponse(userMessage) {
  const response = await fetch(`${FLASK_CHATBOT_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: userMessage,
      history: conversationHistory.slice(-MAX_HISTORY)
    })
  })
  if (!response.ok) throw new Error(`Flask chatbot error: ${response.status}`)
  const data = await response.json()
  return data.reply
}

/**
 * Rule-based fallback — works fully offline, no external API
 */
async function generateRuleBasedResponse(userMessage) {
  const msg = userMessage.toLowerCase()

  // Try FAQ entries from IndexedDB first
  try {
    const faqData = await getFAQEntries()
    for (const faq of faqData.data || []) {
      if (faq.keywords) {
        const keywords = faq.keywords.split(',').map(k => k.trim().toLowerCase())
        if (keywords.some(k => k && msg.includes(k))) return faq.answer
      }
      if (faq.question && msg.includes(faq.question.toLowerCase().substring(0, 10))) {
        return faq.answer
      }
    }
  } catch { /* continue to keyword matching */ }

  // Building-specific responses
  if (msg.includes('mst')) return 'The MST Building is the main 4-floor academic building at the center of campus. It houses classrooms (1F-2F), Computer Labs CL1-CL10 on the 3rd floor, and more rooms on the 4th floor. Use the Navigate tab for directions!'
  if (msg.includes('jst')) return 'JST Building has 4 floors at the back of campus — lecture rooms on 1F, laboratories on 2F, and seminar areas on 3F-4F. Check the Map tab for details.'
  if (msg.includes('rst')) return 'RST Building is the 3-floor administrative building. 1F: Registrar & Accounting. 2F: Guidance, Safety, Student Affairs. 3F: IT Office, Silakbo. Located left of the main gate.'
  if (msg.includes('library')) return 'The Library is on the ground floor, left wing. Open Mon-Fri 8AM-6PM, Sat 8AM-12PM. Two floors with study areas and digital resources.'
  if (msg.includes('registrar')) return 'Registrar Office is on the 1st floor of RST Building with 7 service windows. Hours: Mon-Fri 8AM-5PM.'
  if (msg.includes('cl') || msg.includes('computer lab')) return 'Computer Labs CL1-CL10 are on the 3rd floor of the MST Building. Use the Navigate tab for turn-by-turn directions!'
  if (msg.includes('canteen') || msg.includes('cafeteria')) return 'The Cafeteria is between the MST Building and Gymnasium, open 7AM-6PM daily.'
  if (msg.includes('comfort room') || msg.includes('restroom') || msg.includes(' cr')) return 'Comfort rooms are on every floor of all buildings (MST, JST, RST), near stairwells.'
  if (msg.includes('gym')) return 'The Gymnasium is at the back of campus with basketball/volleyball courts and fitness equipment.'
  if (msg.includes('navigate') || msg.includes('direction') || msg.includes('where is') || msg.includes('how to get')) return 'Use the Navigate tab for turn-by-turn directions! Select your start and destination to find the shortest route across campus.'
  if (msg.includes('offline')) return "TechnoPath works offline! The map, navigation, and room info all work without internet after your first visit. Feedback will sync when you reconnect."
  if (msg.includes('hello') || msg.includes('hi') || msg.includes('kumusta')) return "Hello! I'm your SEAIT Campus Assistant. Ask me about buildings, rooms, offices, or use the Navigate tab for directions!"

  return "I can help with SEAIT campus info! Ask about:\n• Buildings (MST, JST, RST)\n• Computer Labs (CL1-CL10)\n• Offices (Registrar, CICT, Guidance)\n• Facilities (Library, Cafeteria, Gym)\n\nOr use the Navigate tab for directions!"
}

/**
 * Main chat function — Flask AI first, offline rules as fallback
 */
export async function sendMessage(userMessage) {
  if (!userMessage?.trim()) throw new Error('Message is required')

  conversationHistory.push({ role: 'user', content: userMessage })
  await saveToHistory('user', userMessage)

  let response
  let source = 'flask'

  if (isOnline()) {
    try {
      response = await generateFlaskResponse(userMessage)
    } catch (flaskErr) {
      console.warn('[Chatbot] Flask unavailable, using rule-based fallback:', flaskErr.message)
      response = await generateRuleBasedResponse(userMessage)
      source = 'fallback'
    }
  } else {
    response = await generateRuleBasedResponse(userMessage)
    source = 'offline'
  }

  conversationHistory.push({ role: 'assistant', content: response })
  await saveToHistory('assistant', response)

  if (conversationHistory.length > MAX_HISTORY * 2) {
    conversationHistory.splice(0, conversationHistory.length - MAX_HISTORY * 2)
  }

  return { reply: response, source, isOffline: !isOnline() }
}

export function clearHistory() {
  conversationHistory.length = 0
}

export function getStatus() {
  return {
    isOnline: isOnline(),
    hasFlaskUrl: !!FLASK_CHATBOT_URL,
    hasAIKey: true, // Key is server-side in Flask — always true when Flask is available
    historyLength: conversationHistory.length,
    isAIEnabled: isOnline() && !!FLASK_CHATBOT_URL
  }
}

export default { sendMessage, clearHistory, getStatus, initChatHistory }
