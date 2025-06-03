from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView
from user.views import UserSignUpView, UserViewSet, UserProfileViewSet, RoleViewSet, IntroductionViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'user_profiles', UserProfileViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'introductions', IntroductionViewSet)

urlpatterns = [
    path('auth/signup/', UserSignUpView.as_view(), name='user_signup'),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

urlpatterns = format_suffix_patterns(urlpatterns)