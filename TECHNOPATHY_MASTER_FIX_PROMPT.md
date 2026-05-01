# TechnoPath — MASTER FIX & CONTINUOUS VERIFICATION PROMPT
### For: Windsurf Kimi K2.5 AI
### Repository: `https://github.com/kirbygeagonia-create/Technopathy.git`
### Total Issues: 29 (9 Critical 🔴 · 12 Major 🟠 · 8 Config/Security 🔵)

---

## ⚙️ YOUR OPERATING PROTOCOL — READ THIS BEFORE DOING ANYTHING

You are a Senior Software Engineer. Your ONLY job is to fix every issue in this document.
You must operate in this exact loop for **every single issue**:

```
FOR EACH ISSUE:
  STEP 1 → READ     Open the exact file listed. Read the relevant lines.
  STEP 2 → FIX      Apply the exact code change described.
  STEP 3 → SAVE     Write the file to disk.
  STEP 4 → VERIFY   Re-open the file. Confirm the fix is present using the
                    grep command listed in the issue's VERIFY section.
  STEP 5 → REPORT   Print one of:
              ✅ FIXED & VERIFIED: [ID] — [description]
              ❌ FAILED: [ID] — [reason] → immediately retry from STEP 1

AFTER ALL 29 ISSUES:
  STEP 6 → RUN FULL VERIFICATION SCAN (Section at end of this document)
  STEP 7 → Print the FINAL VERIFICATION REPORT table
  STEP 8 → Any ❌ in the table = go back to STEP 1 for that issue
  STEP 9 → Only stop when ALL 29 show ✅ in the FINAL REPORT
```

**Rules:**
- Never skip an issue
- Never assume a fix is already in place without reading the file first
- Never stop early — loop until the Final Report shows all 29 ✅
- If a file doesn't exist, create it with the correct content shown below
- Fix issues in the numbered order listed

---

## 🔴 CRITICAL BUGS — Core Features Broken

---

### ISSUE-C01 🔴 Pathfinding Field Name Mismatch — Navigation Completely Broken
**Files:** `frontend/src/services/pathfinder.js` and `backend_django/apps/navigation/serializers.py`

**Problem:** The backend serializes edge fields as `from_node` / `to_node` (nested objects) but `pathfinder.js` reads `from_node_id` / `to_node_id` (integers). Node coordinates are `x`/`y` in the model but the pathfinder reads `x_position`/`y_position`. Every Dijkstra value is `undefined` — navigation never works.

**Step 1 — Fix the Navigation Serializer:**
Find in `backend_django/apps/navigation/serializers.py`:
```python
class NavigationEdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationEdge
        fields = '__all__'
```
Replace with:
```python
class NavigationEdgeSerializer(serializers.ModelSerializer):
    from_node_id = serializers.IntegerField(source='from_node.id', read_only=True)
    to_node_id   = serializers.IntegerField(source='to_node.id',   read_only=True)

    class Meta:
        model  = NavigationEdge
        fields = ['id', 'from_node_id', 'to_node_id', 'distance',
                  'is_bidirectional', 'is_deleted', 'created_at', 'updated_at']
```

Find the `NavigationNodeSerializer` and confirm or add explicit `x` and `y` fields:
```python
class NavigationNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = NavigationNode
        fields = ['id', 'name', 'node_type', 'map_svg_id', 'x', 'y',
                  'floor', 'is_deleted', 'facility', 'room']
```

**Step 2 — Fix pathfinder.js coordinate reading:**
In `frontend/src/services/pathfinder.js`, find all occurrences of:
```javascript
x_position
y_position
```
Replace every occurrence with `x` and `y` respectively.

**VERIFY:**
```bash
grep -n "x_position\|y_position" frontend/src/services/pathfinder.js
# → must return 0 results
grep -n "from_node_id\|to_node_id" backend_django/apps/navigation/serializers.py
# → must return at least 2 results
```

---

### ISSUE-C02 🔴 AdminNavGraph Sends Integer Coordinates — Backend Expects Floats (0.0–1.0)
**File:** `frontend/src/components/admin/AdminNavGraph.vue`

**Problem:** The admin node editor saves coordinates as raw integers (e.g. `x: 10, y: 0`). The `NavigationNode` model stores `x`/`y` as `FloatField` (normalized 0.0–1.0). Any nodes created via the admin UI cluster in one corner of the map.

**Find the node creation/save logic in `AdminNavGraph.vue` where x and y are saved.** Look for code like:
```javascript
x: event.clientX,   // or offsetX, or any raw pixel value
y: event.clientY,
```
OR mock data like:
```javascript
{ x: 10, y: 0 }
{ x: 5,  y: 3 }
```

**Replace** any raw pixel coordinate being saved with normalized values:
```javascript
// Before saving a node's position, normalize to 0.0–1.0 range:
const svgRect = svgElement.getBoundingClientRect()
const x = (event.clientX - svgRect.left) / svgRect.width
const y = (event.clientY - svgRect.top)  / svgRect.height
// Then save: { x: parseFloat(x.toFixed(6)), y: parseFloat(y.toFixed(6)) }
```

**VERIFY:**
```bash
grep -n "x: [0-9]\+," frontend/src/components/admin/AdminNavGraph.vue
# → must return 0 results (no bare integer x/y assignments)
grep -n "getBoundingClientRect\|toFixed" frontend/src/components/admin/AdminNavGraph.vue
# → must return results showing normalization is in place
```

---

### ISSUE-C03 🔴 QR Scanner Sends Wrong Query Parameter — Navigate View Gets Blank Page
**Files:** Any `QRScanner` view file and `frontend/src/views/NavigateView.vue`

**Problem:** The QR scanner routes with `query: { destination: location }`. NavigateView only reads `route.query.to` and `route.query.from`. The `destination` param is silently ignored.

