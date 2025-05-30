from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView
from user.views import UserRegistrationView, UserViewSet, UserProfileViewSet, RoleViewSet, IntroductionViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'user_profiles', UserProfileViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'introductions', IntroductionViewSet)

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]