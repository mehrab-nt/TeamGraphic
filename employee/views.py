from rest_framework import filters
from api.permissions import ApiAccess, IsOwner, IsNotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, EmployeeLevel
from api.models import ApiCategory
from .serializers import EmployeeSerializer, EmployeeLevelSerializer, EmployeeBriefSerializer, EmployeeSignInWithPasswordSerializer, EmployeeApiList
from api.serializers import ApiCategorySerializer
from .filters import EmployeeFilter, EmployeeLevelFilter
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from user.serializers import UserChangePasswordSerializer
from rest_framework.throttling import ScopedRateThrottle



@extend_schema(tags=['Employee'])
class EmployeeViewSet(CustomMixinModelViewSet):
    """
    MEH: Employee Model viewset
    (Employee dont back super user in any way)
    """
    queryset = Employee.objects.filter(user__is_superuser=False)
    serializer_class = EmployeeSerializer
    filterset_class = EmployeeFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['user__first_name', 'user__last_name']
    ordering_fields = ['rate']
    throttle_scope = ''
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        '__all__': ['employee_manager'],
        'create': ['create_employee']
    }

    def get_queryset(self):
        qs = super().get_queryset().select_related('user')
        if self.action == 'change_password':
            return qs
        return qs.select_related('user', 'user__user_profile', 'level').order_by('-user')

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeBriefSerializer
        return super().get_serializer_class()

    @extend_schema(summary="Current Employee info")
    @action(detail=False, methods=['get', 'put', 'patch'],
            url_path='current', permission_classes=[IsOwner])
    def current_employee(self, request):
        """
        MEH: current Employee info
        """
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(request.user.employee_profile, request)
        return self.custom_get(request.user.employee_profile)

    @extend_schema(summary="Current Employee info")
    @action(detail=False, methods=['get'],
            url_path='current/api-list', serializer_class=EmployeeApiList,
            permission_classes=[IsOwner])
    def current_employee_api_list(self, request):
        """
        MEH: current Employee info
        """
        return self.custom_get(request.user.employee_profile.level)

    @extend_schema(tags=['Employee'], summary="Sign In Employee with password")
    @action(detail=False, methods=['post'],
            url_path='sign-in-employee', serializer_class=EmployeeSignInWithPasswordSerializer, filter_backends=[None],
            permission_classes=[IsNotAuthenticated], throttle_scope = 'auth', throttle_classes=[ScopedRateThrottle])
    def sign_in_employee(self, request):
        """
        MEH: Employee Sign In with password (POST ACTION) and get `access_token` & `refresh_token`
        Only Employee that not authenticated have permission
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(summary="Change Password request")
    @action(detail=False, methods=['put'],
            url_path='change-password', serializer_class=UserChangePasswordSerializer, filter_backends=[None],
            permission_classes=[IsOwner])
    def change_password(self, request, pk=None):
        """
        MEH: Employee User can try change old password (most authenticate)
        """
        # employee = self.get_object()
        # self.check_object_permissions(request, employee) # MEH: Check obj permission manually
        return self.custom_update(request.user, request)


@extend_schema(tags=['Employee-Level'])
class EmployeeLevelViewSet(CustomMixinModelViewSet):
    """
    MEH: Employee Level Model viewset
    """
    queryset = (EmployeeLevel.objects.select_related('manager')
                .prefetch_related('api_items'))
    serializer_class = EmployeeLevelSerializer
    filterset_class = EmployeeLevelFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title']
    ordering_fields = ['title']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        '__all__': ['employee_level_access_manager'],
        'create': ['create_employee_level_access']
    }

    def create(self, request, *args, **kwargs):
        """
        MEH: Override this for automatically set manager who create Employee-Level
        """
        if getattr(request.user, 'employee_profile', False): # MEH: Make sure correct Employee manager received here!
            employee = request.user.employee_profile
            return self.custom_create(request, manager=employee)
        raise PermissionDenied(TG_PERMISSION_DENIED)

    @extend_schema(summary='Api Item list for each EmployeeLevel')
    @action(detail=False, methods=['get'], serializer_class=ApiCategorySerializer,
            url_path='api-list')
    def employee_level_api_item_list(self, request):
        """
        MEH: List of Api Item a EmployeeLevel can have for Employee (role_base=False)
        """
        api_category_list = ApiCategory.objects.prefetch_related('api_items').filter(role_base=False)
        return self.custom_get(api_category_list)
