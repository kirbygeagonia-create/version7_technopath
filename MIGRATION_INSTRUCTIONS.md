# TechnoPath Migration Prompt — For Windsurf Kimi 2.5
# Copy and paste this entire prompt into Windsurf

---

## CONTEXT

You are helping migrate the **TechnoPath: SEAIT Guide Map and Navigation System** from a Flutter/Dart mobile app with a Node.js + Dart backend into a **Python Django backend + Progressive Web App (PWA) frontend**. The project is located at:

```
C:\Users\User\Downloads\SAD\version4_technopath\
```

The system is a 2D campus guide map and navigation system for South East Asian Institute of Technology (SEAIT). It must work **fully offline** as a PWA, with an online Django admin panel for administrators.

---

## TASK 1 — ARCHIVE FLUTTER/DART FILES (Move, Do Not Delete)

Create a new folder at the project root:
```
_flutter_archive/
```

Move the following folders and files INTO `_flutter_archive/`. Do not delete them — they are kept for reference only:

**Folders to move:**
- `lib/` — entire Flutter Dart source code
- `android/` — Android platform files
- `ios/` — iOS platform files
- `linux/` — Linux platform files
- `macos/` — macOS platform files
- `windows/` — Windows platform files
- `build/` — Flutter build output
- `.dart_tool/` — Dart build artifacts
- `.idea/` — IntelliJ/Android Studio settings
- `backend_dart/` — Dart alternative backend (replaced by Django)
- `backend/` — Node.js backend (replaced by Django)
- `test/` — Flutter unit tests

**Files to move:**
- `pubspec.yaml` — Flutter project config
- `pubspec.lock` — Flutter locked dependencies
- `analysis_options.yaml` — Dart analyzer config
- `.metadata` — Flutter metadata
- `.flutter-plugins-dependencies` — Flutter plugin metadata
- `version4_technopath.iml` — IntelliJ module config

**Do NOT move:**
- `chatbot_flask/` — keep in place, still used
- `assets/` — keep in place, map assets still needed
- `.windsurf/` — keep in place
- `.gitignore` — keep in place
- `README.md` — keep in place
- `SYSTEM_DOCUMENTATION.md` — keep in place

---

## TASK 2 — SET UP DJANGO BACKEND

### 2.1 Create the Django project structure

Create the following folder and file structure at the project root:

```
backend_django/
├── manage.py
├── requirements.txt
├── .env.example
├── technopath/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── facilities/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    ├── rooms/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    ├── navigation/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    ├── chatbot/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    ├── notifications/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    ├── feedback/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    └── users/
        ├── __init__.py
        ├── models.py
        ├── serializers.py
        ├── views.py
        └── urls.py
```

### 2.2 Create requirements.txt

```
django>=4.2
djangorestframework>=3.15
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3
python-decouple>=3.8
Pillow>=10.0
flask>=3.0
flask-cors>=4.0
```

### 2.3 Create backend_django/technopath/settings.py

```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-technopath-seait-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'apps.users',
    'apps.facilities',
    'apps.rooms',
    'apps.navigation',
    'apps.chatbot',
    'apps.notifications',
    'apps.feedback',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'technopath.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'technopath.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'technopath.db',
    }
}

AUTH_USER_MODEL = 'users.AdminUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True
```

