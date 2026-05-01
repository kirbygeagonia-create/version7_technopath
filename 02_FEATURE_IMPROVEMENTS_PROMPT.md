# TechnoPath — Feature Improvements & Backend Data Prompt
### For: Windsurf Kimi K2.5 AI
### Project: `https://github.com/kirbygeagonia-create/Technopathy.git`
### Phase: Backend Data Handling + Feature Enhancements

---

## HOW YOU MUST OPERATE — READ FIRST

You are a Senior Full-Stack Engineer. For each task below, follow this loop:

```
LOOP for each task:
  1. READ     → Open and understand the relevant files listed
  2. IMPLEMENT → Write the code exactly as specified
  3. SAVE     → Write all files
  4. VERIFY   → Re-read the file to confirm the change is present
  5. REPORT   → Print ✅ DONE: [Task ID] or ❌ FAILED: [Task ID] — [reason]
  
After all tasks:
  6. Run the FINAL VERIFICATION CHECKLIST
  7. Print the FINAL REPORT TABLE
  8. Retry any ❌ until all are ✅
```

Do not skip tasks. Do not assume code is written without re-reading the file.

---

## SECTION A — CRITICAL DEPLOYMENT FIXES (Do These First)

---

### TASK-A01 — Add VITE_FLASK_CHATBOT_URL to render.yaml Frontend
**File:** `render.yaml`
**Why:** The chatbot URL env var is missing from the frontend Vite build on Render. Without it, the AI chatbot is broken in production.

**Find the frontend service envVars block:**
```yaml
  - type: web
    name: technopath-frontend
    ...
    envVars:
      - key: NODE_VERSION
        value: "18.20.4"
      - key: VITE_API_BASE_URL
        value: https://technopath-backend-or73.onrender.com/api
```
**Add after VITE_API_BASE_URL:**
```yaml
      - key: VITE_FLASK_CHATBOT_URL
        value: https://technopath-chatbot.onrender.com
```

**Verify:** `grep -n "VITE_FLASK_CHATBOT_URL" render.yaml` → must return 1 result under the frontend service.

---

### TASK-A02 — Document Flask Chatbot SQLite Limitation
**File:** `chatbot_flask/app.py` — near Line 48

**Find:**
```python
DB_PATH = Path(__file__).parent / "chatbot.db"
```
**Replace with:**
```python
# NOTE: chatbot.db is a local SQLite file. On Render's free tier, this file is
# wiped on every deployment and restart — chat history is non-persistent.
# For production persistence, migrate chat_history to your PostgreSQL database.
# See: backend_django/apps/chatbot/ for the Django-managed chat history model.
DB_PATH = Path(__file__).parent / "chatbot.db"
```

**Verify:** Comment block is present above `DB_PATH`.

---

## SECTION B — BACKEND DATA IMPROVEMENTS

---

### TASK-B01 — Add Full-Text Search to Facilities and Rooms
**Files:** `backend_django/apps/facilities/views.py`, `backend_django/apps/rooms/views.py`

**Why:** Currently the admin and mobile app cannot search across facility/room names, descriptions, or keywords in a single query.

**In `facilities/views.py`, find the list view queryset and add search support:**
```python
# Find the class that lists facilities (e.g., FacilityListView or similar list endpoint)
# Add this filter logic to the get_queryset or list method:
from django.db.models import Q

def get_queryset(self):
    qs = Facility.objects.all()
    q = self.request.query_params.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(floor__icontains=q) |
            Q(building__icontains=q)
        )
    return qs.order_by('name')
```

**Apply the same pattern in `rooms/views.py`:**
```python
def get_queryset(self):
    qs = Room.objects.select_related('facility').all()
    q = self.request.query_params.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(room_number__icontains=q) |
            Q(facility__name__icontains=q)
        )
    return qs.order_by('facility__name', 'name')
```

**Verify:** Both view files contain `Q(name__icontains=q)` search logic.

---

### TASK-B02 — Add Soft Delete to Announcements
**Files:** `backend_django/apps/announcements/models.py`, `backend_django/apps/announcements/views.py`

**Why:** Currently deleting an announcement is permanent and irreversible. Admins need a way to archive/hide without permanently destroying records.

