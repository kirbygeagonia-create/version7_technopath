# TechnoPath — Security & Backend Fix Prompt
### For: Windsurf Kimi K2.5 AI
### Project: `https://github.com/kirbygeagonia-create/version7_technopath.git`
### Run Order: Prompt 2 of 5

---

## ⚙️ OPERATING PROTOCOL — READ BEFORE DOING ANYTHING

```
FOR EACH ISSUE:
  STEP 1 → READ     Open the exact file listed. Read the relevant lines.
  STEP 2 → FIX      Apply the exact code change described.
  STEP 3 → SAVE     Write the file to disk.
  STEP 4 → VERIFY   Run the grep command listed. Confirm expected result.
  STEP 5 → REPORT   Print:
              ✅ FIXED & VERIFIED: [Issue ID] — [description]
              ❌ FAILED: [Issue ID] — [reason] → retry from STEP 1

AFTER ALL ISSUES:
  STEP 6 → Run the FINAL VERIFICATION CHECKLIST
  STEP 7 → Print the FINAL REPORT
  STEP 8 → Any ❌ = return to STEP 1 for that issue
  STEP 9 → Only stop when ALL issues show ✅
```

---

## 📋 CURRENT REPO STATE — ALREADY DONE (DO NOT RE-APPLY)

| What | Status |
|------|--------|
| `funtion_systems/` directory | ✅ DELETED |
| Root-level `package.json` | ✅ DELETED |
| Flask CORS `origins=` explicit whitelist | ✅ ALREADY DONE — skip ISSUE-06 |
| `.gitignore` merge conflict markers | ✅ CLEAN (0 markers) — skip ISSUE-06 |
| Navigation serializer field aliases | ✅ ALREADY DONE |

---

## 🔴 ISSUE-01 — SQL Injection in Chatbot Analytics

**File:** `chatbot_flask/app.py`
**Confirmed present:** Lines ~217, ~223 still use `.format(days)` in raw SQL.

**Find:**
```python
cursor = conn.execute(
    "SELECT COUNT(*) FROM chat_history WHERE created_at >= datetime('now', '-{} days')".format(days)
)
```
**Replace with:**
```python
cursor = conn.execute(
    "SELECT COUNT(*) FROM chat_history WHERE created_at >= datetime('now', ? || ' days')",
    (f'-{days}',)
)
```

**Find:**
```python
cursor = conn.execute(
    "SELECT user_message, bot_reply FROM chat_history WHERE created_at >= datetime('now', '-{} days') ORDER BY created_at DESC".format(days)
)
```
**Replace with:**
```python
cursor = conn.execute(
    "SELECT user_message, bot_reply FROM chat_history WHERE created_at >= datetime('now', ? || ' days') ORDER BY created_at DESC",
    (f'-{days}',)
)
```

**Verify:**
```bash
grep -n "\.format(days)" chatbot_flask/app.py
# EXPECT: 0 results ✅
```

---

## 🔴 ISSUE-02 — Rate Limiter Commented Out — Re-Enable It

**File:** `chatbot_flask/app.py`
**Confirmed:** Limiter is commented out on lines ~33–38 and ~275.

**Find:**
```python
# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     default_limits=["60 per minute"],
#     storage_uri="memory://",
# )
```
**Replace with:**
```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)
```

**Find:**
```python
@app.route("/chat", methods=["POST"])
# @limiter.limit("20 per minute")  # Temporarily disabled
def chat():
```
**Replace with:**
```python
@app.route("/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
```

**Verify:**
```bash
grep -n "limiter = Limiter(" chatbot_flask/app.py
# EXPECT: 1 uncommented result ✅
grep -n "@limiter.limit" chatbot_flask/app.py
# EXPECT: 1 uncommented result ✅
```

---

## 🟠 ISSUE-03 — JWT Tokens in localStorage — Move to sessionStorage

**Context:** Moving to sessionStorage means admins will be logged out when the browser tab is closed. This is intentional for XSS security hardening. If your team prefers persistent sessions, skip this issue.

**File:** `frontend/src/stores/authStore.js`
**Confirmed:** All 11 `localStorage` references to `tp_token`, `tp_refresh`, `tp_user` are still present.

