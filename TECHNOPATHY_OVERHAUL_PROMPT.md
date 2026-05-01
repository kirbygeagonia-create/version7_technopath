# TechnoPath — Complete System Overhaul Prompt
### For: Windsurf Kimi K2.5 AI
### Repository: `https://github.com/kirbygeagonia-create/Technopathy.git`
### Scope: QR Cleanup · Functionality Audit · Onboarding Fix · UI/UX Overhaul

---

## ⚙️ OPERATING PROTOCOL

Apply every task in order. For each task:

```
STEP 1 → READ     Open the exact file listed. Read the target lines.
STEP 2 → CHANGE   Apply the exact code change described.
STEP 3 → SAVE     Write the file.
STEP 4 → VERIFY   Run the grep/check command shown. Confirm expected result.
STEP 5 → REPORT   Print:
           ✅ DONE: [TASK-ID] — [description]
           ❌ FAILED: [TASK-ID] — [reason] → retry from STEP 1
```

After all tasks, run the **Final Verification Scan**. Never stop until every item shows ✅.

---

## PART 1 — QR SCANNER CLEANUP

---

### TASK-Q01 · Clarify: QR Code Generator in Settings (KEEP — Not a Scanner)
**File:** `frontend/src/views/SettingsView.vue`

The `qrcode.vue` usage in SettingsView is a **QR code generator** that creates a shareable link for the app — it is NOT a QR scanner and should be KEPT. However, its section label should be clarified.

**Find in SettingsView.vue:**
```html
<div class="settings-item-subtitle">QR code to open the app</div>
```
**Replace with:**
```html
<div class="settings-item-subtitle">Share app link via QR code</div>
```

**VERIFY:**
```bash
grep -n "QR code to open" frontend/src/views/SettingsView.vue
# EXPECT: 0 results ✅
grep -n "Share app link" frontend/src/views/SettingsView.vue
# EXPECT: 1 result ✅
```

---

### TASK-Q02 · Confirm No Hidden QR Scanner Imports Anywhere
**Search the entire codebase for any scanner-related imports, routes, or dead code:**

```bash
grep -rn "jsqr\|jsQR\|QrScanner\|qr-scanner\|BarcodeDetector\|getUserMedia.*scan\|QRScannerView" \
  frontend/src backend_django --include="*.vue" --include="*.js" --include="*.py" 2>/dev/null
```

If any result is found that references a QR *scanner* (not generator): delete that file or remove that import/route entirely.

**VERIFY:**
```bash
grep -rn "QRScannerView\|qr-scanner\|jsqr" frontend/src --include="*.vue" --include="*.js"
# EXPECT: 0 results ✅
```

---

## PART 2 — BROKEN FUNCTIONALITY FIXES

---

### TASK-F01 · CRITICAL: `/core/ratings/` Endpoint Missing — Rating Submissions Silently Fail
**Files:** `backend_django/apps/core/urls.py` and `backend_django/apps/core/views.py`

**Problem:** `HomeView.submitRating()` posts to `/api/core/ratings/` but this endpoint does not exist in `core/urls.py`. Every app rating submission returns 404 and is lost.

**Fix Option A — Add the endpoint to core (preferred):**

In `backend_django/apps/core/views.py`, add at the bottom:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status

class AppRatingView(APIView):
    """Public endpoint for app ratings submitted from HomeView."""
    permission_classes = []

    def post(self, request):
        rating  = request.data.get('rating')
        comment = request.data.get('comment', '')
        if not rating or not isinstance(rating, int) or not (1 <= rating <= 5):
            return Response({'error': 'rating must be an integer 1–5'},
                            status=http_status.HTTP_400_BAD_REQUEST)
        # Store as a Feedback entry so it appears in the admin Feedback panel
        from apps.feedback.models import Feedback
        Feedback.objects.create(
            rating   = rating,
            comment  = comment,
            category = 'general',
        )
        return Response({'message': 'Rating submitted. Thank you!'}, status=http_status.HTTP_201_CREATED)
