from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

from django.db.models import Exists, OuterRef, Q
from .models import NotificationReadStatus
from django.contrib.auth import get_user_model

User = get_user_model()

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


class UnreadCountView(APIView):
    """
    GET /api/notifications/unread-count/
    Returns the count of unread notifications for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Count notifications that don't have a read status for this user
        unread_count = Notification.objects.filter(
            ~Exists(
                NotificationReadStatus.objects.filter(
                    user=request.user,
                    notification=OuterRef('pk')
                )
            )
        ).count()
        return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)


class SendNotificationView(APIView):
    """
    POST /api/notifications/send/
    Creates a notification that will be visible to users.
    Requires admin/staff permissions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Check if user has permission to send notifications
        if not request.user.is_staff and not getattr(request.user, 'role', '') in ['admin', 'super_admin', 'dean', 'program_head']:
            return Response(
                {'error': 'You do not have permission to send notifications.'},
                status=status.HTTP_403_FORBIDDEN
            )

        title = request.data.get('title')
        message = request.data.get('body')  # Frontend sends 'body', not 'message'
        target_audience = request.data.get('target', 'all')  # Frontend sends 'target', not 'target_audience'
        priority_str = request.data.get('priority', 'normal')
        notification_type = request.data.get('type', 'info')

        if not title or not message:
            return Response(
                {'error': 'Title and message are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Map priority string to integer
        priority_map = {'low': 1, 'normal': 1, 'high': 2}
        priority = priority_map.get(priority_str, 1)

        # Create the notification in database
        notification = Notification.objects.create(
            title=title,
            message=message,
            type=notification_type,
            priority=priority,
            created_by=request.user,
            source_label=getattr(request.user, 'department', 'System'),
            source_color='orange',
            is_read=False
        )

        # Determine target users based on audience
        target_users = self.get_target_users(target_audience, request.user)
        
        # Create NotificationReadStatus for all target users (unread)
        read_status_objects = [
            NotificationReadStatus(user=user, notification=notification)
            for user in target_users
        ]
        if read_status_objects:
            NotificationReadStatus.objects.bulk_create(read_status_objects, ignore_conflicts=True)

        # TODO: Integrate Firebase Cloud Messaging here for push notifications

        return Response({
            'status': 'success',
            'notification_id': notification.id,
            'recipients_count': len(target_users),
            'message': f'Notification created for {len(target_users)} users.'
        }, status=status.HTTP_201_CREATED)

    def get_target_users(self, target_audience, sender):
        """Get users based on target audience selection."""
        if target_audience == 'all':
            return User.objects.filter(is_active=True)
        elif target_audience == 'students':
            return User.objects.filter(is_active=True, role='student')
        elif target_audience == 'faculty':
            return User.objects.filter(is_active=True, role__in=['faculty', 'teacher'])
        elif target_audience == 'department':
            sender_dept = getattr(sender, 'department', None)
            if sender_dept:
                return User.objects.filter(is_active=True, department=sender_dept)
            return User.objects.none()
        else:
            return User.objects.filter(is_active=True)


class NotificationHistoryView(APIView):
    """Get notification history for the current user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Return recent notifications sent by this user
        notifications = Notification.objects.filter(
            sender=request.user
        ).order_by('-created_at')[:50]
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
