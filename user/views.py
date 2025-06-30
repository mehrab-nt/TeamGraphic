from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.permissions import IsOwnerOrAdmin
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import User, Role, Introduction
from .serializers import (UserSignUpSerializer, UserSignInSerializer, UserSerializer, UserProfileSerializer, UserRoleSerializer,
                          UserKeySerializer, UserAccountingSerializer, AddressSerializer, IntroductionSerializer, RoleSerializer)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .filters import CustomerQueryFilter, CustomerFilter
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema
from api.tg_massages import *


@extend_schema(tags=["Auth"])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["Auth"])
class CustomTokenVerifyView(TokenVerifyView):
    pass


@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'head', 'options', 'delete', 'put', 'patch']
    filterset_class = CustomerFilter
    filter_backends = [
        DjangoFilterBackend,
        CustomerQueryFilter,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['first_name', 'id']
    # permission_classes = [IsAuthenticated]
    # MEH: Custom Pagination :) even LimitOffsetPagination
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 100

    def get_object(self, *args, **kwargs):
        if not self.kwargs.get('phone_number'):
            lookup_value = self.kwargs.get(self.lookup_field, '')
            try:
                return self.queryset.get(pk=int(lookup_value))
            except ObjectDoesNotExist:
                raise NotFound(TG_USER_NOT_FOUND_BY_ID)
            except ValueError:
                raise NotFound(TG_EXPECTED_ID_NUMBER)
        lookup_value = self.kwargs.get('phone_number')
        try:
            return self.queryset.get(phone_number=lookup_value)
        except ObjectDoesNotExist:
            raise NotFound(TG_USER_NOT_FOUND_BY_PHONE)

    def set_update(self, queryset, request, *args, **kwargs):
        serializer = self.get_serializer(queryset, data=request.data, partial=(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Auth'], operation_id='user_signup')
    @action(detail=False, http_method_names=['post'], methods=['post'],
            url_path='sign-up', serializer_class=UserSignUpSerializer)
    def sign_up(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": TG_USER_CREATED}, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Auth'], operation_id='user_signin')
    @action(detail=False, http_method_names=['post'], methods=['post'],
            url_path='sign-in', serializer_class=UserSignInSerializer,
            permission_classes=[AllowAny])
    def sign_in(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            url_path='by-phone/(?P<phone_number>\\d{11})')
    def get_by_phone(self, request, phone_number=None):
        try:
            queryset = self.get_object(phone_number=phone_number)
        except ObjectDoesNotExist:
            raise NotFound(TG_USER_NOT_FOUND_BY_PHONE)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='profile', serializer_class=UserProfileSerializer)
    def profile(self, request, pk=None):
        user = self.get_object(pk=pk)
        queryset = user.user_profile
        if request.method in ['PUT', 'PATCH']:
            self.set_update(queryset, request)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'],
            url_path='key', serializer_class=UserKeySerializer)
    def key(self, request, pk=None):
        queryset = self.get_object(pk=pk)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='accounting', serializer_class=UserAccountingSerializer)
    def accounting(self, request, pk=None):
        queryset = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            self.set_update(queryset, request)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Users-Role'])
    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='role', serializer_class=UserRoleSerializer, filter_backends=[None])
    def activation(self, request, pk=None):
        queryset = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            self.set_update(queryset, request)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, http_method_names=['get', 'post'], methods=['get', 'post'],
            url_path='addresses', serializer_class=AddressSerializer, filter_backends=[None],
            permission_classes=[IsOwnerOrAdmin])
    def address_list(self, request, pk=None):
        user = self.get_object(pk=pk)
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)
        queryset = user.user_addresses
        if not queryset.exists():
            raise NotFound(TG_DATA_EMPTY)
        return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get', 'put', 'patch', 'delete'],
            url_path='addresses/(?P<address_id>\d+)', serializer_class=AddressSerializer, filter_backends=[None],
            permission_classes=[IsOwnerOrAdmin])
    def address_detail(self, request, pk=None, address_id=None):
        user = self.get_object(pk=pk)
        try:
            queryset = user.user_addresses.get(pk=address_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        except ValueError:
            raise NotFound(TG_EXPECTED_ID_NUMBER)
        if request.method == 'DELETE':
            if queryset.is_default:
                raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
            queryset.delete()
            return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(queryset, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Users-Introduction"])
class IntroductionViewSet(viewsets.ModelViewSet):
    queryset = Introduction.objects.all()
    serializer_class = IntroductionSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Roles"])
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default:
            raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
        self.perform_destroy(instance)
        return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)
