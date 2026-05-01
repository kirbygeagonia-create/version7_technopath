# TechnoPath — UI Polish, Skeletons & Animations Prompt
### For: Windsurf Kimi K2.5 AI
### Project: `https://github.com/kirbygeagonia-create/version7_technopath.git`
### Run Order: Prompt 1 of 5

---

## ⚙️ OPERATING PROTOCOL — READ BEFORE DOING ANYTHING

```
FOR EACH TASK:
  STEP 1 → READ     Open the exact file listed. Read the target lines.
  STEP 2 → FIX      Apply the exact code change described.
  STEP 3 → SAVE     Write the file to disk.
  STEP 4 → VERIFY   Run the grep command shown. Confirm expected result.
  STEP 5 → REPORT   Print:
              ✅ FIXED & VERIFIED: [Task ID] — [description]
              ❌ FAILED: [Task ID] — [reason] → retry from STEP 1

AFTER ALL TASKS:
  STEP 6 → Run the FINAL VERIFICATION SUITE at the bottom
  STEP 7 → Print the FINAL REPORT
  STEP 8 → Any ❌ = go back to STEP 1 for that task
  STEP 9 → Only stop when ALL items show ✅
```

---

## 📋 CURRENT REPO STATE — ALREADY DONE (DO NOT RE-APPLY)

The following fixes are confirmed present in the repo. **Do not touch these files for these issues:**

| What | Status |
|------|--------|
| `funtion_systems/` directory | ✅ DELETED — do not recreate |
| Root-level `package.json` | ✅ DELETED — do not recreate |
| Manual `serviceWorker.register()` in `main.js` | ✅ REMOVED |
| `Facility` model `x_position`/`y_position` fields | ✅ ADDED (migration 0003 exists) |
| Flask CORS `origins=` explicit list | ✅ ALREADY DONE |
| `vite.config.js` `skipWaiting` | ✅ ALREADY ABSENT — do not add it |

**All frontend source lives exclusively in `frontend/src/`. Do not create or reference `funtion_systems/`.**

---

## 📦 LIBRARY NOTES

| Library | How to get it | Notes |
|---------|--------------|-------|
| **boneyard-js** | `npm install boneyard-js` inside `frontend/` | Run this first |
| **Animata** | Copy-paste only — Vue CSS port provided below | ❌ Do NOT run `npm install animata` |
| **loading-ui** | Copy-paste only — Vue CSS port provided below | ❌ Do NOT run `npm install loading-ui` |

---

## TASK 1 — Fix Critical Router Bug in SplashScreen

**File:** `frontend/src/views/SplashScreen.vue`

**Problem confirmed:** `useRouter()` is incorrectly wrapped in `ref()`, adding a broken proxy layer.

**Find:**
```javascript
const router    = ref(useRouter())
```
**Replace with:**
```javascript
const router    = useRouter()
```

**Find:**
```javascript
router.value.replace('/')
```
**Replace with:**
```javascript
router.replace('/')
```

**Verify:**
```bash
grep "ref(useRouter" frontend/src/views/SplashScreen.vue
# EXPECT: 0 results ✅
grep "router\.value\." frontend/src/views/SplashScreen.vue
# EXPECT: 0 results ✅
```

---

## TASK 2 — Install boneyard-js and Create AppSkeleton Component

```bash
cd frontend && npm install boneyard-js
```

**Create `frontend/src/components/AppSkeleton.vue`:**

```vue
<template>
  <Skeleton
    :loading="loading"
    :name="name"
    :animate="animate"
    :transition="220"
    :stagger="55"
    :color="skColor"
    dark-color="#252525"
    :class="wrapClass"
  >
    <slot />
  </Skeleton>
</template>

<script setup>
import { Skeleton } from 'boneyard-js'
import { computed } from 'vue'

const props = defineProps({
  loading:   { type: Boolean, required: true },
  name:      { type: String,  default: undefined },
  animate:   { type: String,  default: 'shimmer' },
  wrapClass: { type: String,  default: '' },
  dark:      { type: Boolean, default: false },
})

const skColor = computed(() => props.dark ? '#252525' : '#e6e6e6')
</script>
```

**Verify:**
```bash
grep "boneyard-js" frontend/package.json
# EXPECT: 1 result ✅
ls frontend/src/components/AppSkeleton.vue
# EXPECT: file exists ✅
cd frontend && npm run build
# EXPECT: success ✅
```

---

## TASK 3 — Replace HomeView Inline Skeletons with Boneyard

