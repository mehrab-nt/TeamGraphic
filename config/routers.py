from rest_framework.routers import DefaultRouter
from .views import PriceListConfigViewSet

router = DefaultRouter()
router.register('config/price-list', PriceListConfigViewSet, basename='price-list-config')
