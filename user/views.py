from rest_framework import status, filters
from datetime import datetime, date
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from api.permissions import ApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Role, Introduction, Address
from django.db.models import Subquery, OuterRef
from .serializers import (UserSignUpSerializer, UserSignInSerializer, UserSerializer,
                          UserImportGetDataSerializer, UserImportSetDataSerializer, UserDownloadDataSerializer,
                          UserProfileSerializer,UserRoleSerializer,
                          UserKeySerializer, UserAccountingSerializer, AddressSerializer, IntroductionSerializer, RoleSerializer)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .filters import CustomerQueryFilter, CustomerFilter
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkDeleteSerializer
from file_manager.apps import ExcelHandler


@extend_schema(tags=["Auth"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    MEH: Get Refresh Token
    /api/token/refresh/
    """
    pass


@extend_schema(tags=["Auth"])
class CustomTokenVerifyView(TokenVerifyView):
    """
    MEH: Verify Access Token
    /api/token/verify/
    """
    pass


@extend_schema(tags=['Users'])
class UserViewSet(CustomMixinModelViewSet):
    """
    MEH: User Model view set
    /api/user/
    """
    queryset = User.objects.prefetch_related('user_profile')
    serializer_class = UserSerializer
    permission_classes = [ApiAccess] # MEH: Handle Access for Employee (List, Obj, and per default and custom @action)
    filterset_class = CustomerFilter
    filter_backends = [
        DjangoFilterBackend,
        CustomerQueryFilter,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['first_name', 'last_name', 'phone_number'] # MEH: Get search query
    ordering_fields = ['date_joined', 'order_count', 'last_order_date']
    required_api_keys = { # MEH: API static key foa each action, save exactly in DB -> Api Item with Category
        'list': 'get_users',
        'retrieve': 'get_users',
        'get_by_phone': 'get_users',
        'create': 'create_user',
        'update': 'update_user',
        'partial_update': 'update_user',
        'profile': 'update_user',
        'destroy': 'delete_user',
        'activation': 'active_user',
        'download_user_list': 'download_user_list',
        'import_user_list': 'import_user_list',
        'get_address_list': 'get_address_list',
        'address_detail': 'get_address_list',
        'create_address': 'create_address',
    }

    def get_queryset(self):
        """
        MEH: Set subquery for getting province from default Address if there is any & Use it on filter User Province
        """
        default_province_id = Subquery(
            Address.objects.filter(user=OuterRef('pk'), is_default=True).values('province')[:1]
        )
        return User.objects.annotate(default_province_id=default_province_id)

    def get_object(self, *args, **kwargs):
        """
        MEH: Override get single user (with pk or phone_number) (DEFAULT GET OBJECT ACTION)
        also use auto for PUT & DELETE
        Object Access check again after In has_object_permission
        """
        queryset = self.get_queryset()
        if not self.kwargs.get('phone_number'):
            lookup_value = self.kwargs.get(self.lookup_field, '')
            try:
                obj = queryset.get(pk=int(lookup_value))
                return obj
            except ObjectDoesNotExist:
                raise NotFound(TG_USER_NOT_FOUND_BY_ID)
            except ValueError:
                raise NotFound(TG_EXPECTED_ID_NUMBER)
        lookup_value = self.kwargs.get('phone_number')
        try:
            return queryset.get(phone_number=lookup_value)
        except ObjectDoesNotExist:
            raise NotFound(TG_USER_NOT_FOUND_BY_PHONE)

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
        queryset = self.get_object(phone_number=phone_number)
        return self.custom_get(queryset)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='profile', serializer_class=UserProfileSerializer)
    def profile(self, request, pk=None):
        """
        MEH: Get User Profile information and Update it (with pk) (GET/PUT ACTION)
        """
        user = self.get_object(pk=pk)
        queryset = user.user_profile
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(queryset, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(queryset)

    @action(detail=True, methods=['get'],
            url_path='key', serializer_class=UserKeySerializer)
    def key(self, request, pk=None):
        """
        MEH: Get User Key information (GET ACTION)
        Update block (auto generated and never change)
        """
        queryset = self.get_object(pk=pk)
        return self.custom_get(queryset)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='accounting', serializer_class=UserAccountingSerializer)
    def accounting(self, request, pk=None):
        """
        MEH: Get User Accounting information and Update it (GET/PUT ACTION)
        """
        queryset = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(queryset, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(queryset)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='activation', serializer_class=UserRoleSerializer, filter_backends=[None])
    def activation(self, request, pk=None):
        """
        MEH: Update User Activation (is_active) (GET/PUT ACTION)
        """
        queryset = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(queryset, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(queryset)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get'],
            url_path='address-list', serializer_class=AddressSerializer, filter_backends=[None])
    def get_address_list(self, request, pk=None):
        """
        MEH: Get User (with pk) Address list (GET ACTION)
        """
        user = self.get_object(pk=pk)
        queryset = user.user_addresses.all()
        if not queryset.exists():
            raise NotFound(TG_DATA_EMPTY)
        return self.custom_get(queryset)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['post'],
            url_path='address-add', serializer_class=AddressSerializer, filter_backends=[None])
    def create_address(self, request, pk=None):
        """
        MEH: Add New Address for User (with pk) (POST ACTION)
        """
        user = self.get_object(pk=pk)
        return self.custom_create(request.data, user=user)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get', 'put', 'patch', 'delete'],
            url_path='address/(?P<address_id>\d+)', serializer_class=AddressSerializer, filter_backends=[None])
    def address_detail(self, request, pk=None, address_id=None):
        """
        MEH: Get User Address Detail (with pk), Update and Delete it (PUT/DELETE ACTION)
        """
        user = self.get_object(pk=pk)
        try:
            instance = user.user_addresses.get(pk=address_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        except ValueError:
            raise NotFound(TG_EXPECTED_ID_NUMBER)
        if request.method == 'DELETE':
            return self.custom_destroy(instance)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(instance, request.data, partial=(request.method == 'PATCH'))
        return self.custom_get(instance)

    @extend_schema(
        request={ # MEH: Set this for API document
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
    @action(detail=False, methods=['get', 'post'],
            url_path='import_users', serializer_class=UserImportGetDataSerializer, filter_backends=[], pagination_class=None)
    def import_users(self, request):
        """
        MEH: Create User list from Excel File (up to 1000) (POST ACTION)
        give any Excel file with any col and row (Handle valid col header and row data)
        """
        if request.method == 'GET': # MEH: Set this for showing valid cel field for Excel...
            return Response({'detail': list(UserImportSetDataSerializer().get_fields().keys())}, status=status.HTTP_200_OK)
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
        self.serializer_class = UserImportSetDataSerializer # MEH: Change Serializer class to Validate Posted Data with Excel
        res = self.custom_create(user_data_list, many=True) # MEH: Check, Validate (Raise Exception if any) & Save Data in DB 1 by 1
        self.serializer_class = UserImportGetDataSerializer # MEH: Change back for View purpose in DRF UI
        return res

    @extend_schema(responses={200: UserDownloadDataSerializer(many=True)})
    @action(detail=False, methods=['get'],
            url_path='download')
    def download_user_list(self, request):
        """
        MEH: Get User List with Filter and write data in Excel (up to 1000) (GET ACTION)
        (Direct Download)
        todo: Re Design Excel file later
        """
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
        return ExcelHandler.generate_excel(headers, rows, file_name='users.xlsx', check_field='national_id')


# MEH: Get Introduction List and Add single object (POST) update (PUT) and protected remove (DELETE)
@extend_schema(tags=["Users-Introduction"])
class IntroductionViewSet(CustomMixinModelViewSet):
    queryset = Introduction.objects.all()
    serializer_class = IntroductionSerializer
    permission_classes = [IsAuthenticated]


# MEH: Get Role List and Add single object (POST) update (PUT) and protected remove (DELETE)
@extend_schema(tags=["Roles"])
class RoleViewSet(CustomMixinModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    #  MEH: Delete List of object todo: work more after
    @extend_schema(
        request=BulkDeleteSerializer,
        responses={
           204: OpenApiResponse(description="Successfully deleted roles."),
           400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
        description='Send JSON data in the body like this: {"ids": [1, 2, 3]}'
    )
    @action(detail=False, methods=['delete'], serializer_class=BulkDeleteSerializer,
            url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        MEH: Delete List of Role Objects
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        self.serializer_class = RoleSerializer
        return self.custom_list_destroy(ids)
