from django.urls import path
from . import views

urlpatterns = [
    path('', views.FeedbackListView.as_view(), name='feedback-list'),
    path('<int:pk>/', views.FeedbackDetailView.as_view(), name='feedback-detail'),
]