```

In `backend_django/apps/core/urls.py`, add to `urlpatterns`:
```python
path('ratings/', views.AppRatingView.as_view(), name='app-rating'),
```

**VERIFY:**
```bash
grep -n "AppRatingView\|ratings/" backend_django/apps/core/urls.py
# EXPECT: 1 result ✅
grep -n "class AppRatingView" backend_django/apps/core/views.py
# EXPECT: 1 result ✅
```

---

### TASK-F02 · CRITICAL: FavoritesView Navigation Broken — Wrong Type Key
**File:** `frontend/src/views/FavoritesView.vue`

**Problem:** MapView saves favorites with `type: marker.marker_type` which is `'facility'` or `'room'`. FavoritesView `goToLocation()` checks for `item.type === 'building'` — which never matches. Clicking any saved facility favorite does nothing.

**Find in FavoritesView.vue:**
```javascript
function goToLocation(item) {
  if (item.type === 'building') {
    router.push(`/map?building=${item.id}`)
  } else if (item.type === 'room') {
    router.push(`/navigate?room=${item.id}`)
  }
}
```

**Replace with:**
```javascript
function goToLocation(item) {
  // Handles composite IDs saved as "facility_123" or "room_456"
  // Also handles legacy 'building' type for backward compatibility
  if (item.type === 'facility' || item.type === 'building') {
    // Navigate to map and highlight the facility by its svg_id or name
    const target = item.map_svg_id || item.svgId || item.name || ''
    router.push({ path: '/map', query: { highlight: target } })
  } else if (item.type === 'room') {
    router.push({ path: '/navigate', query: { to: item.map_svg_id || item.name || item.id } })
  } else {
    // Fallback: go to map
    router.push('/map')
  }
}
```

**VERIFY:**
```bash
grep -n "item.type === 'building'" frontend/src/views/FavoritesView.vue
# EXPECT: 0 results (removed) ✅
grep -n "item.type === 'facility'" frontend/src/views/FavoritesView.vue
# EXPECT: 1 result ✅
```

---

### TASK-F03 · FavoritesView — Add Empty Skeleton and Description Field
**File:** `frontend/src/views/FavoritesView.vue`

The favorite card shows `<p>{{ item.type }}</p>` — raw type like `"facility"` or `"room"`. Replace with readable label.

**Find in FavoritesView.vue template:**
```html
<div class="favorite-info">
  <h3>{{ item.name }}</h3>
  <p>{{ item.type }}</p>
</div>
```
**Replace with:**
```html
<div class="favorite-info">
  <h3>{{ item.name }}</h3>
  <p>{{ item.description || formatFavoriteType(item.type) }}</p>
</div>
```

**Add function in `<script setup>`:**
```javascript
function formatFavoriteType(type) {
  const labels = { facility: 'Building / Facility', room: 'Room', building: 'Building' }
  return labels[type] || type || 'Location'
}
```

**VERIFY:**
```bash
grep -n "formatFavoriteType" frontend/src/views/FavoritesView.vue
# EXPECT: 2 results (definition + usage) ✅
```

---

### TASK-F04 · SettingsView — Add "Restart Tutorial" Option
**File:** `frontend/src/views/SettingsView.vue`

**Problem:** There is no way to replay the onboarding tutorial after skipping or completing it.

**Find the settings list section** (look for other `settings-item` divs). **Add before the QR code section:**
```html
<!-- Restart Tutorial -->
<div class="settings-item" @click="restartTutorial" style="cursor:pointer">
  <div class="settings-item-icon">
    <span class="material-icons">school</span>
  </div>
  <div class="settings-item-content">
    <div class="settings-item-title">Restart Tutorial</div>
    <div class="settings-item-subtitle">Replay the onboarding walkthrough</div>
  </div>
  <span class="material-icons settings-item-arrow">chevron_right</span>
</div>
```

**Add function in `<script setup>` of SettingsView.vue:**
```javascript
function restartTutorial() {
  localStorage.removeItem('tp_onboarding_completed')
  localStorage.removeItem('tp_onboarding_skipped')
  router.push('/')
}
```

**Ensure `useRouter` is imported:**
```javascript
import { useRouter } from 'vue-router'
const router = useRouter()
```

**VERIFY:**
```bash
grep -n "restartTutorial\|Restart Tutorial" frontend/src/views/SettingsView.vue
# EXPECT: 2+ results ✅
```

---

### TASK-F05 · Announcements Not Displayed to Users — Wire to HomeView/NotificationsView
**Files:** `frontend/src/views/HomeView.vue` and `frontend/src/views/NotificationsView.vue`

**Problem:** The backend has a full announcements system at `/api/announcements/`. Neither HomeView nor NotificationsView fetches or shows announcements to public users.

**In `HomeView.vue`**, in the data loading section (find `onMounted` or data fetching block), add an announcements fetch after existing loads:
```javascript
// Load announcements for home feed
const announcementsRef = ref([])
async function loadAnnouncements() {
  try {
    const res = await api.get('/announcements/')
    announcementsRef.value = (res.data || [])
      .filter(a => a.status === 'published')
      .slice(0, 3) // Show max 3 on home
  } catch { /* silent fail */ }
}
```

**Add announcement cards to the HomeView template**, after the `.seait-highlights` section but before the map section:
```html
<!-- Announcements Feed -->
<div class="home-announcements" v-if="announcementsRef.length > 0">
  <h2 class="home-section-title">
    <span class="material-icons">campaign</span>
    Announcements
  </h2>
  <div
    v-for="ann in announcementsRef"
    :key="ann.id"
    class="announcement-card"
  >
    <div class="announcement-header">
      <span
        class="announcement-dept-chip"
        :style="{ background: getDeptColor(ann.department_color) }"
      >{{ ann.department_label || 'Campus' }}</span>
      <span class="announcement-date">{{ formatDate(ann.published_at || ann.created_at) }}</span>
    </div>
    <h3 class="announcement-title">{{ ann.title }}</h3>
    <p class="announcement-body" v-if="ann.body">{{ ann.body.substring(0, 120) }}{{ ann.body.length > 120 ? '…' : '' }}</p>
  </div>