**In `announcements/models.py`, add soft-delete fields to the Announcement model:**
```python
# Add these fields to the Announcement model class:
is_archived   = models.BooleanField(default=False, help_text='Archived announcements are hidden from public but not deleted.')
archived_at   = models.DateTimeField(null=True, blank=True)
archived_by   = models.ForeignKey(
    'users.AdminUser',
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name='archived_announcements'
)
```

**Create and run the migration:**
```bash
python manage.py makemigrations announcements
python manage.py migrate
```

**In `announcements/views.py`, update the public list view to exclude archived:**
```python
# In AnnouncementPublicListView or equivalent, filter the queryset:
announcements = Announcement.objects.filter(is_archived=False).order_by('-created_at')
```

**Add an archive action endpoint. In `announcements/views.py`, add:**
```python
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_announcement(request, pk):
    """Soft-delete an announcement (hide without permanent deletion)."""
    try:
        ann = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    ann.is_archived = True
    ann.archived_at = timezone.now()
    ann.archived_by = request.user if hasattr(request.user, 'role') else None
    ann.save(update_fields=['is_archived', 'archived_at', 'archived_by'])
    return Response({'status': 'archived', 'id': pk})
```

**In `announcements/urls.py`, register the new endpoint:**
```python
path('<int:pk>/archive/', archive_announcement, name='announcement-archive'),
```

**Verify:** `is_archived` field is in `announcements/models.py`. `archive_announcement` view is in `views.py`. URL is registered in `urls.py`.

---

### TASK-B03 — Add Feedback Analytics Endpoint
**Files:** `backend_django/apps/feedback/views.py`, `backend_django/apps/feedback/urls.py`

**Why:** The admin dashboard has no API endpoint that summarizes feedback data (average rating, category breakdown, trend over time). This must be built for the dashboard analytics section to work.

**Add this view to `feedback/views.py`:**
```python
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Feedback

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_analytics(request):
    """
    Returns a summary of feedback for the admin dashboard.
    Query params:
      days (int, default 30) — how many days back to look
    """
    try:
        days = max(1, min(int(request.query_params.get('days', 30)), 365))
    except (TypeError, ValueError):
        days = 30

    since = timezone.now() - timedelta(days=days)
    qs    = Feedback.objects.filter(created_at__gte=since)

    # Overall stats
    total      = qs.count()
    avg_rating = qs.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg']
    flagged    = qs.filter(is_flagged=True).count()

    # Breakdown by category
    by_category = list(
        qs.values('category')
          .annotate(count=Count('id'), avg_rating=Avg('rating'))
          .order_by('-count')
    )

    # Daily submission trend
    daily_trend = list(
        qs.annotate(day=TruncDate('created_at'))
          .values('day')
          .annotate(count=Count('id'))
          .order_by('day')
    )

    # Rating distribution (1–5 stars)
    rating_dist = {}
    for r in range(1, 6):
        rating_dist[str(r)] = qs.filter(rating=r).count()

    return Response({
        'period_days':   days,
        'total':         total,
        'avg_rating':    round(avg_rating, 2) if avg_rating else None,
        'flagged':       flagged,
        'by_category':  by_category,
        'daily_trend':  [{'date': str(d['day']), 'count': d['count']} for d in daily_trend],
        'rating_dist':  rating_dist,
    })
```

**In `feedback/urls.py`, register it:**
```python
path('analytics/', feedback_analytics, name='feedback-analytics'),
```

**Verify:** `feedback_analytics` function is in `feedback/views.py`. URL is registered. Response includes `total`, `avg_rating`, `by_category`, `daily_trend`, `rating_dist`.

---

### TASK-B04 — Add Notification Read-All Endpoint
**Files:** `backend_django/apps/notifications/views.py`, `backend_django/apps/notifications/urls.py`

**Why:** The admin can only mark notifications as read one by one. There is no bulk "mark all as read" action, which is a common UX need.

