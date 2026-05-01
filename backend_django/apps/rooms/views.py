from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Room
from .serializers import RoomSerializer
from apps.users.permissions import CanManageRoom
from apps.facilities.models import Facility


class RoomListView(generics.ListCreateAPIView):
    queryset = Room.objects.filter(is_deleted=False)
    serializer_class = RoomSerializer
    permission_classes = [CanManageRoom]

    def perform_create(self, serializer):
        """
        On POST, validate that non-super-admin users can only create rooms
        in facilities belonging to their department.
        """
        user = self.request.user
        if user.role != 'super_admin':
            facility_id = self.request.data.get('facility')
            if facility_id:
                try:
                    facility = Facility.objects.get(pk=facility_id)
                    if facility.department and facility.department.code != user.department:
                        from rest_framework.exceptions import PermissionDenied
                        raise PermissionDenied(
                            'You can only add rooms to facilities in your department.'
                        )
                except Facility.DoesNotExist:
                    pass  # Let serializer validation handle invalid FK
        serializer.save()


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.filter(is_deleted=False)
    serializer_class = RoomSerializer
    permission_classes = [CanManageRoom]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()



# Default highlight colors per course code — used when course_color is not set on individual rooms.
COURSE_DEFAULT_COLORS = {
    'BSIT':         '#FF5722',
    'BSCS':         '#2196F3',
    'BSECE':        '#9C27B0',
    'BSEd':         '#4CAF50',
    'Criminology':  '#FF9800',
    'BSHM':         '#E91E63',
    'BSA':          '#00BCD4',
    'BSBA':         '#795548',
    'STEM':         '#607D8B',
    'ABM':          '#FFC107',
    'HUMSS':        '#3F51B5',
    'GAS':          '#009688',
}

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Count


@api_view(['GET'])
@permission_classes([AllowAny])
def course_list_view(request):
    """
    Returns all distinct course codes that have rooms assigned,
    with their highlight color and room count.
    Used by the Course Filter feature on the campus map.
    """
    rows = (
        Room.objects
        .filter(is_deleted=False, is_active=True)
        .exclude(course_code__isnull=True)
        .exclude(course_code='')
        .values('course_code', 'course_color')
        .annotate(room_count=Count('id'))
        .order_by('course_code')
    )

    # Deduplicate by course_code (different rooms may have different colors set)
    seen = {}
    for row in rows:
        code = row['course_code']
        if code not in seen:
            color = row['course_color'] or COURSE_DEFAULT_COLORS.get(code, '#9E9E9E')
            seen[code] = {'course_code': code, 'course_color': color, 'room_count': 0}
        seen[code]['room_count'] += row['room_count']

    return Response(list(seen.values()))
