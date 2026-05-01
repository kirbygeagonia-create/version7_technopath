from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from .models import Announcement
from apps.users.permissions import CanApproveAnnouncements, CanPostAnnouncement
from apps.users.views import write_audit


class AnnouncementPublicListView(APIView):
    """Public endpoint — mobile app syncs from here. Returns published only.
    Filters by user's ID/username for specific_users scope announcements."""
    permission_classes = []

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        user_id = str(getattr(user, 'id', ''))
        username = getattr(user, 'username', '') or getattr(user, 'email', '')
        
        # Get all published announcements
        qs = Announcement.objects.filter(
            status='published', is_deleted=False
        ).order_by('-created_at')[:200]
        
        # Filter to only show visible announcements
        visible = []
        for a in qs:
            if a.scope == 'campus_wide':
                visible.append(a)
            elif a.scope == 'all_college' and getattr(user, 'role', None) == 'college_student':
                visible.append(a)
            elif a.scope == 'basic_ed_only' and getattr(user, 'role', None) == 'basic_ed_student':
                visible.append(a)
            elif a.scope == 'department' and getattr(user, 'department', None) == a.target_department:
                visible.append(a)
            elif a.scope == 'specific_users':
                targets = [str(t).lower() for t in (a.target_users or [])]
                if user_id.lower() in targets or username.lower() in targets:
                    visible.append(a)
        
        return Response([{
            'id':           a.id,
            'title':        a.title,
            'content':      a.content,
            'source_label': a.source_label,
            'source_color': a.source_color,
            'scope':        a.scope,
            'approved_at':  a.approved_at,
            'created_at':   a.created_at,
        } for a in visible])


class AnnouncementCreateView(APIView):
    """Admin creates an announcement. Publishes directly or submits for approval."""
    permission_classes = [CanPostAnnouncement]

    def post(self, request):
        d = request.data
        if not d.get('title') or not d.get('content'):
            return Response({'error': 'Title and content are required.'},
                            status=http_status.HTTP_400_BAD_REQUEST)

        user  = request.user
        scope = d.get('scope', 'campus_wide')

        # Determine if user can publish directly without approval
        publishes_direct = False
        if user.role == 'super_admin':
            publishes_direct = True
        elif user.role == 'dean':
            # Dean can only publish directly for department-scoped announcements
            # Campus-wide announcements from Dean require Super Admin approval
            if scope == 'department':
                publishes_direct = True
            # else: campus-wide goes to pending_approval for Super Admin
        # Program Head and Basic Ed Head always need approval

        a = Announcement(
            title             = d['title'].strip(),
            content           = d['content'].strip(),
            created_by        = user,
            source_label      = user.get_department_label(),
            source_color      = user.get_department_color(),
            scope             = scope,
            target_department = d.get('target_department', ''),
            target_users      = d.get('target_users', []) if scope == 'specific_users' else [],
            status            = 'pending_approval',
            requires_approval = not publishes_direct,
        )
        a.save()

        if publishes_direct:
            a.publish(approved_by_user=user)
            write_audit(user, 'publish', 'announcement', a.id, a.title, request=request)
            return Response({
                'id':      a.id,
                'status':  'published',
                'message': 'Announcement published and queued for all users.',
            }, status=http_status.HTTP_201_CREATED)
        else:
            write_audit(user, 'create', 'announcement', a.id, a.title, request=request)
            return Response({
                'id':      a.id,
                'status':  'pending_approval',
                'message': 'Announcement submitted for Super Admin approval.',
            }, status=http_status.HTTP_201_CREATED)


class AnnouncementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, pk):
        try:
            return Announcement.objects.get(pk=pk, is_deleted=False)
        except Announcement.DoesNotExist:
            return None

    def put(self, request, pk):
        a = self._get(pk)
        if not a:
            return Response({'error': 'Not found.'}, status=404)
        user       = request.user
        is_creator = a.created_by_id == user.id
        is_super   = user.role == 'super_admin'
        if not (is_creator or is_super):
            return Response({'error': 'Permission denied.'}, status=403)
        if a.status == 'published' and not is_super:
            return Response({'error': 'Published announcements can only be edited by the Super Admin.'},
                            status=403)
        old = {'title': a.title, 'content': a.content}
        a.title   = request.data.get('title', a.title).strip()
        a.content = request.data.get('content', a.content).strip()
        a.save()
        write_audit(user, 'update', 'announcement', a.id, a.title,
                    old_val=old, new_val={'title': a.title, 'content': a.content},
                    request=request)
        return Response({'message': 'Updated.'})

    def delete(self, request, pk):
        a = self._get(pk)
        if not a:
            return Response({'error': 'Not found.'}, status=404)
        user = request.user
        if not (a.created_by_id == user.id or user.role == 'super_admin'):
            return Response({'error': 'Permission denied.'}, status=403)
        a.is_deleted = True
        a.save()
        write_audit(user, 'soft_delete', 'announcement', a.id, a.title, request=request)
        return Response({'message': 'Deleted.'})


class AnnouncementApproveView(APIView):
    """Only Super Admin can approve announcements. Dean has no approval authority."""
    permission_classes = [CanApproveAnnouncements]

    def post(self, request, pk):
        try:
            a = Announcement.objects.select_related('created_by').get(pk=pk, is_deleted=False)
        except Announcement.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

        if a.status != 'pending_approval':
            return Response({'error': f'Cannot approve — status is already "{a.status}".'}, status=400)
        a.publish(approved_by_user=request.user)
        write_audit(request.user, 'approve', 'announcement', a.id, a.title, request=request)
        return Response({'message': 'Approved and published to all users.'})


class AnnouncementRejectView(APIView):
    """Only Super Admin can reject announcements. Dean has no approval authority."""
    permission_classes = [CanApproveAnnouncements]

    def post(self, request, pk):
        try:
            a = Announcement.objects.select_related('created_by').get(pk=pk, is_deleted=False)
        except Announcement.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

        if a.status != 'pending_approval':
            return Response({'error': f'Cannot reject — status is already "{a.status}".'}, status=400)
        a.reject(rejected_by_user=request.user, note=request.data.get('note', ''))
        write_audit(request.user, 'reject', 'announcement', a.id, a.title, request=request)
        return Response({'message': 'Announcement rejected.', 'note': request.data.get('note', '')})


class PendingApprovalsView(APIView):
    """Only Super Admin can view pending announcements for approval. Dean has no approval authority."""
    permission_classes = [CanApproveAnnouncements]

    def get(self, request):
        qs = Announcement.objects.filter(
            status='pending_approval', is_deleted=False
        ).select_related('created_by').order_by('-created_at')

        return Response([{
            'id':           a.id,
            'title':        a.title,
            'content':      a.content,
            'source_label': a.source_label,
            'source_color': a.source_color,
            'scope':        a.scope,
            'created_by':   a.created_by.display_name if a.created_by else 'Unknown',
            'department':   a.created_by.get_department_label() if a.created_by else '',
            'created_at':   a.created_at,
        } for a in qs])


class MyAnnouncementsView(APIView):
    """Each admin sees their own submissions and their status."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Announcement.objects.filter(
            created_by=request.user, is_deleted=False
        ).order_by('-created_at')
        return Response([{
            'id':             a.id,
            'title':          a.title,
            'content':        a.content,
            'status':         a.status,
            'scope':          a.scope,
            'rejection_note': a.rejection_note,
            'created_at':     a.created_at,
        } for a in qs])


class AnnouncementArchiveView(APIView):
    """Super Admin archives a published announcement (removes from public feed)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != 'super_admin':
            return Response({'error': 'Only the Super Admin can archive announcements.'}, status=403)
        try:
            a = Announcement.objects.get(pk=pk, is_deleted=False)
        except Announcement.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        if a.status != 'published':
            return Response({'error': f'Only published announcements can be archived (current: {a.status}).'}, status=400)
        a.archive(archived_by_user=request.user)
        write_audit(request.user, 'archive', 'announcement', a.id, a.title, request=request)
        return Response({'message': 'Announcement archived.'})