</div>
```

**Add helper functions:**
```javascript
function getDeptColor(colorName) {
  const colors = {
    orange: '#FF9800', teal: '#009688', blue: '#2196F3',
    green: '#4CAF50', red: '#F44336', purple: '#9C27B0',
    amber: '#FFC107', charcoal: '#607D8B', dark_blue: '#1565C0',
    brown: '#795548', indigo: '#3F51B5', dark_green: '#2E7D32',
  }
  return colors[colorName] || '#FF9800'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
}
```

**Add CSS for announcement cards (inside HomeView `<style>` or `homeview.css`):**
```css
.home-announcements { padding: 16px; }
.home-section-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 18px; font-weight: 600;
  color: var(--color-primary-text);
  margin-bottom: 12px;
}
.announcement-card {
  background: var(--color-bg);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-left: 4px solid var(--color-primary);
}
.announcement-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 8px;
}
.announcement-dept-chip {
  font-size: 11px; font-weight: 600; color: #fff;
  padding: 3px 10px; border-radius: 99px; letter-spacing: 0.3px;
}
.announcement-date { font-size: 12px; color: var(--color-text-secondary); }
.announcement-title { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
.announcement-body { font-size: 13px; color: var(--color-text-secondary); line-height: 1.5; }
```

**Call `loadAnnouncements()` inside `onMounted`.**

**VERIFY:**
```bash
grep -n "loadAnnouncements\|announcementsRef\|/announcements/" frontend/src/views/HomeView.vue
# EXPECT: 3+ results ✅
```

---

## PART 3 — ONBOARDING TUTORIAL FIX

---

### TASK-O01 · CRITICAL: Replace Hardcoded Highlight Positions With DOM-Based Targeting
**File:** `frontend/src/components/OnboardingTutorial.vue`

**Root Cause:** `getHighlightStyle()` returns hardcoded pixel/offset values guessing where UI elements are. When the actual DOM elements are at different positions (due to device size, scroll, etc.) the orange highlight box appears in empty space — it points at nothing.

**Full replacement of the `getHighlightStyle` function:**

Find the entire `getHighlightStyle` function and replace it:

```javascript
const getHighlightStyle = () => {
  const key = steps[currentStep.value].highlight
  if (!key) return {}

  // Map each step key to a CSS selector that targets the actual DOM element
  const selectors = {
    search:    '.home-search-input-wrapper',
    map:       '.seait-embedded-map',
    favorites: '.desktop-fab-btn.desktop-ratings-btn, .favorites-view, [href="/favorites"]',
    chatbot:   '.desktop-fab-btn.desktop-chatbot-btn',
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
```

**Also update the onboarding steps** to correct descriptions that no longer match the current UI:

Find the `steps` array and replace with:
```javascript
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
  },
]
```

**VERIFY:**
```bash
grep -n "getBoundingClientRect\|selectors\[key\]" frontend/src/components/OnboardingTutorial.vue
# EXPECT: 2 results ✅

grep -n "calc(var(--safe" frontend/src/components/OnboardingTutorial.vue
# EXPECT: 0 results (all hardcoded positions removed) ✅
```

---

### TASK-O02 · Onboarding Highlight Must Use `position: fixed` in CSS
**File:** `frontend/src/assets/onboarding.css`

The `.onboarding-highlight` div must use `fixed` positioning since we now set `top/left/width/height` from `getBoundingClientRect()` (which gives viewport-relative coords).

**Find:**
```css
.onboarding-highlight {
  position: absolute;
  border-radius: 12px;
  pointer-events: none;
  z-index: 999;
}
```
**Replace with:**
```css
.onboarding-highlight {
  position: fixed;   /* Must match getBoundingClientRect() viewport coords */
  border-radius: 12px;
  pointer-events: none;
  z-index: 1002;     /* Above overlay (1000) and card (1001) */
  transition: all 0.3s ease;
}
```

**VERIFY:**
```bash
grep -n "position: fixed" frontend/src/assets/onboarding.css
# EXPECT: at least 1 result inside .onboarding-highlight ✅
```

---

### TASK-O03 · Onboarding: Refresh Highlight Position on Step Change
**File:** `frontend/src/components/OnboardingTutorial.vue`

When the user taps Next/Back, the highlight must recalculate its position because a new element is being targeted. Add a `nextTick` flush after step changes.

**Find the imports at the top of `<script setup>`:**
```javascript
import { ref, computed, onMounted } from 'vue'
```
**Replace with:**
```javascript
import { ref, computed, onMounted, nextTick, watch } from 'vue'
```

**Add a watcher after the `steps` array:**
```javascript
// Re-calculate highlight position after DOM settles on step change
watch(currentStep, async () => {
  await nextTick()
  // Force re-render of highlight by touching a reactive value
  // (getHighlightStyle is called reactively in the template)
})
```

**VERIFY:**
```bash
grep -n "nextTick\|watch" frontend/src/components/OnboardingTutorial.vue
# EXPECT: 2 results ✅
```

---

## PART 4 — UI/UX OVERLAY DESIGN SYSTEM

**Goal:** Chatbot, Notifications, and Ratings/Feedback should NOT navigate to a new full page. Instead they slide up as a floating overlay panel that blurs the HomeView content behind it, keeping the user feeling "inside" the home tab.

---

### TASK-U01 · Create Reusable `BottomSheetOverlay` Component
**Create new file:** `frontend/src/components/BottomSheetOverlay.vue`

```vue
<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="overlay-fade">
      <div
        v-if="modelValue"
        class="bso-backdrop"
        @click="$emit('update:modelValue', false)"
      >
        <Transition name="overlay-slide">
          <div
            v-if="modelValue"
            class="bso-sheet"
            :style="{ maxHeight: maxHeight }"
            @click.stop
          >
            <!-- Drag Handle -->
            <div class="bso-handle-bar" @click="$emit('update:modelValue', false)">
              <div class="bso-handle"></div>
            </div>
            <!-- Dynamic Content Slot -->
            <slot />
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, required: true },
  maxHeight:  { type: String,  default: '85vh' },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.bso-backdrop {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: flex-end;
}