**File:** `frontend/src/views/HomeView.vue`

**Add to `<script setup>` imports:**
```javascript
import { registerBones } from 'boneyard-js'
import AppSkeleton from '../components/AppSkeleton.vue'

registerBones({
  'home-announcement': {
    width: 400, height: 90,
    bones: [
      { x: 0, y: 0,  w: 22, h: 18, r: 9 },
      { x: 0, y: 26, w: 68, h: 16, r: 6 },
      { x: 0, y: 50, w: 90, h: 12, r: 5 },
      { x: 0, y: 68, w: 72, h: 12, r: 5 },
    ]
  }
})
```

**Replace the `v-if="announcementsLoading"` skeleton block with:**
```html
<template v-if="announcementsLoading">
  <div v-for="n in 3" :key="n" class="home-announcement-sk-wrap">
    <AppSkeleton :loading="true" name="home-announcement" animate="shimmer" />
  </div>
</template>
```

**Add scoped CSS:**
```css
.home-announcement-sk-wrap {
  height: 90px;
  margin-bottom: 12px;
  border-radius: 12px;
  overflow: hidden;
}
```

**Verify:**
```bash
grep "AppSkeleton" frontend/src/views/HomeView.vue
# EXPECT: 1+ results ✅
```

---

## TASK 4 — Replace NavigateView Spinner with Boneyard + CometSpinner

**Create `frontend/src/components/CometSpinner.vue`:**
*(Ported from `github.com/turbostarter/loading-ui` — React → Vue CSS port)*

```vue
<template>
  <span role="status" aria-label="Loading" class="comet-spinner" :style="{ width: size, height: size }">
    <span class="comet-inner" />
    <span class="sr-only">Loading</span>
  </span>
</template>

<script setup>
defineProps({ size: { type: String, default: '40px' } })
</script>

<style scoped>
.comet-spinner {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  container-type: size;
}
.comet-inner {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  animation: cometShadow 1.7s infinite ease, cometRotate 1.7s infinite ease;
}
@keyframes cometShadow {
  0%, 5%, 95%, 100% {
    box-shadow:
      0 -83cqmin 0 -40cqmin #FF9800,
      0 -83cqmin 0 -41cqmin #FF9800,
      0 -83cqmin 0 -42cqmin rgba(255,152,0,0.6),
      0 -83cqmin 0 -43cqmin rgba(255,152,0,0.3),
      0 -83cqmin 0 -44cqmin rgba(255,152,0,0.1);
  }
  38% {
    box-shadow:
      0 -83cqmin 0 -40cqmin #FF9800,
      calc(83cqmin * -0.454) calc(83cqmin * -0.892) 0 -41cqmin #FF9800,
      calc(83cqmin * -0.777) calc(83cqmin * -0.629) 0 -42cqmin rgba(255,152,0,0.6),
      calc(83cqmin * -0.934) calc(83cqmin * -0.358) 0 -43cqmin rgba(255,152,0,0.3),
      calc(83cqmin * -0.988) calc(83cqmin * -0.108) 0 -44cqmin rgba(255,152,0,0.1);
  }
}
@keyframes cometRotate {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
</style>
```

**In `frontend/src/views/NavigateView.vue`, add to `<script setup>`:**
```javascript
import { registerBones } from 'boneyard-js'
import AppSkeleton from '../components/AppSkeleton.vue'
import CometSpinner from '../components/CometSpinner.vue'

registerBones({
  'navigate-map': {
    width: 390, height: 520,
    bones: [
      { x: 0, y: 0,   w: 100, h: 48,  r: 24 },
      { x: 0, y: 56,  w: 100, h: 340, r: 16 },
      { x: 0, y: 404, w: 100, h: 72,  r: 16 },
      { x: 4, y: 420, w: 50,  h: 16,  r: 6  },
      { x: 4, y: 442, w: 32,  h: 12,  r: 5  },
    ]
  }
})
```

**Replace the `.svg-map-loading` div with:**
```html
<div v-if="!mapLoaded && !mapError" class="svg-map-skeleton-wrap">
  <AppSkeleton :loading="true" name="navigate-map" animate="shimmer" wrap-class="map-sk-full" />
  <div class="map-sk-center">
    <CometSpinner size="52px" />
    <p class="map-sk-hint">Loading campus map…</p>
  </div>
</div>

<div v-if="mapError" class="svg-map-error-state">
  <span class="material-icons">map_off</span>
  <p>{{ mapError }}</p>
</div>
```

