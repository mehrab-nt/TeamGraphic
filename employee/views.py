from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from api.permissions import ApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee
from .serializers import EmployeeSerializer
from .filters import EmployeeFilter
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkDeleteSerializer


# MEH: User List view set
@extend_schema(tags=['Employee'])
class EmployeeViewSet(CustomMixinModelViewSet):
    queryset = Employee.objects.prefetch_related('user')
    serializer_class = EmployeeSerializer
    # MEH: Handle Access for Employee (List, Obj, and per default and custom @action)
    permission_classes = [ApiAccess]
    filterset_class = EmployeeFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    # MEH: Get search query
    search_fields = ['user__first_name', 'user__last_name']
    ordering_fields = ['rate']

    # MEH: Override get single user (with ID or phone_number) | Access check after In has_object_permission
    # def get_object(self, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     if not self.kwargs.get('phone_number'):
    #         lookup_value = self.kwargs.get(self.lookup_field, '')
    #         try:
    #             obj = queryset.get(pk=int(lookup_value))
    #             return obj
    #         except ObjectDoesNotExist:
    #             raise NotFound(TG_USER_NOT_FOUND_BY_ID)
    #         except ValueError:
    #             raise NotFound(TG_EXPECTED_ID_NUMBER)
    #     lookup_value = self.kwargs.get('phone_number')
    #     try:
    #         return queryset.get(phone_number=lookup_value)
    #     except ObjectDoesNotExist:
    #         raise NotFound(TG_USER_NOT_FOUND_BY_PHONE)
    #
    # # MEH: Override post single User or Bulk list
