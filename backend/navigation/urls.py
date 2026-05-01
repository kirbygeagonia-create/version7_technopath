from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'paths', views.SvgPathViewSet, basename='svgpath')
router.register(r'nodes', views.NavigationNodeViewSet, basename='navigationnode')

urlpatterns = [
    path('', include(router.urls)),
    path('grid-settings/', views.grid_settings, name='grid_settings'),
    path('route/', views.find_route, name='find_route'),
]
