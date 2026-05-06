# TechnoPath V7 — Full System Analysis & Fix Prompt
**Repository:** `kirbygeagonia-create/version7_technopath`  
**Stack:** Vue 3 (Vite) + Django REST Framework + Flask Chatbot  
**Date Analyzed:** May 2026

---

## EXECUTIVE SUMMARY

The system is architecturally sound. Most core features exist and are wired correctly. However, **7 critical bugs** and **5 missing features** were identified that break or partially disable: Facilities Management notifications (to users), Rooms Management notifications, Admin "Send Notification" endpoint, Announcement auto-notification for direct-publish, the chatbot Flask proxy, FAQ AI management, and the SVG Path Manager save/delete flow.

---

## ✅ WHAT IS WORKING CORRECTLY

| Feature | Status | Notes |
|---|---|---|
| Django Notification Model | ✅ OK | Full CRUD, read/unread, per-user tracking |
| Facility Signals (Django) | ✅ OK | `signals.py` auto-creates notifications on add/edit/delete |
| Announcement → Notification (approval flow) | ✅ OK | `publish()` method creates Notification on approval |
| User Notifications View (`/notifications`) | ✅ OK | Reads from `/api/notifications/`, marks read/unread, delete |
| Admin Send Notification Component | ✅ Mostly OK | Component exists; backend `SendNotificationView` exists |
| Admin FAQ CRUD | ✅ OK | Full create/edit/delete wired to `/api/faq/` |
| FAQ AI Maker (Analyze) | ✅ OK | `FAQMakerAnalyzeView` in Django; frontend calls it |
| Feedback Submit | ✅ OK | POST to `/api/feedback/` with offline fallback |
| Admin Feedback View | ✅ OK | `AdminFeedback.vue` renders list |
| Router / Nav Guards | ✅ OK | JWT auth gate on `/admin`, splash redirect |
| JWT Token Auto-Refresh | ✅ OK | Interceptor in `api.js` retries on 401 |
| Admin Path Manager (visual editor) | ✅ OK | SVG click-to-add-point, delete mode, groups |
| Admin NavGraph | ✅ OK | Node/edge import/export, SVG map upload |
| Chatbot Offline Fallback | ✅ OK | Rule-based fallback in `aiChatbot.js` |
| Chatbot FAQ matching | ✅ OK | IndexedDB FAQ lookup before calling Flask |

---

## 🔴 BUG #1 — Facility Form Fields Mismatch (`floors` vs `total_floors`)

### Location
`frontend/src/components/admin/AdminFacilities.vue` — `form` object and `saveFacility()`