**Step 1 — Find the QR scanner routing code.** Search for:
```bash
grep -rn "destination:" frontend/src --include="*.vue"
```
Find the line that does something like:
```javascript
router.push({ path: '/navigate', query: { destination: locationId } })
```
**Replace with:**
```javascript
router.push({ path: '/navigate', query: { to: locationId } })
```

**Step 2 — Confirm NavigateView reads `route.query.to`.** In `NavigateView.vue`, find the `onMounted` or `watch` that sets the initial destination. Confirm it reads:
```javascript
const toParam = route.query.to
```
If it still references `route.query.destination`, replace with `route.query.to`.

**VERIFY:**
```bash
grep -rn "query.*destination\b" frontend/src --include="*.vue"
# → must return 0 results (no route using 'destination' key)
grep -n "route.query.to" frontend/src/views/NavigateView.vue
# → must return at least 1 result
```

---

### ISSUE-C04 🔴 Feedback Category Values Mismatch — All Submissions Fail Validation
**Files:** `frontend/src/views/FeedbackView.vue` and `backend_django/apps/feedback/models.py`

**Problem:** The Feedback model uses `snake_case` choices like `map_accuracy`, `navigation`, `general`. FeedbackView sends title-case strings like `"Map Accuracy"`, `"Navigation"`, `"General"`. Django DRF rejects every category value, silently dropping or erroring submissions.

**Step 1 — Find the categories array in FeedbackView.vue:**
```javascript
const categories = ['General', 'Map Accuracy', 'Navigation', 'Facilities', 'Other']
```
OR however it's defined. Check what values are sent to the API in the submit handler.

**Step 2 — Check the exact CATEGORIES choices in `backend_django/apps/feedback/models.py`:**
```python
CATEGORIES = [
    ('general',       'General'),
    ('map_accuracy',  'Map Accuracy'),
    ('navigation',    'Navigation'),
    ('facilities',    'Facilities'),
    ('other',         'Other'),
]
```

**Step 3 — Fix FeedbackView.vue** to send the snake_case key, not the display label. Change the categories definition to objects:
```javascript
const categories = [
  { value: 'general',      label: 'General' },
  { value: 'map_accuracy', label: 'Map Accuracy' },
  { value: 'navigation',   label: 'Navigation' },
  { value: 'facilities',   label: 'Facilities' },
  { value: 'other',        label: 'Other' },
]
```
Update the template to display `cat.label` and bind `cat.value`:
```html
<button
  v-for="cat in categories"
  :key="cat.value"
  :class="{ 'feedback-selected': category === cat.value }"
  @click="category = cat.value"
>{{ cat.label }}</button>
```
Confirm the submit payload sends `category` (which is now a snake_case value, not a label).

**VERIFY:**
```bash
grep -n "'General'\|'Map Accuracy'\|'Navigation'" frontend/src/views/FeedbackView.vue
# → must return 0 results as bare strings in the categories list
grep -n "cat.value\|cat.label" frontend/src/views/FeedbackView.vue
# → must return results
```

---

### ISSUE-C05 🔴 InfoView Calls Admin-Only Endpoint for Public Directory — 403 for All Users
**Files:** `frontend/src/views/InfoView.vue` and `backend_django/apps/users/views.py`

**Problem:** InfoView requests `/api/users/` for instructor and employee listings. That endpoint requires admin authentication. Public users always receive a 403 and see hardcoded fake data. The backend already has a `PublicDirectoryView` at `/api/users/public-directory/` — InfoView just needs to use it.

**In `InfoView.vue`**, find where it calls the users API for instructors/employees:
```javascript
// Look for something like:
const res = await api.get('/users/')
// OR
const res = await api.get('/users/?role=instructor')
```
**Replace with the public endpoint:**
```javascript
const res = await api.get('/users/public-directory/')
```

Confirm this endpoint exists in `backend_django/apps/users/urls.py`. If not, add:
```python
path('public-directory/', PublicDirectoryView.as_view(), name='public-directory'),
```
And confirm `PublicDirectoryView` has `permission_classes = []`.

**VERIFY:**
```bash
grep -n "public-directory" frontend/src/views/InfoView.vue
# → must return at least 1 result
grep -n "public-directory\|PublicDirectoryView" backend_django/apps/users/urls.py
# → must return at least 1 result
grep -n "permission_classes = \[\]" backend_django/apps/users/views.py
# → must confirm PublicDirectoryView has empty permission_classes
```

---

### ISSUE-C06 🔴 PWA Icons Wrong Path — App Will Not Install on Any Device
**Files:** `frontend/vite.config.js`, `frontend/public/manifest.json`

**Problem:** Both files reference `/icons/icon-192.png` and `/icons/icon-512.png`. The `frontend/public/` directory has no `icons/` folder. The actual icon files are in `web/icons/` outside Vite's scope. The PWA install prompt will silently fail on all devices.

**Step 1 — Copy the icons into the correct location:**
```bash
mkdir -p frontend/public/icons
cp web/icons/* frontend/public/icons/
```

**Step 2 — Check and standardize filenames.** The icons in `web/icons/` may be named `Icon-192.png` (capital I). Rename or copy to lowercase:
```bash
ls web/icons/
# Copy with lowercase names:
cp web/icons/Icon-192.png frontend/public/icons/icon-192.png
cp web/icons/Icon-512.png frontend/public/icons/icon-512.png
# Copy any other sizes found
```

**Step 3 — Confirm `vite.config.js` references match exactly:**
The manifest section in `vite.config.js` should have:
```javascript
icons: [
  { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
  { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
],
```

**Step 4 — Confirm `frontend/public/manifest.json` uses the same paths.**

**VERIFY:**
```bash
ls frontend/public/icons/
# → must show icon-192.png and icon-512.png (lowercase)
grep -n "icon-192\|icon-512" frontend/vite.config.js
# → must return results with paths matching /icons/icon-*.png
```