### 2.4 Create backend_django/technopath/urls.py

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('apps.users.urls')),
    path('api/facilities/', include('apps.facilities.urls')),
    path('api/rooms/', include('apps.rooms.urls')),
    path('api/navigation/', include('apps.navigation.urls')),
    path('api/chatbot/', include('apps.chatbot.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/feedback/', include('apps.feedback.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 2.5 Create Database Models

#### apps/users/models.py
```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class AdminUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'super_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class AdminUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('super_admin', 'Safety and Security Office'),
        ('program_head', 'Program Head'),
        ('dean', 'Dean'),
    ]
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='program_head')
    department = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AdminUserManager()
    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'
```

#### apps/facilities/models.py
```python
from django.db import models

class Facility(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=500, blank=True, null=True)
    map_svg_id = models.CharField(max_length=100, blank=True, null=True, help_text='SVG element ID e.g. building-RST')
    total_floors = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities'

    def __str__(self):
        return self.name
```

#### apps/rooms/models.py
```python
from django.db import models
from apps.facilities.models import Facility

class Room(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    floor = models.IntegerField(default=1)
    map_svg_id = models.CharField(max_length=100, blank=True, null=True, help_text='SVG element ID e.g. RST-F1-CL1')
    room_type = models.CharField(max_length=50, default='classroom',
        choices=[('classroom','Classroom'),('office','Office'),('lab','Laboratory'),
                 ('facility','Facility'),('staircase','Staircase'),('restroom','Restroom'),('other','Other')])
    is_crucial = models.BooleanField(default=False)
    search_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rooms'

    def __str__(self):
        return f'{self.facility.code} - {self.name} (Floor {self.floor})'
```

#### apps/navigation/models.py
```python
from django.db import models
from apps.facilities.models import Facility
from apps.rooms.models import Room

class NavigationNode(models.Model):
    NODE_TYPES = [
        ('room', 'Room'), ('facility', 'Facility'), ('waypoint', 'Waypoint'),
        ('entrance', 'Entrance'), ('staircase', 'Staircase'),
        ('elevator', 'Elevator'), ('junction', 'Junction'),
    ]
    name = models.CharField(max_length=200)
    node_type = models.CharField(max_length=20, choices=NODE_TYPES)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    map_svg_id = models.CharField(max_length=100, blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    floor = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_nodes'

    def __str__(self):
        return f'{self.name} ({self.node_type})'

class NavigationEdge(models.Model):
    from_node = models.ForeignKey(NavigationNode, on_delete=models.CASCADE, related_name='edges_from')
    to_node = models.ForeignKey(NavigationNode, on_delete=models.CASCADE, related_name='edges_to')
    distance = models.IntegerField()
    is_bidirectional = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_edges'

    def __str__(self):
        return f'{self.from_node.name} → {self.to_node.name} ({self.distance})'
```

#### apps/chatbot/models.py
```python
from django.db import models

class FAQEntry(models.Model):
    CATEGORIES = [
        ('location', 'Location'), ('schedule', 'Schedule'),
        ('academic', 'Academic'), ('services', 'Services'), ('general', 'General'),
    ]
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES, default='general')
    keywords = models.TextField(default='', blank=True, help_text='Comma-separated keywords for offline matching')
    usage_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faq_entries'

    def __str__(self):
        return self.question[:80]

class AIChatLog(models.Model):
    MODES = [('online', 'Online AI'), ('offline', 'Offline FAQ Fallback')]
    user_query = models.TextField()
    ai_response = models.TextField(blank=True, null=True)
    mode = models.CharField(max_length=10, choices=MODES)
    response_time_ms = models.IntegerField(blank=True, null=True)
    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    faq_entry = models.ForeignKey(FAQEntry, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_logs'
```

#### apps/notifications/models.py
```python
from django.db import models

class Notification(models.Model):
    TYPES = [
        ('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'),
        ('error', 'Error'), ('emergency', 'Emergency'),
        ('facility_update', 'Facility Update'), ('navigation_update', 'Navigation Update'),
        ('system_maintenance', 'System Maintenance'), ('app_update', 'App Update'),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=TYPES, default='info')
    data_json = models.TextField(default='{}')
    priority = models.IntegerField(default=1, choices=[(1,'Low'),(2,'Medium'),(3,'High'),(4,'Urgent')])
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
```

#### apps/feedback/models.py
```python
from django.db import models
from apps.facilities.models import Facility
from apps.rooms.models import Room

class Feedback(models.Model):
    CATEGORIES = [
        ('map_accuracy', 'Map Accuracy'), ('ai_chatbot', 'AI Chatbot'),
        ('navigation', 'Navigation'), ('general', 'General'),
        ('bug_report', 'Bug Report'), ('facility', 'Facility'), ('room', 'Room'),
    ]
    rating = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORIES, default='general')
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'
```

### 2.6 Create .env.example at project root

```
SECRET_KEY=django-insecure-technopath-seait-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2.7 Create backend_django/manage.py

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technopath.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

---

## TASK 3 — SET UP VUE.JS PWA FRONTEND

Create the following folder structure at the project root:

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── public/
│   ├── manifest.json
│   ├── sw.js
│   └── maps/
│       └── (SVG map files will go here)
└── src/
    ├── main.js
    ├── App.vue
    ├── router/
    │   └── index.js
    ├── stores/
    │   ├── mapStore.js
    │   ├── chatbotStore.js
    │   └── syncStore.js
    ├── services/
    │   ├── api.js
    │   ├── db.js
    │   ├── geolocation.js
    │   └── pathfinder.js
    ├── views/
    │   ├── HomeView.vue
    │   ├── MapView.vue
    │   ├── NavigateView.vue
    │   ├── ChatbotView.vue
    │   └── NotificationsView.vue
    └── components/
        ├── MapCanvas.vue
        ├── FloorMapSVG.vue
        ├── NavigationPanel.vue
        ├── ChatbotWidget.vue
        ├── QRScanner.vue
        └── NotificationBadge.vue
```

### 3.1 Create frontend/package.json

```json
{
  "name": "technopath-pwa",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "leaflet": "^1.9.4",
    "dexie": "^3.2.0",
    "fuse.js": "^7.0.0",
    "jsqr": "^1.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "vite-plugin-pwa": "^0.19.0"
  }
}
```

### 3.2 Create frontend/vite.config.js

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,jpg}'],
        runtimeCaching: [
          {
            urlPattern: /^http:\/\/localhost:8000\/api\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 86400 }
            }
          }
        ]
      },
      manifest: {
        name: 'TechnoPath SEAIT Guide',
        short_name: 'TechnoPath',
        description: 'SEAIT Campus Guide Map and Navigation System',
        theme_color: '#FF9800',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      }
    })
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 3.3 Create frontend/src/services/db.js (IndexedDB via Dexie)