### Problem
The Vue form uses field names `floors` and `room_count`, but the Django `Facility` model uses `total_floors`. When you save a new or edited facility, the backend ignores the `floors` field (it doesn't exist on the model), causing floor count to always be `1` (the default).

**Vue form (WRONG):**
```js
form.value = {
  id: null, name: '', room: '', code: '',
  facility_type: 'academic', description: '',
  total_floors: 1,   // ← form shows 'floors' in template, but v-model is 'total_floors'
  room_count: 0      // ← not a real model field
}
```

**Template (WRONG):**
```html
<label>Number of Floors</label>
<input v-model="form.floors" type="number" min="1" />  <!-- v-model is 'floors' not 'total_floors' -->
```

**Django model field:** `total_floors = models.IntegerField(default=1)`  
**Django model field does NOT have:** `room_count` or `floors`

### Fix
In `AdminFacilities.vue`, fix the `form` ref and all `v-model` bindings:

```js
// BEFORE
form.value = { id: null, name: '', room: '', code: '', facility_type: 'academic', description: '', total_floors: 1, room_count: 0 }

// AFTER
form.value = { id: null, name: '', code: '', facility_type: 'academic', description: '', total_floors: 1 }
```

```html
<!-- BEFORE -->
<input v-model="form.floors" type="number" min="1" />

<!-- AFTER -->
<input v-model="form.total_floors" type="number" min="1" />
```

Remove all references to `form.room`, `form.floors`, and `form.room_count` in template. Remove the "Room" and "Room Count" form fields entirely (rooms are managed in the Rooms panel, not Facilities).

---

## 🔴 BUG #2 — Facilities `saveFacility()` Has No Success Toast or Error Feedback

### Location
`frontend/src/components/admin/AdminFacilities.vue` — `saveFacility()` function

### Problem
When a facility is saved successfully, the frontend closes the modal and reloads — but shows **no success toast**. If it fails, error is only logged to console, not shown to user. The signals on Django side WILL fire and create the notification, but admins see no confirmation in the UI.

### Fix
```js
// BEFORE
async function saveFacility() {
  try {
    if (showEditModal.value) {
      await api.put(`/facilities/${form.value.id}/`, form.value)
    } else {
      await api.post('/facilities/', form.value)
    }
    closeModal()
    loadFacilities()
  } catch (e) {
    console.error('Failed to save facility:', e)
    showToast('Failed to save facility', 'error')
  }
}

// AFTER
async function saveFacility() {
  try {
    if (showEditModal.value) {
      await api.put(`/facilities/${form.value.id}/`, form.value)
      showToast(`Facility "${form.value.name}" updated successfully`, 'success')
    } else {
      await api.post('/facilities/', form.value)
      showToast(`Facility "${form.value.name}" added — users will be notified`, 'success')
    }
    closeModal()
    await loadFacilities()
  } catch (e) {
    console.error('Failed to save facility:', e)
    const msg = e.response?.data?.detail || e.response?.data?.code?.[0] || 'Failed to save facility'
    showToast(msg, 'error')
  }
}
```

Also fix `deleteFacility()`:
```js
// AFTER
async function deleteFacility() {
  try {
    await api.delete(`/facilities/${facilityToDelete.value.id}/`)
    showToast(`Facility "${facilityToDelete.value.name}" removed — users will be notified`, 'success')
    showDeleteModal.value = false
    facilityToDelete.value = null
    await loadFacilities()
  } catch (e) {
    console.error('Failed to delete facility:', e)
    showToast('Failed to delete facility', 'error')
  }
}
```

---

## 🔴 BUG #3 — Rooms Management: No Automatic User Notification on Add/Edit/Delete

### Location
`backend_django/apps/rooms/views.py` — `RoomListView`, `RoomDetailView`  
`backend_django/apps/rooms/` — no `signals.py` file exists

### Problem
Facilities have `signals.py` that auto-creates user notifications when facilities are added/edited/deleted. **Rooms have NO signals file.** When a room is added, edited, or deleted via the admin panel, users receive **zero notification**. There is also no `apps.py` `ready()` hook to load signals.

### Fix — Create `backend_django/apps/rooms/signals.py`:

```python
"""
Django signals for Room model.
Automatically creates notifications when rooms are added, updated, or deleted.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Room
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)

_soft_deleted_rooms = set()


def _notify_room(title, message, notification_type='room_update'):
    try:
        Notification.objects.create(
            title=title,
            message=message,
            type=notification_type,
            source_label='Campus Facilities',
            source_color='blue',
            priority=1,
            is_read=False,
        )
        logger.info(f'[Room Signal] Created notification: {title}')
    except Exception as e:
        logger.error(f'[Room Signal] Error creating notification: {e}', exc_info=True)


@receiver(pre_save, sender=Room)
def detect_room_soft_delete(sender, instance, **kwargs):
    if instance.pk is None:
        return
    try:
        original = Room.objects.filter(pk=instance.pk).first()
        if original and not original.is_deleted and instance.is_deleted:
            _soft_deleted_rooms.add(instance.pk)
    except Exception as e:
        logger.error(f'[Room Signal] pre_save error: {e}')


@receiver(post_save, sender=Room)
def notify_on_room_change(sender, instance, created, **kwargs):
    try:
        facility_name = instance.facility.name if instance.facility_id else 'Unknown Building'

        if instance.pk in _soft_deleted_rooms:
            _soft_deleted_rooms.discard(instance.pk)
            _notify_room(
                f'Room Removed: {instance.name}',
                f'Room "{instance.name}" in {facility_name} has been removed.',
                'room_update'
            )
            return

        if instance.is_deleted:
            return

        if created:
            _notify_room(
                f'New Room Available: {instance.name}',
                f'Room "{instance.name}" (Floor {instance.floor}) in {facility_name} is now available.',
                'room_update'
            )
        else:
            _notify_room(
                f'Room Updated: {instance.name}',
                f'Room "{instance.name}" in {facility_name} has been updated.',
                'room_update'
            )
    except Exception as e:
        logger.error(f'[Room Signal] post_save error: {e}', exc_info=True)
```

### Fix — Update `backend_django/apps/rooms/apps.py`:

```python
from django.apps import AppConfig

class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rooms'
    verbose_name = 'Rooms'

    def ready(self):
        import apps.rooms.signals  # noqa
```

---

## 🔴 BUG #4 — Announcement Direct-Publish Does NOT Create Notification

### Location
`backend_django/apps/announcements/views.py` — `AnnouncementCreateView.post()`

### Problem
When a `super_admin` or `dean` (for department scope) creates an announcement, it is **published directly** (`publishes_direct = True`). However, `Notification` is only created inside the `publish()` method, which is called only by `AnnouncementApproveView`. The direct-publish path in `AnnouncementCreateView` saves the announcement with `status='published'` but **skips calling `a.publish()`**, so no notification is ever created for direct-publish announcements.

Looking at the create view code:
```python
# views.py — AnnouncementCreateView (simplified)
if publishes_direct:
    a.status = 'published'
    a.approved_by = user
    a.approved_at = timezone.now()
    a.save()  # ← save() directly — does NOT call a.publish()
    # NO Notification.objects.create() here!
```

### Fix
In `AnnouncementCreateView.post()`, replace the direct `a.save()` with `a.publish(approved_by_user=user)`:

```python
# BEFORE
if publishes_direct:
    a.status = 'published'
    a.approved_by = user
    a.approved_at = timezone.now()
    a.save()

# AFTER
if publishes_direct:
    a.publish(approved_by_user=user)  # This calls save() AND creates Notification
```

This ensures the `publish()` method (which creates the Notification) runs for both direct publishes and approval-based publishes.

---

## 🔴 BUG #5 — Admin "Send Notification" Role Check Is Wrong

### Location
`backend_django/apps/notifications/views.py` — `SendNotificationView.post()`

### Problem
The permission check uses an incorrect condition:
```python
# WRONG — checks is_staff OR role in list (two separate conditions)
if not request.user.is_staff and not getattr(request.user, 'role', '') in ['admin', 'super_admin', 'dean', 'program_head']:
```

This means a user with `is_staff=False` and `role='dean'` would **pass** the check incorrectly because:
- `not is_staff` = `True`  
- `not role in list` = `False`  
- `True and False` = `False` → user is allowed  

But a user with `is_staff=True` and `role='guest'` would also be allowed. The logic is broken.

Also, `role='admin'` is not a valid role in the system (valid roles: `super_admin`, `dean`, `program_head`, `basic_ed_head`).

### Fix
```python
# AFTER
ALLOWED_ROLES = {'super_admin', 'dean', 'program_head', 'basic_ed_head'}
user_role = getattr(request.user, 'role', '')
if user_role not in ALLOWED_ROLES:
    return Response(
        {'error': 'You do not have permission to send notifications.'},
        status=status.HTTP_403_FORBIDDEN
    )
```

---

## 🔴 BUG #6 — Chatbot Flask Proxy URL Mismatch in Production

### Location
`frontend/src/services/aiChatbot.js` line 15  
`frontend/vite.config.js` proxy config

### Problem
The chatbot uses:
```js
const FLASK_CHATBOT_URL = import.meta.env.VITE_FLASK_CHATBOT_URL || '/chatbot-api'
```

The Vite dev proxy rewrites `/chatbot-api` → `http://localhost:5187`. **This only works in development.**

In production (Render/deployment), there is no Vite proxy. If `VITE_FLASK_CHATBOT_URL` is not set in the production environment variables, all chatbot requests go to `/chatbot-api` on the same domain as the frontend, which doesn't exist. The chatbot silently falls back to rule-based replies with no error shown to user.

### Fix — Two steps:

**Step 1:** In your production `.env` / Render environment variables, add:
```
VITE_FLASK_CHATBOT_URL=https://your-flask-chatbot-service.onrender.com
```

**Step 2:** In `aiChatbot.js`, improve error visibility:
```js
// AFTER
async function generateFlaskResponse(userMessage) {
  try {
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
    return { reply: data.reply, messageId: data.message_id }
  } catch (err) {
    console.warn('[Chatbot] Flask unreachable, using rule-based fallback:', err.message)
    throw err  // Let caller handle fallback
  }
}
```

---

## 🔴 BUG #7 — AdminFacilities `postAnnouncement()` Uses `window.dispatchEvent` — Does Nothing Useful

### Location
`frontend/src/components/admin/AdminFacilities.vue` — `postAnnouncement()` function

### Problem
The "Post Announcement" button in the facility management panel dispatches a `CustomEvent` on `window`:
```js
window.dispatchEvent(new CustomEvent('facility-announcement', { detail: {...} }))
```
**No listener handles this event anywhere in the codebase.** The announcement goes nowhere. It shows a toast but no real announcement is created in the backend.

### Fix
Remove the `postAnnouncement()` function and the related template section (the announcement textarea and button). Announcements should be created via the dedicated `AdminAnnouncements.vue` panel. If you want a quick-announce shortcut, redirect the admin to the announcements panel:

```js
// REPLACE postAnnouncement() with:
function goToAnnouncements() {
  window.dispatchEvent(new CustomEvent('admin-navigate', { detail: 'announcements' }))
}
```

```html
<!-- REPLACE the announcement textarea block with: -->
<div class="announcement-shortcut">
  <p>To post a campus announcement about this facility, use the Announcements panel.</p>
  <button class="btn-secondary" @click="goToAnnouncements">
    <span class="material-icons">campaign</span>
    Go to Announcements
  </button>
</div>
```

---

## ⚠️ ISSUE #8 — AdminRooms: No Success Toast on Save/Delete (UX Gap)

### Location
`frontend/src/components/admin/AdminRooms.vue`

### Problem
The room save and delete operations call the API but import `showToast` is present — however, the success case for save doesn't always call `showToast`. More importantly, since Rooms now will have signals (Bug #3 fix), the admin needs to see "Users will be notified" feedback.

### Fix
After each successful room operation, add:
```js
// After room create:
showToast(`Room "${form.value.name}" added — users will be notified`, 'success')

// After room update:
showToast(`Room "${form.value.name}" updated — users will be notified`, 'success')

// After room delete:
showToast(`Room deleted — users will be notified`, 'success')
```

---

## ⚠️ ISSUE #9 — NotificationsView: Guest Users Always See "No Notifications"

### Location
`frontend/src/views/NotificationsView.vue` — `fetchNotifications()`

### Problem
```js
const res = await api.get('/notifications/')
```

The `NotificationListView` on Django uses `IsAuthenticatedOrReadOnly`. Guest (unauthenticated) users should be able to see notifications — they are read-only. However, the Vue `api.js` instance only sends `Authorization: Bearer <token>` if a token exists. If no token exists (guest), the API call still goes through but returns **all** notifications (correct behavior), yet the frontend may show 0 if the backend returns a non-array or paginated response.

Check that your Django notification list returns a plain array (not `{count, results, next}` pagination). If `DEFAULT_PAGINATION_CLASS` is set in Django REST Framework settings, you may get a paginated response object, and `res.data` will be an object, not an array.

### Fix
In `NotificationsView.vue`:
```js
// BEFORE
notifications.value = res.data || []

// AFTER — handle both paginated and non-paginated responses
const data = res.data
notifications.value = Array.isArray(data) ? data : (data.results || [])
```

---

## ⚠️ ISSUE #10 — SVG Path Manager: No Notification When Path is Saved/Deleted

### Location
`frontend/src/components/admin/AdminPathManager.vue`  
`backend_django/apps/navigation/views.py`

### Problem
When a navigation path (SVG walking route) is saved or deleted, no notification is sent to users. Users who have the app open won't know that routes have changed. This is lower priority than facilities/rooms but should be consistent.

### Fix — Add to `backend_django/apps/navigation/` a `signals.py`:

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Path
from apps.notifications.models import Notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Path)
def notify_path_change(sender, instance, created, **kwargs):
    try:
        if created:
            Notification.objects.create(
                title='Navigation Route Updated',
                message=f'A new walking route has been added on campus. Tap Navigate to use it.',
                type='info',
                source_label='Campus Navigation',
                source_color='teal',
                priority=1,
            )
    except Exception as e:
        logger.error(f'[Path Signal] {e}')