---

### ISSUE-C07 🔴 NavigateView Hardcoded Locations — Admin Panel Changes Have No Effect
**File:** `frontend/src/views/NavigateView.vue`

**Problem:** The `locations` dropdown list in NavigateView is a static hardcoded array of 18 building names. `loadData()` fetches map markers for the visual but never populates the navigation dropdown. Adding/removing buildings in the admin panel has zero effect on navigation options.

**Find the hardcoded locations array in `NavigateView.vue`:**
```javascript
const locations = ref([
  { id: 'entrance', name: 'Main Entrance' },
  { id: 'mst',      name: 'MST Building' },
  // ... more hardcoded items
])
```

**Replace** the static array with a computed property loaded from the backend paths API. In the `loadData` function that already fetches `availablePaths`, extract unique location IDs and names:
```javascript
const locations = ref([])

async function loadData() {
  // ... existing paths fetch ...
  const pathsRes = await api.get('/navigation/paths/')
  availablePaths.value = pathsRes.data

  // Build locations list from all unique elementIds in paths
  const locationMap = new Map()
  for (const path of pathsRes.data) {
    // Each path has elementIds array — first element is the "from" node
    if (path.elementIds && path.elementIds.length > 0) {
      const nodeId = path.elementIds[0]
      if (!locationMap.has(nodeId)) {
        locationMap.set(nodeId, { id: nodeId, name: path.from_name || nodeId })
      }
    }
    // Also add destination
    if (path.to) {
      if (!locationMap.has(path.to)) {
        locationMap.set(path.to, { id: path.to, name: path.name || path.to })
      }
    }
  }
  locations.value = Array.from(locationMap.values())
}
```

**VERIFY:**
```bash
grep -n "Main Entrance\|MST Building\|hardcoded" frontend/src/views/NavigateView.vue
# → must return 0 results (no hardcoded location names)
grep -n "locationMap\|from availablePaths\|locations.value" frontend/src/views/NavigateView.vue
# → must return results showing dynamic population
```

---

### ISSUE-C08 🔴 super_admin Role Label Incorrect — Shows Wrong Title Everywhere
**File:** `backend_django/apps/users/models.py`

**Problem:** `ROLE_CHOICES` has `('super_admin', 'Safety and Security Office')` — the same label as the `safety_security` department. The System Administrator role displays the wrong name in audit logs, admin panel, and all announcement attributions.

**Find in `models.py`:**
```python
ROLE_CHOICES = [
    ('super_admin',   'Safety and Security Office'),
```
**Replace with:**
```python
ROLE_CHOICES = [
    ('super_admin',   'System Administrator'),
```

**VERIFY:**
```bash
grep -n "super_admin.*Safety\|super_admin.*Security" backend_django/apps/users/models.py
# → must return 0 results
grep -n "super_admin.*System Administrator" backend_django/apps/users/models.py
# → must return 1 result
```

---

### ISSUE-C09 🔴 Favorites ID Collision Between MapView and HomeView
**Files:** `frontend/src/views/MapView.vue` and `frontend/src/views/HomeView.vue`

**Problem:** MapView saves favorites with timestamp-based IDs; HomeView saves with database marker IDs. These can silently collide. Deleting a favorite by ID will remove the wrong item.

**Fix — Standardize to composite ID in both files.**

In `MapView.vue`, find where favorites are saved. Replace any bare numeric or timestamp ID:
```javascript
// Find:
id: Date.now()
// OR:
id: marker.id

// Replace with composite:
id: `${marker.marker_type}_${marker.id || marker.map_svg_id || marker.name}`
```

In `HomeView.vue`, find the equivalent favorites save and apply the same composite ID pattern:
```javascript
id: `${marker.marker_type}_${marker.id || marker.map_svg_id || marker.name}`
```

Confirm both files use identical composite ID format when reading favorites for deletion/duplicate-check.

**VERIFY:**
```bash
grep -n "id: Date.now()" frontend/src/views/MapView.vue
# → must return 0 results
grep -n "marker_type.*marker.id\|composite" frontend/src/views/MapView.vue
# → must return at least 1 result
grep -n "marker_type.*marker.id\|composite" frontend/src/views/HomeView.vue
# → must return at least 1 result
```

---

## 🟠 MAJOR BUGS — Broken Functionality / Security

---

### ISSUE-M01 🟠 AdminFeedback Ignores canViewDeptFeedback — Deans Locked Out
**File:** `frontend/src/components/admin/AdminFeedback.vue`

**Problem:** AdminView correctly shows the Feedback nav button to users with `canViewDeptFeedback`. But AdminFeedback.vue only renders content for users with `canViewAllFeedback`. Deans see the button, click it, and get the permission-denied screen.

**In `AdminFeedback.vue`**, find the permission check that gates the content render:
```javascript
// Find something like:
if (!auth.canViewAllFeedback) { /* show denied */ }
```
OR in the template:
```html
<div v-if="auth.canViewAllFeedback">
```

**Replace with** an OR condition that also allows dept-level viewers:
```javascript
if (!auth.canViewAllFeedback && !auth.canViewDeptFeedback) { /* show denied */ }
```
OR in template:
```html
<div v-if="auth.canViewAllFeedback || auth.canViewDeptFeedback">
```

Also ensure that when `canViewDeptFeedback` is true (Dean), the API request filters by department:
```javascript
const endpoint = auth.canViewAllFeedback
  ? '/feedback/'
  : `/feedback/?department=${auth.department}`
```

**VERIFY:**
```bash
grep -n "canViewDeptFeedback" frontend/src/components/admin/AdminFeedback.vue
# → must return at least 2 results (permission check AND API filter)
```

---

### ISSUE-M02 🟠 Notification Read Status Doesn't Sync Across Devices
**File:** `frontend/src/views/NotificationsView.vue`