```javascript
import Dexie from 'dexie'

const db = new Dexie('TechnoPathDB')

db.version(1).stores({
  facilities: '++id, code, map_svg_id, is_deleted',
  rooms: '++id, facility_id, code, map_svg_id, floor, is_deleted',
  navigation_nodes: '++id, map_svg_id, node_type, floor, is_deleted',
  navigation_edges: '++id, from_node_id, to_node_id',
  faq_entries: '++id, category, keywords, is_deleted',
  notifications: '++id, type, is_read, created_at',
  feedback: '++id, category, created_at',
  sync_meta: 'key'
})

export default db
```

### 3.4 Create frontend/src/services/pathfinder.js (Dijkstra in JavaScript)

```javascript
// Dijkstra's algorithm — ported from pathfinder.dart
// Works fully offline using navigation_nodes and navigation_edges from IndexedDB

export function dijkstra(nodes, edges, startId, endId) {
  const distances = {}
  const previous = {}
  const visited = new Set()
  const queue = []

  nodes.forEach(n => {
    distances[n.id] = Infinity
    previous[n.id] = null
  })
  distances[startId] = 0
  queue.push({ id: startId, dist: 0 })

  while (queue.length > 0) {
    queue.sort((a, b) => a.dist - b.dist)
    const { id: currentId } = queue.shift()

    if (visited.has(currentId)) continue
    visited.add(currentId)

    if (currentId === endId) break

    const neighbors = edges.filter(
      e => (!e.is_deleted) && (
        e.from_node_id === currentId ||
        (e.is_bidirectional && e.to_node_id === currentId)
      )
    )

    for (const edge of neighbors) {
      const neighborId = edge.from_node_id === currentId ? edge.to_node_id : edge.from_node_id
      if (visited.has(neighborId)) continue
      const newDist = distances[currentId] + edge.distance
      if (newDist < distances[neighborId]) {
        distances[neighborId] = newDist
        previous[neighborId] = currentId
        queue.push({ id: neighborId, dist: newDist })
      }
    }
  }

  // Reconstruct path
  const path = []
  let current = endId
  while (current !== null) {
    path.unshift(current)
    current = previous[current]
  }

  if (path[0] !== startId) return null // No path found
  return { path, distance: distances[endId] }
}
```

### 3.5 Create frontend/src/services/geolocation.js

```javascript
// GPS location service using Web Geolocation API — works offline

export function watchLocation(onUpdate, onError) {
  if (!navigator.geolocation) {
    onError('Geolocation is not supported by this browser.')
    return null
  }

  const watchId = navigator.geolocation.watchPosition(
    (position) => {
      onUpdate({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
        accuracy: position.coords.accuracy
      })
    },
    (error) => onError(error.message),
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
  )

  return watchId
}

export function stopWatching(watchId) {
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId)
  }
}

// Convert real GPS coordinates to SVG/image pixel coordinates
// Call this once with your campus boundary GPS points after map is finalized
export function gpsToMapCoords(lat, lng, mapBounds) {
  const { minLat, maxLat, minLng, maxLng, mapWidth, mapHeight } = mapBounds
  const x = ((lng - minLng) / (maxLng - minLng)) * mapWidth
  const y = ((maxLat - lat) / (maxLat - minLat)) * mapHeight
  return { x, y }
}
```

---

## TASK 4 — UPDATE ROOT FILES

### 4.1 Create a new README.md at the project root

```markdown
# TechnoPath: SEAIT Guide Map and Navigation System

A Progressive Web App (PWA) campus guide and navigation system for
South East Asian Institute of Technology, Inc. (SEAIT).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python Django + Django REST Framework |
| AI Chatbot | Python Flask |
| Frontend | Vue.js 3 + Vite (PWA) |
| 2D Map | Leaflet.js + SVG |
| Offline Storage | IndexedDB (Dexie.js) |
| Pathfinding | Dijkstra (JavaScript, client-side) |
| GPS | Web Geolocation API |
| QR Scanning | jsQR (browser-based) |
| Database | SQLite (dev) / PostgreSQL (prod) |

## Project Structure

```
version4_technopath/
├── backend_django/     ← Django REST API (Python)
├── frontend/           ← Vue.js PWA
├── chatbot_flask/      ← Flask AI Chatbot (Python)
├── assets/             ← Map images and static assets
└── _flutter_archive/   ← Original Flutter app (reference only)
```

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### Start Backend (Django)
```bash
cd backend_django
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Runs at http://localhost:8000
```

### Start Frontend (Vue.js PWA)
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173
```

