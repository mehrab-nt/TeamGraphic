from rest_framework.routers import DefaultRouter
from .views import ProductReportViewSet, CounterReportViewSet, MonthlySaleReportViewSet

router = DefaultRouter()
router.register(r'report/product', ProductReportViewSet, basename='product-report')
router.register(r'report/counter', CounterReportViewSet, basename='counter-report')
router.register(r'report/monthly-sale', MonthlySaleReportViewSet, basename='monthly-sale-report')
