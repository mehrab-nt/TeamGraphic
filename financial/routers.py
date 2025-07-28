from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DepositViewSet

router = DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'deposit', DepositViewSet, basename='deposit')
