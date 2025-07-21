from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from .views import ApiCategoryViewSet, ApiItemViewSet
from user.views import UserViewSet, RoleViewSet, IntroductionViewSet
from employee.views import EmployeeViewSet, EmployeeLevelViewSet
from file_manager.views import FileDirectoryViewSet, FileItemViewSet
from product.views import ProductViewSet, ProductCategoryViewSet, GalleryCategoryViewSet, GalleryImageViewSet, \
    DesignViewSet, FileFieldViewSet, SizeViewSet, TirageViewSet, DurationViewSet, SheetPaperViewSet, PaperViewSet, \
    OptionCategoryViewSet, OptionViewSet, BannerViewSet, ColorViewSet, FoldingViewSet, PageViewSet
from report.views import ProductReportViewSet


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
router.register(r'gallery/category', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery/image', GalleryImageViewSet, basename='gallery-image')
router.register(r'design', DesignViewSet, basename='design')
router.register(r'product/category', ProductCategoryViewSet, basename='product-category')
router.register(r'product/item', ProductViewSet, basename='product-item')
router.register(r'option/category', OptionCategoryViewSet, basename='option-category')
router.register(r'option/item', OptionViewSet, basename='option-item')
router.register(r'product/file-field', FileFieldViewSet, basename='product-file-field')
router.register(r'product/size', SizeViewSet, basename='product-size')
router.register(r'product/tirage', TirageViewSet, basename='product-tirage')
router.register(r'product/duration', DurationViewSet, basename='product-duration')
router.register(r'product/banner', BannerViewSet, basename='product-banner')
router.register(r'product/color', ColorViewSet, basename='product-color')
router.register(r'product/sheet-paper', SheetPaperViewSet, basename='product-sheet-paper')
router.register(r'product/paper', PaperViewSet, basename='product-paper')
router.register(r'product/folding', FoldingViewSet, basename='product-folding')
router.register(r'product/page', PageViewSet, basename='product-page')
router.register(r'report/product', ProductReportViewSet, basename='product-report')


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
    path('', include('user.urls')),
]
