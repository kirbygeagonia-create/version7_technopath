from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Facility
from .serializers import FacilitySerializer
from apps.users.permissions import ReadOnlyOrSuperAdmin


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class FacilityListView(generics.ListCreateAPIView):
    queryset = Facility.objects.filter(is_deleted=False)
    serializer_class = FacilitySerializer
    permission_classes = [ReadOnlyOrSuperAdmin]
    pagination_class = StandardResultsSetPagination


class FacilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Facility.objects.filter(is_deleted=False)
    serializer_class = FacilitySerializer
    permission_classes = [ReadOnlyOrSuperAdmin]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