.bso-sheet {
  width: 100%;
  background: var(--color-bg, #ffffff);
  border-radius: 28px 28px 0 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.18);
}

.bso-handle-bar {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
  cursor: pointer;
}

.bso-handle {
  width: 40px;
  height: 4px;
  background: var(--color-border, #e0e0e0);
  border-radius: 99px;
}

/* Transitions */
.overlay-fade-enter-active,
.overlay-fade-leave-active { transition: opacity 0.25s ease; }
.overlay-fade-enter-from,
.overlay-fade-leave-to    { opacity: 0; }

.overlay-slide-enter-active,
.overlay-slide-leave-active { transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1); }
.overlay-slide-enter-from,
.overlay-slide-leave-to    { transform: translateY(100%); }
</style>
```

**VERIFY:**
```bash
ls frontend/src/components/BottomSheetOverlay.vue
# EXPECT: file exists ✅
grep -n "bso-backdrop\|bso-sheet\|overlay-slide" frontend/src/components/BottomSheetOverlay.vue
# EXPECT: 3+ results ✅
```

---

### TASK-U02 · HomeView — Replace Full-Page Navigation With Overlay Sheets
**File:** `frontend/src/views/HomeView.vue`

**Step 1 — Import the new component and update reactive state:**

Find the imports block in `<script setup>` and add:
```javascript
import BottomSheetOverlay from '../components/BottomSheetOverlay.vue'
import ChatbotView        from './ChatbotView.vue'
import NotificationsView  from './NotificationsView.vue'
```

Add these refs alongside existing state:
```javascript
const showChatbotSheet       = ref(false)
const showNotificationsSheet = ref(false)
// showRating already exists — keep it
```

**Step 2 — Change the FAB button actions.** Find:
```javascript
const goToNotifications = () => router.push('/notifications')
const goToChatbot       = () => router.push('/chatbot')
```
**Replace with:**
```javascript
const goToNotifications = () => { showNotificationsSheet.value = true }
const goToChatbot       = () => { showChatbotSheet.value       = true }
```

**Step 3 — Add overlay sheets to the template.** At the BOTTOM of the `<template>`, just before the closing `</div>`, add:

```html
<!-- Chatbot Overlay Sheet -->
<BottomSheetOverlay v-model="showChatbotSheet" max-height="90vh">
  <div class="sheet-inner-scroll">
    <ChatbotView :embedded="true" @close="showChatbotSheet = false" />
  </div>
</BottomSheetOverlay>

<!-- Notifications Overlay Sheet -->
<BottomSheetOverlay v-model="showNotificationsSheet" max-height="88vh">
  <div class="sheet-inner-scroll">
    <NotificationsView :embedded="true" @close="showNotificationsSheet = false" />
  </div>
</BottomSheetOverlay>
```

**Step 4 — Add shared sheet inner scroll CSS** (in HomeView `<style>` section):
```css
.sheet-inner-scroll {
  flex: 1;
  overflow-y: auto;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}
```

**Step 5 — Update the existing Rating modal** to also use the sheet style (replace the current `.modal-overlay` rating dialog wrapper with BottomSheetOverlay):
```html
<!-- Rating Sheet -->
<BottomSheetOverlay v-model="showRating" max-height="60vh">
  <div class="rating-sheet-content">
    <h3 class="rating-sheet-title">Rate TechnoPath</h3>
    <div class="star-rating">
      <span
        v-for="n in 5"
        :key="n"
        class="star material-icons"
        :class="{ filled: n <= rating }"
        @click="rating = n"
      >{{ n <= rating ? 'star' : 'star_border' }}</span>
    </div>
    <p class="rating-hint">{{ ratingHint }}</p>
    <textarea
      v-model="ratingComment"
      class="rating-textarea"
      placeholder="Leave a comment (optional)"
      rows="3"
    ></textarea>
    <div class="rating-actions">
      <button class="rating-cancel-btn" @click="showRating = false">Cancel</button>
      <button class="rating-submit-btn" @click="submitRating">Submit</button>
    </div>
  </div>