### Start Chatbot (Flask)
```bash
cd chatbot_flask
python app.py
# Runs at http://localhost:5000
```

## Admin Panel
Access the Django admin at: http://localhost:8000/admin/

Role-based access:
- **Safety and Security Office** — full system control
- **Program Head** — department rooms and announcements
- **Dean** — oversight and validation
```

### 4.2 Update .gitignore

Add these lines to the existing .gitignore:

```
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.env
*.db
*.sqlite3

# Node
node_modules/
dist/
.vite/

# Django
backend_django/staticfiles/
backend_django/media/

# Flutter archive (keep files, ignore build artifacts inside)
_flutter_archive/build/
_flutter_archive/.dart_tool/
```

---

## TASK 5 — VERIFY THE FINAL STRUCTURE

After all tasks are complete, the project root should look like this:

```
version4_technopath/
├── _flutter_archive/       ← All moved Flutter/Dart/Node files
├── backend_django/         ← NEW: Django Python backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── technopath/
│   └── apps/
├── frontend/               ← NEW: Vue.js PWA frontend
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── chatbot_flask/          ← KEPT: Flask chatbot (unchanged)
│   ├── app.py
│   └── requirements.txt
├── assets/                 ← KEPT: Map assets
│   └── maps/
├── .windsurf/              ← KEPT
├── .gitignore              ← UPDATED
└── README.md               ← UPDATED
```

---

## TASK 6 — MOBILE PWA + ADMIN-TO-USER SYNC

This task covers three critical requirements:
- The app must be fully installable and usable on **Android and iPhone**
- The **admin panel is desktop-only** (Safety and Security Office, Program Heads, Dean)
- When an admin saves changes on desktop, those **updates must reach mobile users** the next time they connect to the internet

---

### 6.1 Update frontend/index.html for Mobile and iOS PWA Support

Replace the contents of `frontend/index.html` with:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />

    <!-- Mobile viewport — critical for all phones -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />

    <!-- PWA Meta Tags -->
    <meta name="theme-color" content="#FF9800" />
    <meta name="mobile-web-app-capable" content="yes" />
    <meta name="application-name" content="TechnoPath" />

    <!-- iOS Safari PWA — required for iPhone home screen install -->
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="default" />
    <meta name="apple-mobile-web-app-title" content="TechnoPath" />
    <link rel="apple-touch-icon" href="/icons/icon-192.png" />
    <link rel="apple-touch-startup-image" href="/icons/splash.png" />

    <!-- Standard PWA -->
    <link rel="icon" type="image/png" href="/icons/icon-192.png" />
    <link rel="manifest" href="/manifest.json" />

    <title>TechnoPath — SEAIT Campus Guide</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

---

### 6.2 Update frontend/public/manifest.json for Android and iOS Install

```json
{
  "name": "TechnoPath SEAIT Campus Guide",
  "short_name": "TechnoPath",
  "description": "SEAIT Campus Guide Map and Navigation System",
  "start_url": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#ffffff",
  "theme_color": "#FF9800",
  "lang": "en",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "categories": ["education", "navigation"],
  "screenshots": []
}
```

---

### 6.3 Create frontend/src/assets/main.css — Mobile-First Global Styles

Create `frontend/src/assets/main.css` with the following content:

```css
/* Mobile-first reset and base styles for TechnoPath PWA */

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --color-primary: #FF9800;
  --color-primary-dark: #E65100;
  --color-primary-light: #FFE0B2;
  --color-bg: #ffffff;
  --color-surface: #f5f5f5;
  --color-text: #212121;
  --color-text-secondary: #757575;
  --color-border: #e0e0e0;
  --color-danger: #d32f2f;
  --color-success: #388e3c;
  --bottom-nav-height: 64px;
  --top-bar-height: 56px;
  --safe-area-bottom: env(safe-area-inset-bottom, 0px);
}

html, body {
  height: 100%;
  width: 100%;
  overflow: hidden; /* prevent scroll bounce on iOS */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 16px;
  color: var(--color-text);
  background: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -webkit-tap-highlight-color: transparent; /* remove tap flash on mobile */
  touch-action: manipulation;
}