```

Update `backend_django/apps/navigation/apps.py`:
```python
def ready(self):
    import apps.navigation.signals  # noqa
```

---

## 📋 COMPLETE FIX PROMPT FOR AI CODING ASSISTANT (Windsurf/Cursor/Copilot)

> Copy and paste this entire block into your AI coding assistant to apply all fixes at once.

---

```
You are fixing the TechnoPath V7 system (Vue 3 + Django REST Framework + Flask).
Apply ALL of the following fixes exactly as described. Do not skip any step.

=============================================================================
FIX 1: AdminFacilities.vue — Field name mismatch (floors vs total_floors)
=============================================================================
FILE: frontend/src/components/admin/AdminFacilities.vue

1. Find the `form` ref initialization. Change it to:
   form.value = { id: null, name: '', code: '', facility_type: 'academic', description: '', total_floors: 1 }
   (Remove: room, floors, room_count fields)

2. In the template modal body, find:
   <input v-model="form.floors" type="number" min="1" />
   Change to:
   <input v-model="form.total_floors" type="number" min="1" />

3. Remove the entire "Room" form-group (the <div class="form-group"> containing label "Room" and input v-model="form.room")

4. Remove the entire "Room Count" form-group (label "Room Count" input v-model="form.room_count")

5. In closeModal(), update form reset to match the new fields:
   form.value = { id: null, name: '', code: '', facility_type: 'academic', description: '', total_floors: 1 }

