from django.urls import path
from . import views

urlpatterns = [
    path('maps/', views.MapGalleryView.as_view(), name='map-gallery'),
    path('maps/<str:filename>/', views.MapGalleryView.as_view(), name='map-delete'),
    path('import/', views.ImportMapView.as_view(), name='import-map'),
    path('nodes/', views.NavigationNodeListView.as_view(), name='node-list'),
    path('nodes/<int:pk>/', views.NavigationNodeDetailView.as_view(), name='node-detail'),
    path('edges/', views.NavigationEdgeListView.as_view(), name='edge-list'),
    path('edges/<int:pk>/', views.NavigationEdgeDetailView.as_view(), name='edge-detail'),
    path('route/', views.FindRouteView.as_view(), name='find-route'),
    path('grid-settings/', views.GridSettingsView.as_view(), name='grid-settings'),
    path('paths/', views.NavigationPathsView.as_view(), name='navigation-paths'),
    path('paths/<int:pk>/', views.NavigationPathDetailView.as_view(), name='navigation-path-detail'),
]