#app {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Touch targets must be at least 48x48px for accessibility on mobile */
button, a, [role="button"] {
  min-height: 48px;
  min-width: 48px;
  cursor: pointer;
  border: none;
  background: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  -webkit-tap-highlight-color: transparent;
}

/* Bottom navigation bar — sits above iPhone home indicator */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: calc(var(--bottom-nav-height) + var(--safe-area-bottom));
  padding-bottom: var(--safe-area-bottom);
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.08);
}

/* Top bar */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--top-bar-height);
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

/* Main content area — sits between top bar and bottom nav */
.main-content {
  position: fixed;
  top: var(--top-bar-height);
  bottom: calc(var(--bottom-nav-height) + var(--safe-area-bottom));
  left: 0;
  right: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch; /* smooth scroll on iOS */
}

/* Map fills full screen between top and bottom bars */
.map-container {
  position: fixed;
  top: var(--top-bar-height);
  bottom: calc(var(--bottom-nav-height) + var(--safe-area-bottom));
  left: 0;
  right: 0;
  overflow: hidden;
}

/* Card component */
.card {
  background: var(--color-bg);
  border-radius: 12px;
  padding: 16px;
  margin: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}

/* Primary button */
.btn-primary {
  background: var(--color-primary);
  color: #fff;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  width: 100%;
  min-height: 48px;
}

.btn-primary:active {
  background: var(--color-primary-dark);
}

/* Admin-only: desktop panel styles applied only on screens wider than 768px */
@media (min-width: 768px) {
  .admin-panel {
    display: flex;
    flex-direction: row;
    height: 100vh;
  }

  .admin-sidebar {
    width: 260px;
    min-width: 260px;
    background: var(--color-surface);
    border-right: 1px solid var(--color-border);
    padding: 24px 0;
    overflow-y: auto;
  }

  .admin-main {
    flex: 1;
    overflow-y: auto;
    padding: 32px;
  }
}

/* Hide admin panel completely on mobile screens */
@media (max-width: 767px) {
  .admin-panel-desktop-only {
    display: none !important;
  }
}
```

---

### 6.4 Create frontend/src/services/sync.js — Admin-to-User Data Sync

This is the core sync service. When a mobile user opens the app with internet, this runs automatically and downloads all updated data from Django into IndexedDB. When an admin saves changes on desktop, those changes are stored in Django. This service bridges them.

Create `frontend/src/services/sync.js`:

```javascript
import db from './db.js'
import api from './api.js'

// Key stored in IndexedDB sync_meta table to track last sync time
const LAST_SYNC_KEY = 'last_sync_timestamp'

// Check if device is online
export function isOnline() {
  return navigator.onLine
}

// Get the last time this device synced with the server
async function getLastSync() {
  try {
    const meta = await db.sync_meta.get(LAST_SYNC_KEY)
    return meta ? meta.value : null
  } catch {
    return null
  }
}

// Save the current time as last sync timestamp
async function setLastSync(timestamp) {
  await db.sync_meta.put({ key: LAST_SYNC_KEY, value: timestamp })
}

// Main sync function — call this on app startup when online
export async function syncAllData() {
  if (!isOnline()) {
    console.log('[Sync] Device is offline — skipping sync, using cached data')
    return { success: false, reason: 'offline' }
  }

  try {
    console.log('[Sync] Online — starting data sync from server...')
    const lastSync = await getLastSync()
    const syncStart = new Date().toISOString()

    // Fetch all data from Django API in parallel
    const [
      facilitiesRes,
      roomsRes,
      nodesRes,
      edgesRes,
      faqRes,
      notificationsRes
    ] = await Promise.all([
      api.get('/facilities/'),
      api.get('/rooms/'),
      api.get('/navigation/nodes/'),
      api.get('/navigation/edges/'),
      api.get('/chatbot/faq/'),
      api.get('/notifications/')
    ])

    // Write all fetched data into IndexedDB (replaces existing data)
    await db.transaction('rw',
      db.facilities,
      db.rooms,
      db.navigation_nodes,
      db.navigation_edges,
      db.faq_entries,
      db.notifications,
      async () => {
        await db.facilities.clear()
        await db.facilities.bulkPut(facilitiesRes.data)

        await db.rooms.clear()
        await db.rooms.bulkPut(roomsRes.data)

        await db.navigation_nodes.clear()
        await db.navigation_nodes.bulkPut(nodesRes.data)

        await db.navigation_edges.clear()
        await db.navigation_edges.bulkPut(edgesRes.data)

        await db.faq_entries.clear()
        await db.faq_entries.bulkPut(faqRes.data)

        await db.notifications.clear()
        await db.notifications.bulkPut(notificationsRes.data)
      }
    )

    // Save sync timestamp
    await setLastSync(syncStart)

    console.log('[Sync] Sync complete — all data saved to IndexedDB for offline use')
    return { success: true, syncedAt: syncStart }

  } catch (error) {
    console.error('[Sync] Sync failed:', error.message)
    return { success: false, reason: error.message }
  }
}

