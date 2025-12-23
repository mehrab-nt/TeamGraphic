from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductCategoryViewSet, GalleryCategoryViewSet, GalleryImageViewSet, \
    DesignViewSet, FileFieldViewSet, SizeViewSet, DurationViewSet, \
    SheetPaperViewSet, PaperViewSet, ColorViewSet, FoldingViewSet, BannerViewSet, \
    OptionCategoryViewSet, OptionViewSet, PriceListCategoryViewSet, PriceListTableViewSet

router = DefaultRouter()
router.register(r'gallery/category', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery/image', GalleryImageViewSet, basename='gallery-image')
router.register(r'design', DesignViewSet, basename='design')
router.register(r'product/category', ProductCategoryViewSet, basename='product-category')
router.register(r'product/item', ProductViewSet, basename='product-item')
router.register(r'option/category', OptionCategoryViewSet, basename='option-category')
router.register(r'option/item', OptionViewSet, basename='option-item')
router.register(r'product/file-field', FileFieldViewSet, basename='product-file-field')
router.register(r'product/size', SizeViewSet, basename='product-size')
router.register(r'product/duration', DurationViewSet, basename='product-duration')
router.register(r'product/banner', BannerViewSet, basename='product-banner')
router.register(r'product/color', ColorViewSet, basename='product-color')
router.register(r'product/sheet-paper', SheetPaperViewSet, basename='product-sheet-paper')
router.register(r'product/paper', PaperViewSet, basename='product-paper')
router.register(r'product/folding', FoldingViewSet, basename='product-folding')
router.register(r'price-list/category', PriceListCategoryViewSet, basename='price-list-category')
router.register(r'price-list/table', PriceListTableViewSet, basename='price-list-table')
