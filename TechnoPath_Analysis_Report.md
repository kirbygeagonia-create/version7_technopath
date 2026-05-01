# TechnoPath: SEAIT Guide Map and Navigation System
## Conflict Analysis Report & Windsurf Kimi K2.5 Fix Prompt

**Repository:** `https://github.com/kirbygeagonia-create/version7_technopath.git`  
**Analyzed by:** Senior Software Engineer — System Conflict Analysis  
**Date:** May 1, 2026

---

## 1. Analysis Summary

The TechnoPath system is a Vue 3 + Django REST Framework PWA for campus navigation. The codebase is architecturally sound in its `frontend/` directory but suffers from **four categories of confirmed conflicts and errors** that can cause broken builds, navigation failures, incorrect map markers, and dead import references. The root cause is the presence of a legacy staging directory (`funtion_systems/`) that diverged heavily from the canonical `frontend/src/` codebase, combined with a field-name mismatch between the Django model layer and the Vue frontend.

---

## 2. Identified Issues

### ISSUE 1 — Diverged Duplicate View & Service Files
**Severity: HIGH | Causes build confusion and developer errors**

The directory `funtion_systems/` contains 8 files that also exist in `frontend/src/` but with **significant content divergence**:

| File | Divergence (diff lines) |
|---|---|
| `NavigateView.vue` | 1,451 lines different |
| `HomeView.vue` | 711 lines different |
| `AdminView.vue` | 364 lines different |
| `MapView.vue` | 130 lines different |
| `pathfinder.js` | Identical (safe) |
| `offlineData.js` | Identical (safe) |
| `geolocation.js` | Present in both |
| `InfoView.vue` | Present in both |

The `funtion_systems/` versions of `NavigateView.vue` and `HomeView.vue` are substantially older and are NOT referenced by the Vite build. However, their presence creates severe confusion for developers and AI coding assistants (including Windsurf), which may patch the wrong file.

**Fix:** Archive or delete `funtion_systems/`. The canonical source is exclusively `frontend/src/`.

---

### ISSUE 2 — Broken Imports Inside `funtion_systems/`
**Severity: HIGH | Runtime crash if any file from this directory is loaded**

`funtion_systems/offlineData.js` and `funtion_systems/pathfinder.js` import from relative paths that do not exist in that directory:

```js
// funtion_systems/offlineData.js
import db from './db.js'      // ❌ MISSING — no db.js in funtion_systems/
import api from './api.js'    // ❌ MISSING — no api.js in funtion_systems/
import { isOnline } from './sync.js'  // ❌ MISSING — no sync.js in funtion_systems/

// funtion_systems/pathfinder.js
import api from './api.js'    // ❌ MISSING
```

These files cannot execute. If any future developer imports them, the app will crash at module load time.

**Fix:** Delete `funtion_systems/` entirely, or at minimum remove the broken JS files.

---

### ISSUE 3 — Duplicate `sw.js` Service Worker Conflict
**Severity: MEDIUM | Can cause stale PWA caching in production**

Two service worker files exist:
- `frontend/public/sw.js` — correct location, served by Vite
- `funtion_systems/sw.js` — orphan file, never served

The Vite config also registers a `VitePWA`-generated service worker separately. This means there are potentially **three service worker definitions** in the repository. If the wrong one is deployed or cached, users will receive stale assets with no update path.

**Fix:** Confirm `frontend/public/sw.js` is the correct one (it is). Delete `funtion_systems/sw.js`. Ensure `vite-plugin-pwa` is the only SW generator — do not manually manage `sw.js` alongside it.

---

### ISSUE 4 — Root-Level `package.json` Version Conflict
**Severity: MEDIUM | Can break CI/CD and automated tooling**

There is a `package.json` at the repository root:
```json
{ "devDependencies": { "vite": "^8.0.8" } }
```

And a correct one at `frontend/package.json` which pins:
```json
{ "devDependencies": { "vite": "^6.2.0", "@vitejs/plugin-vue": "^5.2.0" } }
```

Vite `^8.0.8` does not exist (latest stable is 6.x as of this writing). Running `npm install` at the repo root will either fail or install a mismatched version. Any CI pipeline that runs from the root directory will be broken.

**Fix:** Delete root `package.json`. All frontend tooling must run from `frontend/`.

---

