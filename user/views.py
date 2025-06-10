from rest_framework import viewsets, mixins, status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.permissions import IsNotAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import User, UserProfile, Role, Introduction, Address
from .serializers import UserSignUpSerializer, UserSignInSerializer, UserSerializer, UserProfileSerializer, \
    UserKeySerializer, UserAccountingSerializer, RoleSerializer, IntroductionSerializer, AddressSerializer
from .filters import UserFilter, CustomerFilter


class UserSignUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "User created."}, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        self.permission_classes = [IsNotAuthenticated, IsAdminUser]
        return super().get_permissions()


class UserSignInView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsNotAuthenticated, IsAdminUser]
    serializer_class = UserSignInSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    filter_backends = [
        DjangoFilterBackend,
        CustomerFilter,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['first_name', 'id']
    # permission_classes = [IsAuthenticated]
    # MEH: Custom Pagination :) even LimitOffsetPagination
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 100



class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.prefetch_related('user').all()
    serializer_class = UserProfileSerializer
    # permission_classes = [IsAuthenticated]

#
# class UserKeyViewSet(APIView):
#     def get(self, request):
#         queryset = User.objects.all()
#         serializer = UserKeySerializer({
#             'id': queryset.all()[0].id,
#             'phone_number': queryset.all()[0].phone_number,
#             'public_key': queryset.all()[0].public_key,
#             'private_key': queryset.all()[0].private_key,
#         })
#         return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    # permission_classes = [IsAuthenticated]


class IntroductionViewSet(viewsets.ModelViewSet):
    queryset = Introduction.objects.all()
    serializer_class = IntroductionSerializer
    # permission_classes = [IsAuthenticated]


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsNotAuthenticated]
