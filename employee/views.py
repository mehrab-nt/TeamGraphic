from rest_framework import viewsets, status, filters
from api.permissions import ApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, EmployeeLevel
from api.models import ApiCategory
from .serializers import EmployeeSerializer, EmployeeLevelSerializer
from api.serializers import ApiCategorySerializer
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
    queryset = Employee.objects.all()
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
        '__all__': 'get_employee',
        'create': 'create_employee',
    }

    def get_queryset(self):
        """
        MEH: Override Super QS for filter SuperUser from User List
        Api don't back super-user information in any way!
        """
        return super().get_queryset().select_related('user', 'user__user_profile', 'level').filter(user__is_superuser=False)


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
        '__all__': 'get_employee_level_access',
        'create': 'create_employee_level_access',
    }

    def get_queryset(self):
        """
        MEH: Override Super QS for reduce query
        """
        return super().get_queryset().select_related('manager').prefetch_related('api_items')

    def create(self, request, *args, **kwargs):
        """
        MEH: Override this for automatically set manager who create Employee-Level
        """
        if getattr(request.user, 'employee_profile', False): # MEH: Make sure correct Employee manager received here!
            employee = request.user.employee_profile
            return self.custom_create(request.data, manager=employee)
        raise PermissionDenied(TG_PERMISSION_DENIED)

    @action(detail=False, methods=['get'], serializer_class=ApiCategorySerializer,
            url_path='api-list')
    def employee_level_api_item_list(self, request):
        """
        MEH: List of Api Item a Employee can have (role_base=False)
        """
        api_category_list = ApiCategory.objects.prefetch_related('api_items').filter(role_base=False)
        if not api_category_list:
            raise NotFound(TG_DATA_EMPTY)
        return self.custom_get(api_category_list)