=============================================================================
FIX 2: AdminFacilities.vue — Add success toasts and proper error messages
=============================================================================
FILE: frontend/src/components/admin/AdminFacilities.vue

Replace the entire saveFacility() function with:
```javascript
async function saveFacility() {
  try {
    if (showEditModal.value) {
      await api.put(`/facilities/${form.value.id}/`, form.value)
      showToast(`Facility "${form.value.name}" updated — users will be notified`, 'success')
    } else {
      await api.post('/facilities/', form.value)
      showToast(`Facility "${form.value.name}" added — users will be notified`, 'success')
    }
    closeModal()
    await loadFacilities()
  } catch (e) {
    console.error('Failed to save facility:', e)
    const msg = e.response?.data?.code?.[0] || e.response?.data?.detail || 'Failed to save facility'
    showToast(msg, 'error')
  }
}
```

Replace the entire deleteFacility() function with:
```javascript
async function deleteFacility() {
  try {
    await api.delete(`/facilities/${facilityToDelete.value.id}/`)
    showToast(`Facility "${facilityToDelete.value.name}" removed — users will be notified`, 'success')
    showDeleteModal.value = false
    facilityToDelete.value = null
    await loadFacilities()
  } catch (e) {
    console.error('Failed to delete facility:', e)
    showToast('Failed to delete facility', 'error')
  }
}
```