</BottomSheetOverlay>
```

Add the computed hint and missing CSS to HomeView style:
```javascript
const ratingHint = computed(() => {
  const hints = ['', 'Very Poor', 'Poor', 'Okay', 'Good', 'Excellent']
  return hints[rating.value] || ''
})
```

```css
.rating-sheet-content {
  padding: 20px 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.rating-sheet-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary-text);
}
.star-rating { display: flex; gap: 8px; }
.star { font-size: 40px; cursor: pointer; color: #ccc; transition: color 0.15s; }
.star.filled { color: #FF9800; }
.rating-hint { font-size: 14px; color: var(--color-text-secondary); min-height: 20px; }
.rating-textarea {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}
.rating-actions { display: flex; gap: 12px; width: 100%; }
.rating-cancel-btn {
  flex: 1;
  padding: 14px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: transparent;
  font-size: 15px;
  cursor: pointer;
}
.rating-submit-btn {
  flex: 2;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: var(--color-primary);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
```

**Remove the old `.modal-overlay` rating dialog** from the template (the `<div v-if="showRating" class="modal-overlay">` block is replaced by the BottomSheetOverlay above).

**VERIFY:**
```bash
grep -n "BottomSheetOverlay\|showChatbotSheet\|showNotificationsSheet" frontend/src/views/HomeView.vue
# EXPECT: 6+ results ✅

grep -n "router.push('/notifications')\|router.push('/chatbot')" frontend/src/views/HomeView.vue
# EXPECT: 0 results (replaced with sheet refs) ✅

grep -n "modal-overlay.*showRating\|v-if=\"showRating\".*modal" frontend/src/views/HomeView.vue
# EXPECT: 0 results (old dialog removed) ✅
```

---

### TASK-U03 · ChatbotView — Add `embedded` Prop Support
**File:** `frontend/src/views/ChatbotView.vue`

When rendered inside the overlay sheet, the Chatbot must not show its full-page back button (it's already inside a sheet with a handle to dismiss).

**Find in `<script setup>`:**
```javascript
// Add prop support for embedded mode
const props = defineProps({
  embedded: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])
```

**In the template, find the back button in the chatbot header:**
```html
<button class="chatbot-back-btn" @click="goBack">
  <span class="material-icons">arrow_back</span>
</button>
```
**Replace with:**
```html
<button v-if="!props.embedded" class="chatbot-back-btn" @click="goBack">
  <span class="material-icons">arrow_back</span>
</button>
```

Also update the chatbot header height/top-padding when embedded:
```html
<header class="chatbot-header" :class="{ 'chatbot-header-embedded': props.embedded }">
```

Add CSS:
```css
.chatbot-header-embedded {
  padding-top: 8px;  /* Less top padding when inside sheet (handle already provides space) */
}
```

**VERIFY:**
```bash
grep -n "embedded\|props.embedded" frontend/src/views/ChatbotView.vue
# EXPECT: 3+ results ✅
```

---

### TASK-U04 · NotificationsView — Add `embedded` Prop Support
**File:** `frontend/src/views/NotificationsView.vue`

Same embedded-mode treatment for the notifications view.

**Add prop in `<script setup>`:**
```javascript
const props = defineProps({
  embedded: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])
```

**In the template header, find the back button:**
```html
<button class="notifications-back-btn" @click="goBack">
  <span class="material-icons">arrow_back</span>
</button>
```
**Replace with:**
```html
<button v-if="!props.embedded" class="notifications-back-btn" @click="goBack">
  <span class="material-icons">arrow_back</span>
</button>
```

**VERIFY:**
```bash
grep -n "props.embedded\|embedded" frontend/src/views/NotificationsView.vue
# EXPECT: 2+ results ✅
```

---

## PART 5 — SKELETON LOADING

---

### TASK-S01 · Add Skeleton Loading to InfoView
**File:** `frontend/src/views/InfoView.vue`

**Problem:** InfoView shows nothing while data loads, causing a jarring blank screen.

**Find the `loading` state** (or add it if missing):
```javascript
const loading = ref(true)
```

**In the template, find where items are listed** (the `v-for` loop over `items`). **Wrap it with a loading skeleton:**

```html
<!-- Skeleton loading state -->
<div v-if="loading" class="infoview-skeleton-list">
  <div v-for="n in 5" :key="n" class="infoview-skeleton-card">
    <div class="skeleton skeleton-icon"></div>
    <div class="skeleton-text-block">
      <div class="skeleton skeleton-title"></div>
      <div class="skeleton skeleton-subtitle"></div>
    </div>
  </div>
</div>

<!-- Real content -->
<div v-else>
  <!-- existing v-for content stays here unchanged -->
</div>
```

**Add skeleton CSS to `frontend/src/assets/infoview.css`:**
```css
.infoview-skeleton-list { padding: 16px; }
.infoview-skeleton-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--color-bg);
  border-radius: 16px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.skeleton-icon {
  width: 48px; height: 48px; border-radius: 12px; flex-shrink: 0;
}
.skeleton-text-block { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.skeleton-title   { height: 16px; width: 60%; border-radius: 8px; }
.skeleton-subtitle{ height: 12px; width: 40%; border-radius: 8px; }
/* .skeleton class with shimmer is already defined in animations.css */
```

**VERIFY:**
```bash
grep -n "infoview-skeleton\|v-if=\"loading\"" frontend/src/views/InfoView.vue
# EXPECT: 2+ results ✅
```

---

### TASK-S02 · Add Skeleton Loading to FavoritesView
**File:** `frontend/src/views/FavoritesView.vue`

**Find the favorites list render.** Add loading ref and skeleton:
```javascript
const isLoading = ref(true)

function loadFavorites() {
  isLoading.value = true
  const saved = localStorage.getItem('tp_favorites')
  favorites.value = saved ? JSON.parse(saved) : []
  isLoading.value = false
}
```

**In template, before the `v-if="favorites.length === 0"` block, add:**
```html
<div v-if="isLoading" class="favorites-skeleton">
  <div v-for="n in 4" :key="n" class="fav-skeleton-card">
    <div class="skeleton" style="width:48px;height:48px;border-radius:12px;flex-shrink:0"></div>
    <div style="flex:1;display:flex;flex-direction:column;gap:8px">
      <div class="skeleton" style="height:14px;width:55%;border-radius:6px"></div>
      <div class="skeleton" style="height:11px;width:35%;border-radius:6px"></div>
    </div>
  </div>
</div>

<div v-else-if="favorites.length === 0" class="empty-state">
  <!-- existing empty state -->
</div>

<div v-else class="favorites-list">
  <!-- existing v-for -->
</div>
```

**VERIFY:**
```bash
grep -n "isLoading\|fav-skeleton" frontend/src/views/FavoritesView.vue
# EXPECT: 2+ results ✅
```

---

### TASK-S03 · Add Skeleton Loading to HomeView Announcements
**File:** `frontend/src/views/HomeView.vue`

In the announcements section added in TASK-F05, add a loading state:
```javascript
const announcementsLoading = ref(true)

async function loadAnnouncements() {
  announcementsLoading.value = true
  try {
    const res = await api.get('/announcements/')
    announcementsRef.value = (res.data || []).filter(a => a.status === 'published').slice(0, 3)
  } catch { /* silent fail */ } finally {
    announcementsLoading.value = false
  }
}
```

**In the template announcements section, add skeleton before the real cards:**
```html
<div class="home-announcements">
  <h2 class="home-section-title">
    <span class="material-icons">campaign</span> Announcements
  </h2>
  <!-- Skeleton -->
  <template v-if="announcementsLoading">
    <div v-for="n in 2" :key="n" class="announcement-card" style="gap:10px;display:flex;flex-direction:column">
      <div class="skeleton" style="height:12px;width:30%;border-radius:6px"></div>
      <div class="skeleton" style="height:16px;width:75%;border-radius:6px"></div>
      <div class="skeleton" style="height:11px;width:90%;border-radius:6px"></div>
    </div>
  </template>
  <!-- Real cards -->
  <template v-else-if="announcementsRef.length > 0">
    <div v-for="ann in announcementsRef" :key="ann.id" class="announcement-card">
      <!-- content from TASK-F05 -->
    </div>
  </template>
</div>
```

**VERIFY:**
```bash
grep -n "announcementsLoading\|skeleton.*announcement" frontend/src/views/HomeView.vue
# EXPECT: 2+ results ✅
```

---

## PART 6 — HOME TAB VISUAL IMPROVEMENTS

---

### TASK-V01 · Improve FAB Buttons — Replace Icon-Only With Labeled Pill Buttons
**File:** `frontend/src/views/HomeView.vue`

The three FABs (Notifications, Ratings, Chatbot) are small icon-only circles that are easy to miss. Replace with pill-shaped labeled buttons.

**Find the FAB container:**
```html
<div class="desktop-fab-container">
  <button class="desktop-fab-btn desktop-notification-btn" @click="goToNotifications" title="Notifications">
    <span class="material-icons">notifications</span>
    <span v-if="unreadNotifications > 0" class="notification-badge">...</span>
  </button>
  <button class="desktop-fab-btn desktop-ratings-btn" @click="openRateApp" title="Ratings & Feedback">
    <span class="material-icons">star</span>
  </button>
  <button class="desktop-fab-btn desktop-chatbot-btn" @click="goToChatbot" title="Chatbot">
    <span class="material-icons">smart_toy</span>
  </button>
</div>
```

**Replace with:**
```html
<div class="home-action-pills">
  <button class="home-pill-btn home-pill-notifications" @click="goToNotifications">
    <span class="material-icons">notifications</span>
    <span class="home-pill-label">Alerts</span>
    <span v-if="unreadNotifications > 0" class="home-pill-badge">
      {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
    </span>
  </button>
  <button class="home-pill-btn home-pill-chatbot" @click="goToChatbot">
    <span class="material-icons">smart_toy</span>
    <span class="home-pill-label">Ask AI</span>
  </button>
  <button class="home-pill-btn home-pill-rating" @click="openRateApp">
    <span class="material-icons">star_rate</span>
    <span class="home-pill-label">Rate</span>
  </button>
</div>
```

**Add CSS (in HomeView style or homeview.css):**
```css
.home-action-pills {
  display: flex;
  gap: 8px;
  padding: 0 4px;
  justify-content: flex-end;
}

.home-pill-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 99px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.home-pill-btn:active { transform: scale(0.96); }
.home-pill-btn .material-icons { font-size: 18px; }

.home-pill-notifications {
  background: var(--color-primary);
  color: #fff;
}
.home-pill-chatbot {
  background: #1565C0;
  color: #fff;
}
.home-pill-rating {
  background: #fff;
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
}
.home-pill-badge {
  position: absolute;
  top: -4px; right: -4px;
  background: #F44336;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 99px;
  min-width: 18px;
  text-align: center;
}
```

**Remove the old `.desktop-fab-container` CSS** (the old styles for `.desktop-fab-btn`, `.desktop-notification-btn`, `.desktop-chatbot-btn`) from HomeView's style section.

**VERIFY:**
```bash
grep -n "home-action-pills\|home-pill-btn" frontend/src/views/HomeView.vue
# EXPECT: 4+ results ✅
grep -n "desktop-fab-btn\|desktop-fab-container" frontend/src/views/HomeView.vue
# EXPECT: 0 results (old removed) ✅
```

---

### TASK-V02 · Improve Menu Bottom Sheet — Add Quick-Access Navigation Icons
**File:** `frontend/src/views/HomeView.vue`

The menu sheet currently only shows text items. Add a quick-nav icon grid at the top for the most used features.

**Find the `.menu-sheet-content` div and add a quick-nav grid BEFORE the existing menu items:**
```html
<div class="menu-quick-nav">
  <button class="menu-quick-item" @click="() => { showMenu = false; router.push('/map') }">
    <span class="material-icons">map</span>
    <span>Map</span>
  </button>
  <button class="menu-quick-item" @click="() => { showMenu = false; router.push('/navigate') }">
    <span class="material-icons">directions</span>
    <span>Navigate</span>
  </button>
  <button class="menu-quick-item" @click="() => { showMenu = false; router.push('/favorites') }">
    <span class="material-icons">favorite</span>
    <span>Favorites</span>
  </button>
  <button class="menu-quick-item" @click="() => { showMenu = false; router.push('/feedback') }">
    <span class="material-icons">feedback</span>
    <span>Feedback</span>
  </button>
</div>
<div class="menu-divider"></div>
```

**Add CSS:**
```css
.menu-quick-nav {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 8px 0 16px;
}
.menu-quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  background: var(--color-surface);
  border: none;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary-text);
  cursor: pointer;
  transition: background 0.15s;
}
.menu-quick-item:active { background: var(--color-surface-2); }
.menu-quick-item .material-icons {
  font-size: 24px;
  color: var(--color-primary);
}
```

**VERIFY:**
```bash
grep -n "menu-quick-nav\|menu-quick-item" frontend/src/views/HomeView.vue
# EXPECT: 4+ results ✅
```

---

## 🔁 FINAL VERIFICATION SCAN

Run every command. Print ✅ (expected) or ❌ (unexpected). Fix any ❌ before stopping.

```bash
# PART 1 — QR Cleanup
grep -n "Share app link" frontend/src/views/SettingsView.vue
# EXPECT: 1 result ✅

grep -rn "QRScannerView\|qr-scanner\|jsqr" frontend/src --include="*.vue" --include="*.js"
# EXPECT: 0 results ✅

# PART 2 — Functionality
grep -n "AppRatingView\|ratings/" backend_django/apps/core/urls.py
# EXPECT: 1 result ✅

grep -n "class AppRatingView" backend_django/apps/core/views.py
# EXPECT: 1 result ✅

grep -n "item.type === 'facility'" frontend/src/views/FavoritesView.vue
# EXPECT: 1 result ✅

grep -n "item.type === 'building'" frontend/src/views/FavoritesView.vue
# EXPECT: 0 results ✅ (removed as primary check, may appear in fallback comment)

grep -n "restartTutorial" frontend/src/views/SettingsView.vue
# EXPECT: 2+ results ✅

grep -n "loadAnnouncements\|/announcements/" frontend/src/views/HomeView.vue
# EXPECT: 2+ results ✅

# PART 3 — Onboarding
grep -n "getBoundingClientRect" frontend/src/components/OnboardingTutorial.vue
# EXPECT: 1 result ✅

grep -n "calc(var(--safe" frontend/src/components/OnboardingTutorial.vue
# EXPECT: 0 results ✅

grep -n "position: fixed" frontend/src/assets/onboarding.css
# EXPECT: at least 1 result (inside .onboarding-highlight) ✅

grep -n "nextTick\|watch" frontend/src/components/OnboardingTutorial.vue
# EXPECT: 2 results ✅

# PART 4 — Overlay System
ls frontend/src/components/BottomSheetOverlay.vue
# EXPECT: file exists ✅

grep -n "bso-backdrop\|overlay-slide" frontend/src/components/BottomSheetOverlay.vue
# EXPECT: 2 results ✅

grep -n "showChatbotSheet\|showNotificationsSheet" frontend/src/views/HomeView.vue
# EXPECT: 4+ results ✅

grep -n "router.push('/notifications')\|router.push('/chatbot')" frontend/src/views/HomeView.vue
# EXPECT: 0 results ✅

grep -n "props.embedded" frontend/src/views/ChatbotView.vue
# EXPECT: 2+ results ✅

grep -n "props.embedded" frontend/src/views/NotificationsView.vue
# EXPECT: 2+ results ✅

# PART 5 — Skeleton Loading
grep -n "infoview-skeleton\|v-if=\"loading\"" frontend/src/views/InfoView.vue
# EXPECT: 2+ results ✅

grep -n "isLoading\|fav-skeleton" frontend/src/views/FavoritesView.vue
# EXPECT: 2+ results ✅

# PART 6 — Visual Improvements
grep -n "home-action-pills\|home-pill-btn" frontend/src/views/HomeView.vue
# EXPECT: 4+ results ✅

grep -n "desktop-fab-container\b" frontend/src/views/HomeView.vue
# EXPECT: 0 results ✅

grep -n "menu-quick-nav" frontend/src/views/HomeView.vue
# EXPECT: 2+ results ✅
```

---

## 📊 FINAL REPORT — PRINT THIS WHEN DONE

```
╔════════════════════════════════════════════════════════════════╗
║         TECHNOPATHY SYSTEM OVERHAUL — COMPLETION REPORT        ║
╠════════════════════════════════════════════════════════════════╣
║  PART 1 — QR CLEANUP                                           ║
║  Q01  QR Settings Label Clarified                ✅ / ❌       ║
║  Q02  No Hidden QR Scanner Imports               ✅ / ❌       ║
╠════════════════════════════════════════════════════════════════╣
║  PART 2 — FUNCTIONALITY FIXES                                  ║
║  F01  /core/ratings/ Endpoint Created            ✅ / ❌       ║
║  F02  FavoritesView Navigation Fixed             ✅ / ❌       ║
║  F03  Favorites Type Label Readable              ✅ / ❌       ║
║  F04  Settings Restart Tutorial Added            ✅ / ❌       ║
║  F05  Announcements Feed on HomeView             ✅ / ❌       ║
╠════════════════════════════════════════════════════════════════╣
║  PART 3 — ONBOARDING FIX                                       ║
║  O01  Highlight Uses getBoundingClientRect()     ✅ / ❌       ║
║  O02  Highlight CSS Uses position:fixed          ✅ / ❌       ║
║  O03  Highlight Recalculates on Step Change      ✅ / ❌       ║
╠════════════════════════════════════════════════════════════════╣
║  PART 4 — OVERLAY DESIGN SYSTEM                                ║
║  U01  BottomSheetOverlay Component Created       ✅ / ❌       ║
║  U02  HomeView Uses Sheets (Not Full Nav)        ✅ / ❌       ║
║  U03  ChatbotView Supports embedded Prop         ✅ / ❌       ║
║  U04  NotificationsView Supports embedded Prop   ✅ / ❌       ║
╠════════════════════════════════════════════════════════════════╣
║  PART 5 — SKELETON LOADING                                     ║
║  S01  InfoView Skeleton Loading                  ✅ / ❌       ║
║  S02  FavoritesView Skeleton Loading             ✅ / ❌       ║
║  S03  Announcements Skeleton Loading             ✅ / ❌       ║
╠════════════════════════════════════════════════════════════════╣
║  PART 6 — VISUAL IMPROVEMENTS                                  ║
║  V01  FAB Replaced With Labeled Pill Buttons     ✅ / ❌       ║
║  V02  Menu Sheet Quick-Nav Grid Added            ✅ / ❌       ║
╠════════════════════════════════════════════════════════════════╣
║  TOTAL PASSED:    ___ / 19                                     ║
║  STATUS:  [ ALL CLEAR ✅ ]  OR  [ NEEDS RETRY ❌ ]            ║
╚════════════════════════════════════════════════════════════════╝
```

**Do NOT stop until all 19 show ✅. If any ❌ appears, re-apply that task and re-run its verify command.**

---

## 📋 IMPLEMENTATION NOTES FOR THE DEVELOPER

### Why the QR "scanner" was not removed from Settings
The `qrcode.vue` package and its usage in `SettingsView.vue` is a QR code **generator** — it creates a QR image that users can share to open the app. This is functional, useful, and should stay. There was never a QR *scanner* (camera-based reader) in the codebase — so there is nothing to remove except updating the label to be clearer (TASK-Q01).

### Why the overlay approach is better than routing
Routing Chatbot/Notifications as full pages requires the user to navigate "away" from home and return. The `BottomSheetOverlay` approach (TASK-U01/U02) keeps the user anchored to the home context, with the blurred background providing awareness of where they are. The `Teleport to="body"` ensures the overlay sits above all other content correctly regardless of DOM hierarchy.

### Onboarding fix explanation
The original `getHighlightStyle()` used hardcoded `bottom: 'calc(140px + ...)'` offsets that were guesses. Different devices, different window heights, and any layout changes would place the highlight box in empty space. The replacement (TASK-O01) uses `document.querySelector()` + `getBoundingClientRect()` to find the REAL pixel position of each target element at the moment the step is shown — guaranteed accurate on any device.
