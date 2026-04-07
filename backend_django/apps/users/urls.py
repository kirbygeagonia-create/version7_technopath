from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user-list'),
    path('me/', views.me_view, name='user-me'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
