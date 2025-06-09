from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsNotAuthenticated
from rest_framework.response import Response
from .models import User, UserProfile, Role, Introduction, Address
from .serializers import UserSignUpSerializer, UserSignInSerializer, UserSerializer, UserProfileSerializer, \
    UserKeySerializer, UserAccountingSerializer, RoleSerializer, IntroductionSerializer, AddressSerializer


class UserSignUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsNotAuthenticated]  # Allow anyone to register
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "User created."}, status=status.HTTP_201_CREATED)


class UserSignInView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsNotAuthenticated]
    serializer_class = UserSignInSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
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