**Add CSS:**
```css
.svg-map-skeleton-wrap { position: absolute; inset: 0; z-index: 10; }
.map-sk-full { width: 100%; height: 100%; }
.map-sk-center {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  pointer-events: none;
}
.map-sk-hint {
  font-size: 13px; font-weight: 500; color: #FF9800;
  background: linear-gradient(90deg, rgba(255,152,0,0.4), #FF9800 50%, rgba(255,152,0,0.4));
  background-size: 200% auto;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  animation: mapHintShimmer 2s linear infinite;
}
@keyframes mapHintShimmer {
  0% { background-position: 200% center; } 100% { background-position: -200% center; }
}
.svg-map-error-state {
  position: absolute; inset: 0; z-index: 10;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
  background: var(--color-surface, #fff); color: #F44336;
}
```

**Verify:**
```bash
ls frontend/src/components/CometSpinner.vue
# EXPECT: file exists ✅
grep "svg-map-loading" frontend/src/views/NavigateView.vue
# EXPECT: 0 results (old div removed) ✅
```

---

## TASK 5 — Vertical Tile Wipe on SplashScreen

**Create `frontend/src/components/VerticalTileWipe.vue`:**
*(Animata vertical-tiles preloader — ported from React/Framer Motion to pure Vue CSS)*

```vue
<template>
  <div ref="container" class="tile-wipe-root" :class="{ 'tile-wipe-exit': active }">
    <div class="tile-wipe-tiles">
      <div
        v-for="tile in tiles"
        :key="tile.id"
        class="tile-wipe-col"
        :style="{ width: tile.width + 'px', left: tile.left + 'px', transitionDelay: tile.delay + 'ms' }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  active:   { type: Boolean, default: false },
  minWidth: { type: Number,  default: 30 },
  color:    { type: String,  default: '#FF9800' },
})

const container = ref(null)
const containerWidth = ref(390)
let ro = null

onMounted(() => {
  if (container.value) containerWidth.value = container.value.offsetWidth
  ro = new ResizeObserver(([e]) => { containerWidth.value = e.contentRect.width })
  if (container.value) ro.observe(container.value)
})
onUnmounted(() => ro?.disconnect())

const tiles = computed(() => {
  const count = Math.max(5, Math.floor(containerWidth.value / props.minWidth))
  const w = containerWidth.value / count + 1
  const mid = Math.floor((count - 1) / 2)
  return Array.from({ length: count }, (_, i) => ({
    id: i, width: w, left: i * w,
    delay: Math.abs(i - mid) * 45,
  }))
})
</script>

<style scoped>
.tile-wipe-root {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 9998; overflow: hidden;
}
.tile-wipe-tiles { position: relative; width: 100%; height: 100%; }
.tile-wipe-col {
  position: absolute; top: 0; height: 100%;
  background: v-bind(color);
  transform: translateY(0);
  transition: transform 0.55s cubic-bezier(0.45, 0, 0.55, 1);
}
.tile-wipe-exit .tile-wipe-col { transform: translateY(100%); }
</style>
```

**Update `frontend/src/views/SplashScreen.vue`:**

Add import:
```javascript
import VerticalTileWipe from '../components/VerticalTileWipe.vue'
```

Add to template (inside `.splash-screen` div, at the very end):
```html
<VerticalTileWipe :active="isExiting" color="#FF9800" />
```

Extend exit delay from `450` to `620`:
```diff
- }, 450)
+ }, 620)
```

**Verify:**
```bash
ls frontend/src/components/VerticalTileWipe.vue
# EXPECT: file exists ✅
grep "VerticalTileWipe" frontend/src/views/SplashScreen.vue
# EXPECT: 2 results (import + usage) ✅
```

---

## TASK 6 — Boneyard Skeleton for ChatbotView

**File:** `frontend/src/views/ChatbotView.vue`

Add to `<script setup>`:
```javascript
import { registerBones } from 'boneyard-js'
import AppSkeleton from '../components/AppSkeleton.vue'

registerBones({
  'chatbot-faq': {
    width: 390, height: 240,
    bones: [
      { x: 0, y: 0,   w: 100, h: 52, r: 12 },
      { x: 0, y: 60,  w: 100, h: 52, r: 12 },
      { x: 0, y: 120, w: 100, h: 52, r: 12 },
      { x: 0, y: 180, w: 100, h: 52, r: 12 },
    ]
  }
})

const chatLoading = ref(true)
onMounted(() => { setTimeout(() => { chatLoading.value = false }, 700) })
```