**Find the state initializer:**
```javascript
state: () => ({
    user:         JSON.parse(localStorage.getItem('tp_user')  || 'null'),
    token:        localStorage.getItem('tp_token')            || null,
    refreshToken: localStorage.getItem('tp_refresh')          || null,
  }),
```
**Replace with:**
```javascript
state: () => ({
    user:         JSON.parse(sessionStorage.getItem('tp_user')  || 'null'),
    token:        sessionStorage.getItem('tp_token')            || null,
    refreshToken: sessionStorage.getItem('tp_refresh')          || null,
  }),
```

**Find the login action set:**
```javascript
localStorage.setItem('tp_token',   access)
localStorage.setItem('tp_refresh', refresh)
localStorage.setItem('tp_user',    JSON.stringify(user))
```
**Replace with:**
```javascript
// SECURITY: sessionStorage clears on tab close (reduces XSS exposure window)
sessionStorage.setItem('tp_token',   access)
sessionStorage.setItem('tp_refresh', refresh)
sessionStorage.setItem('tp_user',    JSON.stringify(user))
```

**Find BOTH `removeItem` blocks (logout and clearTokens):**
```javascript
localStorage.removeItem('tp_token')
localStorage.removeItem('tp_refresh')
localStorage.removeItem('tp_user')
```
**Replace each with:**
```javascript
sessionStorage.removeItem('tp_token')
sessionStorage.removeItem('tp_refresh')
sessionStorage.removeItem('tp_user')
```

**File:** `frontend/src/services/api.js`

**Find and replace all 4 remaining localStorage references:**
```javascript
// Find → Replace each:
const token = localStorage.getItem('tp_token')
→ const token = sessionStorage.getItem('tp_token')

const refresh = localStorage.getItem('tp_refresh')
→ const refresh = sessionStorage.getItem('tp_refresh')

localStorage.setItem('tp_token', newToken)
→ sessionStorage.setItem('tp_token', newToken)

localStorage.removeItem('tp_token')
localStorage.removeItem('tp_refresh')
→ sessionStorage.removeItem('tp_token')
   sessionStorage.removeItem('tp_refresh')
```

**Verify:**
```bash
grep -rn "localStorage.getItem('tp_" frontend/src/
# EXPECT: 0 results ✅
grep -rn "localStorage.setItem('tp_" frontend/src/
# EXPECT: 0 results ✅
```

---

## 🟠 ISSUE-04 — Create `frontend/.env.example` with Correct Variable Names

**Context:** This file does not exist yet. The code reads `VITE_FLASK_CHATBOT_URL` but no example file documents this. Port must be `5187`.

**Create `frontend/.env.example`:**
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_FLASK_CHATBOT_URL=http://localhost:5187
```

**Verify:**
```bash
grep "VITE_FLASK_CHATBOT_URL" frontend/.env.example
# EXPECT: 1 result with port 5187 ✅
grep "VITE_CHATBOT_URL[^_]" frontend/.env.example
# EXPECT: 0 results ✅
```

---

## 🟠 ISSUE-05 — Flask debug=True Hardcoded

**File:** `chatbot_flask/app.py`
**Confirmed:** Line ~299 still has `debug=True` literal.

**Find:**
```python
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5187, debug=True)
```
**Replace with:**
```python
if __name__ == "__main__":
    init_db()
    _flask_debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5187, debug=_flask_debug)