**Add to `notifications/views.py`:**
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all unread notifications for the current user as read."""
    updated = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    return Response({'marked_read': updated})
```

**In `notifications/urls.py`, add:**
```python
path('mark-all-read/', mark_all_read, name='notifications-mark-all-read'),
```

**Verify:** `mark_all_read` view exists. URL registered.

---

### TASK-B05 — Add API Endpoint Health Check
**Files:** `backend_django/technopath/urls.py` or `backend_django/apps/core/views.py`

**Why:** There is no `/api/health/` endpoint. Render's health check, uptime monitors, and the frontend's offline detection all benefit from a lightweight endpoint that returns the system's current status.

**Add to `core/views.py`:**
```python
from django.db import connection
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Lightweight health check for Render, uptime monitors, and frontend PWA."""
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        pass

    return Response({
        'status':    'ok' if db_ok else 'degraded',
        'database':  'connected' if db_ok else 'error',
        'timestamp': timezone.now().isoformat(),
        'version':   '1.0.0',
    }, status=200 if db_ok else 503)
```

**In `technopath/urls.py`, add the route (no auth required):**
```python
from apps.core.views import health_check
# Inside urlpatterns:
path('api/health/', health_check, name='health-check'),
```

**Also add to `render.yaml` under the backend service:**
```yaml
    healthCheckPath: /api/health/
```

**Verify:** `health_check` view is in `core/views.py`. `/api/health/` is registered in `urls.py`. `healthCheckPath` is in `render.yaml`.

---

## SECTION C — FEATURE IMPROVEMENTS

---

### TASK-C01 — Add Paginated Feedback List for Admin
**File:** `backend_django/apps/feedback/views.py`

**Why:** The feedback list endpoint returns all records at once. As feedback grows, this will cause slow API responses and heavy memory use.

**Find the FeedbackListView (or equivalent list view). Update to use Django REST Framework pagination:**
```python
from rest_framework.pagination import PageNumberPagination

class FeedbackPagination(PageNumberPagination):
    page_size             = 20
    page_size_query_param = 'page_size'
    max_page_size         = 100

class FeedbackListView(generics.ListAPIView):
    serializer_class = FeedbackSerializer
    pagination_class = FeedbackPagination

    def get_queryset(self):
        qs = Feedback.objects.all().order_by('-created_at')
        category = self.request.query_params.get('category')
        flagged  = self.request.query_params.get('flagged')
        if category:
            qs = qs.filter(category=category)
        if flagged == 'true':
            qs = qs.filter(is_flagged=True)
        return qs
```

**Verify:** `FeedbackPagination` class exists in `feedback/views.py`.

---

### TASK-C02 — Add Announcement Scheduled Publishing
**Files:** `backend_django/apps/announcements/models.py`, `backend_django/apps/announcements/views.py`

**Why:** Admins currently must manually publish announcements at the exact moment they want them visible. Adding a `publish_at` datetime field allows scheduling.

**Add to the Announcement model:**
```python
publish_at = models.DateTimeField(
    null=True, blank=True,
    help_text='If set, the announcement will not be visible until this datetime. Leave blank to publish immediately.'
)
```

**Run migration:**
```bash
python manage.py makemigrations announcements
python manage.py migrate
```

**Update the public list view queryset to filter by schedule:**
```python
from django.utils import timezone