In template, before the FAQ section:
```html
<div v-if="chatLoading" class="chatbot-faq-sk-wrap">
  <AppSkeleton :loading="true" name="chatbot-faq" animate="shimmer" />
</div>
```

Change the existing FAQ div from `v-if="showFAQ"` to `v-else-if="showFAQ"`.

Add CSS: `.chatbot-faq-sk-wrap { padding: 16px; height: 256px; }`

**Verify:**
```bash
grep "chatbot-faq" frontend/src/views/ChatbotView.vue
# EXPECT: 1+ results ✅
grep "v-else-if=\"showFAQ\"" frontend/src/views/ChatbotView.vue
# EXPECT: 1 result ✅
```

---

## TASK 7 — BouncingDots Typing Indicator + PulseDot Status

**Create `frontend/src/components/BouncingDots.vue`:**
*(Ported from `github.com/turbostarter/loading-ui` — React → Vue CSS port)*

```vue
<template>
  <span role="status" class="bouncing-dots">
    <span v-for="i in dots" :key="i" class="bouncing-dot"
      :style="{ backgroundColor: color, animationDelay: `${(i-1) * 0.2}s` }" />
    <span class="sr-only">Typing…</span>
  </span>
</template>

<script setup>
defineProps({ dots: { type: Number, default: 3 }, color: { type: String, default: '#FF9800' } })
</script>

<style scoped>
.bouncing-dots { display: inline-flex; align-items: center; gap: 5px; }
.bouncing-dot {
  width: 8px; height: 8px; border-radius: 50%;
  animation: bdAnim 1.4s ease-in-out infinite;
}
@keyframes bdAnim {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50%       { transform: scale(1.2); opacity: 1;   }
}
</style>
```

**Create `frontend/src/components/PulseDot.vue`:**
*(Ported from `github.com/turbostarter/loading-ui` — React → Vue CSS port)*

```vue
<template>
  <span role="status" class="pulse-dot"
    :style="{ width: size, height: size, backgroundColor: color }">
    <span class="sr-only">{{ label }}</span>
  </span>
</template>

<script setup>
defineProps({
  size:  { type: String, default: '10px' },
  color: { type: String, default: '#4CAF50' },
  label: { type: String, default: 'Active' },
})
</script>

<style scoped>
.pulse-dot {
  display: inline-block; border-radius: 50%;
  animation: pdAnim 1.2s ease-in-out infinite;
}
@keyframes pdAnim {
  0%, 100% { transform: scale(1);   opacity: 0.8; }
  50%       { transform: scale(1.5); opacity: 1;   }
}
</style>
```

**In `ChatbotView.vue`, add imports and state:**
```javascript
import BouncingDots from '../components/BouncingDots.vue'
import PulseDot     from '../components/PulseDot.vue'

const isBotTyping    = ref(false)
const chatbotChecked = ref(false)
```

Set `isBotTyping.value = true` BEFORE the fetch/axios call to the chatbot API, and `isBotTyping.value = false` in the `finally` block.

**Fix connection check to use a 5-second timeout:**
```javascript
async function checkFlaskStatus() {
  try {
    const ctrl = new AbortController()
    const tid  = setTimeout(() => ctrl.abort(), 5000)
    const res  = await fetch(`${FLASK_URL}/health`, { signal: ctrl.signal })
    clearTimeout(tid)
    flaskConnected.value = res.ok
  } catch {
    flaskConnected.value = false
  } finally {
    chatbotChecked.value = true
  }
}
```

**Add typing bubble to the messages list:**
```html
<div v-if="isBotTyping" class="chatbot-typing-bubble">
  <BouncingDots color="#FF9800" />
</div>
```

**Update status display:**
```html
<span v-if="isOffline" class="status-offline">
  <span class="material-icons">wifi_off</span> Offline Mode
</span>
<span v-else-if="flaskConnected" class="status-ai">
  <PulseDot color="#4CAF50" size="8px" label="AI connected" /> AI Powered
</span>
<span v-else-if="chatbotChecked" class="status-basic">
  <span class="material-icons">chat</span> Basic Mode
</span>
<span v-else class="status-connecting">
  <span class="material-icons">chat</span> Connecting…
</span>
```

**Add CSS:**
```css
.chatbot-typing-bubble {
  display: flex; align-items: center;
  padding: 12px 16px;
  background: var(--color-surface-alt, #f5f5f5);
  border-radius: 18px 18px 18px 4px;
  width: fit-content; margin: 6px 0;
}
```

