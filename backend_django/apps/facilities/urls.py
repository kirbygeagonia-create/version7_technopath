from django.urls import path
from . import views

urlpatterns = [
    path('', views.FacilityListView.as_view(), name='facility-list'),
    path('<int:pk>/', views.FacilityDetailView.as_view(), name='facility-detail'),
]
