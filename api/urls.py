from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import MyTokenObtainPairView
from user.views import UserSignUpView, UserViewSet, UserProfileViewSet, RoleViewSet, IntroductionViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'user_profiles', UserProfileViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'introductions', IntroductionViewSet)

urlpatterns = [
    path('auth/signup/', UserSignUpView.as_view(), name='user_signup'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),
]
