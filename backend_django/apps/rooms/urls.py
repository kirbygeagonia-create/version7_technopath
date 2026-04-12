from django.urls import path
from . import views

urlpatterns = [
    path('', views.RoomListView.as_view(), name='room-list'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
    # Course filter — returns distinct course codes with colors + room counts
    path('courses/', views.course_list_view, name='room-courses'),
]
