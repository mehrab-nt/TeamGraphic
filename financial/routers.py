from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DepositViewSet, OfflineBankAccountViewSet, OnlineBankAccountViewSet, \
    CashBackPercentViewSet, CashBackViewSet

router = DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'deposit', DepositViewSet, basename='deposit')
router.register(r'offline-bank', OfflineBankAccountViewSet, basename='offline_bank')
router.register(r'online-bank', OnlineBankAccountViewSet, basename='online_bank')
router.register(r'cash-back-percent', CashBackPercentViewSet, basename='cash_back_percent')
router.register(r'cash-back', CashBackViewSet, basename='cash_back')