=============================================================================
FIX 3: Create rooms/signals.py — Auto-notify users on room changes
=============================================================================
CREATE FILE: backend_django/apps/rooms/signals.py

Content:
```python
"""
Django signals for Room model.
Automatically creates user notifications when rooms are added, updated, or removed.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Room
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)
_soft_deleted_rooms = set()


def _notify_room(title, message):
    try:
        Notification.objects.create(
            title=title,
            message=message,
            type='room_update',
            source_label='Campus Facilities',
            source_color='blue',
            priority=1,
            is_read=False,
        )
        logger.info(f'[Room Signal] Notification created: {title}')
    except Exception as e:
        logger.error(f'[Room Signal] Failed to create notification: {e}', exc_info=True)


@receiver(pre_save, sender=Room)
def detect_room_soft_delete(sender, instance, **kwargs):
    if instance.pk is None:
        return
    try:
        original = Room.objects.filter(pk=instance.pk).first()
        if original and not original.is_deleted and instance.is_deleted:
            _soft_deleted_rooms.add(instance.pk)
    except Exception as e:
        logger.error(f'[Room Signal] pre_save error: {e}')


@receiver(post_save, sender=Room)
def notify_on_room_change(sender, instance, created, **kwargs):
    try:
        facility_name = 'Unknown Building'
        try:
            facility_name = instance.facility.name
        except Exception:
            pass

        if instance.pk in _soft_deleted_rooms:
            _soft_deleted_rooms.discard(instance.pk)
            _notify_room(
                f'Room Removed: {instance.name}',
                f'Room "{instance.name}" in {facility_name} has been removed from the system.'
            )
            return

        if instance.is_deleted:
            return

        if created:
            _notify_room(
                f'New Room: {instance.name}',
                f'Room "{instance.name}" (Floor {instance.floor}) in {facility_name} is now available.'
            )
        else:
            _notify_room(
                f'Room Updated: {instance.name}',
                f'Room "{instance.name}" in {facility_name} has been updated.'
            )
    except Exception as e:
        logger.error(f'[Room Signal] post_save error: {e}', exc_info=True)
```