**Problem:** `NotificationsView` marks notifications as read by mutating local objects and updating IndexedDB. The backend uses a separate `NotificationReadStatus` table. On a second device or after clearing storage, all notifications re-appear as unread.

**Find the read-status update in `NotificationsView.vue`:**
```javascript
notif.is_read = true
db.notifications.update(notif.id, { is_read: true })
```

**Add a backend sync call alongside the local update:**
```javascript
async function markAsRead(notif) {
  // Local update (immediate UI feedback)
  notif.is_read = true
  await db.notifications.update(notif.id, { is_read: true })
  // Backend sync (persist across devices)
  try {
    await api.post(`/notifications/${notif.id}/mark-read/`)
  } catch (e) {
    console.warn('[Notifications] Could not sync read status to server:', e.message)
  }
}
```

Confirm the backend has a `mark-read` endpoint in `backend_django/apps/notifications/urls.py`. If it's missing, add it to the notifications views and urls.

**VERIFY:**
```bash
grep -n "mark-read\|markAsRead" frontend/src/views/NotificationsView.vue
# → must return results showing API call alongside local update
```

---

### ISSUE-M03 🟠 authStore.logout() Has No Redirect — Admin Panel Stays Visible
**File:** `frontend/src/stores/authStore.js`

**Problem:** `logout()` clears tokens but never redirects. The admin shell remains fully rendered until the user manually navigates, and any queued API calls will return 401.

**Find in `authStore.js`:**
```javascript
logout(router = null, redirectPath = '/') {
  api.post('/users/logout/').catch(() => {})
  this.token = this.refreshToken = this.user = null
  sessionStorage.removeItem('tp_token')
  sessionStorage.removeItem('tp_refresh')
  sessionStorage.removeItem('tp_user')
  
  if (router) {
    router.push(redirectPath)
  }
},
```

If this is already present, confirm that **every call site that calls `logout()`** passes the router. Search:
```bash
grep -rn "logout()" frontend/src --include="*.vue"
```

For any call like `auth.logout()` without the router argument, update to:
```javascript
auth.logout(router, '/admin/login')
```

Also add a fallback in the logout action itself for when no router is passed:
```javascript
logout(router = null, redirectPath = '/admin/login') {
  api.post('/users/logout/').catch(() => {})
  this.token = this.refreshToken = this.user = null
  sessionStorage.removeItem('tp_token')
  sessionStorage.removeItem('tp_refresh')
  sessionStorage.removeItem('tp_user')
  
  if (router) {
    router.push(redirectPath)
  } else {
    // Hard fallback if no router injected
    window.location.href = redirectPath
  }
},
```

**VERIFY:**
```bash
grep -n "window.location.href = redirectPath\|router.push(redirectPath)" frontend/src/stores/authStore.js
# → must return both lines
grep -rn "auth.logout()" frontend/src --include="*.vue"
# → every call site must pass router as first argument
```

---

### ISSUE-M04 🟠 ProfileView Computes isLoggedIn From sessionStorage — Bypasses Auth Store
**File:** `frontend/src/views/ProfileView.vue`

**Problem:**
```javascript
const isLoggedIn = computed(() => !!sessionStorage.getItem('tp_token'))
```
This bypasses Pinia entirely. Token expiry or manual `clearTokens()` calls won't update the UI until a page reload.

**Find in `ProfileView.vue`:**
```javascript
const isLoggedIn = computed(() => !!sessionStorage.getItem('tp_token'))
// OR:
const isLoggedIn = computed(() => !!localStorage.getItem('tp_token'))
```
**Replace with:**
```javascript
import { useAuthStore } from '../stores/authStore.js'
const auth = useAuthStore()
const isLoggedIn = computed(() => auth.isLoggedIn)
```

If `useAuthStore` is already imported, just fix the computed:
```javascript
const isLoggedIn = computed(() => auth.isLoggedIn)
```

**VERIFY:**
```bash
grep -n "sessionStorage.getItem.*token\|localStorage.getItem.*token" frontend/src/views/ProfileView.vue
# → must return 0 results
grep -n "auth.isLoggedIn" frontend/src/views/ProfileView.vue
# → must return at least 1 result
```

---

### ISSUE-M05 🟠 NavigationNode Missing is_active in IndexedDB Schema — Wrong Query Results
**File:** `frontend/src/services/db.js`

**Problem:** `db.js` indexes `navigation_nodes` on `is_active`. The `NavigationNode` Django model only has `is_deleted` — there is no `is_active` field. All queries filtering by `is_active` return wrong results.

**Find in `db.js`:**
```javascript
navigation_nodes: '++id, map_svg_id, node_type, floor, is_active',
```
**Replace with:**
```javascript
navigation_nodes: '++id, map_svg_id, node_type, floor, is_deleted',
```

Then search for any code that filters navigation nodes by `is_active`:
```bash
grep -rn "is_active" frontend/src/services/ frontend/src/stores/ frontend/src/views/
```
Replace every `is_active` filter on navigation nodes with `is_deleted === false`:
```javascript
// Old:
.filter(node => node.is_active)
// New:
.filter(node => !node.is_deleted)
```

**VERIFY:**
```bash
grep -n "is_active" frontend/src/services/db.js
# → must return 0 results in the navigation_nodes schema line
grep -n "is_deleted" frontend/src/services/db.js
# → must return at least 1 result in navigation_nodes schema
```

---

### ISSUE-M06 🟠 Flask Chatbot CORS Open to All Origins — Any Site Can Send Requests
**File:** `chatbot_flask/app.py`

**Problem:** Flask CORS is initialized with no origin restrictions. Any website on the internet can call the chatbot API and consume your OpenAI credits.

