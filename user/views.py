from rest_framework import status, filters
from datetime import datetime, date
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from api.permissions import ApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Role, Introduction, Address
from api.models import ApiCategory
from django.db.models import Subquery, OuterRef, Count, Prefetch
from .serializers import (UserSignUpSerializer, UserSignInSerializer, UserSerializer,
                          UserImportFieldDataSerializer, UserImportDataSerializer, UserDownloadDataSerializer,
                          UserProfileSerializer, UserActivationSerializer, UserManualVerifyPhoneSerializer,
                          UserKeySerializer, UserAccountingSerializer, AddressSerializer, IntroductionSerializer,
                          RoleSerializer)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .filters import CustomerFilter
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkDeleteSerializer, ApiCategorySerializer
from file_manager.apps import ExcelHandler


@extend_schema(tags=["Auth"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    MEH: Get Refresh Token
    """
    permission_classes = [AllowAny]
    pass


@extend_schema(tags=["Auth"])
class CustomTokenVerifyView(TokenVerifyView):
    """
    MEH: Verify Access Token
    """
    permission_classes = [AllowAny]
    pass


@extend_schema(tags=['Users'])
class UserViewSet(CustomMixinModelViewSet):
    """
    MEH: User Model viewset
    """
    queryset = User.objects.all() # MEH: Override in get_query_set()
    serializer_class = UserSerializer
    filterset_class = CustomerFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['first_name', 'last_name', 'phone_number'] # MEH: Get search query
    ordering_fields = ['date_joined', 'order_count', 'last_order_date']
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        **dict.fromkeys(['list', 'retrieve', 'get_by_phone', 'key'], 'get_users'),
        **dict.fromkeys(['update', 'partial_update', 'profile', 'accounting'], 'update_user'),
        **dict.fromkeys(['get_address_list', 'address_detail'], 'get_address'),
        'create': 'create_user',
        'destroy': 'delete_user',
        'activation': 'active_user',
        **dict.fromkeys(['import_user_list', 'import_user_list_valid_field'], 'import_user_list'),
        'download_user_list': 'download_user_list',
        'create_address': 'create_address',
        'manually_verify_phone': 'verify_phone',
    }

    def get_queryset(self, *args, **kwargs):
        """
        MEH: Override queryset
        to parse only required table per action
        """
        qs = super().get_queryset().filter(is_employee=False, is_superuser=False).order_by('-date_joined')
        if self.action in ['key', 'manually_verify_phone', 'activation', 'create_address']:
            return qs
        if self.action == 'accounting':
            return qs.select_related('role')
        if self.action == 'profile':
            return qs.select_related('user_profile')
        if self.action == 'get_address_list':
            return qs.prefetch_related('user_addresses')
        return (
            qs.select_related('role', 'user_profile', 'introduce_from', 'introducer')
            .annotate(default_province=Subquery(Address.objects.filter(user=OuterRef('pk'), is_default=True).values('province__name')[:1]))
            .annotate(invite_user_count=Count('invite_user_list'))
        )

    def get_object(self, *args, **kwargs):
        """
        MEH: Override get single User (with pk or phone_number at same time)
        """
        if self.kwargs.get('phone_number'):
            lookup_value = self.kwargs.get('phone_number')
            try:
                queryset = self.get_queryset()
                return queryset.get(phone_number=lookup_value)
            except ObjectDoesNotExist:
                raise NotFound(TG_USER_NOT_FOUND_BY_PHONE)
        return super().get_object(*args, **kwargs) # MEH: Super default behavior with pk

    @extend_schema(tags=['Auth'])
    @action(detail=False, methods=['post'],
            url_path='sign-up', serializer_class=UserSignUpSerializer,
            permission_classes=[IsNotAuthenticated])
    def sign_up(self, request):
        """
        MEH: User Sign Up action (POST ACTION) for customer that not authenticated
        """
        return self.custom_create(request.data)

    @extend_schema(tags=['Auth'])
    @action(detail=False, methods=['post'],
            url_path='sign-in', serializer_class=UserSignInSerializer,
            permission_classes=[IsNotAuthenticated])
    def sign_in(self, request):
        """
        User Sign In action (POST ACTION) and get Access & Refresh Token for customer that not authenticated
        handle serializer manually
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            url_path='by-phone/(?P<phone_number>\\d{11})')
    def get_by_phone(self, request, phone_number=None):
        """
        MEH: Get User by phone_number (GET ACTION)
        """
        user = self.get_object(phone_number=phone_number)
        return self.custom_get(user)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='profile', serializer_class=UserProfileSerializer)
    def profile(self, request, pk=None):
        """
        MEH: Get User Profile information and Update it (with pk) (GET/PUT ACTION)
        """
        user = self.get_object(pk=pk)
        use_profile = user.user_profile
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(use_profile, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(use_profile)

    @action(detail=True, methods=['get'],
            url_path='key', serializer_class=UserKeySerializer)
    def key(self, request, pk=None):
        """
        MEH: Get User Key information (GET ACTION)
        Update block (auto generated and never change)
        """
        user_key = self.get_object(pk=pk)
        return self.custom_get(user_key)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='accounting', serializer_class=UserAccountingSerializer)
    def accounting(self, request, pk=None):
        """
        MEH: Get User Accounting information and Update it (GET/PUT ACTION)
        """
        user_accounting = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(user_accounting, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(user_accounting)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='activation', serializer_class=UserActivationSerializer, filter_backends=[None])
    def activation(self, request, pk=None):
        """
        MEH: Update User Activation (is_active) (GET/PUT ACTION)
        """
        user_activation = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(user_activation, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(user_activation)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get'],
            url_path='address-list', serializer_class=AddressSerializer, filter_backends=[None])
    def get_address_list(self, request, pk=None):
        """
        MEH: Get User (with pk) Address list (GET ACTION)
        Inline Queryset
        """
        address_list = Address.objects.select_related('user', 'province', 'city').filter(user__pk=pk).order_by('-is_default', 'title')
        if not address_list:
            raise NotFound(TG_DATA_EMPTY)
        return self.custom_get(address_list)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get', 'put', 'patch', 'delete'],
            url_path='address/(?P<address_id>\d+)', serializer_class=AddressSerializer, filter_backends=[None])
    def address_detail(self, request, pk=None, address_id=None):
        """
        MEH: Get User Address Detail (with pk), Update and Delete it (PUT/DELETE ACTION)
        """
        address_list = Address.objects.select_related('user', 'province', 'city').filter(user__pk=pk)
        try:
            address = address_list.get(pk=address_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        except ValueError:
            raise NotFound(TG_EXPECTED_ID_NUMBER)
        if request.method == 'DELETE':
            return self.custom_destroy(address)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(address, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(address)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['post'],
            url_path='address-add', serializer_class=AddressSerializer, filter_backends=[None])
    def create_address(self, request, pk=None):
        """
        MEH: Add New Address for User (with pk) (POST ACTION)
        """
        user = self.get_object(pk=pk)
        return self.custom_create(request.data, user=user)

    @extend_schema(
        request={ # MEH: Set this for API document (DRF & SCHEMA)
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'excel_file': {'type': 'string', 'format': 'binary'},
                    'role': {'type': 'integer'}
                },
                'required': ['excel_file', 'role'],
            }
        },
    )
    @action(detail=False, methods=['post'],
            url_path='import', serializer_class=UserImportFieldDataSerializer, filter_backends=[], pagination_class=None)
    def import_user_list(self, request):
        """
        MEH: Create User list from Excel File (up to 1000) (POST ACTION)
        give any Excel file with any col and row (Handle valid col header and row data)
        """
        check_serializer = self.get_serializer(data=request.data)
        check_serializer.is_valid(raise_exception=True)
        excel_file = check_serializer.validated_data['excel_file']
        required_fields = ['phone_number', 'first_name'] # MEH: Required field check in Excel col
        profile_fields = [ # MEH: Nested User Profile data Handle
            name for name, field in UserProfileSerializer().get_fields().items()
            if not getattr(field, 'read_only', False)
        ]
        allowed_fields = set(UserSerializer().get_fields().keys()) # MEH: Allowed field that serializer accept
        extra_fields = {'role':check_serializer.validated_data['role'].pk} # MEH: Selected Role in form for all User in Excel
        user_data_list = ExcelHandler.import_excel(
            excel_file, allowed_fields, required_fields,
            nested_fields=profile_fields,
            nested_field_category='user_profile',
            extra_fields=extra_fields,
        )
        self.serializer_class = UserImportDataSerializer # MEH: Change Serializer class to Validate Posted Data with Excel
        res = self.custom_create(user_data_list, many=True) # MEH: Check, Validate (Raise Exception if any) & Save Data in DB 1 by 1
        self.serializer_class = UserImportFieldDataSerializer # MEH: Change back for View purpose in DRF UI
        return res

    @action(detail=False, methods=['get'],
            url_path='import-fields', serializer_class=UserImportDataSerializer, filter_backends=[None], pagination_class=None)
    def import_user_list_valid_field(self, request):
        """
        MEH: Set this for showing valid cel field for Excel...
        """
        all_fields = self.get_serializer_fields()
        return Response({'detail': list(all_fields.keys())}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: OpenApiTypes.BINARY}, # or a more specific file/media type
        parameters=[
            OpenApiParameter(
                name='check_field',
                description='Used for highlight User row in Excel file, if check_filed is None or 0',
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
                enum=list(UserDownloadDataSerializer().get_fields().keys())
            )
        ]
    )
    @action(detail=False, methods=['get'],
            url_path='download', serializer_class=None)
    def download_user_list(self, request):
        """
        MEH: Get User List with Filter and write data in Excel (up to 1000) (GET ACTION)
        (Direct Download)
        """
        check_field = request.query_params.get('check_field')
        queryset = self.filter_queryset(self.get_queryset()) # MEH: For apply filters/search/order like list()
        headers = list(UserDownloadDataSerializer().get_fields().keys()) # MEH: Get Header from Serializer
        rows = []
        for user in queryset:
            serializer = UserDownloadDataSerializer(user)
            row = []
            for field in headers:
                value = serializer.data.get(field)
                if isinstance(value, int) or isinstance(datetime, date):
                    row.append(value)
                elif not value:
                    value = '-'
                    row.append(value)
                else:
                    row.append(str(value))
            rows.append(row)
        return ExcelHandler.generate_excel(headers, rows, file_name='users.xlsx', check_field=str(check_field))

    @action(detail=True, methods=['get', 'put', 'partial'],
            url_path='manually-verify-phone', serializer_class=UserManualVerifyPhoneSerializer, filter_backends=[None])
    def manually_verify_phone(self, request, pk=None):
        """
        MEH: Update User verified_phone (PUT ACTION)
        """
        user_verified_phone = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(user_verified_phone, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(user_verified_phone)


@extend_schema(tags=["Users-Introduction"])
class IntroductionViewSet(CustomMixinModelViewSet):
    """
    MEH: Introduction Model viewset
    """
    queryset = Introduction.objects.all().order_by('sort_number')
    serializer_class = IntroductionSerializer
    permission_classes = [ApiAccess] # MEH: Handle Access for Employee (List, Obj, and per default and custom @action)
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title'] # MEH: Get search query
    ordering_fields = ['title', 'number']
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        '__all__': "full_introductions"
    }


