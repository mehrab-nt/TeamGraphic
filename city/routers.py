from rest_framework.routers import DefaultRouter
from .views import ProvinceViewSet

router = DefaultRouter()
router.register(r'province', ProvinceViewSet, basename='province')