**Verify:**
```bash
ls frontend/src/components/BouncingDots.vue frontend/src/components/PulseDot.vue
# EXPECT: both files exist ✅
grep "isBotTyping" frontend/src/views/ChatbotView.vue
# EXPECT: 2+ results ✅
```

---

## TASK 8 — Boneyard Skeleton for ProfileView

**File:** `frontend/src/views/ProfileView.vue`

Add to `<script setup>`:
```javascript
import { registerBones } from 'boneyard-js'
import AppSkeleton from '../components/AppSkeleton.vue'

registerBones({
  'profile-card': {
    width: 390, height: 280,
    bones: [
      { x: 33, y: 0,   w: 34, h: 80,  r: '50%' },
      { x: 25, y: 92,  w: 50, h: 20,  r: 8     },
      { x: 20, y: 120, w: 60, h: 14,  r: 6     },
      { x: 0,  y: 155, w: 40, h: 14,  r: 6     },
      { x: 55, y: 155, w: 45, h: 14,  r: 6     },
      { x: 0,  y: 180, w: 40, h: 14,  r: 6     },
      { x: 55, y: 180, w: 45, h: 14,  r: 6     },
      { x: 0,  y: 205, w: 40, h: 14,  r: 6     },
      { x: 55, y: 205, w: 45, h: 14,  r: 6     },
    ]
  }
})

const skeletonLoading = ref(true)
onMounted(() => { setTimeout(() => { skeletonLoading.value = false }, 450) })
```

Wrap template content:
```html
<div v-if="skeletonLoading" class="profile-sk-wrap">
  <AppSkeleton :loading="true" name="profile-card" animate="shimmer" />
</div>
<div class="profile-content" v-else>
  <!-- existing content unchanged -->
</div>
```

CSS: `.profile-sk-wrap { padding: 24px; height: 320px; }`

**Verify:**
```bash
grep "profile-card\|skeletonLoading" frontend/src/views/ProfileView.vue
# EXPECT: 2+ results ✅
```

---

## TASK 9 — Page Transitions + Animata Staggered Card Entry

**`frontend/src/App.vue`** — wrap RouterView:
```html
<RouterView v-slot="{ Component, route }">
  <Transition :name="route.meta.transition || 'page-slide'" mode="out-in">
    <component :is="Component" :key="route.path" />
  </Transition>
</RouterView>
```

**`frontend/src/assets/main.css`** — add:
```css
/* Page transitions */
.page-slide-enter-active,
.page-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity, transform;
}
.page-slide-enter-from { opacity: 0; transform: translateY(10px); }
.page-slide-leave-to   { opacity: 0; transform: translateY(-6px); }
```

**Create `frontend/src/assets/animations.css`:**
```css
/*
  Animata staggered-card pattern (github.com/codse/animata)
  Original: Framer Motion AnimatePresence + motion.li with delay: i * 0.06
  Ported to: CSS animation-delay equivalents
*/
@keyframes animataStaggerIn {
  from { opacity: 0; transform: translateY(12px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)    scale(1);    }
}
.stagger-card { opacity: 0; animation: animataStaggerIn 0.35s cubic-bezier(0,0,0.2,1) forwards; }
.stagger-card:nth-child(1)  { animation-delay:   0ms; }
.stagger-card:nth-child(2)  { animation-delay:  60ms; }
.stagger-card:nth-child(3)  { animation-delay: 120ms; }
.stagger-card:nth-child(4)  { animation-delay: 180ms; }
.stagger-card:nth-child(5)  { animation-delay: 240ms; }
.stagger-card:nth-child(6)  { animation-delay: 300ms; }
.stagger-card:nth-child(7)  { animation-delay: 360ms; }
.stagger-card:nth-child(8)  { animation-delay: 420ms; }
```

**Import animations.css in `frontend/src/main.js`:**
```javascript
import './assets/animations.css'
```

**Apply `.stagger-card` class:**
- `HomeView.vue` → `<div class="highlight-card stagger-card">`
- `HomeView.vue` → `<div class="announcement-card stagger-card" v-for="...">`
- `InfoView.vue` → `<div class="infoview-item-card stagger-card" v-for="...">`
- `FavoritesView.vue` → `<div class="favorite-card stagger-card" v-for="...">`

**Verify:**
```bash
grep "Transition" frontend/src/App.vue
# EXPECT: 1+ results ✅
grep "stagger-card" frontend/src/assets/animations.css
# EXPECT: 1+ results ✅
ls frontend/src/assets/animations.css
# EXPECT: file exists ✅
```