// Upload any queued offline feedback/ratings when back online
export async function syncOfflineQueue() {
  if (!isOnline()) return

  try {
    const pendingFeedback = await db.feedback
      .where('synced')
      .equals(0)
      .toArray()

    for (const item of pendingFeedback) {
      try {
        await api.post('/feedback/', item)
        await db.feedback.update(item.id, { synced: 1 })
      } catch (err) {
        console.warn('[Sync] Could not upload feedback item:', err.message)
      }
    }
  } catch (err) {
    console.warn('[Sync] Offline queue sync failed:', err.message)
  }
}

// Listen for connectivity changes and auto-sync when coming back online
export function registerConnectivityListener(onSyncComplete) {
  window.addEventListener('online', async () => {
    console.log('[Sync] Connection restored — syncing data...')
    const result = await syncAllData()
    await syncOfflineQueue()
    if (onSyncComplete) onSyncComplete(result)
  })

  window.addEventListener('offline', () => {
    console.log('[Sync] Connection lost — app will continue working offline')
  })
}
```

---

### 6.5 Update frontend/src/main.js — Run Sync on App Startup

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import './assets/main.css'
import { syncAllData, registerConnectivityListener } from './services/sync.js'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

// On app load: sync data from Django to IndexedDB if online
syncAllData().then(result => {
  if (result.success) {
    console.log('TechnoPath: Data synced at', result.syncedAt)
  } else {
    console.log('TechnoPath: Running offline with cached data')
  }
})

// Auto-sync whenever the device reconnects to the internet
registerConnectivityListener((result) => {
  console.log('TechnoPath: Reconnected and synced:', result)
})
```

---

### 6.6 Create frontend/src/stores/syncStore.js — Sync State for UI

```javascript
import { defineStore } from 'pinia'
import { syncAllData, isOnline } from '../services/sync.js'

export const useSyncStore = defineStore('sync', {
  state: () => ({
    isOnline: navigator.onLine,
    isSyncing: false,
    lastSyncedAt: null,
    syncError: null
  }),

  actions: {
    async sync() {
      this.isSyncing = true
      this.syncError = null
      const result = await syncAllData()
      this.isSyncing = false
      if (result.success) {
        this.lastSyncedAt = result.syncedAt
      } else {
        this.syncError = result.reason
      }
    },

    updateOnlineStatus() {
      this.isOnline = navigator.onLine
    }
  }
})
```

---

### 6.7 Update frontend/src/App.vue — Offline Banner + Sync Status

```vue
<template>
  <div id="app-root">

    <!-- Offline banner — shown automatically when device loses internet -->
    <div v-if="!syncStore.isOnline" class="offline-banner">
      You are offline — map and navigation still work using saved data
    </div>

    <!-- Sync indicator — shown when syncing data from server -->
    <div v-if="syncStore.isSyncing" class="sync-banner">
      Updating map data...
    </div>

    <!-- Router view renders the current page -->
    <router-view />

  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useSyncStore } from './stores/syncStore.js'

const syncStore = useSyncStore()

function updateStatus() {
  syncStore.updateOnlineStatus()
}

onMounted(() => {
  window.addEventListener('online', updateStatus)
  window.addEventListener('offline', updateStatus)
})

onUnmounted(() => {
  window.removeEventListener('online', updateStatus)
  window.removeEventListener('offline', updateStatus)
})
</script>

<style scoped>
#app-root {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.offline-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: #616161;
  color: #fff;
  text-align: center;
  padding: 8px 16px;
  font-size: 13px;
}

.sync-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: #FF9800;
  color: #fff;
  text-align: center;
  padding: 8px 16px;
  font-size: 13px;
}
</style>
```

---

### 6.8 Create frontend/src/views/AdminView.vue — Desktop-Only Admin Panel

This view is only accessible to logged-in admins and is designed for desktop use. On mobile it shows a message telling the user to use a desktop browser.

