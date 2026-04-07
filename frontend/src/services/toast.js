import { reactive } from 'vue'

// Global toast state
export const toastState = reactive({
  message: '',
  type: 'info', // 'info', 'success', 'warning', 'error'
  visible: false,
  timeout: null
})

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast: 'info', 'success', 'warning', 'error'
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
export function showToast(message, type = 'info', duration = 3000) {
  // Clear existing timeout
  if (toastState.timeout) {
    clearTimeout(toastState.timeout)
  }
  
  // Set toast content
  toastState.message = message
  toastState.type = type
  toastState.visible = true
  
  // Auto-hide after duration
  toastState.timeout = setTimeout(() => {
    hideToast()
  }, duration)
}

/**
 * Hide the toast notification
 */
export function hideToast() {
  toastState.visible = false
  toastState.message = ''
  if (toastState.timeout) {
    clearTimeout(toastState.timeout)
    toastState.timeout = null
  }
}

/**
 * Smart alert that adapts based on context
 * @param {string} title - Alert title
 * @param {string} message - Alert message
 * @param {string} type - Alert type
 */
export function showSmartAlert(title, message, type = 'info') {
  // On mobile, use toast
  if (window.innerWidth < 768) {
    showToast(`${title}: ${message}`, type, 4000)
  } else {
    // On desktop, could use a modal or more prominent notification
    showToast(`${title}: ${message}`, type, 5000)
  }
}

/**
 * Connection status alert
 */
export function showConnectionAlert(isOnline) {
  if (isOnline) {
    showToast('Back online! Syncing data...', 'success', 3000)
  } else {
    showToast('You are offline. Using cached data.', 'warning', 4000)
  }
}

/**
 * Error alert with user-friendly messages
 */
export function showErrorAlert(error, context = '') {
  let message = 'Something went wrong. Please try again.'
  
  if (error.response?.status === 500) {
    message = 'Server error. Running in offline mode with cached data.'
  } else if (error.response?.status === 404) {
    message = 'Resource not found.'
  } else if (error.message?.includes('Network Error')) {
    message = 'Network error. Check your connection.'
  }
  
  if (context) {
    message = `${context}: ${message}`
  }
  
  showToast(message, 'error', 5000)
}

/**
 * Success confirmation
 */
export function showSuccess(message) {
  showToast(message, 'success', 3000)
}

/**
 * Warning notification
 */
export function showWarning(message) {
  showToast(message, 'warning', 4000)
}

export default {
  showToast,
  hideToast,
  showSmartAlert,
  showConnectionAlert,
  showErrorAlert,
  showSuccess,
  showWarning,
  toastState
}
