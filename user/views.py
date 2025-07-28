from rest_framework import status, filters
from datetime import datetime, date
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.permissions import ApiAccess, IsNotAuthenticated, IsOwner
from rest_framework.decorators import action
from rest_framework.throttling import ScopedRateThrottle
from api.throttles import PhoneNumberRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from financial.models import DepositConfirmStatus
from financial.serializers import CreditSerializer, DepositBriefInfoForUserManualListSerializer
from .models import User, Role, Introduction, Address
from api.models import ApiCategory
from django.db.models import Subquery, OuterRef
from .serializers import UserSignUpRequestSerializer, UserSignUpVerifySerializer, UserSignUpManualSerializer, \
    UserSerializer, UserBriefSerializer, UserChangePasswordSerializer, UserResendCodeSerializer, \
    UserSignInRequestSerializer, UserSignInWithCodeSerializer, UserSignInWithPasswordSerializer, \
    UserImportFieldDataSerializer, UserImportDataSerializer, UserDownloadDataSerializer, \
    UserProfileSerializer, UserActivationSerializer, UserManualVerifyPhoneSerializer, UserKeySerializer, \
    UserAccountingSerializer, AddressSerializer, AddressBriefSerializer, IntroductionSerializer, RoleSerializer
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .filters import CustomerFilter
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkDeleteSerializer, ApiCategorySerializer
from file_manager.excel_handler import ExcelHandler
from message.models import WebMessage, WebMessageType
from message.serializers import WebMessageSerializer


@extend_schema(tags=["Auth"], summary="Get Refresh Token")
class CustomTokenRefreshView(TokenRefreshView):
    """
    MEH: Send `refresh_token` to get a new `access_token`
    """
    permission_classes = [AllowAny]
    pass


@extend_schema(tags=["Auth"], summary="Verify Access Token")
class CustomTokenVerifyView(TokenVerifyView):
    """
    MEH: Send `access_token` token to get status OK if verified
    """
    permission_classes = [AllowAny]
    pass


