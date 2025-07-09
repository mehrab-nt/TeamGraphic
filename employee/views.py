from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from api.permissions import ApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, EmployeeLevel
from .serializers import EmployeeSerializer, EmployeeLevelSerializer, EmployeeLevelSetSerializer
from .filters import EmployeeFilter, EmployeeLevelFilter
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.responses import *
from api.mixins import CustomMixinModelViewSet


@extend_schema(tags=['Employee'])
class EmployeeViewSet(CustomMixinModelViewSet):
    """
    MEH: Employee Model viewset
    """
    queryset = Employee.objects.prefetch_related('user', 'level')
    serializer_class = EmployeeSerializer
    filterset_class = EmployeeFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['user__first_name', 'user__last_name']
    ordering_fields = ['rate']
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        **dict.fromkeys(['list', 'retrieve', 'update', 'partial_update', 'destroy'], 'get_employee'),
        'create': 'create_employee',
        'set_level_for_employee': 'get_employee_level_access'
    }

    def get_queryset(self): # MEH: Api don't back super_user data in any way!
        """
        MEH: Override Super QS for filter SuperUser from User List
        Api don't back super-user information in any way!
        """
        return super().get_queryset().filter(user__is_superuser=False)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='set_level', serializer_class=EmployeeLevelSetSerializer, filter_backends=[None])
    def set_level_for_employee(self, request, pk=None):
        """
        MEH: Update User Employee Level (Get/PUT ACTION)
        """
        queryset = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(queryset, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(queryset)


@extend_schema(tags=['Employee-Level'])
class EmployeeLevelViewSet(CustomMixinModelViewSet):
    """
    MEH: Employee Level Model viewset
    """
    queryset = EmployeeLevel.objects.all()
    serializer_class = EmployeeLevelSerializer
    filterset_class = EmployeeLevelFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title']
    ordering_fields = ['title']
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        **dict.fromkeys(['list', 'retrieve', 'update', 'partial_update', 'destroy'], 'get_employee_level_access'),
        'create': 'create_employee_level_access',
    }

    def create(self, request, *args, **kwargs):
        """
        MEH: Override this for automatically set manager who create Employee-Level
        """
        if getattr(request.user, 'employee_profile', False): # MEH: Make sure correct Employee received here!
            employee = request.user.employee_profile
            return self.custom_create(request.data, manager=employee)
        raise PermissionDenied(TG_PERMISSION_DENIED)