```

**Verify:**
```bash
grep -n "debug=True" chatbot_flask/app.py
# EXPECT: 0 results ✅
grep -n "FLASK_DEBUG" chatbot_flask/app.py
# EXPECT: 1+ results ✅
```

---

## ~~ISSUE-06~~ — SKIP — Already Clean

`.gitignore` has **zero** merge conflict markers (confirmed `grep -c "<<<<<<" .gitignore` = 0). No action needed.

However, **do add these lines** to `.gitignore` if not already present:
```
*.msi
node-portable.zip
__pycache__/
*.pyc
.env
*.db
*.sqlite3
dist/
staticfiles/
```

---

## 🟡 ISSUE-07 — Feedback Rating Has No Range Validation

**File:** `backend_django/apps/feedback/serializers.py`
**Confirmed:** Still uses `fields = '__all__'` with no rating validation.

**Find:**
```python
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['is_flagged', 'flag_reason', 'created_at']
```
**Replace with:**
```python
class FeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        allow_null=True,
        required=False,
        help_text='Rating must be between 1 and 5.'
    )

    class Meta:
        model = Feedback
        fields = [
            'id', 'rating', 'comment', 'category',
            'facility', 'room', 'is_anonymous', 'location', 'created_at'
        ]
        read_only_fields = ['id', 'is_flagged', 'flag_reason', 'created_at']
```

**Verify:**
```bash
grep -n "min_value=1" backend_django/apps/feedback/serializers.py
# EXPECT: 1 result ✅
grep -n "__all__" backend_django/apps/feedback/serializers.py
# EXPECT: 0 results ✅
```

---

## 🟡 ISSUE-08 — Audit Log Hard-Coded 300 Limit With No Pagination

**File:** `backend_django/apps/users/views.py`
**Confirmed:** `qs = qs[:300]` is still present.

**Find:**
```python
qs = qs[:300]
return Response([{
```
**Replace with:**
```python
# Pagination
page_size = min(int(request.query_params.get('page_size', 50)), 200)
page      = max(int(request.query_params.get('page', 1)), 1)
total     = qs.count()
qs        = qs[(page - 1) * page_size : page * page_size]
return Response({
    'count':     total,
    'page':      page,
    'page_size': page_size,
    'pages':     (total + page_size - 1) // page_size,
    'results': [{
```

**Find the closing of the response list. Change:**
```python
} for l in qs])
```
**To:**
```python
} for l in qs]
})
```

**Verify:**
```bash
grep -n "'count'" backend_django/apps/users/views.py
# EXPECT: 1+ result inside AuditLogView ✅
grep -n "qs\[:300\]" backend_django/apps/users/views.py
# EXPECT: 0 results ✅
```

---

## 🟡 ISSUE-09 — Token Refresh Uses Relative URL

**File:** `frontend/src/services/api.js`

**Find:**
```javascript
const res = await axios.post('/api/auth/refresh/', { refresh })
```
**Replace with:**
```javascript
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const res = await axios.post(`${backendUrl}/auth/refresh/`, { refresh })
```

**Verify:**
```bash
grep -n "VITE_API_BASE_URL" frontend/src/services/api.js
# EXPECT: 1+ result in the refresh call ✅
grep -n "'/api/auth/refresh/'" frontend/src/services/api.js
# EXPECT: 0 results (no bare relative URL) ✅
```

---

## 🟡 ISSUE-10 — Add Clarifying Comment for Broken Announcement Scopes

**File:** `backend_django/apps/announcements/views.py`

Find the `all_college` / `basic_ed_only` scope check and add a comment block before it:
```python
# NOTE: 'all_college' and 'basic_ed_only' scopes are reserved for a future
# student-facing authentication system. The roles 'college_student' and
# 'basic_ed_student' do not exist in AdminUser.ROLE_CHOICES yet.
# Until student auth is implemented, these scopes match no users.
# Do not create announcements with these scopes via the admin panel
# without first implementing student role support.
elif a.scope == 'all_college' and getattr(user, 'role', None) == 'college_student':
    visible.append(a)
elif a.scope == 'basic_ed_only' and getattr(user, 'role', None) == 'basic_ed_student':
    visible.append(a)