=============================================================================
FIX 3b: Update rooms/apps.py to load signals
=============================================================================
FILE: backend_django/apps/rooms/apps.py

Replace entire content with:
```python
from django.apps import AppConfig

class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rooms'
    verbose_name = 'Rooms'

    def ready(self):
        import apps.rooms.signals  # noqa: F401
```

=============================================================================
FIX 4: announcements/views.py — Direct-publish must call publish() to create Notification
=============================================================================
FILE: backend_django/apps/announcements/views.py

In the AnnouncementCreateView.post() method, find the section where publishes_direct is True.
It currently does something like:
    a.status = 'published'
    a.approved_by = user  
    a.approved_at = timezone.now()
    a.save()

Replace that entire block with:
    a.publish(approved_by_user=user)

This ensures the Notification is always created when an announcement is published,
whether directly or through approval.

IMPORTANT: Make sure the announcement object `a` is already saved (pk exists) before calling publish().
The publish() method calls self.save() internally, so do NOT call a.save() before a.publish() in the direct path.

=============================================================================
FIX 5: notifications/views.py — Fix SendNotificationView permission check
=============================================================================
FILE: backend_django/apps/notifications/views.py

In SendNotificationView.post(), replace the permission check:

BEFORE:
    if not request.user.is_staff and not getattr(request.user, 'role', '') in ['admin', 'super_admin', 'dean', 'program_head']:

AFTER:
    ALLOWED_ROLES = {'super_admin', 'dean', 'program_head', 'basic_ed_head'}
    user_role = getattr(request.user, 'role', '')
    if user_role not in ALLOWED_ROLES:
        return Response(
            {'error': 'You do not have permission to send notifications.'},
            status=status.HTTP_403_FORBIDDEN
        )

=============================================================================
FIX 6: notifications/views.py — Fix NotificationListView response for guests
=============================================================================
FILE: frontend/src/views/NotificationsView.vue

In the fetchNotifications() function, find:
    notifications.value = res.data || []

Replace with:
    const data = res.data
    notifications.value = Array.isArray(data) ? data : (data.results || [])

=============================================================================
FIX 7: AdminFacilities.vue — Remove broken postAnnouncement(), add redirect
=============================================================================
FILE: frontend/src/components/admin/AdminFacilities.vue

1. Delete the entire postAnnouncement() function.
2. Delete the entire announceFacilityChange() function.
3. Delete the v-model="announcementText" ref declaration.
4. In the template, find and remove the "announcement" section (textarea + "Post Announcement" button).
5. Add this function:
   function goToAnnouncements() {
     window.dispatchEvent(new CustomEvent('admin-navigate', { detail: 'announcements' }))
   }
6. Add a simple link button in the template where the announcement section was:
   <button class="btn-secondary" @click="goToAnnouncements">
     <span class="material-icons">campaign</span>
     Post Announcement
   </button>

=============================================================================
FIX 8: AdminRooms.vue — Add "users will be notified" toasts on save/delete
=============================================================================
FILE: frontend/src/components/admin/AdminRooms.vue

After every successful room create API call, add:
    showToast(`Room "${form.value.name}" added — users will be notified`, 'success')

After every successful room update API call, add:
    showToast(`Room "${form.value.name}" updated — users will be notified`, 'success')

After every successful room delete API call, add:
    showToast('Room deleted — users will be notified', 'success')

Make sure `showToast` is imported at the top:
    import { showToast } from '../../services/toast.js'

=============================================================================
FIX 9: ENVIRONMENT VARIABLE — Flask chatbot URL for production
=============================================================================
In your production environment (Render dashboard or .env.production file), add:

    VITE_FLASK_CHATBOT_URL=https://YOUR-FLASK-SERVICE-URL.onrender.com

