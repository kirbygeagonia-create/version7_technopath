from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import AdminUser
from .serializers import AdminUserSerializer, UserMeSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    serializer = UserMeSerializer(request.user)
    return Response(serializer.data)

class UserListView(generics.ListAPIView):
    queryset = AdminUser.objects.filter(is_active=True)
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]
