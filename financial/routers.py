from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DepositViewSet, OfflineBankAccountViewSet, OnlineBankAccountViewSet

router = DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'deposit', DepositViewSet, basename='deposit')
router.register(r'offline-bank', OfflineBankAccountViewSet, basename='offline_bank')
router.register(r'online-bank', OnlineBankAccountViewSet, basename='online_bank')
