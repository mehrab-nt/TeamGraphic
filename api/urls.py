from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import MyTokenObtainPairView
from user.views import UserSignUpView, UserSignInView, UserViewSet, UserProfileViewSet, RoleViewSet, \
    IntroductionViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'signup', UserSignUpView, basename='signup')
router.register(r'signin', UserSignInView, basename='signin')
router.register(r'user', UserViewSet, basename='user')
router.register(r'user_profiles', UserProfileViewSet, basename='user_profiles')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'introductions', IntroductionViewSet, basename='introductions')
router.register(r'addresses', AddressViewSet, basename='addresses')

urlpatterns = [
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),
]