```vue
<template>
  <div>

    <!-- Mobile users see this message instead of the admin panel -->
    <div v-if="isMobile" class="mobile-admin-block">
      <div class="mobile-admin-message">
        <h2>Admin Panel</h2>
        <p>The administrative panel is designed for desktop use.</p>
        <p>Please access this on a desktop or laptop computer.</p>
      </div>
    </div>

    <!-- Desktop admin panel -->
    <div v-else class="admin-panel">

      <!-- Sidebar -->
      <aside class="admin-sidebar">
        <div class="admin-logo">TechnoPath Admin</div>
        <nav class="admin-nav">
          <a
            v-for="item in allowedMenuItems"
            :key="item.key"
            :class="['admin-nav-item', { active: activeSection === item.key }]"
            @click="activeSection = item.key"
          >
            {{ item.label }}
          </a>
          <a class="admin-nav-item danger" @click="logout">Logout</a>
        </nav>
        <div class="admin-user-info">
          <span>{{ authStore.user?.username }}</span>
          <span class="admin-role">{{ authStore.user?.user_type_display }}</span>
        </div>
      </aside>

      <!-- Main content -->
      <main class="admin-main">

        <!-- Dashboard — all admin types -->
        <section v-if="activeSection === 'dashboard'">
          <h1>Dashboard</h1>
          <p>Welcome, {{ authStore.user?.username }}.</p>
        </section>

        <!-- Facilities — super_admin only -->
        <section v-if="activeSection === 'facilities' && isSuperAdmin">
          <h1>Manage Facilities</h1>
          <p>Add, edit, or remove campus buildings.</p>
          <!-- Facility CRUD components go here -->
        </section>

        <!-- Rooms — super_admin and program_head -->
        <section v-if="activeSection === 'rooms' && canManageRooms">
          <h1>Manage Rooms</h1>
          <p>Update classroom assignments, office designations, and room labels.</p>
          <!-- Room CRUD components go here -->
        </section>

        <!-- Notifications — super_admin only -->
        <section v-if="activeSection === 'notifications' && isSuperAdmin">
          <h1>Send Notifications</h1>
          <p>Push announcements to all app users.</p>
          <!-- Notification form goes here -->
        </section>

        <!-- FAQ — super_admin only -->
        <section v-if="activeSection === 'faq' && isSuperAdmin">
          <h1>Manage FAQ / Offline Chatbot</h1>
          <p>Add and edit questions and answers for offline chatbot fallback.</p>
          <!-- FAQ CRUD goes here -->
        </section>

        <!-- Dean oversight -->
        <section v-if="activeSection === 'oversight' && isDean">
          <h1>Oversight</h1>
          <p>Review and validate departmental updates.</p>
          <!-- Audit log view goes here -->
        </section>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore.js'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const activeSection = ref('dashboard')

// Detect if user is on a mobile device
const isMobile = computed(() => window.innerWidth < 768)

const isSuperAdmin = computed(() => authStore.user?.user_type === 'super_admin')
const isDean = computed(() => authStore.user?.user_type === 'dean')
const canManageRooms = computed(() =>
  ['super_admin', 'program_head'].includes(authStore.user?.user_type)
)

// Build menu based on role
const allowedMenuItems = computed(() => {
  const items = [{ key: 'dashboard', label: 'Dashboard' }]
  if (isSuperAdmin.value) {
    items.push({ key: 'facilities', label: 'Facilities' })
    items.push({ key: 'notifications', label: 'Notifications' })
    items.push({ key: 'faq', label: 'FAQ / Chatbot' })
  }
  if (canManageRooms.value) {
    items.push({ key: 'rooms', label: 'Rooms' })
  }
  if (isDean.value) {
    items.push({ key: 'oversight', label: 'Oversight' })
  }
  return items
})

function logout() {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  if (!authStore.isLoggedIn) {
    router.push('/admin/login')
  }
})
</script>

<style scoped>
.mobile-admin-block {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  padding: 32px;
  text-align: center;
}

.mobile-admin-message h2 {
  font-size: 22px;
  margin-bottom: 12px;
  color: var(--color-primary);
}

.mobile-admin-message p {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.admin-logo {
  padding: 20px 24px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary);
  border-bottom: 1px solid var(--color-border);
}

.admin-nav {
  padding: 16px 0;
}

.admin-nav-item {
  display: block;
  padding: 12px 24px;
  font-size: 15px;
  cursor: pointer;
  color: var(--color-text);
  transition: background 0.15s;
}

.admin-nav-item:hover,
.admin-nav-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.admin-nav-item.danger {
  color: var(--color-danger);
  margin-top: auto;
}

.admin-user-info {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 260px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  font-size: 13px;
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.admin-role {
  font-size: 11px;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-main h1 {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 8px;
}
</style>
```

---

### 6.9 Create frontend/src/stores/authStore.js — Admin Authentication