```

**Verify:**
```bash
grep -n "student auth" backend_django/apps/announcements/views.py
# EXPECT: 1 result ✅
```

---

## 🟡 ISSUE-11 — Flask Chatbot Missing From render.yaml

**Context:** `render.yaml` does **not exist** in the repo. Create it from scratch, then add the Flask chatbot service as part of it. Prompt 5 (TASK-A01 and TASK-B05) will add further entries to this same file — create it now with all three services so later prompts can amend it.

**Create `render.yaml` at the repo root:**
```yaml
services:
  # Django Backend API
  - type: web
    name: technopath-backend
    runtime: python
    plan: free
    rootDir: backend_django
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
    startCommand: gunicorn technopath.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.0"
      - key: DEBUG
        value: "false"
      - key: SECRET_KEY
        sync: false   # Set manually in Render dashboard
      - key: DATABASE_URL
        sync: false   # Set manually in Render dashboard — use PostgreSQL
      - key: ALLOWED_HOSTS
        value: ".onrender.com"

  # Flask Chatbot AI Service
  - type: web
    name: technopath-chatbot
    runtime: python
    plan: free
    rootDir: chatbot_flask
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.0"
      - key: FLASK_DEBUG
        value: "false"
      - key: OPENAI_API_KEY
        sync: false   # Set manually in Render dashboard — NEVER commit this key

  # Vue 3 Frontend (Vite)
  - type: web
    name: technopath-frontend
    runtime: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: NODE_VERSION
        value: "18.20.4"
      - key: VITE_API_BASE_URL
        value: https://technopath-backend.onrender.com/api
      - key: VITE_FLASK_CHATBOT_URL
        value: https://technopath-chatbot.onrender.com
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

**Verify:**
```bash
grep -n "technopath-chatbot" render.yaml
# EXPECT: 1 result ✅
grep -n "FLASK_DEBUG" render.yaml
# EXPECT: 1 result ✅
grep -n "OPENAI_API_KEY" render.yaml
# EXPECT: 1 result with sync: false ✅
grep -n "VITE_FLASK_CHATBOT_URL" render.yaml
# EXPECT: 1 result ✅
```

---

## 🔵 ISSUE-12 — Django DEBUG Default Must Be False

**File:** `backend_django/technopath/settings.py`

Find every line with `DEBUG` and `default=True`:
```python
_debug = config('DEBUG', default=True, cast=bool)
```
and:
```python
DEBUG = config('DEBUG', default=True, cast=bool)
```
**Replace `default=True` with `default=False` in all occurrences.**

**Verify:**
```bash
grep -n "DEBUG.*default=True" backend_django/technopath/settings.py
# EXPECT: 0 results ✅
```

---

## 🔵 ISSUE-13 — WhiteNoise Not in Middleware

**File:** `backend_django/technopath/settings.py`

**Find:**
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
```
**Replace with:**
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
```

**After `STATIC_ROOT`, add:**
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Verify:**
```bash
grep -n "WhiteNoiseMiddleware" backend_django/technopath/settings.py
# EXPECT: 1 result ✅
grep -n "STATICFILES_STORAGE" backend_django/technopath/settings.py
# EXPECT: 1 result ✅
```

---

## 🔵 ISSUE-14 — API Throttle Rates Too Permissive

**File:** `backend_django/technopath/settings.py`

**Find:**
```python
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/minute',
        'user': '1000/minute',
    },
```
**Replace with:**
```python
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'user': '120/minute',
    },
```

**Verify:**
```bash
grep -n "1000/minute" backend_django/technopath/settings.py
# EXPECT: 0 results ✅
```

---

## 🔵 ISSUE-15 — No Guard for Missing DATABASE_URL in Production

**File:** `backend_django/technopath/settings.py`

Find the database block. **Replace** the `else` branch (local SQLite fallback) with a guard:

```python
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
elif not DEBUG:
    raise RuntimeError(
        '\n\n'
        '  DATABASE_URL is not set and DEBUG=False.\n'
        '  This means the app is running in production without a database.\n'
        '  Create a PostgreSQL instance in Render and set DATABASE_URL.\n'
        '  SQLite on Render is wiped on every restart — all data would be lost.\n'
    )
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'technopath.db',
        }
    }
```

**Verify:**
```bash
grep -n "RuntimeError" backend_django/technopath/settings.py
# EXPECT: 1 result ✅
```

---

## 🔵 ISSUE-16 — Insecure Placeholder in Root .env.example

**File:** `.env.example` (root level — create if missing)

