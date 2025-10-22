from rest_framework.routers import DefaultRouter
from .views import ProvinceViewSet, CityViewSet

router = DefaultRouter()
router.register(r'province', ProvinceViewSet, basename='province')
router.register(r'city', CityViewSet, basename='city')