### ISSUE 5 — `Facility` Model Missing `x_position` / `y_position` Fields
**Severity: HIGH | Map markers render at wrong positions or crash**

`frontend/src/views/HomeView.vue` and `MapView.vue` render facility map markers using:
```js
left: `${marker.x_position * 100}%`,
top:  `${marker.y_position * 100}%`,
```

However, the Django `Facility` model (`backend_django/apps/facilities/models.py`) does **not** have `x_position` or `y_position` fields. It has `latitude` and `longitude` (geographic coordinates), not SVG-relative positions. The serializer uses `fields = '__all__'`, so these fields are simply absent from API responses.

This means all facility markers render at position `NaN%` (i.e., `0, 0` top-left corner), stacking on top of each other.

**Fix:** Add `x_position` and `y_position` FloatField to the `Facility` model, create a migration, and update the admin panel to populate them. Alternatively, map `latitude`/`longitude` to `x_position`/`y_position` in the serializer if the coordinates are already in SVG-relative format.

---

### ISSUE 6 — Flask Chatbot Missing Production CORS Origins
**Severity: LOW-MEDIUM | Chatbot fails when deployed to a real domain**

`chatbot_flask/app.py` restricts CORS to only `localhost` origins. The Django backend has a similar issue — `settings.py` lists only localhost in `CORS_ALLOWED_ORIGINS`. When the system is deployed to a production URL (e.g., a GitHub Pages domain or a VPS), all API and chatbot calls from the frontend will be blocked by CORS.

**Fix:** Add the production domain to both `CORS_ALLOWED_ORIGINS` in `settings.py` and the CORS origins list in `chatbot_flask/app.py`. Store these as environment variables via `.env`.

---

### ISSUE 7 — Vite Base URL vs. Service Worker Registration Mismatch
**Severity: MEDIUM | PWA install/offline mode broken in production**

`vite.config.js` sets `base: '/seait-technopath/'` (a subdirectory deployment). But `main.js` registers the service worker at:
```js
navigator.serviceWorker.register('/sw.js')
```

This path does not account for the base URL. In production, the correct path would be `/seait-technopath/sw.js`. The `VitePWA` plugin handles this automatically — but the **manual `serviceWorker.register()` call in `main.js` overrides it** with the wrong path.

**Fix:** Remove the manual `serviceWorker.register()` call from `main.js`. `vite-plugin-pwa` with `registerType: 'autoUpdate'` already handles registration correctly and respects the `base` URL.

---

## 3. Windsurf Kimi K2.5 Prompt

Copy and paste the following prompt directly into Windsurf Kimi K2.5 with the repository open:

---

