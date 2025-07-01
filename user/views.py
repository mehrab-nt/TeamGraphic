from pickle import FALSE

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from api.permissions import UserApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Role, Introduction
from .serializers import (UserSignUpSerializer, UserSignInSerializer, UserSerializer, UserProfileSerializer,UserRoleSerializer,
                          UserKeySerializer, UserAccountingSerializer, AddressSerializer, IntroductionSerializer, RoleSerializer)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .filters import CustomerQueryFilter, CustomerFilter
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkDeleteSerializer


# MEH: Get Refresh Token
@extend_schema(tags=["Auth"])
class CustomTokenRefreshView(TokenRefreshView):
    pass


# MEH: Verify Access Token
@extend_schema(tags=["Auth"])
class CustomTokenVerifyView(TokenVerifyView):
    pass


# MEH: User List view set
@extend_schema(tags=['Users'])
class UserViewSet(CustomMixinModelViewSet):
    queryset = User.objects.prefetch_related('user_profile')
    serializer_class = UserSerializer
    # MEH: Handle Access for Employee (List, Obj, and per default and custom @action)
    permission_classes = [UserApiAccess]
    filterset_class = CustomerFilter
    filter_backends = [
        DjangoFilterBackend,
        CustomerQueryFilter,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    # MEH: Get search query
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['first_name', 'id']

    # MEH: Override get single user (with ID or phone_number) | Access check after In has_object_permission
    def get_object(self, *args, **kwargs):
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

    # MEH: Override post single User or Bulk list
    def create(self, request, *args, **kwargs):
        return self.custom_create(request, password='12345678')

    # MEH: User Sign Up action (POST) for customer
    @extend_schema(tags=['Auth'])
    @action(detail=False, methods=['post'],
            url_path='sign-up', serializer_class=UserSignUpSerializer,
            permission_classes=[IsNotAuthenticated])
    def sign_up(self, request):
        return self.custom_create(request)

    # MEH: User Sign In action (POST) and get Access & Refresh Token
    @extend_schema(tags=['Auth'])
    @action(detail=False, methods=['post'],
            url_path='sign-in', serializer_class=UserSignInSerializer,
            permission_classes=[IsNotAuthenticated])
    def sign_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    # MEH: Get User by phone_number
    @action(detail=False, methods=['get'],
            url_path='by-phone/(?P<phone_number>\\d{11})')
    def get_by_phone(self, request, phone_number=None):
        queryset = self.get_object(phone_number=phone_number)
        return self.custom_get(queryset)

    # MEH: Get User Profile information and Update it with ID
    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='profile', serializer_class=UserProfileSerializer)
    def profile(self, request, pk=None):
        user = self.get_object(pk=pk)
        queryset = user.user_profile
        if request.method in ['PUT', 'PATCH']:
            self.custom_update(queryset, request)
        return self.custom_get(queryset)

    # MEH: Get User Key information (Update not work)
    @action(detail=True, methods=['get'],
            url_path='key', serializer_class=UserKeySerializer)
    def key(self, request, pk=None):
        queryset = self.get_object(pk=pk)
        return self.custom_get(queryset)

    # MEH: Get User Accounting information and Update it
    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='accounting', serializer_class=UserAccountingSerializer)
    def accounting(self, request, pk=None):
        queryset = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            self.custom_update(queryset, request)
        return self.custom_get(queryset)

    # MEH: Get User Role and Active information and Update it
    @extend_schema(tags=['Users-Role'])
    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='role', serializer_class=UserRoleSerializer, filter_backends=[None])
    def activation(self, request, pk=None):
        queryset = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            self.custom_update(queryset, request)
        return self.custom_get(queryset)

    # MEH: Get User Address list and Add New Address (POST)
    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get', 'post'],
            url_path='addresses', serializer_class=AddressSerializer, filter_backends=[None])
    def address_list(self, request, pk=None):
        user = self.get_object(pk=pk)
        if request.method == 'POST':
            return self.custom_create(request, user=user)
        queryset = user.user_addresses.all()
        if not queryset.exists():
            raise NotFound(TG_DATA_EMPTY)
        return self.custom_get(queryset)

    # MEH: Get User Address Detail, Update and Delete it
    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get', 'put', 'patch', 'delete'],
            url_path='addresses/(?P<address_id>\d+)', serializer_class=AddressSerializer, filter_backends=[None])
    def address_detail(self, request, pk=None, address_id=None):
        user = self.get_object(pk=pk)
        try:
            instance = user.user_addresses.get(pk=address_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        except ValueError:
            raise NotFound(TG_EXPECTED_ID_NUMBER)
        if request.method == 'DELETE':
            return self.custom_destroy(instance, is_default=instance.is_default)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(instance, request)
        return self.custom_get(instance)


# MEH: Get Introduction List and Add single object (POST) update (PUT) and protected remove (DELETE)
@extend_schema(tags=["Users-Introduction"])
class IntroductionViewSet(CustomMixinModelViewSet):
    queryset = Introduction.objects.all()
    serializer_class = IntroductionSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.custom_destroy(instance)

# MEH: Get Role List and Add single object (POST) update (PUT) and protected remove (DELETE)
@extend_schema(tags=["Roles"])
class RoleViewSet(CustomMixinModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.custom_destroy(instance, is_default=instance.is_default)

    #  MEH: Delete List of object todo: work more after
    @extend_schema(
        request=BulkDeleteSerializer,
        responses={
           204: OpenApiResponse(description="Successfully deleted roles."),
           400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['delete'],
            url_path='bulk-delete')
    def bulk_delete(self, request):
        return self.custom_bulk_destroy(request)
