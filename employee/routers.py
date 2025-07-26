from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, EmployeeLevelViewSet

router = DefaultRouter()
router.register(r'employee', EmployeeViewSet, basename='employee')
router.register(r'employee-level', EmployeeLevelViewSet, basename='employee-level')