@extend_schema(tags=['User'])
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
        filters.OrderingFilter
    ]
    search_fields = ['first_name', 'last_name', 'phone_number'] # MEH: Get search query
    ordering_fields = ['date_joined', 'order_count', 'last_order_date']
    throttle_scope = ''
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        **dict.fromkeys(['list', 'retrieve'], ['get_users', 'customer_dashboard']),
        **dict.fromkeys(['get_by_phone', 'key'], ['get_users']),
        **dict.fromkeys(['update', 'partial_update', 'accounting'], ['update_user']),
        'profile': ['update_user', 'customer_dashboard'],
        **dict.fromkeys(['get_address_list', 'address_detail'], ['get_address', 'customer_dashboard']),
        **dict.fromkeys(['sign_up_manual', 'create'], ['create_user']),
        'destroy': ['delete_user'],
        'activation': ['active_user'],
        **dict.fromkeys(['import_user_list', 'import_user_list_valid_field'], ['import_user_list']),
        'download_user_list': ['download_user_list'],
        'create_address': ['create_address', 'customer_address'],
        'manually_verify_phone': ['verify_phone'],
        'web_message_list': ['message_manager']
    }

    def get_queryset(self, *args, **kwargs):
        """
        MEH: Override queryset
        to parse only required table per action
        """
        user = self.request.user
        is_employee = getattr(user, 'is_employee', False)
        if user.is_superuser or is_employee:
            if self.action in ['change_password', 'web_message_list', 'order_web_message_list']:
                return  super().get_queryset()
            qs = super().get_queryset().filter(is_employee=False, is_superuser=False).order_by('-date_joined')
            if self.action == 'list':
                return qs.select_related('role').prefetch_related('credit', 'company')
            if self.action in ['key', 'manually_verify_phone', 'activation', 'create_address']:
                return qs
            if self.action == 'accounting':
                return qs.select_related('role')
            if self.action == 'profile':
                return qs.select_related('user_profile')
            if self.action in ['credit_info', 'manual_deposit_list']:
                return qs.select_related('credit')
            return (
                qs.select_related('role', 'user_profile', 'introduce_from', 'introducer')
                .annotate(default_province=Subquery(Address.objects.filter(user=OuterRef('pk'), is_default=True).values('province__name')[:1]))
            )
        return User.objects.filter(id=user.id) # MEH: Just return own obj for regular user

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

    def get_serializer_class(self):
        if self.action == 'list':
            return UserBriefSerializer
        return super().get_serializer_class()

    @extend_schema(tags=['Auth'], summary="Sign Up for Customer in-person")
    @action(detail=False, methods=['post'],
            url_path='sign-up', serializer_class=UserSignUpManualSerializer)
    def sign_up_manual(self, request):
        """
        MEH: User Sign Up (POST ACTION) Only Employee with access have permission
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(tags=['Auth'], summary="Sign Up request code")
    @action(detail=False, methods=['post'],
            url_path='sign-up-request', serializer_class=UserSignUpRequestSerializer, filter_backends=[None],
            permission_classes=[IsNotAuthenticated], throttle_scope = 'phone', throttle_classes=[PhoneNumberRateThrottle])
    def sign_up_request(self, request):
        """
        MEH: User request Sign Up (POST ACTION) and get code via SMS Only User that not authenticated have permission
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(tags=['Auth'], summary="Request resend code")
    @action(
        detail=False, methods=['post'],
        url_path='resend-code', serializer_class=UserResendCodeSerializer, filter_backends=[None],
        permission_classes=[IsNotAuthenticated], throttle_scope='phone', throttle_classes=[PhoneNumberRateThrottle]
    )
    def resend_code(self, request):
        """
        MEH: Re-send the last verification code
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(tags=['Auth'], summary="Sign Up verify code")
    @action(detail=False, methods=['post'],
            url_path='sign-up-verify', serializer_class=UserSignUpVerifySerializer, filter_backends=[None],
            permission_classes=[IsNotAuthenticated], throttle_scope = 'auth', throttle_classes=[ScopedRateThrottle])
    def sign_up_verify(self, request):
        """
        MEH: User Sign Up (POST ACTION) to verify SMS code
        Only User that not authenticated have permission
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(tags=['Auth'], summary="Sign In with password")
    @action(detail=False, methods=['post'],
            url_path='sign-in-with-password', serializer_class=UserSignInWithPasswordSerializer, filter_backends=[None],
            permission_classes=[IsNotAuthenticated], throttle_scope = 'auth', throttle_classes=[ScopedRateThrottle])
    def sign_in_with_password(self, request):
        """
        MEH: User Sign In with password (POST ACTION) and get `access_token` & `refresh_token`
        Only User that not authenticated have permission
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(tags=['Auth'], summary="Sign In request code")
    @action(detail=False, methods=['post'],
            url_path='sign-in-request', serializer_class=UserSignInRequestSerializer, filter_backends=[None],
            permission_classes=[IsNotAuthenticated], throttle_scope = 'phone', throttle_classes=[PhoneNumberRateThrottle])
    def sign_in_request(self, request):
        """
        MEH: User request Sign In (POST ACTION) and get SMS code
        Only User that not authenticated have permission.
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(tags=['Auth'], summary="Sign In verify code")
    @action(detail=False, methods=['post'],
            url_path='sign-in-verify', serializer_class=UserSignInWithCodeSerializer, filter_backends=[None],
            permission_classes=[IsNotAuthenticated], throttle_scope = 'auth', throttle_classes=[ScopedRateThrottle])
    def sign_in_verify(self, request):
        """
        MEH: User Sign In with code (POST ACTION) to verify SMS code and get `access_token` & `refresh_token`
        Only User that not authenticated have permission
        """
        return self.custom_create(request, response_data_back=True)

    @extend_schema(tags=['Auth'], summary="Change Password request")
    @action(detail=True, methods=['put'],
            url_path='change-password', serializer_class=UserChangePasswordSerializer, filter_backends=[None],
            permission_classes=[IsOwner])
    def change_password(self, request, pk=None):
        """
        MEH: User can try change old password (most authenticate)
        """
        user = self.get_object(pk=pk)
        self.check_object_permissions(request, user)
        return self.custom_update(user, request, response_data_back=True)

    @extend_schema(summary="Get User by phone number")
    @action(detail=False, methods=['get'],
            url_path='by-phone/(?P<phone_number>\\d{11})')
    def get_by_phone(self, request, phone_number=None):
        """
        MEH: Get User by `phone_number` (GET ACTION)
        """
        user = self.get_object(phone_number=phone_number)
        return self.custom_get(user)

    @extend_schema(summary="Get User Profile information")
    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='profile', serializer_class=UserProfileSerializer, filter_backends=[None])
    def profile(self, request, pk=None):
        """
        MEH: Get User Profile information and Update it with `pk` (GET/PUT ACTION)
        """
        user = self.get_object(pk=pk)
        self.check_object_permissions(request, user)
        user_profile = user.user_profile
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(user_profile, request, partial=(request.method == 'PATCH'))
        return self.custom_get(user_profile)

    @extend_schema(summary="Get User Key information")
    @action(detail=True, methods=['get'],
            url_path='key', serializer_class=UserKeySerializer, filter_backends=[None])
    def key(self, request, pk=None):
        """
        MEH: Get User Key information with `pk` (GET ACTION)
        Update block (auto generated and never change)
        """
        user = self.get_object(pk=pk)
        return self.custom_get(user)

    @extend_schema(summary="Get User Accounting information")
    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='accounting', serializer_class=UserAccountingSerializer, filter_backends=[None])
    def accounting(self, request, pk=None):
        """
        MEH: Get User Accounting information and Update it with `pk` (GET/PUT ACTION)
        """
        user = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(user, request, partial=(request.method == 'PATCH'))
        return self.custom_get(user)

    @extend_schema(summary="Get User Activation information")
    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='activation', serializer_class=UserActivationSerializer, filter_backends=[None])
    def activation(self, request, pk=None):
        """
        MEH: Get User Activation information with `pk` to Update `is_active` (GET/PUT ACTION)
        """
        user = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(user, request, partial=(request.method == 'PATCH'))
        return self.custom_get(user)

    @extend_schema(tags=['User-Address'], summary="Get User Address list")
    @action(detail=True, methods=['get'],
            url_path='address-list', serializer_class=AddressBriefSerializer, filter_backends=[None])
    def get_address_list(self, request, pk=None):
        """
        MEH: Get User full Address list with `pk` (GET ACTION)
        Inline Queryset
        """
        address_list = Address.objects.select_related('user', 'province', 'city').filter(user__pk=pk).order_by('-is_default', 'title')
        if address_list.exists():
            self.check_object_permissions(request, address_list.first())
        return self.custom_get(address_list)

    @extend_schema(tags=['User-Address'], summary="User Address details")
    @action(detail=True, methods=['get', 'put', 'patch', 'delete'],
            url_path='address/(?P<address_id>\d+)', serializer_class=AddressSerializer, filter_backends=[None])
    def address_detail(self, request, pk=None, address_id=None):
        """
        MEH: Get User Address Detail `user.pk` & `address_id`, Update and Delete it (PUT/DELETE ACTION)
        """
        address_list = Address.objects.select_related('user', 'province', 'city').filter(user__pk=pk)
        try:
            address = address_list.get(pk=address_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        except ValueError:
            raise NotFound(TG_EXPECTED_ID_NUMBER)
        self.check_object_permissions(request, address)
        if request.method == 'DELETE':
            return self.custom_destroy(address)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(address, request, partial=(request.method == 'PATCH'))
        return self.custom_get(address)

    @extend_schema(tags=['User-Address'], summary="Add Address for User")
    @action(detail=True, methods=['post'],
            url_path='address-add', serializer_class=AddressSerializer, filter_backends=[None])
    def create_address(self, request, pk=None):
        """
        MEH: Add New Address for User with `pk` (POST ACTION)
        """
        user = self.get_object(pk=pk)
        self.check_object_permissions(request, user)
        return self.custom_create(request, user=user)

    @extend_schema(
        summary = "Upload Excel for add User list",
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
            url_path='import', serializer_class=UserImportFieldDataSerializer, filter_backends=[None], pagination_class=None)
    def import_user_list(self, request):
        """
        MEH: Create User list from Excel File (up to 1000) (POST ACTION)
        give any Excel file with any col and row (Handle valid col header and row data)
        """
        check_serializer = self.get_validate_data(request.data)
        excel_file = check_serializer['excel_file']
        required_fields = ['phone_number', 'first_name'] # MEH: Required field check in Excel col
        profile_fields = [ # MEH: Nested User Profile data Handle
            name for name, field in UserProfileSerializer().get_fields().items()
            if not getattr(field, 'read_only', False)
        ]
        allowed_fields = set(UserSerializer().get_fields().keys()) # MEH: Allowed field that serializer accept
        extra_fields = {'role':check_serializer['role'].pk} # MEH: Selected Role in form for all User in Excel
        user_data_list = ExcelHandler.import_excel(
            excel_file, allowed_fields, required_fields,
            nested_fields=profile_fields,
            nested_field_category='user_profile',
            extra_fields=extra_fields,
        )
        serializer = UserImportDataSerializer(data=user_data_list, many=True) # MEH: Change Serializer class to Validate Posted Data with Excel
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) # MEH: Check, Validate (Raise Exception if any) & Save Data in DB 1 by 1 (CustomBulkListSerializer)
        return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)

    @extend_schema(summary = "Valid header for Import Excel")
    @action(detail=False, methods=['get'],
            url_path='import-fields', serializer_class=UserImportDataSerializer, filter_backends=[None], pagination_class=None)
    def import_user_list_valid_field(self, request):
        """
        MEH: Get a list of valid User field for upload Excel
        """
        all_fields = self.get_serializer_fields()
        return Response({'detail': list(all_fields.keys())}, status=status.HTTP_200_OK)

    @extend_schema(
        summary = "Download Excel of User list",
        responses={200: OpenApiTypes.BINARY}, # or a more specific file/media type
        parameters=[
            OpenApiParameter(
                name='check_field',
                description='Used for highlight User row in Excel file, if check_filed is None or 0 in Excel cell',
                required=False,
                type=str,
                location='query',
                enum=list(UserDownloadDataSerializer().get_fields().keys())
            )
        ]
    )
    @action(detail=False, methods=['get'],
            url_path='download', serializer_class=None)
    def download_user_list(self, request):
        """
        MEH: Direct Download Excel of User List with Filter (up to 1000) (GET ACTION)
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

    @extend_schema(summary="Verify User phone number manually")
    @action(detail=True, methods=['get', 'put', 'partial'],
            url_path='manually-verify-phone', serializer_class=UserManualVerifyPhoneSerializer, filter_backends=[None])
    def manually_verify_phone(self, request, pk=None):
        """
        MEH: Get User Verify phone information with `pk` to Update `verified_phone` manually (GET/PUT ACTION)
        """
        user = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(user, request, partial=(request.method == 'PATCH'))
        return self.custom_get(user)

    @extend_schema(summary="Get User web message list")
    @action(detail=True, methods=['get'],
            url_path='web-message', serializer_class=WebMessageSerializer, filter_backends=[None])
    def web_message_list(self, request, pk=None):
        """
        MEH: Get User Web Message list (without Order)
        """
        user = self.get_object(pk=pk)
        web_message_list = (WebMessage.objects.select_related('user', 'employee', 'department')
                            .filter(user=user).exclude(type=WebMessageType.ORDER)
                            .order_by('-last_update_date'))
        return self.custom_get(web_message_list)

    @extend_schema(summary="Get User request order web message list")
    @action(detail=True, methods=['get'],
            url_path='order-message', serializer_class=WebMessageSerializer, filter_backends=[None])
    def order_web_message_list(self, request, pk=None):
        """
        MEH: Get User Web Message list (just Order)
        """
        user = self.get_object(pk=pk)
        web_message_list = (WebMessage.objects.select_related('user', 'employee', 'department')
                            .filter(user=user, type=WebMessageType.ORDER)
                            .order_by('-last_update_date'))
        return self.custom_get(web_message_list)

    @extend_schema(
        summary="Get User Credit info with deposit list",
        parameters=[
            OpenApiParameter(name='deposit_type', type=OpenApiTypes.STR, location='query'),
            OpenApiParameter(name='submit_date__gte', type=OpenApiTypes.DATE, location='query'),
            OpenApiParameter(name='submit_date__lte', type=OpenApiTypes.DATE, location='query'),
            OpenApiParameter(name='page', type=OpenApiTypes.INT, location='query'),
            OpenApiParameter(name='size', type=OpenApiTypes.INT, location='query'),
        ],
    )
    @action(detail=True, methods=['get'],
            url_path='credit', serializer_class=CreditSerializer, filter_backends=[None])
    def credit_info(self, request, pk=None):
        """
        MEH: Get User Credit info
        """
        user = self.get_object(pk=pk)
        return self.custom_get(user.credit)

    @action(detail=True, methods=['get'],
            url_path='manual-deposit-list', serializer_class=DepositBriefInfoForUserManualListSerializer, filter_backends=[None])
    def manual_deposit_list(self, request, pk=None):
        """
        MEH: Get User manual_deposit info
        """
        user = self.get_object(pk=pk)
        deposit_list = user.credit.deposit_list.exclude(confirm_status=DepositConfirmStatus.AUTO)
        return self.custom_get(deposit_list)


@extend_schema(tags=["User-Introduction"])
class IntroductionViewSet(CustomMixinModelViewSet):
    """
    MEH: Introduction Model viewset
    """
    queryset = Introduction.objects.all().order_by('sort_number')
    serializer_class = IntroductionSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title'] # MEH: Get search query
    ordering_fields = ['title', 'number']
    permission_classes = [ApiAccess] # MEH: Handle Access for Employee (List, Obj, and per default and custom @action)
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        '__all__': ['full_introductions']
    }


@extend_schema(tags=["Role"])
class RoleViewSet(CustomMixinModelViewSet):
    """
    MEH: Role Model viewset
    """
    queryset = (Role.objects.prefetch_related('api_items')
                .order_by('-is_default', 'sort_number'))
    serializer_class = RoleSerializer
    permission_classes = [ApiAccess]
    required_api_keys = { # MEH: API static key for each action, save exactly in DB -> Api Item with Category
        '__all__': ['get_user_role_access'],
        'create': ['create_user_role_access']
    }

    @extend_schema(summary='Api Item list for each Role for User')
    @action(detail=False, methods=['get'], serializer_class=ApiCategorySerializer,
            url_path='api-list')
    def role_api_item_list(self, request):
        """
        MEH: List of Api Item a Role can have for User (role_base=True)
        """
        api_category_list = ApiCategory.objects.prefetch_related('api_items').filter(role_base=True)
        return self.custom_get(api_category_list)

    @extend_schema(summary='Delete a list of Role')
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
        MEH: Delete List of Role Objects (use POST ACTION for sending list of id `ids` in request body)
        """
        validated_data = self.get_validate_data(request.data)
        ids = validated_data['ids']
        roles = self.get_queryset().filter(id__in=ids)
        return self.custom_list_destroy([roles])
