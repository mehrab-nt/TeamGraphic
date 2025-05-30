# from django.shortcuts import render
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets, generics
# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.parsers import JSONParser
from users.models import *
from users.serializers import *
from .permissions import IsOwnerOrAdminOrReadOnly, IsOwnerOrAdmin
# from django.core.exceptions import ObjectDoesNotExist
# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.reverse import reverse
# from rest_framework import renderers


class UserDetailsApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser, IsOwnerOrAdmin]
    lookup_field = 'public_key'
    lookup_url_kwarg = 'public_key'


class UserListApiView(generics.ListCreateAPIView):
    queryset = User.objects.prefetch_related('user_profile')
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user_profile__phone_number__isnull=False).order_by('-date_joined')
    # user=self.request.user


class UserProfileApiView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsOwnerOrAdmin]