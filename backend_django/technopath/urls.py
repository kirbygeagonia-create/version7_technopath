from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        'message': 'TechnoPath API Server',
        'version': '1.0.0',
        'endpoints': {
            'admin':         '/admin/',
            'auth_login':    '/api/users/login/',   # custom login with permissions dict
            'auth_refresh':  '/api/auth/refresh/',
            'facilities':    '/api/facilities/',
            'rooms':         '/api/rooms/',
            'navigation':    '/api/navigation/',
            'chatbot':       '/api/chatbot/',
            'notifications': '/api/notifications/',
            'core':          '/api/core/',
        },
        'frontend': 'http://localhost:5173',
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),

    # FIX: Removed duplicate TokenObtainPairView at /api/auth/login/
    # The custom LoginView at /api/users/login/ is the correct one —
    # it returns permissions dict, writes audit log, and handles lockout.
    # The simplejwt default endpoint was a security surface with no permissions.
    # Keep only the refresh endpoint from simplejwt.
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/users/',         include('apps.users.urls')),
    path('api/facilities/',    include('apps.facilities.urls')),
    path('api/rooms/',         include('apps.rooms.urls')),
    path('api/navigation/',    include('apps.navigation.urls')),
    path('api/chatbot/',       include('apps.chatbot.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/feedback/',      include('apps.feedback.urls')),
    path('api/core/',          include('apps.core.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