@extend_schema(tags=["Roles"])
class RoleViewSet(CustomMixinModelViewSet):
    """
    MEH: Role Model viewset
    """
    queryset = (Role.objects.prefetch_related('api_items')
                .order_by('-is_default', 'sort_number'))
    serializer_class = RoleSerializer
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        **dict.fromkeys(['list', 'retrieve', 'update', 'partial_update', 'destroy', 'bulk_delete', 'role_api_item_list'], 'get_user_role_access'),
        'create': 'create_user_role_access',
    }

    @action(detail=False, methods=['get'], serializer_class=ApiCategorySerializer,
            url_path='api-list')
    def role_api_item_list(self, request):
        """
        MEH: List of Api Item a Role can have (role_base=True)
        """
        api_category_list = ApiCategory.objects.prefetch_related('api_items').filter(role_base=True)
        if not api_category_list:
            raise NotFound(TG_DATA_EMPTY)
        return self.custom_get(api_category_list)

    @extend_schema(
        request=BulkDeleteSerializer,
        responses={
           200: OpenApiResponse(description="Successfully deleted List."),
           400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=BulkDeleteSerializer,
            url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        MEH: Delete List of Role Objects (use POST ACTION for sending list of id in request body)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        self.serializer_class = RoleSerializer
        return self.custom_list_destroy(ids)
