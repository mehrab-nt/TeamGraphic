from rest_framework import viewsets, mixins, status, filters
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
# from .serializers import MyTokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema

@extend_schema(tags=["Auth"])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["Auth"])
class CustomTokenVerifyView(TokenVerifyView):
    pass
