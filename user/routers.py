from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, IntroductionViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'introduction', IntroductionViewSet, basename='introduction')
router.register(r'address', AddressViewSet, basename='address')
