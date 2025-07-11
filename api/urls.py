from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from .views import ApiCategoryViewSet, ApiItemViewSet
from user.views import UserViewSet, RoleViewSet, IntroductionViewSet
from employee.views import EmployeeViewSet, EmployeeLevelViewSet
from file_manager.views import FileDirectoryViewSet, FileItemViewSet
from product.views import ProductViewSet, ProductCategoryViewSet


router = DefaultRouter()
router.register(r'access-category', ApiCategoryViewSet, basename='api-access')
router.register(r'access-item', ApiItemViewSet, basename='api-access-item')
router.register(r'employee', EmployeeViewSet, basename='employee')
router.register(r'employee-level', EmployeeLevelViewSet, basename='employee-level')
router.register(r'user', UserViewSet, basename='user')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'introduction', IntroductionViewSet, basename='introduction')
router.register(r'file-manager/directory', FileDirectoryViewSet, basename='file-directory')
router.register(r'file-manager/item', FileItemViewSet, basename='file-item')
router.register(r'product/category', ProductCategoryViewSet, basename='product-category')
router.register(r'product', ProductViewSet, basename='product')


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
    path('', include('user.urls')),
]