# In AnnouncementPublicListView queryset:
announcements = Announcement.objects.filter(
    is_archived=False
).filter(
    models.Q(publish_at__isnull=True) | models.Q(publish_at__lte=timezone.now())
).order_by('-created_at')
```

**Verify:** `publish_at` field is in the model. Public view filters by `publish_at`.

---

### TASK-C03 — Add Room Occupancy/Availability Status
**Files:** `backend_django/apps/rooms/models.py`, `backend_django/apps/rooms/serializers.py`

**Why:** Rooms currently have no status field. The campus guide cannot tell users if a room is available, occupied, under maintenance, or restricted.

**Add to the Room model:**
```python
STATUS_CHOICES = [
    ('available',    'Available'),
    ('occupied',     'Occupied'),
    ('maintenance',  'Under Maintenance'),
    ('restricted',   'Restricted Access'),
    ('closed',       'Closed'),
]
status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
status_note = models.CharField(max_length=200, blank=True, help_text='Optional note about current status.')
status_updated_at = models.DateTimeField(auto_now=True)
```

**Run migration:**
```bash
python manage.py makemigrations rooms
python manage.py migrate
```

**Add `status` and `status_note` to the room serializer's explicit fields list.**

**Verify:** `STATUS_CHOICES` is in `rooms/models.py`. `status` field is in the serializer.

---

### TASK-C04 — Add Admin Activity Dashboard Stats Endpoint
**File:** `backend_django/apps/core/views.py`, `backend_django/apps/core/urls.py`

**Why:** The admin dashboard currently has no single endpoint that returns a system-wide stats snapshot (total facilities, rooms, announcements, feedback count, notifications). This is needed to populate the dashboard homepage.

**Add to `core/views.py`:**
```python
from apps.facilities.models import Facility
from apps.rooms.models import Room
from apps.announcements.models import Announcement
from apps.feedback.models import Feedback
from apps.notifications.models import Notification
from django.db.models import Avg

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Returns a snapshot of key system stats for the admin dashboard homepage."""
    return Response({
        'facilities':     Facility.objects.count(),
        'rooms':          Room.objects.count(),
        'announcements':  Announcement.objects.filter(is_archived=False).count(),
        'feedback': {
            'total':      Feedback.objects.count(),
            'flagged':    Feedback.objects.filter(is_flagged=True).count(),
            'avg_rating': Feedback.objects.aggregate(avg=Avg('rating'))['avg'],
        },
        'notifications': {
            'total':      Notification.objects.count(),
            'unread':     Notification.objects.filter(is_read=False).count(),
        },
    })
```

**In `core/urls.py` or `technopath/urls.py`, register:**
```python
path('api/dashboard/stats/', dashboard_stats, name='dashboard-stats'),
```

**Verify:** `dashboard_stats` view is in `core/views.py`. URL is registered.

---

### TASK-C05 — Add SVG Map Versioning for Cache Busting
**Files:** `backend_django/apps/navigation/models.py`, `backend_django/apps/navigation/views.py`

**Why:** When admins update the SVG campus map, the PWA's service worker may cache the old version. Without a version/ETag mechanism, users on mobile may see stale maps for hours.

**Add a `version` field to the map model (or relevant model in navigation):**
```python
import uuid

# In the relevant Navigation/Map model:
map_version = models.UUIDField(default=uuid.uuid4, help_text='Auto-updated on every save for cache busting.')

def save(self, *args, **kwargs):
    self.map_version = uuid.uuid4()  # Regenerate on every save
    super().save(*args, **kwargs)
```

**In the navigation serializer, include `map_version` in the response fields.**

**In the navigation view, add an ETag header:**
```python
from django.utils.cache import patch_cache_control
from rest_framework.response import Response

# In the map retrieve/list view:
response = Response(serializer.data)
response['ETag'] = str(instance.map_version)
response['Cache-Control'] = 'no-cache'
return response
```

**Verify:** `map_version` field is in the navigation model. `ETag` header is set in the navigation view response.

---

## SECTION D — NEW-03 XSS GUARD (from verification report)

---

### TASK-D01 — Sanitize v-html SVG Content
**Files:** `frontend/src/components/admin/AdminPathManager.vue`, `frontend/src/views/NavigateView.vue`

**Why:** `v-html` bypasses Vue's XSS protection. Both files render SVG content this way.

**Step 1 — Install DOMPurify:**
```bash
cd frontend && npm install dompurify
```

**Step 2 — In `NavigateView.vue`, add the import and computed sanitizer:**
```javascript
import DOMPurify from 'dompurify'

// In setup() or as a computed property:
const safeSvgContent = computed(() =>
  DOMPurify.sanitize(svgContent.value || '', {
    USE_PROFILES: { svg: true },
    ADD_TAGS: ['use', 'symbol', 'defs', 'clipPath'],
  })
)
```

**Replace the template:**
```html
<!-- Before -->
<g v-if="mapLoaded" v-html="svgContent"></g>
<!-- After -->
<g v-if="mapLoaded" v-html="safeSvgContent"></g>
```

**Apply the same pattern in `AdminPathManager.vue`.**

**Verify:** `import DOMPurify from 'dompurify'` is in both files. `DOMPurify.sanitize` wraps the SVG content. `v-html` binds to the sanitized computed value.

---

## FINAL VERIFICATION CHECKLIST

Run each check and confirm the expected result:

```
SECTION A — DEPLOYMENT FIXES
[ ] TASK-A01: grep -n "VITE_FLASK_CHATBOT_URL" render.yaml → 2 results (1 in frontend envVars, 1 in chatbot env)
[ ] TASK-A02: grep -n "non-persistent" chatbot_flask/app.py → 1 result

SECTION B — BACKEND DATA
[ ] TASK-B01: grep -n "Q(name__icontains" backend_django/apps/facilities/views.py → 1 result
[ ] TASK-B01: grep -n "Q(name__icontains" backend_django/apps/rooms/views.py → 1 result
[ ] TASK-B02: grep -n "is_archived" backend_django/apps/announcements/models.py → 1 result
[ ] TASK-B02: grep -n "archive_announcement" backend_django/apps/announcements/views.py → 1 result
[ ] TASK-B03: grep -n "feedback_analytics" backend_django/apps/feedback/views.py → 1 result
[ ] TASK-B03: grep -n "rating_dist" backend_django/apps/feedback/views.py → 1 result
[ ] TASK-B04: grep -n "mark_all_read" backend_django/apps/notifications/views.py → 1 result
[ ] TASK-B05: grep -n "health_check" backend_django/apps/core/views.py → 1 result
[ ] TASK-B05: grep -n "healthCheckPath" render.yaml → 1 result

SECTION C — FEATURES
[ ] TASK-C01: grep -n "FeedbackPagination" backend_django/apps/feedback/views.py → 1 result
[ ] TASK-C02: grep -n "publish_at" backend_django/apps/announcements/models.py → 1 result
[ ] TASK-C03: grep -n "STATUS_CHOICES" backend_django/apps/rooms/models.py → 1 result
[ ] TASK-C04: grep -n "dashboard_stats" backend_django/apps/core/views.py → 1 result
[ ] TASK-C05: grep -n "map_version" backend_django/apps/navigation/models.py → 1 result

SECTION D — XSS GUARD
[ ] TASK-D01: grep -n "DOMPurify" frontend/src/views/NavigateView.vue → 1 result
[ ] TASK-D01: grep -n "DOMPurify" frontend/src/components/admin/AdminPathManager.vue → 1 result

MIGRATIONS
[ ] python manage.py showmigrations → announcements and rooms show new unapplied migrations
[ ] python manage.py migrate → completes with no errors
```

---

## FINAL REPORT FORMAT

```
╔═══════════════════════════════════════════════════════════════╗
║       TECHNOPATHY FEATURE & BACKEND IMPROVEMENT REPORT       ║
╠═══════════════════════════════════════════════════════════════╣
║  TASK-A01  VITE_FLASK_CHATBOT_URL in render.yaml  ✅ / ❌   ║
║  TASK-A02  Flask SQLite Limitation Documented     ✅ / ❌   ║
║  TASK-B01  Full-Text Search (Facilities/Rooms)    ✅ / ❌   ║
║  TASK-B02  Announcement Soft Delete               ✅ / ❌   ║
║  TASK-B03  Feedback Analytics Endpoint            ✅ / ❌   ║
║  TASK-B04  Notification Mark-All-Read             ✅ / ❌   ║
║  TASK-B05  Health Check Endpoint                  ✅ / ❌   ║
║  TASK-C01  Paginated Feedback List                ✅ / ❌   ║
║  TASK-C02  Announcement Scheduled Publishing      ✅ / ❌   ║
║  TASK-C03  Room Occupancy Status                  ✅ / ❌   ║
║  TASK-C04  Admin Dashboard Stats Endpoint         ✅ / ❌   ║
║  TASK-C05  SVG Map Versioning / Cache Busting     ✅ / ❌   ║
║  TASK-D01  v-html SVG Sanitized with DOMPurify    ✅ / ❌   ║
╠═══════════════════════════════════════════════════════════════╣
║  TOTAL:  ___ / 13 PASSED                                    ║
║  STATUS: [ ALL CLEAR ✅ ] or [ NEEDS RETRY ❌ ]              ║
╚═══════════════════════════════════════════════════════════════╝
```

If any ❌ appears — do NOT stop. Return to that task's section, re-apply the change, re-run its verify command, and update the report. Only stop when all 13 show ✅.