Without this, the chatbot falls back to rule-based replies in production
(the Vite dev proxy only works during local development).

=============================================================================
VERIFICATION CHECKLIST — After applying all fixes, test these manually:
=============================================================================

[ ] Add a new Facility → verify:
    - Toast shows "added — users will be notified"
    - /api/notifications/ returns a new "New Facility: ..." notification
    - Notification appears in user's /notifications view

[ ] Edit a Facility → verify:
    - Toast shows "updated — users will be notified"
    - Notification created for "Facility Updated: ..."

[ ] Delete a Facility → verify:
    - Toast shows "removed — users will be notified"
    - Notification created for "Facility Removed: ..."

[ ] Add a Room → verify:
    - Toast shows "added — users will be notified"
    - Room signal fires, Notification created

[ ] Edit a Room → verify:
    - Notification created for "Room Updated: ..."

[ ] Delete a Room → verify:
    - Notification created for "Room Removed: ..."

[ ] Admin (super_admin) creates announcement → verify:
    - publish() is called
    - Notification appears immediately (no approval needed for super_admin)

[ ] Dean creates department announcement → verify:
    - Notification appears immediately

[ ] Dean creates campus-wide announcement → verify:
    - Goes to pending_approval (no notification yet)
    - Super admin approves → Notification appears

[ ] Admin "Send Notification" panel → verify:
    - super_admin, dean, program_head, basic_ed_head can send
    - Other roles get 403 error

[ ] Chatbot sends a message → verify:
    - Flask backend responds (check VITE_FLASK_CHATBOT_URL is set)
    - If Flask is down, rule-based fallback activates silently

[ ] FAQ AI → admin opens FAQ panel → "Analyze Chat Logs" → suggestions generated
    - Approve a suggestion → becomes an active FAQ
    - Test in chatbot: ask a question matching the new FAQ

[ ] Navigate tab → enter start and destination → route draws on SVG map

[ ] Feedback form → submit → appears in Admin Feedback panel
```

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Mobile/Browser)                    │
│                Vue 3 PWA — port 5173 (dev)                  │
└────────────┬─────────────────────────────┬──────────────────┘
             │                             │
     /api/*  │                   /chatbot-api/*
             ▼                             ▼
┌────────────────────┐          ┌───────────────────┐
│  Django REST API   │          │  Flask Chatbot    │
│  port 8000         │          │  port 5187        │
│                    │          │                   │
│  ├ /api/facilities/│          │  ├ /chat          │
│  ├ /api/rooms/     │          │  ├ /health        │
│  ├ /api/notifs/    │          │  └ /analytics     │
│  ├ /api/faq/       │          └───────────────────┘
│  ├ /api/chatbot/   │
│  ├ /api/announce/  │   ← Django Signals auto-fire:
│  └ /api/feedback/  │     • Facility add/edit/delete
│                    │     • Announcement publish
└────────┬───────────┘     • [Room add/edit/delete — NEEDS FIX #3]
         │
         ▼
┌─────────────────────┐
│  SQLite (dev) /     │
│  PostgreSQL (prod)  │
│                     │
│  notifications      │ ← Central notification store
│  facilities         │   read by /notifications view
│  rooms              │
│  announcements      │
│  faq_entries        │
│  chat_logs          │
└─────────────────────┘
```

---

## PRIORITY ORDER FOR FIXES

| Priority | Fix | Impact |
|---|---|---|
| 🔴 P1 | Fix #3 (Rooms signals) | Users never notified of room changes |
| 🔴 P1 | Fix #4 (Announcement direct-publish) | Super admin announcements create no notification |
| 🔴 P1 | Fix #1 (Facility field mismatch) | Floor count always wrong |
| 🔴 P2 | Fix #2 (Facility toasts) | Admin has no confirmation feedback |
| 🔴 P2 | Fix #5 (Notification permission) | Wrong role check — security gap |
| 🟡 P3 | Fix #6 (Pagination guard) | Guest users may see empty notification list |
| 🟡 P3 | Fix #7 (Remove broken postAnnouncement) | Dead code, confuses admins |
| 🟢 P4 | Fix #8 (Room toasts) | UX only |
| 🟢 P4 | Fix #9 (Flask env var) | Required for production chatbot |
