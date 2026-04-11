from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

from django.db.models import Exists, OuterRef
from .models import NotificationReadStatus

class NotificationListView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Notification.objects.all()
        user = self.request.user
        if user.is_authenticated:
            qs = qs.annotate(
                is_read_by_user=Exists(
                    NotificationReadStatus.objects.filter(
                        notification=OuterRef('pk'),
                        user=user
                    )
                )
            )
        return qs

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Using the same logic for detail view
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Notification.objects.all()
        user = self.request.user
        if user.is_authenticated:
            qs = qs.annotate(
                is_read_by_user=Exists(
                    NotificationReadStatus.objects.filter(
                        notification=OuterRef('pk'),
                        user=user
                    )
                )
            )
        return qs

class MarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        from .models import NotificationReadStatus
        # Find all notifications that this user hasn't read yet
        unread = Notification.objects.exclude(
            notificationreadstatus__user=request.user
        )
        status_objects = [
            NotificationReadStatus(user=request.user, notification=n)
            for n in unread
        ]
        # Bulk create ignoring conflicts if they somehow already exist
        NotificationReadStatus.objects.bulk_create(status_objects, ignore_conflicts=True)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class MarkOneReadView(APIView):
    """
    POST /api/notifications/<pk>/read/
    Marks a single notification as read for the current user.
    Guest users manage read state locally in IndexedDB;
    authenticated admins use this endpoint so read state persists across devices.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)

        NotificationReadStatus.objects.get_or_create(
            user=request.user,
            notification=notification,
        )
        return Response({'status': 'read'}, status=status.HTTP_200_OK)