**Find in `app.py`:**
```python
CORS(app)
# OR:
CORS(app, resources={r"/*": {"origins": "*"}})
```
**Replace with explicit origin whitelist:**
```python
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    # Add your production domain when deployed:
    # "https://technopath-frontend.onrender.com",
], supports_credentials=True)
```

**VERIFY:**
```bash
grep -n "CORS(app)" chatbot_flask/app.py
# → must NOT return a bare CORS(app) with no arguments
grep -n "origins=" chatbot_flask/app.py
# → must return at least 1 result with explicit list
```

---

### ISSUE-M07 🟠 SQL Injection in Flask Chatbot Analytics
**File:** `chatbot_flask/app.py`

**Problem:** Raw SQL uses Python's `.format()` with the `days` parameter from user input — a direct SQL injection vector.

**Find:**
```python
cursor = conn.execute(
    "SELECT COUNT(*) FROM chat_history WHERE created_at >= datetime('now', '-{} days')".format(days)
)
```
and:
```python
cursor = conn.execute(
    "SELECT user_message, bot_reply FROM chat_history WHERE created_at >= datetime('now', '-{} days') ORDER BY created_at DESC".format(days)
)
```

**Replace both with parameterized queries:**
```python
cursor = conn.execute(
    "SELECT COUNT(*) FROM chat_history WHERE created_at >= datetime('now', ? || ' days')",
    (f'-{days}',)
)
```
and:
```python
cursor = conn.execute(
    "SELECT user_message, bot_reply FROM chat_history WHERE created_at >= datetime('now', ? || ' days') ORDER BY created_at DESC",
    (f'-{days}',)
)
```

**VERIFY:**
```bash
grep -n "\.format(days)" chatbot_flask/app.py
# → must return 0 results
```

---

### ISSUE-M08 🟠 Flask Rate Limiter Commented Out — OpenAI Endpoint Unprotected
**File:** `chatbot_flask/app.py`

**Problem:** The Flask-Limiter is fully commented out. The `/chat` endpoint has no rate limiting — it can be hammered to run up unbounded OpenAI costs.

**Find commented-out limiter code** (lines starting with `#`):
```python
# limiter = Limiter(...)
# @limiter.limit("10 per minute")
```

**Uncomment and restore:**
```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)
```
And on the `/chat` route:
```python
@app.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
```

If the limiter is NOT commented out but missing, add it:

**VERIFY:**
```bash
grep -n "limiter = Limiter" chatbot_flask/app.py
# → must return 1 uncommented result
grep -n "@limiter.limit" chatbot_flask/app.py
# → must return at least 1 uncommented result
```

---

### ISSUE-M09 🟠 Flask Chatbot Ignores Conversation History — No Context in AI Replies
**File:** `chatbot_flask/app.py`

**Problem:** The frontend sends a `history` array with every `/chat` request, but Flask ignores it. Every OpenAI call is single-turn with no prior context.

**Find the `generate_reply` function:**
```python
def generate_reply(message: str) -> str:
    ...
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": CAMPUS_CONTEXT},
            {"role": "user",   "content": message}
        ],
```

**Replace with history-aware version:**
```python
def generate_reply(message: str, history: list = None) -> str:
    if not OPENAI_ENABLED or not client:
        return generate_rule_based_reply(message)
    try:
        prior = (history or [])[-6:]  # last 3 turns (6 messages)
        messages = [{"role": "system", "content": CAMPUS_CONTEXT}]
        messages.extend(
            {"role": h["role"], "content": str(h["content"])[:500]}
            for h in prior
        )
        messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
```

**Also update the call site in the `/chat` endpoint:**
```python
history = data.get("history", [])
reply   = generate_reply(message, history=history)
```

**VERIFY:**
```bash
grep -n "history: list\|history=history\|prior = " chatbot_flask/app.py
# → must return 3 results
```

---

### ISSUE-M10 🟠 Flask Debug Mode Has No Guard — Can Run Exposed in Production
**File:** `chatbot_flask/app.py`

**Problem:** `app.run(debug=True)` (or no explicit `debug=False` guard) means if the Flask app is started directly, it exposes the interactive Werkzeug debugger to the network.

**Find at the bottom of `app.py`:**
```python
if __name__ == '__main__':
    app.run(debug=True)
    # OR:
    app.run(host='0.0.0.0', port=5000)
```

**Replace with:**
```python
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    if debug_mode:
        print('[WARNING] Flask running in DEBUG mode — not for production use')
    app.run(
        host='127.0.0.1',  # Bind to localhost only; Gunicorn handles 0.0.0.0 in prod
        port=int(os.getenv('FLASK_PORT', '5187')),
        debug=debug_mode
    )
```

**VERIFY:**
```bash
grep -n "debug=True" chatbot_flask/app.py
# → must return 0 results
grep -n "FLASK_DEBUG" chatbot_flask/app.py
# → must return at least 1 result
```

---

### ISSUE-M11 🟠 Splash Screen Triggers on Every Page Refresh
**File:** `frontend/src/router/index.js`

**Problem:** The splash guard uses `from.matched.length === 0` which is always true on a browser refresh/direct URL load. Users see the full splash animation every time they reload the page.

**Find in the router's `beforeEach` guard:**
```javascript
const isInitialLoad = from.matched.length === 0
if (to.path === '/' && isInitialLoad) {
  next('/splash')
  return
}
```

**Replace with session-aware guard:**
```javascript
const isInitialLoad = from.matched.length === 0
const hasSeenSplash = sessionStorage.getItem('tp_splash_seen')
if (to.path === '/' && isInitialLoad && !hasSeenSplash) {
  sessionStorage.setItem('tp_splash_seen', '1')
  next('/splash')
  return
}
```

**VERIFY:**
```bash
grep -n "tp_splash_seen" frontend/src/router/index.js
# → must return 2 results (getItem and setItem)
```

---

