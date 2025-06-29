from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework.urlpatterns import format_suffix_patterns
# from .views import MyTokenObtainPairView
from .views import CustomTokenRefreshView, CustomTokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from user.views import UserViewSet, RoleViewSet, IntroductionViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'introductions', IntroductionViewSet, basename='introductions')

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),
]
