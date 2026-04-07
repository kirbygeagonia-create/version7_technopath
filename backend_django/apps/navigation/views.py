from rest_framework import generics, permissions
from .models import NavigationNode, NavigationEdge
from .serializers import NavigationNodeSerializer, NavigationEdgeSerializer

class NavigationNodeListView(generics.ListCreateAPIView):
    queryset = NavigationNode.objects.filter(is_deleted=False)
    serializer_class = NavigationNodeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class NavigationNodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NavigationNode.objects.filter(is_deleted=False)
    serializer_class = NavigationNodeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class NavigationEdgeListView(generics.ListCreateAPIView):
    queryset = NavigationEdge.objects.filter(is_deleted=False)
    serializer_class = NavigationEdgeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class NavigationEdgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NavigationEdge.objects.filter(is_deleted=False)
    serializer_class = NavigationEdgeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