### ISSUE-M12 🟠 PWA skipWaiting Conflicts With registerType: prompt
**File:** `frontend/vite.config.js`

**Problem:** `skipWaiting: true` activates a new Service Worker immediately, but `registerType: 'prompt'` is supposed to ask the user first. The SW updates silently, making the user prompt meaningless.

**Find in `vite.config.js`:**
```javascript
workbox: {
  cleanupOutdatedCaches: true,
  skipWaiting: true,
  clientsClaim: true,
```

**Replace with:**
```javascript
workbox: {
  cleanupOutdatedCaches: true,
  // skipWaiting removed: registerType 'prompt' shows a user dialog before
  // activating a new SW. skipWaiting:true would bypass that dialog entirely.
  clientsClaim: true,
```

**VERIFY:**
```bash
grep -n "skipWaiting" frontend/vite.config.js
# → must return 0 results
```

---

## 🔵 CONFIGURATION & SECURITY FIXES

---

### ISSUE-S01 🔵 DEBUG Default Must Be False in All Settings
**File:** `backend_django/technopath/settings.py`

**Verify first:**
```bash
grep -n "default=True\|default=False" backend_django/technopath/settings.py | grep -i debug
```
If any `DEBUG` config line has `default=True`, change to `default=False`.

**VERIFY:**
```bash
grep -n "DEBUG.*default=True" backend_django/technopath/settings.py
# → must return 0 results
```

---

### ISSUE-S02 🔵 Flask App Not Declared in render.yaml — Chatbot Won't Deploy
**File:** `render.yaml`

**Problem:** `render.yaml` only defines the Django backend and frontend services. The Flask chatbot is never deployed.

**Open `render.yaml` and add a Flask service block.** Find the existing services list and append:
```yaml
  - type: web
    name: technopath-chatbot
    runtime: python
    buildCommand: "cd chatbot_flask && pip install -r requirements.txt"
    startCommand: "cd chatbot_flask && gunicorn app:app"
    envVars:
      - key: OPENAI_API_KEY
        sync: false  # Set manually in Render dashboard — never commit this
      - key: FLASK_DEBUG
        value: "false"
      - key: FLASK_PORT
        value: "5187"
```

**VERIFY:**
```bash
grep -n "technopath-chatbot" render.yaml
# → must return 1 result
grep -n "FLASK_DEBUG" render.yaml
# → must return 1 result
```

---

### ISSUE-S03 🔵 .env.example Contains Insecure Placeholder SECRET_KEY
**File:** `.env.example` (root level — create if missing)

**Find or create** `.env.example` at the root. Ensure:
```
SECRET_KEY=REPLACE_WITH_50_RANDOM_CHARS_NEVER_COMMIT_THIS_VALUE
DATABASE_URL=postgres://USER:PASS@HOST:5432/DBNAME
VITE_API_BASE_URL=http://localhost:8000/api
VITE_FLASK_CHATBOT_URL=http://localhost:5187
OPENAI_API_KEY=REPLACE_WITH_YOUR_OPENAI_KEY
```
Remove any line containing `django-insecure-`.

**VERIFY:**
```bash
grep -n "django-insecure" .env.example
# → must return 0 results
```

---

### ISSUE-S04 🔵 Frontend .env.example Has Wrong Chatbot URL Variable Name
**File:** `frontend/.env.example` (create if missing)

**Ensure** the file contains:
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_FLASK_CHATBOT_URL=http://localhost:5187
```

Confirm `aiChatbot.js` reads `VITE_FLASK_CHATBOT_URL` (not `VITE_CHATBOT_URL` or any other variant):
```bash
grep -n "VITE_FLASK_CHATBOT_URL\|VITE_CHATBOT_URL" frontend/src/services/aiChatbot.js
```
If the variable name doesn't match, standardize to `VITE_FLASK_CHATBOT_URL` in both files.

**VERIFY:**
```bash
grep -n "VITE_FLASK_CHATBOT_URL" frontend/.env.example
# → must return 1 result
grep -n "VITE_CHATBOT_URL[^_]" frontend/src/services/aiChatbot.js
# → must return 0 results (no old mismatched name)
```

---

### ISSUE-S05 🔵 .gitignore Has Merge Conflict Markers — Git Will Ignore Wrong Files
**File:** `.gitignore`

**Check for conflict markers:**
```bash
grep -c "<<<<<\|>>>>>\|=======" .gitignore
```
If any are found, open `.gitignore` and manually resolve the conflict. Keep the correct ignore rules from both sides, remove all `<<<<<<<`, `=======`, and `>>>>>>>` lines.

**VERIFY:**
```bash
grep -c "<<<<<<\|>>>>>>" .gitignore
# → must return 0
```

---

### ISSUE-S06 🔵 Feedback Serializer Missing Rating Validation
**File:** `backend_django/apps/feedback/serializers.py`

**Problem:** The `rating` field accepts any integer. A malformed POST can insert ratings of 0, -5, or 999 into the database.

**Find the Feedback serializer and add a validator:**
```python
from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model  = Feedback
        fields = ['id', 'rating', 'comment', 'category',
                  'facility', 'room', 'is_anonymous', 'location', 'created_at']
```

**VERIFY:**
```bash
grep -n "min_value=1\|max_value=5" backend_django/apps/feedback/serializers.py
# → must return 1 result
```

---

### ISSUE-S07 🔵 Token Refresh Uses Hardcoded URL Instead of VITE_API_BASE_URL
**File:** `frontend/src/services/api.js`

**Find in the refresh interceptor:**
```javascript
const res = await axios.post(`http://localhost:8000/api/auth/refresh/`, { refresh })
```
**Replace with:**
```javascript
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const res = await axios.post(`${backendUrl}/auth/refresh/`, { refresh })
```

**VERIFY:**
```bash
grep -n "localhost:8000" frontend/src/services/api.js
# → must return 0 results (no hardcoded URL in the refresh call)
grep -n "VITE_API_BASE_URL" frontend/src/services/api.js
# → must return at least 1 result
```

---

### ISSUE-S08 🔵 Missing 404 Catch-All Route in Vue Router
**File:** `frontend/src/router/index.js`

**Verify:**
```bash
grep -n "pathMatch" frontend/src/router/index.js
```
If the catch-all route is missing, add before the closing `]`:
```javascript
{
  path: '/:pathMatch(.*)*',
  name: 'NotFound',
  beforeEnter: (to, from, next) => {
    console.warn(`[Router] Unmatched route: ${to.fullPath}`)
    next('/')
  }
},
```

**VERIFY:**
```bash
grep -n "pathMatch" frontend/src/router/index.js
# → must return 1 result
```

---

## 🔁 MANDATORY FINAL VERIFICATION SCAN

After completing ALL 29 fixes above, run EVERY command below.
Print `✅` if the command returns the expected result. Print `❌` if it does not.
**If any ❌ appears — return to that issue and re-apply the fix. Then re-run this scan. Repeat until all 29 show ✅.**

```bash
# === CRITICAL BUGS ===

# C01 — Pathfinding field mismatch
grep -n "x_position\|y_position" frontend/src/services/pathfinder.js
# EXPECT: 0 results ✅ / any results ❌

grep -n "from_node_id\|to_node_id" backend_django/apps/navigation/serializers.py
# EXPECT: 2+ results ✅ / 0 results ❌

# C02 — AdminNavGraph coordinate normalization
grep -n "getBoundingClientRect\|toFixed" frontend/src/components/admin/AdminNavGraph.vue
# EXPECT: results present ✅ / 0 results ❌

# C03 — QR Scanner wrong query param
grep -rn "query:.*destination:" frontend/src --include="*.vue"
# EXPECT: 0 results ✅ / any results ❌

# C04 — Feedback category snake_case
grep -n "'General'\|'Map Accuracy'" frontend/src/views/FeedbackView.vue
# EXPECT: 0 results in categories array ✅ / results found ❌

grep -n "cat.value\|cat.label" frontend/src/views/FeedbackView.vue
# EXPECT: 2+ results ✅ / 0 results ❌

# C05 — InfoView public directory endpoint
grep -n "public-directory" frontend/src/views/InfoView.vue
# EXPECT: 1+ results ✅ / 0 results ❌

# C06 — PWA icons present
ls frontend/public/icons/icon-192.png frontend/public/icons/icon-512.png
# EXPECT: both files listed ✅ / error ❌

# C07 — NavigateView no hardcoded locations
grep -n "Main Entrance\|MST Building" frontend/src/views/NavigateView.vue
# EXPECT: 0 results in static array ✅ / results found ❌

# C08 — super_admin role label
grep -n "super_admin.*Safety\|super_admin.*Security" backend_django/apps/users/models.py
# EXPECT: 0 results ✅ / any results ❌

grep -n "super_admin.*System Administrator" backend_django/apps/users/models.py
# EXPECT: 1 result ✅ / 0 results ❌

# C09 — Favorites composite ID
grep -n "id: Date.now()" frontend/src/views/MapView.vue
# EXPECT: 0 results ✅ / any results ❌

grep -n "marker_type" frontend/src/views/MapView.vue frontend/src/views/HomeView.vue
# EXPECT: results in both files ✅ / missing from either ❌

# === MAJOR BUGS ===

# M01 — AdminFeedback dept permission
grep -n "canViewDeptFeedback" frontend/src/components/admin/AdminFeedback.vue
# EXPECT: 2+ results ✅ / 0 or 1 result ❌

# M02 — Notification read sync
grep -n "mark-read\|markAsRead" frontend/src/views/NotificationsView.vue
# EXPECT: results with API call ✅ / 0 results ❌

# M03 — Logout redirect
grep -n "window.location.href\|router.push(redirectPath)" frontend/src/stores/authStore.js
# EXPECT: 2 results ✅ / fewer ❌

# M04 — ProfileView auth store
grep -n "sessionStorage.getItem.*token\|localStorage.getItem.*token" frontend/src/views/ProfileView.vue
# EXPECT: 0 results ✅ / any results ❌

grep -n "auth.isLoggedIn" frontend/src/views/ProfileView.vue
# EXPECT: 1+ results ✅ / 0 results ❌

# M05 — db.js is_active → is_deleted
grep -n "is_active" frontend/src/services/db.js
# EXPECT: 0 results in navigation_nodes line ✅ / result found ❌

# M06 — Flask CORS restricted
grep -n "CORS(app)" chatbot_flask/app.py
# EXPECT: 0 bare CORS(app) calls ✅ / bare call found ❌

grep -n "origins=" chatbot_flask/app.py
# EXPECT: 1+ results ✅ / 0 results ❌

# M07 — SQL injection fixed
grep -n "\.format(days)" chatbot_flask/app.py
# EXPECT: 0 results ✅ / any results ❌

# M08 — Rate limiter active
grep -n "limiter = Limiter" chatbot_flask/app.py
# EXPECT: 1 uncommented result ✅ / 0 or commented ❌

grep -n "@limiter.limit" chatbot_flask/app.py
# EXPECT: 1+ uncommented results ✅ / 0 or commented ❌

# M09 — Chatbot history context
grep -n "history: list\|history=history" chatbot_flask/app.py
# EXPECT: 2 results ✅ / fewer ❌

# M10 — Flask debug guard
grep -n "debug=True" chatbot_flask/app.py
# EXPECT: 0 results ✅ / any results ❌

grep -n "FLASK_DEBUG" chatbot_flask/app.py
# EXPECT: 1+ results ✅ / 0 results ❌