```javascript
import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('technopath_user') || 'null'),
    token: localStorage.getItem('technopath_token') || null,
    refreshToken: localStorage.getItem('technopath_refresh') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => !!state.user,
    isSuperAdmin: (state) => state.user?.user_type === 'super_admin',
  },

  actions: {
    async login(username, password) {
      const response = await api.post('/auth/login/', { username, password })
      const { access, refresh } = response.data

      this.token = access
      this.refreshToken = refresh
      localStorage.setItem('technopath_token', access)
      localStorage.setItem('technopath_refresh', refresh)

      // Fetch user profile
      const userRes = await api.get('/users/me/')
      this.user = userRes.data
      localStorage.setItem('technopath_user', JSON.stringify(userRes.data))
    },

    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('technopath_token')
      localStorage.removeItem('technopath_refresh')
      localStorage.removeItem('technopath_user')
    }
  }
})
```

---

### 6.10 Create frontend/src/services/api.js — Axios HTTP Client with Auth

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// Attach JWT token to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('technopath_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token expiry — auto-refresh then retry
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('technopath_refresh')
        const res = await axios.post('/api/auth/refresh/', { refresh })
        const newToken = res.data.access
        localStorage.setItem('technopath_token', newToken)
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      } catch {
        localStorage.removeItem('technopath_token')
        localStorage.removeItem('technopath_refresh')
        window.location.href = '/admin/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

---

### 6.11 Update frontend/src/router/index.js — Routes with Admin Guard

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // Public mobile routes
  { path: '/', component: () => import('../views/HomeView.vue') },
  { path: '/map', component: () => import('../views/MapView.vue') },
  { path: '/navigate', component: () => import('../views/NavigateView.vue') },
  { path: '/chatbot', component: () => import('../views/ChatbotView.vue') },
  { path: '/notifications', component: () => import('../views/NotificationsView.vue') },

  // Admin routes — require login
  { path: '/admin/login', component: () => import('../views/AdminLoginView.vue') },
  {
    path: '/admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard — redirect to login if not authenticated
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('technopath_token')
    if (!token) {
      next('/admin/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
```

---

### 6.12 Update frontend/src/services/db.js — Add synced field for offline queue

Update the Dexie database definition to add the `synced` field to `feedback` so offline submissions can be queued:

```javascript
import Dexie from 'dexie'

const db = new Dexie('TechnoPathDB')

db.version(1).stores({
  facilities:        '++id, code, map_svg_id, is_deleted',
  rooms:             '++id, facility_id, code, map_svg_id, floor, is_deleted',
  navigation_nodes:  '++id, map_svg_id, node_type, floor, is_deleted',
  navigation_edges:  '++id, from_node_id, to_node_id',
  faq_entries:       '++id, category, keywords, is_deleted',
  notifications:     '++id, type, is_read, created_at',
  feedback:          '++id, category, synced, created_at',
  sync_meta:         'key'
})

export default db
```

---

## IMPORTANT NOTES FOR KIMI

1. **Do not delete any Flutter files** — only move them to `_flutter_archive/`
2. **Do not modify `chatbot_flask/`** — it stays exactly as-is
3. **The `assets/` folder stays at the root** — the frontend will reference maps from there
4. **All Django apps must have `__init__.py`** — otherwise Django won't recognize them as Python packages
5. **The `apps/` directory inside `backend_django/` also needs an `__init__.py`**
6. **After creating all files, run these commands to verify Django is set up correctly:**

```bash
cd backend_django
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py check
```

The command `python manage.py check` should return `System check identified no issues (0 silenced).`

7. **Dart is fully replaced** — `backend_dart/` is archived, no Dart code is needed anywhere in the new system
8. **Node.js backend is fully replaced** — `backend/` (server.js) is archived, Django handles all API endpoints
9. The `map_svg_id` field added to `facilities` and `rooms` models is critical — this is how the SVG map shapes connect to database records
10. **Mobile users (Android + iPhone)** are the primary users — all public-facing views must be mobile-first using the CSS variables and layout classes defined in `main.css`
11. **Admin panel is desktop-only** — `AdminView.vue` already handles this with the `isMobile` check that shows a "use desktop" message on phones
12. **The sync flow is: Admin saves on desktop → Django SQLite updated → Mobile user reconnects → `sync.js` pulls all data → IndexedDB updated → user sees new data offline** — this is fully implemented in Task 6
13. **`syncAllData()` in `sync.js` runs on every app startup** (wired in `main.js`) and also runs automatically whenever the device comes back online via `registerConnectivityListener()`
14. **Offline feedback queue** — feedback submitted while offline is saved to IndexedDB with `synced: 0` and uploaded automatically when the device reconnects via `syncOfflineQueue()`
15. **iOS Safari requires the apple-mobile-web-app meta tags** in `index.html` (already added in Task 6.1) — without these, the app will NOT be installable on iPhones from Safari

---

*This migration is for TechnoPath: SEAIT Guide Map and Navigation System — South East Asian Institute of Technology, Inc., Tupi, South Cotabato, Philippines.*
