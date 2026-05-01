from django.urls import path
from .views import (LoginView, LogoutView, MeView,
                    AdminListCreateView, AdminDetailView, AuditLogView,
                    PublicDirectoryView, UserListView)

urlpatterns = [
    path('',                 UserListView.as_view()),  # GET /api/users/
    path('login/',           LoginView.as_view()),
    path('logout/',          LogoutView.as_view()),
    path('me/',              MeView.as_view()),
    path('admins/',          AdminListCreateView.as_view()),
    path('admins/<int:pk>/', AdminDetailView.as_view()),
    path('audit-log/',       AuditLogView.as_view()),
    path('directory/',       PublicDirectoryView.as_view()),  # Public endpoint for instructors/employees
]
