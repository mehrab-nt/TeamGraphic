from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from api.permissions import IsNotAuthenticated, IsOwnerOrAdmin
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import User, UserProfile, Role, Introduction, Address, GENDER
from .serializers import UserSignUpSerializer, UserSignInSerializer, UserSerializer, UserProfileSerializer, \
    UserKeySerializer, UserAccountingSerializer, RoleSerializer, IntroductionSerializer, AddressSerializer
from .filters import CustomerQueryFilter, CustomerFilter
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, PermissionDenied
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema_view, extend_schema
from backend.tg_massages import *

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
    pagination_class.max_page_size = 1000

    def get_object(self, *args, **kwargs):
        if not self.kwargs.get('phone_number'):
            lookup_value = self.kwargs.get(self.lookup_field, '')
            try:
                return self.queryset.get(pk=int(lookup_value))
            except (ValueError, ObjectDoesNotExist):
                raise NotFound(TG_USER_NOT_FOUND_BY_ID)
        lookup_value = self.kwargs.get('phone_number')
        try:
            return self.queryset.get(phone_number=lookup_value)
        except ObjectDoesNotExist:
            raise NotFound(TG_USER_NOT_FOUND_BY_PHONE)

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

    @extend_schema(operation_id='user_get_by_phone')
    @action(detail=False, methods=['get'],
            url_path='by-phone/(?P<phone_number>\\d{11})')
    def get_by_phone(self, request, phone_number=None):
        try:
            queryset = self.get_object(phone_number=phone_number)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": TG_USER_NOT_FOUND_BY_PHONE}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='profile', serializer_class=UserProfileSerializer)
    def profile(self, request, pk=None):
        try:
            queryset = UserProfile.objects.get(user__pk=pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": TG_DATA_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"detail": TG_EXPECTED_PHONE_NUMBER}, status=status.HTTP_404_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            serializer = UserProfileSerializer(queryset, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'],
            url_path='key', serializer_class=UserKeySerializer)
    def key(self, request, pk=None):
        try:
            queryset = self.get_object(pk=pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": TG_USER_NOT_FOUND_BY_ID}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='accounting', serializer_class=UserAccountingSerializer)
    def accounting(self, request, pk=None):
        try:
            queryset = self.get_object(pk=pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": TG_USER_NOT_FOUND_BY_ID}, status=status.HTTP_404_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(queryset, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, http_method_names=['get', 'post'], methods=['get', 'post'],
            url_path='addresses', serializer_class=AddressSerializer, filter_backends=[None],
            permission_classes=[IsOwnerOrAdmin])
    def address_list(self, request, pk=None):
        if request.method == 'POST':
            try:
                user = User.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return Response({"detail": TG_USER_NOT_FOUND_BY_ID}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            queryset = Address.objects.all().filter(user__pk=pk)
            return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)
        try:
            queryset = Address.objects.all().filter(user__pk=pk)
        except ValueError:
            return Response({"detail": TG_EXPECTED_ID_NUMBER}, status=status.HTTP_404_NOT_FOUND)
        if not queryset.exists():
            return Response({"detail": TG_DATA_EMPTY}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Users-Addresses'])
    @action(detail=True, methods=['get', 'put', 'patch', 'delete'],
            url_path='address/(?P<address_id>\d+)', serializer_class=AddressSerializer, filter_backends=[None],
            permission_classes=[IsOwnerOrAdmin])
    def address_detail(self, request, pk=None, address_id=None):
        try:
            address = Address.objects.get(pk=address_id, user__pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            if address.is_default:
                raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
            address.delete()
            return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)

        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(address, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(self.get_serializer(address).data, status=status.HTTP_200_OK)


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
        return Response(status=status.HTTP_204_NO_CONTENT)
