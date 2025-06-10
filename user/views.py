from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.permissions import IsNotAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import User, UserProfile, Role, Introduction, Address, GENDER
from .serializers import UserSignUpSerializer, UserSignInSerializer, UserSerializer, UserProfileSerializer, \
    UserKeySerializer, UserAccountingSerializer, RoleSerializer, IntroductionSerializer, AddressSerializer
from .filters import CustomerQueryFilter, CustomerFilter
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.exceptions import NotFound
from api.views import CustomModelViewSet

class UserViewSet(CustomModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
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
                raise NotFound("User not found by ID.")
        lookup_value = self.kwargs.get('phone_number')
        try:
            return self.queryset.get(phone_number=lookup_value)
        except ObjectDoesNotExist:
            raise NotFound("User not found by phone number.")

    @action(detail=False, methods=['post'],
            url_path='sign-up', permission_classes=[IsNotAuthenticated, IsAdminUser], serializer_class=UserSignUpSerializer)
    def sign_up(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "User created."}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'],
            url_path='sign-in', permission_classes=[IsNotAuthenticated, IsAdminUser], serializer_class=UserSignInSerializer)
    def sign_in(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            url_path='by-phone/(?P<phone_number>\\d{11})', permission_classes=[IsAdminUser])
    def get_by_phone(self, request, phone_number=None):
        try:
            queryset = self.get_object(phone_number=phone_number)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": "User not Found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='profile', permission_classes=[IsAuthenticated, IsAdminUser], serializer_class=UserProfileSerializer)
    def profile(self, request, pk=None):
        try:
            queryset = UserProfile.objects.get(user__pk=pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": "Profile not Found!"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"detail": "Invalid user ID format. Expected a number."}, status=status.HTTP_404_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            serializer = UserProfileSerializer(queryset, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'],
            url_path='key', permission_classes=[IsAuthenticated, IsAdminUser], serializer_class=UserKeySerializer)
    def key(self, request, pk=None):
        try:
            queryset = self.get_object(pk=pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": "User not Found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put', 'patch'],
            url_path='accounting', permission_classes=[IsAdminUser], serializer_class=UserAccountingSerializer)
    def accounting(self, request, pk=None):
        try:
            queryset = self.get_object(pk=pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({"detail": "User not Found!"}, status=status.HTTP_404_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(queryset, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post', 'put', 'patch', 'delete'],
            url_path='addresses', permission_classes=[IsAdminUser], serializer_class=AddressSerializer, filter_backends=[None])
    def address_list(self, request, pk=None):
        try:
            queryset = Address.objects.all().filter(user__pk=pk)
        except ValueError:
            return Response({"detail": "Invalid user ID format. Expected a number."}, status=status.HTTP_404_NOT_FOUND)
        if not queryset.exists():
            return Response({"detail": "No addresses found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)
    # todo: Post Put Delete

class IntroductionViewSet(CustomModelViewSet):
    queryset = Introduction.objects.all()
    serializer_class = IntroductionSerializer
    permission_classes = [IsAuthenticated]

class RoleViewSet(CustomModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