**Ensure the file contains:**
```
SECRET_KEY=REPLACE_WITH_50_RANDOM_CHARS_NEVER_COMMIT_THIS_VALUE
DATABASE_URL=postgres://USER:PASS@HOST:5432/DBNAME
ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=true
OPENAI_API_KEY=REPLACE_WITH_YOUR_OPENAI_KEY
```

Remove any line containing `django-insecure-`.

**Verify:**
```bash
grep -n "django-insecure" .env.example
# EXPECT: 0 results ✅
grep -n "SECRET_KEY" .env.example
# EXPECT: 1 result ✅
```

---

## 🔵 ISSUE-17 — Splash Screen Shows on Every Refresh

**File:** `frontend/src/router/index.js`
**Confirmed:** Currently uses `localStorage.getItem('tp_splash_v1')` — this persists forever. The prompt wants `sessionStorage` so splash shows once per browser session (clears on tab close).

**Find:**
```javascript
if (to.path === '/' && !localStorage.getItem('tp_splash_v1') && from.path !== '/splash') {
    next('/splash')
    return
  }
```
**Replace with:**
```javascript
const isInitialLoad = from.matched.length === 0
const hasSeenSplash = sessionStorage.getItem('tp_splash_seen')
if (to.path === '/' && isInitialLoad && !hasSeenSplash) {
    sessionStorage.setItem('tp_splash_seen', '1')
    next('/splash')
    return
  }
```

**Verify:**
```bash
grep -n "tp_splash_seen" frontend/src/router/index.js
# EXPECT: 2 results (getItem + setItem) ✅
grep -n "tp_splash_v1" frontend/src/router/index.js
# EXPECT: 0 results ✅
```

---

## 🔵 ISSUE-18 — Missing 404 Catch-All Route

**File:** `frontend/src/router/index.js`

Add this as the LAST route, before the closing `]`:
```javascript
  // 404 catch-all — redirect unknown routes to home
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    beforeEnter: (to, from, next) => {
      console.warn(`[Router] No route matched: ${to.fullPath} — redirecting to home`)
      next('/')
    }
  },
```

**Verify:**
```bash
grep -n "pathMatch" frontend/src/router/index.js
# EXPECT: 1 result ✅
```

---

## 🔵 ISSUE-19 — Flask Chatbot Ignores Conversation History

**File:** `chatbot_flask/app.py`

**Find the `generate_reply` function signature:**
```python
def generate_reply(message: str) -> str:
```
**Replace with:**
```python
def generate_reply(message: str, history: list = None) -> str:
```

**Find the messages list inside `generate_reply`:**
```python
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CAMPUS_CONTEXT},
                {"role": "user", "content": message}
            ],
```
**Replace with:**
```python
        prior = (history or [])[-6:]
        messages = [{"role": "system", "content": CAMPUS_CONTEXT}]
        messages.extend({"role": h["role"], "content": str(h["content"])[:500]} for h in prior)
        messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
```

**Find the call-site in the `/chat` endpoint:**
```python
    reply = generate_reply(message)
```
**Replace with:**
```python
    history = data.get("history", [])
    reply = generate_reply(message, history=history)
```

**Verify:**
```bash
grep -n "history: list" chatbot_flask/app.py
# EXPECT: 1 result ✅
grep -n "data.get(\"history\"" chatbot_flask/app.py
# EXPECT: 1 result ✅
```

---

## 🔁 FINAL VERIFICATION CHECKLIST

