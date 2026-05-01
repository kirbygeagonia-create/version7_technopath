

---

## Prompt Execution Order (confirmed correct)

| Order | File | Role |
|-------|------|------|
| 1st | `WINDSURF_FIX_PROMPT.md` | UI polish — skeletons, animations, components |
| 2nd | `TECHNOPATHY_FIX_PROMPT_WINDSURF.md` | Security & backend fixes |
| 3rd | `TECHNOPATHY_MASTER_FIX_PROMPT.md` | 29-issue comprehensive fix pass |
| 4th | `TECHNOPATHY_OVERHAUL_PROMPT.md` | QR cleanup, onboarding, UI overhaul |
| 5th | `02_FEATURE_IMPROVEMENTS_PROMPT.md` | Deployment + feature enhancements |

---

## ⚠️ REQUIRED ADJUSTMENTS BEFORE RUNNING

### Adjustment 1 — `TECHNOPATHY_MASTER_FIX_PROMPT.md` (Issue-C01): Navigation serializer fix is ALREADY DONE

**What the prompt says to do:** Add `from_node_id` / `to_node_id` and `x_position` / `y_position` aliases to the navigation serializer.

**What's in the repo NOW:**
```python
# backend_django/apps/navigation/serializers.py — ALREADY FIXED
x_position = serializers.FloatField(source='x', read_only=True)
y_position = serializers.FloatField(source='y', read_only=True)
from_node_id = serializers.IntegerField(source='from_node.id', read_only=True)
to_node_id = serializers.IntegerField(source='to_node.id', read_only=True)
```

**Action:** Tell Windsurf to **SKIP Issue-C01**. If it tries to apply it anyway, it may produce a duplicate field declaration error.

---

### Adjustment 2 — `02_FEATURE_IMPROVEMENTS_PROMPT.md` (Task-A01): `render.yaml` does NOT exist yet

**What the prompt says:** Add `VITE_FLASK_CHATBOT_URL` to the frontend envVars in `render.yaml`.

**What's in the repo NOW:** `render.yaml` does not exist at all.

**Action:** Before running Prompt 5, tell Windsurf:  
> "render.yaml does not exist yet. Create it from scratch for a Render.com deployment with the following services: Django backend (technopath-backend), Flask chatbot (technopath-chatbot), and Vue frontend (technopath-frontend). Then apply Task-A01's env var addition."

Without this instruction, Windsurf will throw a file-not-found error and may halt.

---

### Adjustment 3 — `TECHNOPATHY_FIX_PROMPT_WINDSURF.md` (Issue-03): sessionStorage vs localStorage — confirm team intent

**What the prompt says:** Move JWT tokens from `localStorage` → `sessionStorage`.

**Current state:** All token storage is in `localStorage`.

**Important warning:** sessionStorage clears when the browser tab closes. This means **admins will be logged out every time they close and reopen the tab.** This is intentional per the prompt's security rationale (XSS hardening), but you should confirm your team accepts this UX trade-off before running.

If you want to keep localStorage (e.g., admin users expect persistent sessions), skip Issue-03 or change `sessionStorage` back to `localStorage` after running.

**No code change needed before running** — just a team decision.

---

## ✅ ITEMS ALREADY DONE (Skip These Tasks When Windsurf Asks)

| Prompt | Task | What Was Done | Status |
|--------|------|---------------|--------|
| All prompts (legacy files) | — | `funtion_systems/` deleted, root `package.json` deleted, SW manual registration removed, Facility xy fields added | ✅ Done |
| MASTER_FIX | Issue-C01 | Navigation serializer `x_position`, `y_position`, `from_node_id`, `to_node_id` aliases | ✅ Done |
| FIX_WINDSURF | Issue-06 | `.gitignore` merge conflict markers | ✅ Already clean |
| OVERHAUL | TASK-Q01 | SettingsView QR subtitle | ❌ Still needed |

---

## ITEMS CONFIRMED STILL NEEDED (All Prompts Will Do Real Work)

### From WINDSURF_FIX_PROMPT.md
| Task | Status |
|------|--------|
| T1 — Fix `ref(useRouter())` bug in SplashScreen.vue | ❌ Still broken |
| T2–T8 — All skeleton/animation components (boneyard-js, AppSkeleton, CometSpinner, etc.) | ❌ Not done |
| T9 — Page transitions in App.vue | ❌ Not done |
| T10 — Bottom nav bounce, env vars, .env.example | ❌ Not done |

### From TECHNOPATHY_FIX_PROMPT_WINDSURF.md
| Task | Status |
|------|--------|
| Issue-01 — SQL injection in chatbot analytics | ❌ `.format(days)` still on lines 217, 223 |
| Issue-02 — Rate limiter commented out | ❌ Still disabled |
| Issue-03 — JWT localStorage → sessionStorage | ❌ All 12 references still localStorage |
| Issue-04 — .env.example missing / wrong chatbot URL | ❌ File doesn't exist |
| Issue-05 — Flask debug=True hardcoded | ❌ Still debug=True on line 299 |
| Issue-06 — .gitignore conflict markers | ✅ SKIP |
| Issue-07 — Feedback rating no validation | ❌ Still fields = '__all__', no min/max |
| Issue-08 — AuditLog hard-coded 300 limit | ❌ Still qs = qs[:300] |

### From TECHNOPATHY_MASTER_FIX_PROMPT.md
All 29 issues needed — **except skip Issue-C01** (Adjustment 1).

### From TECHNOPATHY_OVERHAUL_PROMPT.md
All tasks needed.

### From 02_FEATURE_IMPROVEMENTS_PROMPT.md
All tasks needed — **create render.yaml first** (Adjustment 2).

---

## Recommended Context Header (Paste at Top of Every Prompt)

```
## SESSION CONTEXT — READ BEFORE STARTING

Repository: version7_technopath (already cloned/open)
The following are ALREADY FIXED in the current repo — DO NOT re-apply:

1. funtion_systems/ directory has been DELETED
2. Root-level package.json has been DELETED
3. Manual serviceWorker.register() in frontend/src/main.js has been REMOVED
4. Facility model has x_position and y_position fields (migration 0003 exists)
5. Navigation serializer already has x_position, y_position, from_node_id, to_node_id aliases — SKIP Issue-C01
6. .gitignore has zero merge conflict markers — SKIP Issue-06

FOR PROMPT 5 ONLY:
render.yaml does not exist. Create it from scratch for Render.com (services:
technopath-backend Django, technopath-chatbot Flask, technopath-frontend Vite)
before applying Task-A01.
```

---

## Safety Verdict

| Risk | Assessment |
|------|-----------|
| Duplicate fix causing errors | LOW — only Issue-C01 is at risk, and it's in the skip list |
| Missing file causing halt | MEDIUM for Prompt 5 only — resolved by Adjustment 2 |
| Irreversible data loss | NONE — all changes are code-only and git-tracked |
| UX regression | LOW — sessionStorage change (Adjustment 3) needs team sign-off |

**✅ All 5 prompts are safe to run in order with the 3 adjustments applied.**