```
You are fixing the TechnoPath SEAIT Guide Map and Navigation System (Vue 3 + Django REST Framework PWA).
The repository is already open. Perform ALL of the following fixes in order:

---

STEP 1 — DELETE the legacy `funtion_systems/` directory entirely.
It is a stale staging folder that is NOT imported by the Vite build.
All canonical source files live in `frontend/src/`.
Deleting it eliminates 8 conflicting duplicate files and 3 broken import chains.
Command: Remove the `funtion_systems/` directory and all its contents.

---

STEP 2 — DELETE the root-level `package.json`.
It pins `vite: ^8.0.8` which is a non-existent version and conflicts with `frontend/package.json`.
The only valid package.json for the frontend is at `frontend/package.json`.
All npm commands must be run from inside the `frontend/` directory.

---

STEP 3 — FIX the service worker registration in `frontend/src/main.js`.
REMOVE this entire block:
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('[SW] Registered:', reg.scope))
      .catch(err => console.warn('[SW] Registration failed:', err))
  }
REASON: vite-plugin-pwa with registerType: 'autoUpdate' already auto-registers the correct SW
at the right base path (/seait-technopath/). The manual call overrides it with a wrong path.

---

STEP 4 — ADD x_position and y_position to the Facility Django model.
File: `backend_django/apps/facilities/models.py`
ADD these two fields to the Facility class after the `longitude` field:
  x_position = models.FloatField(blank=True, null=True, help_text='SVG-relative X position (0.0–1.0)')
  y_position = models.FloatField(blank=True, null=True, help_text='SVG-relative Y position (0.0–1.0)')

Then create a new migration:
  cd backend_django && python manage.py makemigrations facilities --name="add_xy_position_to_facility"

---

STEP 5 — FIX HomeView.vue marker position rendering.
File: `frontend/src/views/HomeView.vue`
Find the markerStyle computed function (around line 920):
  left: `${marker.x_position * 100}%`,
  top: `${marker.y_position * 100}%`,
Change to use safe fallback values:
  left: `${((marker.x_position ?? 0.5) * 100).toFixed(2)}%`,
  top: `${((marker.y_position ?? 0.5) * 100).toFixed(2)}%`,

---

STEP 6 — FIX CORS for production deployment.
File: `backend_django/technopath/settings.py`
In CORS_ALLOWED_ORIGINS, add a line that reads from environment:
  config('CORS_EXTRA_ORIGIN', default='', cast=str),
Then filter empty strings:
  CORS_ALLOWED_ORIGINS = [o for o in [...existing list..., config('CORS_EXTRA_ORIGIN', default='')] if o]

File: `chatbot_flask/app.py`
Replace the hardcoded origins list with:
  import os
  ALLOWED_ORIGINS = [o.strip() for o in os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:4173').split(',') if o.strip()]
  CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

---

STEP 7 — VERIFY imports in NavigateView and MapView still resolve correctly after cleanup.
Files: `frontend/src/views/NavigateView.vue`, `frontend/src/views/MapView.vue`
Confirm these imports resolve:
  - `../services/pathManager.js` ✓
  - `../composables/useLocations.js` ✓
  - `../assets/SEAITMAP.svg` ✓
  - `../services/offlineData.js` ✓
  - `../services/sync.js` ✓
If any are broken, fix the import path relative to `frontend/src/views/`.

---

After all steps, run:
  cd frontend && npm install && npm run build
Confirm the build completes with zero errors. Then run:
  cd ../backend_django && python manage.py migrate
Confirm migrations apply cleanly.
```

---

## 4. Implementation Steps

**Step A — Backup first**
```bash
cd version7_technopath
git checkout -b fix/resolve-conflicts-and-errors
```

**Step B — Apply the Windsurf prompt above.** Let Kimi K2.5 execute steps 1–7 sequentially.

**Step C — Manual verification after Windsurf completes:**
```bash
# Frontend build test
cd frontend && npm install && npm run build

# Django migration check
cd ../backend_django && python manage.py migrate --check

# Confirm funtion_systems is gone
ls funtion_systems/    # Should say: No such file or directory

# Confirm root package.json is gone
cat package.json       # Should say: No such file or directory

# Confirm SW manual registration is removed
grep -n "serviceWorker.register" frontend/src/main.js  # Should return nothing
```

**Step D — Test the live system:**
1. Start Django: `cd backend_django && python manage.py runserver`
2. Start Flask chatbot: `cd chatbot_flask && python app.py`
3. Start Vite: `cd frontend && npm run dev`
4. Navigate to `http://localhost:5173` and verify:
   - Map loads with correct facility markers
   - Navigation pathfinding works (Admin → Map Management → create nodes/edges first)
   - Chatbot responds at `/chatbot` route
   - PWA install prompt appears (SW registered correctly)

**Step E — Commit and push:**
```bash
git add -A
git commit -m "fix: resolve funtion_systems conflicts, SW registration, Facility xy fields, CORS"
git push origin fix/resolve-conflicts-and-errors
```

---

## 5. Summary Table

| # | Issue | File(s) | Severity | Fix |
|---|---|---|---|---|
| 1 | 8 diverged duplicate files in `funtion_systems/` | `funtion_systems/*` | HIGH | Delete directory |
| 2 | Broken imports (`db.js`, `api.js`, `sync.js` missing) | `funtion_systems/offlineData.js`, `pathfinder.js` | HIGH | Delete directory |
| 3 | Duplicate `sw.js` service worker | `funtion_systems/sw.js` | MEDIUM | Delete with directory |
| 4 | Root `package.json` pins nonexistent Vite 8 | `package.json` | MEDIUM | Delete file |
| 5 | Facility model missing `x_position`/`y_position` | `facilities/models.py`, `HomeView.vue` | HIGH | Add fields + migration |
| 6 | CORS hardcoded to localhost only | `settings.py`, `chatbot_flask/app.py` | MEDIUM | Use env variable |
| 7 | Manual SW registration overrides Vite PWA plugin | `frontend/src/main.js` | MEDIUM | Remove manual block |
