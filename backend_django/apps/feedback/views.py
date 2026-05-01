from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Feedback
from .serializers import FeedbackSerializer
from apps.users.permissions import IsAnyAdmin, IsSuperAdmin


class FeedbackListView(APIView):
    """
    GET  — admin-only, role-scoped:
             super_admin → all feedback
             dean / program_head / basic_ed_head → only feedback where
             the linked facility belongs to their department
    POST — public: anyone can submit feedback (no auth required)
    """

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAnyAdmin()]
        return [AllowAny()]

    def get(self, request):
        user = request.user
        if user.role == 'super_admin':
            qs = Feedback.objects.select_related('facility', 'room').order_by('-created_at')
        else:
            # Scope to feedback linked to rooms/facilities in the admin's department
            dept = getattr(user, 'department', None)
            if dept:
                qs = Feedback.objects.select_related('facility', 'room').filter(
                    facility__department__code__iexact=dept
                ).order_by('-created_at')
            else:
                qs = Feedback.objects.none()

        serializer = FeedbackSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=http_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)


class FeedbackDetailView(APIView):
    """
    GET    — any admin (super_admin sees all; others only their dept)
    PATCH  — super_admin only (flag, update status)
    DELETE — super_admin only
    """
    permission_classes = [IsAnyAdmin]

    def _get_object_or_404(self, pk):
        try:
            return Feedback.objects.select_related('facility__department').get(pk=pk)
        except Feedback.DoesNotExist:
            return None

    def _can_access(self, request, obj):
        """Super admin can access any; others only if facility is in their dept."""
        if request.user.role == 'super_admin':
            return True
        if obj.facility and obj.facility.department:
            return (obj.facility.department.code or '').lower() == (request.user.department or '').lower()
        return False

    def get(self, request, pk):
        obj = self._get_object_or_404(pk)
        if not obj:
            return Response({'error': 'Not found.'}, status=404)
        if not self._can_access(request, obj):
            return Response({'error': 'Access denied.'}, status=403)
        return Response(FeedbackSerializer(obj).data)

    def patch(self, request, pk):
        if request.user.role != 'super_admin':
            return Response({'error': 'Only Super Admin can update feedback.'}, status=403)
        obj = self._get_object_or_404(pk)
        if not obj:
            return Response({'error': 'Not found.'}, status=404)
        serializer = FeedbackSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if request.user.role != 'super_admin':
            return Response({'error': 'Only Super Admin can delete feedback.'}, status=403)
        obj = self._get_object_or_404(pk)
        if not obj:
            return Response({'error': 'Not found.'}, status=404)
        obj.delete()
        return Response(status=http_status.HTTP_204_NO_CONTENT)