```bash
# Security
grep -n "\.format(days)" chatbot_flask/app.py                              && echo "FAIL" || echo "PASS ISSUE-01: SQL injection fixed"
grep -n "limiter = Limiter(" chatbot_flask/app.py                          && echo "PASS ISSUE-02: limiter active" || echo "FAIL"
grep -rn "localStorage.getItem('tp_" frontend/src/                        && echo "FAIL" || echo "PASS ISSUE-03: sessionStorage"
grep -n "VITE_FLASK_CHATBOT_URL" frontend/.env.example                    && echo "PASS ISSUE-04: env file" || echo "FAIL"
grep -n "debug=True" chatbot_flask/app.py                                  && echo "FAIL" || echo "PASS ISSUE-05: debug guard"

# ISSUE-06: SKIP (already clean)

grep -n "min_value=1" backend_django/apps/feedback/serializers.py         && echo "PASS ISSUE-07: rating validated" || echo "FAIL"
grep -n "qs\[:300\]" backend_django/apps/users/views.py                   && echo "FAIL" || echo "PASS ISSUE-08: audit paginated"
grep -n "VITE_API_BASE_URL" frontend/src/services/api.js                  && echo "PASS ISSUE-09: refresh URL" || echo "FAIL"
grep -n "student auth" backend_django/apps/announcements/views.py         && echo "PASS ISSUE-10: scope comment" || echo "FAIL"
grep -n "technopath-chatbot" render.yaml                                   && echo "PASS ISSUE-11: render.yaml" || echo "FAIL"
grep -n "DEBUG.*default=True" backend_django/technopath/settings.py       && echo "FAIL" || echo "PASS ISSUE-12: DEBUG safe"
grep -n "WhiteNoiseMiddleware" backend_django/technopath/settings.py      && echo "PASS ISSUE-13: whitenoise" || echo "FAIL"
grep -n "1000/minute" backend_django/technopath/settings.py               && echo "FAIL" || echo "PASS ISSUE-14: throttle"
grep -n "RuntimeError" backend_django/technopath/settings.py              && echo "PASS ISSUE-15: DB guard" || echo "FAIL"
grep -n "django-insecure" .env.example                                     && echo "FAIL" || echo "PASS ISSUE-16: secret key"
grep -n "tp_splash_seen" frontend/src/router/index.js                     && echo "PASS ISSUE-17: splash guard" || echo "FAIL"
grep -n "pathMatch" frontend/src/router/index.js                          && echo "PASS ISSUE-18: 404 route" || echo "FAIL"
grep -n "history: list" chatbot_flask/app.py                               && echo "PASS ISSUE-19: chat history" || echo "FAIL"
```

---

## 📊 FINAL REPORT

```
╔══════════════════════════════════════════════════════════════╗
║         TECHNOPATHY SECURITY & BACKEND FIX REPORT           ║
╠══════════════════════════════════════════════════════════════╣
║  ISSUE-01  SQL Injection Fixed                  ✅ / ❌     ║
║  ISSUE-02  Rate Limiter Re-Enabled              ✅ / ❌     ║
║  ISSUE-03  JWT Moved to sessionStorage          ✅ / ❌     ║
║  ISSUE-04  .env.example Created                 ✅ / ❌     ║
║  ISSUE-05  Flask Debug Guard Added              ✅ / ❌     ║
║  ISSUE-06  .gitignore — SKIPPED (already clean) ✅ SKIP     ║
║  ISSUE-07  Feedback Rating Validated (1–5)      ✅ / ❌     ║
║  ISSUE-08  Audit Log Paginated                  ✅ / ❌     ║
║  ISSUE-09  Token Refresh URL Fixed              ✅ / ❌     ║
║  ISSUE-10  Announcement Scopes Documented       ✅ / ❌     ║
║  ISSUE-11  render.yaml Created w/ Flask Service ✅ / ❌     ║
║  ISSUE-12  DEBUG Default Set to False           ✅ / ❌     ║
║  ISSUE-13  WhiteNoise Configured                ✅ / ❌     ║
║  ISSUE-14  API Throttle Rates Tightened         ✅ / ❌     ║
║  ISSUE-15  DB Guard for Missing DATABASE_URL    ✅ / ❌     ║
║  ISSUE-16  .env.example Sanitized              ✅ / ❌     ║
║  ISSUE-17  Splash Screen Session Guard          ✅ / ❌     ║
║  ISSUE-18  404 Catch-All Route Added            ✅ / ❌     ║
║  ISSUE-19  Chatbot Conversation History Fixed   ✅ / ❌     ║
╠══════════════════════════════════════════════════════════════╣
║  TOTAL:  ___ / 19 PASSED  (Issue-06 skipped)               ║
║  STATUS: [ ALL CLEAR ✅ ] or [ NEEDS RETRY ❌ ]             ║
╚══════════════════════════════════════════════════════════════╝
```

**Do NOT stop until all 19 actionable issues show ✅.**
