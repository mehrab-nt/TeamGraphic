from rest_framework.routers import DefaultRouter
from .views import ProductReportViewSet

router = DefaultRouter()
router.register(r'report/product', ProductReportViewSet, basename='product-report')