---

## TASK 10 — Bottom Nav Bounce + Flask Health Endpoint + Env Files

**Bottom nav bounce CSS** (add to `frontend/src/assets/main.css` or `app.css`):
```css
.app-bottom-nav-item.router-link-exact-active .material-icons,
.app-bottom-nav-item.app-active .material-icons {
  animation: navBounce 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
@keyframes navBounce {
  0%   { transform: scale(1)   translateY(0);   }
  45%  { transform: scale(1.3) translateY(-3px);}
  100% { transform: scale(1)   translateY(0);   }
}
```

**Flask health endpoint** — confirm it already exists in `chatbot_flask/app.py`. If NOT present, add:
```python
@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'ok', 'service': 'technopath-chatbot'}, 200
```

**API base URL guard** in `frontend/src/services/api.js`:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL
if (!BASE_URL && import.meta.env.PROD) {
  console.error('[TechnoPath] ⚠️  VITE_API_BASE_URL not set — API calls will fail in production!')
}
const api = axios.create({
  baseURL: BASE_URL || 'http://localhost:8000/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})
```

**Create `frontend/.env.example`:**
```
VITE_API_BASE_URL=https://your-django-backend.onrender.com/api
VITE_FLASK_CHATBOT_URL=http://localhost:5187
```

**Remove binary files from git tracking:**
```bash
git rm --cached node-installer.msi node-portable.zip nodejs.msi 2>/dev/null || true
```

**Add to root `.gitignore` if not already present:**
```
*.msi
node-portable.zip
```

**Verify:**
```bash
grep "/health" chatbot_flask/app.py
# EXPECT: 1 result ✅
ls frontend/.env.example
# EXPECT: file exists ✅
grep "VITE_FLASK_CHATBOT_URL" frontend/.env.example
# EXPECT: 1 result ✅
git ls-files | grep -E '\.(msi|zip)$'
# EXPECT: empty ✅
```

---

## 🔁 FINAL VERIFICATION SUITE

```bash
echo "=== PROMPT 1 FINAL VERIFICATION ==="
cd frontend

npm run build && echo "PASS: Build" || echo "FAIL: Build"

grep "ref(useRouter"       src/views/SplashScreen.vue     && echo "FAIL: router bug" || echo "PASS: router bug fixed"
grep "router\.value\."     src/views/SplashScreen.vue     && echo "FAIL: router.value" || echo "PASS: no router.value"
grep "boneyard-js"         package.json                   && echo "PASS: boneyard-js" || echo "FAIL: boneyard-js"
test -f src/components/AppSkeleton.vue                    && echo "PASS: AppSkeleton" || echo "FAIL: AppSkeleton"
test -f src/components/CometSpinner.vue                   && echo "PASS: CometSpinner" || echo "FAIL: CometSpinner"
test -f src/components/BouncingDots.vue                   && echo "PASS: BouncingDots" || echo "FAIL: BouncingDots"
test -f src/components/PulseDot.vue                       && echo "PASS: PulseDot" || echo "FAIL: PulseDot"
test -f src/components/VerticalTileWipe.vue               && echo "PASS: VerticalTileWipe" || echo "FAIL: VerticalTileWipe"
grep "Transition"          src/App.vue                    && echo "PASS: page transitions" || echo "FAIL: page transitions"
grep "stagger-card"        src/assets/animations.css      && echo "PASS: stagger CSS" || echo "FAIL: stagger CSS"
grep "navigate-map"        src/views/NavigateView.vue     && echo "PASS: map bones" || echo "FAIL: map bones"
grep "chatbot-faq"         src/views/ChatbotView.vue      && echo "PASS: chatbot bones" || echo "FAIL: chatbot bones"
grep "profile-card"        src/views/ProfileView.vue      && echo "PASS: profile bones" || echo "FAIL: profile bones"
test -f .env.example                                      && echo "PASS: .env.example" || echo "FAIL: .env.example"
grep "/health"             ../chatbot_flask/app.py        && echo "PASS: /health endpoint" || echo "FAIL: /health"
result=$(git ls-files | grep -E '\.(msi|zip)$'); [ -z "$result" ] && echo "PASS: no binaries" || echo "FAIL: binaries tracked"

echo "=== ALL CHECKS COMPLETE ==="
```

All lines must print **PASS**. If any **FAIL** — return to that task, fix, and re-run.