# M11 — Splash session guard
grep -n "tp_splash_seen" frontend/src/router/index.js
# EXPECT: 2 results (get + set) ✅ / fewer ❌

# M12 — PWA skipWaiting removed
grep -n "skipWaiting" frontend/vite.config.js
# EXPECT: 0 results ✅ / any results ❌

# === CONFIG / SECURITY ===

# S01 — DEBUG default safe
grep -n "DEBUG.*default=True" backend_django/technopath/settings.py
# EXPECT: 0 results ✅ / any results ❌

# S02 — Flask in render.yaml
grep -n "technopath-chatbot" render.yaml
# EXPECT: 1 result ✅ / 0 results ❌

# S03 — No insecure SECRET_KEY in .env.example
grep -n "django-insecure" .env.example
# EXPECT: 0 results ✅ / any results ❌

# S04 — Correct chatbot env var
grep -n "VITE_FLASK_CHATBOT_URL" frontend/.env.example
# EXPECT: 1 result ✅ / 0 results ❌

grep -n "VITE_CHATBOT_URL[^_]" frontend/src/services/aiChatbot.js
# EXPECT: 0 results ✅ / any results ❌

# S05 — No gitignore conflict markers
grep -c "<<<<<<\|>>>>>>" .gitignore 2>/dev/null || echo "0"
# EXPECT: 0 ✅ / non-zero ❌

# S06 — Feedback rating validated
grep -n "min_value=1" backend_django/apps/feedback/serializers.py
# EXPECT: 1 result ✅ / 0 results ❌

# S07 — Token refresh uses env var
grep -n "localhost:8000" frontend/src/services/api.js
# EXPECT: 0 results ✅ / any results ❌

grep -n "VITE_API_BASE_URL" frontend/src/services/api.js
# EXPECT: 1+ results ✅ / 0 results ❌

# S08 — 404 catch-all route
grep -n "pathMatch" frontend/src/router/index.js
# EXPECT: 1 result ✅ / 0 results ❌
```

---

## 📊 FINAL VERIFICATION REPORT — PRINT THIS WHEN DONE

```
╔══════════════════════════════════════════════════════════════════╗
║            TECHNOPATHY — MASTER FIX VERIFICATION REPORT         ║
╠══════════════════════════════════════════════════════════════════╣
║  CRITICAL BUGS                                                   ║
║  C01  Pathfinding Field Name Mismatch Fixed         ✅ / ❌     ║
║  C02  AdminNavGraph Coordinate Normalization Fixed   ✅ / ❌     ║
║  C03  QR Scanner Query Param Fixed                  ✅ / ❌     ║
║  C04  Feedback Category snake_case Fixed             ✅ / ❌     ║
║  C05  InfoView Public Directory Endpoint Fixed       ✅ / ❌     ║
║  C06  PWA Icons Copied to Correct Path              ✅ / ❌     ║
║  C07  NavigateView Dynamic Locations Fixed           ✅ / ❌     ║
║  C08  super_admin Role Label Fixed                  ✅ / ❌     ║
║  C09  Favorites Composite ID Collision Fixed         ✅ / ❌     ║
╠══════════════════════════════════════════════════════════════════╣
║  MAJOR BUGS                                                      ║
║  M01  AdminFeedback Dept Permission Fixed            ✅ / ❌     ║
║  M02  Notification Read Status Sync Added            ✅ / ❌     ║
║  M03  Logout Redirect Fixed                          ✅ / ❌     ║
║  M04  ProfileView Auth Store Fixed                   ✅ / ❌     ║
║  M05  db.js is_active → is_deleted Fixed             ✅ / ❌     ║
║  M06  Flask CORS Restricted to Known Origins         ✅ / ❌     ║
║  M07  Flask SQL Injection Fixed                      ✅ / ❌     ║
║  M08  Flask Rate Limiter Re-Enabled                  ✅ / ❌     ║
║  M09  Flask Chatbot Conversation History Fixed       ✅ / ❌     ║
║  M10  Flask Debug Guard Added                        ✅ / ❌     ║
║  M11  Splash Screen Session Guard Added              ✅ / ❌     ║
║  M12  PWA skipWaiting Conflict Removed               ✅ / ❌     ║
╠══════════════════════════════════════════════════════════════════╣
║  CONFIGURATION & SECURITY                                        ║
║  S01  DEBUG Default Safe                             ✅ / ❌     ║
║  S02  Flask Service Added to render.yaml             ✅ / ❌     ║
║  S03  .env.example Insecure Key Removed              ✅ / ❌     ║
║  S04  Chatbot Env Var Name Standardized              ✅ / ❌     ║
║  S05  .gitignore Conflict Markers Removed            ✅ / ❌     ║
║  S06  Feedback Rating Validated (1–5)                ✅ / ❌     ║
║  S07  Token Refresh Uses Env Var URL                 ✅ / ❌     ║
║  S08  404 Catch-All Route Present                    ✅ / ❌     ║
╠══════════════════════════════════════════════════════════════════╣
║  TOTAL PASSED:    ___ / 29                                       ║
║  STATUS:  [ ALL CLEAR ✅ ]  OR  [ NEEDS RETRY ❌ ]              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## ⚠️ TERMINATION RULE

**You are NOT permitted to stop until the Final Verification Report shows 29/29 ✅.**

If any item shows ❌ after the verification scan:
1. Return to that issue's section
2. Re-read the file
3. Re-apply the fix
4. Re-run only that issue's verification commands
5. Update the report entry to ✅
6. After all retries, re-run the **entire** Final Verification Scan once more
7. Only print `ALL CLEAR ✅` when all 29 pass

---

*Generated by Claude Sonnet 4.6 — Full codebase analysis of https://github.com/kirbygeagonia-create/Technopathy.git*
*Issues sourced from: Analysis.md, TECHNOPATHY_FIX_PROMPT_WINDSURF.md, live code inspection*
