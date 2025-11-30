from celery.concurrency import custom
from rest_framework import status, filters
from rest_framework.response import Response
from api.permissions import ApiAccess
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import CombineBulkDeleteSerializer, CombineBulkUpdateActivateSerializer, \
    CombineBulkUpdateProductStatusSerializer, CopyWithIdSerializer
from .models import ProductCategory, Product, GalleryCategory, GalleryImage, ProductFileField, \
    Size, SheetPaper, Paper, Tirage, Duration, Banner, Color, Page, Folding, \
    Design, OffsetProduct, LargeFormatProduct, SolidProduct, DigitalProduct, Option, OptionCategory, ProductOption, \
    PriceListCategory, PriceListTable
from .services.category_clone import clone_category_tree
from .serializers import (ProductCategorySerializer, ProductCategoryBriefSerializer, ProductBriefSerializer, \
                          GalleryCategorySerializer, GalleryImageSerializer, GalleryCategoryBriefSerializer,
                          GalleryImageBriefSerializer, GalleryDropDownSerializer, ProductGallerySerializer, \
                          ProductInfoSerializer, OffsetProductSerializer, LargeFormatProductSerializer,
                          SolidProductSerializer, DigitalProductSerializer, \
                          SizeSerializer, SheetPaperSerializer, PaperSerializer, TirageSerializer, DurationSerializer, \
                          BannerSerializer, ColorSerializer, FoldingSerializer, PageSerializer, \
                          FileFieldSerializer, ProductFileSerializer, FileFieldBriefSerializer,
                          FileFieldDropDownSerializer, \
                          DesignSerializer, ProductDesignSerializer, DesignBriefSerializer, DesignDropDownSerializer, \
                          OptionCategorySerializer, OptionSerializer, ProductOptionSerializer,
                          OptionCategoryBriefSerializer, OptionBriefSerializer, \
                          OptionCategorySelectListSerializer, OptionProductListSerializer, \
                          ProductManualPriceSerializer, ProductFormulaPriceSerializer, ProductInCategorySerializer, \
                          PriceListCategorySerializer, PriceListTableSerializer, PriceListCategoryBriefSerializer,
                          PriceListTableBriefSerializer, ProductCategoryTreeSerializer, GalleryCategoryTreeSerializer)
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from file_manager.excel_handler import ExcelHandler
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from copy import deepcopy
from django.db.models import ManyToManyField
from django.utils import timezone
from django.db import transaction


@extend_schema(tags=['Product-Category'])
class ProductCategoryViewSet(CustomMixinModelViewSet):
    """
    MEH: Product Category Model viewset
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title']
    ordering_fields = ['parent_category_display', 'sort_number', 'title']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['product_manager', 'create_product'],
        'product_list': ['product_manager', 'price_list_manager', 'create_product']
    }

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        if self.action == 'product_list':
            return qs
        return qs.select_related('gallery', 'image', 'landing')

    @extend_schema(exclude=True) # MEH: Hidden list from Api Documentation (only Admin work)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'], pagination_class=None,
            serializer_class=ProductCategoryTreeSerializer)
    def tree(self, request):
        # Get only root categories
        roots = ProductCategory.objects.root_nodes()
        return self.custom_get(roots)

    @extend_schema(
        summary='Tree list of Both Product & Category',
        parameters=[
            OpenApiParameter(
                name='parent_id',
                type=int,
                required=False,
                description='ID of the parent category'
            ),
        ],
    )
    @action(detail=False, methods=['get'],
            url_path='explorer')
    def product_explore_view(self, request):
        """
        MEH: Return mixed list of Category `type='CAT'` & Product `type in ['OFF','LAR',...]`
        for parent_id = x or root level parent_id = None
        """
        return self.get_explorer_list(request=request, category_model=ProductCategory, item_model=Product,
                                      category_serializer=ProductCategoryBriefSerializer,
                                      item_serializer=ProductBriefSerializer,
                                      filter_backends=self.filter_backends)

    @extend_schema(
        summary='Delete list of Categories & Products',
        request=CombineBulkDeleteSerializer,
        responses={
            200: OpenApiResponse(description="Successfully deleted Categories & Products."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkDeleteSerializer,
            url_path='bulk-delete', filter_backends=[None])
    def bulk_delete(self, request):
        """
        MEH: Delete List of Category & Product Item Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, cat_qs = self.explorer_bulk_queryset(request, ProductCategory, Product)
        parents = {cat.parent_category for cat in cat_qs if cat.parent_category}
        response = self.custom_list_destroy([itm_qs, cat_qs])
        ProductCategory.objects.rebuild()
        return response

    @extend_schema(
        summary='Change Status list of Categories & Products',
        request=CombineBulkUpdateProductStatusSerializer,
        responses={
            200: OpenApiResponse(description="Successfully Change status in Categories & Products."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkUpdateProductStatusSerializer,
            url_path='bulk-update-status', filter_backends=[None])
    def bulk_update_status(self, request):
        """
        MEH: Change status field in List of Category & Product Item Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, cat_qs = self.explorer_bulk_queryset(request, ProductCategory, Product)
        update_field = self.explorer_bulk_update_fields(request, field_name='status')
        return self.custom_list_update([itm_qs, cat_qs], update_field, update_sub=True)

    @action(detail=False, methods=['post'], serializer_class=CopyWithIdSerializer,
            url_path='copy', filter_backends=[None])
    def copy_category(self, request):
        """
        MEH: Copy a Product Category & Create all detail except M2M child cat & product! (use POST ACTION for sending id in request body)
        """
        validated_data = self.get_validate_data(request.data)
        category_id = validated_data.get('id', None)
        try:
            original_category = ProductCategory.objects.get(pk=category_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        # category_copy = deepcopy(original_category)
        # category_copy.pk = None
        # category_copy.title += " (copy)"
        # category_copy.save()
        new_root = clone_category_tree(original_category, parent_copy=original_category.parent_category)
        return Response({"detail": TG_DATA_COPIED}, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Get list of Product in Category")
    @action(detail=True, methods=['get'], serializer_class=ProductInCategorySerializer,
            url_path='product-list', filter_backends=[None])
    def product_list(self, request, pk=None):
        """
        MEH: Product List in category until last child (for price table)
        """
        category = self.get_object(pk=pk)
        all_category_ids = category.get_descendants(include_self=True).values_list('id', flat=True)
        products = Product.objects.filter(parent_category_id__in=all_category_ids).select_related('parent_category').order_by('type')
        return self.custom_get(products)


@extend_schema(tags=['Product-Item'])
class ProductViewSet(CustomMixinModelViewSet):
    """
    MEH: Product Model viewset
    """
    queryset = Product.objects.all()
    serializer_class = ProductInfoSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title']
    ordering_fields = ['parent_category_display', 'sort_number', 'title']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['product_manager', 'create_product'],
        **dict.fromkeys(['create', 'copy_product'], ['create_product'])
    }

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return qs.select_related('image', 'template', 'parent_category').order_by('sort_number', 'parent_category')
        if self.action == 'designs':
            return qs.prefetch_related('designs', 'designs__category', 'designs__image')
        if self.action == 'gallery':
            return qs.select_related('gallery')
        if self.action == 'files':
            return qs.prefetch_related('files')
        return qs

    @extend_schema(exclude=True) # MEH: Hidden list from Api Documentation (only Admin work)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Page 2 of Product Edit (Offset)")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=OffsetProductSerializer,
            url_path='offset', filter_backends=[None])
    def offset_product_detail(self, request, pk=None):
        """
        MEH: Product Fields
        Page 2 of Product Edit (Offset)
        """
        try:
            offset_product = OffsetProduct.objects.prefetch_related('size_list', 'tirage_list', 'page_list',
                                                                    'folding_list', 'duration_list').get(product_info__pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(offset_product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(offset_product)

    @extend_schema(summary="Page 2 of Product Edit (LargeFormat)")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=LargeFormatProductSerializer,
            url_path='large-format', filter_backends=[None])
    def large_format_product_detail(self, request, pk=None):
        """
        MEH: Product Fields
        Page 2 of Product Edit (LargeFormat)
        """
        try:
            large_format_product = LargeFormatProduct.objects.prefetch_related('banner_list').get(product_info__pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(large_format_product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(large_format_product)

    @extend_schema(summary="Page 2 of Product Edit (Solid-Product)")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=SolidProductSerializer,
            url_path='solid', filter_backends=[None])
    def solid_product_detail(self, request, pk=None):
        """
        MEH: Product Fields
        Page 2 of Product Edit (Solid-Product)
        """
        try:
            solid_product = SolidProduct.objects.prefetch_related('color_list').get(product_info__pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(solid_product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(solid_product)

    @extend_schema(summary="Page 2 of Product Edit (Digital)")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=DigitalProductSerializer,
            url_path='digital', filter_backends=[None])
    def digital_product_detail(self, request, pk=None):
        """
        MEH: Product Fields
        Page 2 of Product Edit (Digital)
        """
        try:
            digital_product = DigitalProduct.objects.prefetch_related('size_list', 'paper_list',
                                                                      'paper_list__size', 'paper_list__sheet_paper',
                                                                      'cover_paper_list', 'cover_paper_list__size',
                                                                      'cover_paper_list__sheet_paper',
                                                                      'folding_list').get(product_info__pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(digital_product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(digital_product)

    @extend_schema(summary="Page 3 of Product Edit")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=ProductGallerySerializer,
            url_path='gallery', filter_backends=[None])
    def gallery_field(self, request, pk=None):
        """
        MEH: Product Gallery
        Page 3 of Product Edit
        """
        product = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(product)

    @extend_schema(summary="Page 4 of Product Edit")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=ProductDesignSerializer,
            url_path='designs', filter_backends=[None])
    def designs_field(self, request, pk=None):
        """
        MEH: Product Design List
        Page 4 of Product Edit
        """
        product = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(product)

    @extend_schema(summary="Page 5 of Product Edit")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=ProductFileSerializer,
            url_path='files', filter_backends=[None])
    def files_field(self, request, pk=None):
        """
        MEH: Product File List
        Page 5 of Product Edit
        """
        product = self.get_object(pk=pk)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(product)

    @extend_schema(summary="Page 6 of Product Edit")
    @action(detail=True, methods=['get', 'post'], serializer_class=ProductOptionSerializer,
            url_path='options', filter_backends=[None])
    def option_field_list(self, request, pk=None):
        """
        MEH: Product Option List
        Page 6 of Product Edit
        """
        product = self.get_object(pk=pk)
        if request.method == 'POST':
            with transaction.atomic():
                if not isinstance(request.data, list):
                    return Response({'detail': TG_DATA_MOST_LIST}, status=status.HTTP_400_BAD_REQUEST)
                incoming_options = self.get_validate_data(request.data, many=True)
                dependency_map = {}
                for opt_data in incoming_options:
                    opt_id = opt_data['option'].id
                    deps = [dep.id for dep in opt_data.get('dependent_option', [])]
                    dependency_map[opt_id] = deps
                if ProductOption.detect_cycle(dependency_map): # MEH: Detect cycles
                    return Response({'detail': TG_PREVENT_CIRCULAR_CATEGORY}, status=status.HTTP_400_BAD_REQUEST)
                incoming_option_ids = [opt['option'].id for opt in incoming_options] # MEH: Now work on DB with clean data
                existing_options = product.option_list.select_related('option').prefetch_related('dependent_option')
                existing_options.exclude(option_id__in=incoming_option_ids).delete() # MEH: Delete old options not in list
                valid_option_ids = set(existing_options.values_list("option__id", flat=True)) # MEH: for Ignore unrelated option_id in sending list
                for option_data in incoming_options: # MEH: Upsert
                    deps = option_data.pop('dependent_option', [])
                    option = option_data['option']
                    product_option, _ = ProductOption.objects.update_or_create( # MEH: Update if exists, else create
                        product=product,
                        option=option,
                        defaults=option_data
                    )
                    option_specific_valid_ids = valid_option_ids - {option.id} # MEH: Drop option id itself
                    valid_dependent_ids = [oid.id for oid in deps if oid.id in option_specific_valid_ids]
                    product_option.dependent_option.set(valid_dependent_ids) # MEH: Set M2M dependent_option field
                return Response({'detail': TG_DATA_UPDATED}, status=status.HTTP_200_OK)
        option_list = product.option_list.select_related('option').prefetch_related('dependent_option')
        return self.custom_get(option_list)

    @extend_schema(summary="Page 7 of Product Edit (Offset)")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=ProductManualPriceSerializer,
            url_path='manual_price', filter_backends=[None])
    def manual_price(self, request, pk=None):
        """
        MEH: Product Manual Price List (Offset)
        Page 7 of Product Edit
        """
        try:
            offset_product = OffsetProduct.objects.get(product_info__pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(offset_product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(offset_product)

    @extend_schema(summary="Page 7 of Product Edit (Digital)")
    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=ProductFormulaPriceSerializer,
            url_path='formula_price', filter_backends=[None])
    def formula_price(self, request, pk=None):
        """
        MEH: Product Manual Price List (Digital)
        Page 7 of Product Edit
        """
        try:
            digital_product = DigitalProduct.objects.get(product_info__pk=pk)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(digital_product, request, partial=(request.method == 'PATCH'))
        return self.custom_get(digital_product)

    @action(detail=False, methods=['post'], serializer_class=CopyWithIdSerializer,
            url_path='copy', filter_backends=[None])
    def copy_product(self, request):
        """
        MEH: Copy a Product Object & Create all detail (use POST ACTION for sending id in request body)
        """
        validated_data = self.get_validate_data(request.data)
        product_id = validated_data.get('id', None)
        try:
            original_product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        product_copy = deepcopy(original_product)
        product_copy.pk = None
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        product_copy.title = f"{original_product.title} (copy: {timestamp})"
        product_copy.save()
        for field in original_product._meta.get_fields():
            if isinstance(field, ManyToManyField) and not field.auto_created:
                value = getattr(original_product, field.name).all()
                getattr(product_copy, field.name).set(value)
        related_info_model = {
            'OFF': 'offset_info',
            'LAR': 'large_format_info',
            'SLD': 'solid_info',
            'DIG': 'digital_info',
        }.get(original_product.type)
        if not related_info_model:
            product_copy.delete()
            return Response({"detail": "Invalid product type"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            original_data = getattr(original_product, related_info_model)
        except ObjectDoesNotExist:
            product_copy.delete()
            return Response({"detail": "Related product info not found"}, status=status.HTTP_404_NOT_FOUND)
        data_copy = deepcopy(original_data)
        data_copy.pk = None
        data_copy.product_info = product_copy
        data_copy.save()
        for field in original_data._meta.get_fields():
            if isinstance(field, ManyToManyField) and not field.auto_created:
                value = getattr(original_data, field.name).all()
                getattr(data_copy, field.name).set(value)
        return Response({"detail": TG_DATA_COPIED}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Gallery'])
class GalleryCategoryViewSet(CustomMixinModelViewSet):
    """
    MEH: Gallery Category Model viewset
    """
    queryset = GalleryCategory.objects.all().order_by('sort_number', 'name')
    serializer_class = GalleryCategorySerializer
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['name']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['gallery_manager'],
        **dict.fromkeys(['gallery_explore_view', 'list', 'retrieve'], ['gallery_list', 'gallery_manager']),
        'drop_down_list': ['product_manager', 'create_product', 'gallery_list', 'gallery_manager']
    }

    @action(detail=False, methods=['get'], pagination_class=None,
            serializer_class=GalleryCategoryTreeSerializer)
    def tree(self, request):
        # Get only root categories
        roots = GalleryCategory.objects.root_nodes()
        return self.custom_get(roots)

    @extend_schema(
        summary='Tree list of Both Categories & Images',
        parameters=[
            OpenApiParameter(
                name='parent_id',
                type=int,
                required=False,
                description='ID of the parent Category'
            ),
        ],
    )
    @action(detail=False, methods=['get'],
            url_path='explorer')
    def gallery_explore_view(self, request):
        """
        MEH: Return mixed list of Category `type='dir'` and Image Item `type='webp'`
        for parent_id = x or root level parent_id = None
        """
        return self.get_explorer_list(request=request, category_model=GalleryCategory, item_model=GalleryImage,
                                      category_serializer=GalleryCategoryBriefSerializer,
                                      item_serializer=GalleryImageBriefSerializer,
                                      filter_backends=self.filter_backends ,paginate=True)

    @extend_schema(
        summary='Delete list of Categories & Images',
        request=CombineBulkDeleteSerializer,
        responses={
            200: OpenApiResponse(description="Successfully deleted Categories & Images."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkDeleteSerializer,
            url_path='bulk-delete', filter_backends=[None])
    def bulk_delete(self, request):
        """
        MEH: Delete List of Category & Image Item Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, cat_qs = self.explorer_bulk_queryset(request, GalleryCategory, GalleryImage)
        return self.custom_list_destroy([itm_qs, cat_qs])

    @extend_schema(summary='for DropDown List')
    @action(detail=False, methods=['get'], serializer_class=GalleryDropDownSerializer,
            url_path='list', filter_backends=[None])
    def drop_down_list(self, request):
        """
        MEH: Tree-based List of Gallery Category (id & name with tree based title)
        """
        category_list = self.get_queryset().model.objects.order_by('tree_id', 'lft')
        return self.custom_get(category_list)


@extend_schema(tags=['Gallery'])
class GalleryImageViewSet(CustomMixinModelViewSet):
    """
    MEH: Gallery Image Model viewset
    """
    queryset = GalleryImage.objects.select_related('parent_category').order_by('sort_number', 'name')
    serializer_class = GalleryImageSerializer
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['name']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['gallery_manager'],
        **dict.fromkeys(['list', 'retrieve'], ['gallery_list', 'gallery_manager'])
    }


@extend_schema(tags=['Product-Fields'])
class FileFieldViewSet(CustomMixinModelViewSet):
    """
    MEH: File Field Model viewset
    """
    queryset = ProductFileField.objects.all()
    serializer_class = FileFieldSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title']
    ordering_fields = ['sort_number', 'title']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['field_manager'],
        'drop_down_list': ['product_manager', 'create_product', 'field_manager']
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return FileFieldBriefSerializer
        return super().get_serializer_class()

    @extend_schema(summary='for DropDown List')
    @action(detail=False, methods=['get'], serializer_class=FileFieldDropDownSerializer,
            url_path='list', filter_backends=[None])
    def drop_down_list(self, request):
        """
        MEH: List of File Field (id & title)
        """
        file_field_list = self.get_queryset()
        return self.custom_get(file_field_list)


@extend_schema(tags=['Design'])
class DesignViewSet(CustomMixinModelViewSet):
    """
    MEH: Design Model viewset
    """
    queryset = Design.objects.select_related('image').prefetch_related('category')
    serializer_class = DesignSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title', 'category__title']
    ordering_fields = ['sort_number', 'title']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['design_manager'],
        'drop_down_list': ['product_manager', 'create_product', 'design_manager']
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return DesignBriefSerializer
        return super().get_serializer_class()

    @extend_schema(
        summary='for DropDown List',
        parameters=[
            OpenApiParameter(
                name='category_id',
                description='Used for filter related Design to product category',
                required=False,
                type=int,
                location='query',
            )
        ]
    )
    @action(detail=False, methods=['get'], serializer_class=DesignDropDownSerializer,
            url_path='list', filter_backends=[None])
    def drop_down_list(self, request):
        """
        MEH: List of Design (id & title)
        """
        category_id = request.query_params.get('category_id')
        if category_id:
            try:
                category_filter = ProductCategory.objects.get(id=category_id)
            except ObjectDoesNotExist:
                raise NotFound(TG_DATA_EMPTY)
            return self.custom_get(category_filter.design_list)
        design_list = self.get_queryset()
        return self.custom_get(design_list)


@extend_schema(tags=['Product-Fields'])
class TirageViewSet(CustomMixinModelViewSet):
    """
    MEH: Tirage Model viewset
    """
    queryset = Tirage.objects.all()
    serializer_class = TirageSerializer
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['field_manager'],
        'list': ['product_manager', 'create_product', 'field_manager']
    }


@extend_schema(tags=['Product-Fields'])
class SizeViewSet(TirageViewSet):
    """
    MEH: Size Model viewset
    """
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'display_name']
    ordering_fields = ['display_name']


@extend_schema(tags=['Product-Fields'])
class PageViewSet(TirageViewSet):
    """
    MEH: Page Model viewset
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer


@extend_schema(tags=['Product-Fields'])
class DurationViewSet(TirageViewSet):
    """
    MEH: Duration Model viewset
    """
    queryset = Duration.objects.all()
    serializer_class = DurationSerializer


@extend_schema(tags=['Product-Fields'])
class BannerViewSet(TirageViewSet):
    """
    MEH: Banner Model viewset
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    filter_backends = [
        filters.OrderingFilter
    ]
    ordering_fields = ['width', 'title', 'is_active']


@extend_schema(tags=['Product-Fields'])
class ColorViewSet(TirageViewSet):
    """
    MEH: Color Model viewset
    """
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


@extend_schema(tags=['Product-Fields'])
class SheetPaperViewSet(TirageViewSet):
    """
    MEH: Sheet Paper Model viewset
    """
    queryset = SheetPaper.objects.all()
    serializer_class = SheetPaperSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['material', 'display_name']
    ordering_fields = ['inventory']
    required_api_keys = {
        '__all__': ['field_manager']
    }


@extend_schema(tags=['Product-Fields'])
class PaperViewSet(TirageViewSet):
    """
    MEH: Paper Model viewset
    """
    queryset = Paper.objects.select_related('size', 'sheet_paper')
    serializer_class = PaperSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['size__display_name', 'sheet_paper__display_name']
    ordering_fields = ['inventory', 'per_paper_price']


@extend_schema(tags=['Product-Fields'])
class FoldingViewSet(TirageViewSet):
    """
    MEH: Folding Model viewset
    """
    queryset = Folding.objects.all()
    serializer_class = FoldingSerializer


@extend_schema(tags=['Option'])
class OptionCategoryViewSet(CustomMixinModelViewSet):
    """
    MEH: Option Model viewset
    """
    queryset = OptionCategory.objects.all().order_by('sort_number')
    serializer_class = OptionCategorySerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['option_manager'],
        'create': ['create_option'],
        **dict.fromkeys(['bulk_delete', 'destroy'], ['delete_option'])
    }

    @extend_schema(
        summary='Tree list of Both Categories & Images',
        parameters=[
            OpenApiParameter(
                name='parent_id',
                type=int,
                required=False,
                description='ID of the parent Category'
            ),
        ],
    )
    @action(detail=False, methods=['get'],
            url_path='explorer', filter_backends=[None])
    def option_explore_view(self, request):
        """
        MEH: Return mixed list of Option Category `type='dir'` and Option Item `type='opt'`
        for parent_id = x or root level parent_id = None
        """
        return self.get_explorer_list(request=request, category_model=OptionCategory, item_model=Option,
                                      category_serializer=OptionCategoryBriefSerializer, item_serializer=OptionBriefSerializer)

    @extend_schema(
        summary='Delete list of Categories & Options',
        request=CombineBulkDeleteSerializer,
        responses={
            200: OpenApiResponse(description="Successfully deleted Categories & Options."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkDeleteSerializer,
            url_path='bulk-delete', filter_backends=[None])
    def bulk_delete(self, request):
        """
        MEH: Delete List of Category & Option Item Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, cat_qs = self.explorer_bulk_queryset(request, OptionCategory, Option)
        return self.custom_list_destroy([itm_qs, cat_qs])

    @extend_schema(
        summary='Change Activation list of Categories & Options',
        request=CombineBulkUpdateActivateSerializer,
        responses={
            200: OpenApiResponse(description="Successfully Change is_active in Categories & Options."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkUpdateActivateSerializer,
            url_path='bulk-update-activation', filter_backends=[None])
    def bulk_update_is_active(self, request):
        """
        MEH: Change is_active field in List of Category & Option Item Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, cat_qs = self.explorer_bulk_queryset(request, OptionCategory, Option)
        update_field = self.explorer_bulk_update_fields(request, field_name='is_active')
        return self.custom_list_update([itm_qs, cat_qs], update_field, update_sub=True)

    @action(detail=False, methods=['get'], serializer_class=OptionCategorySelectListSerializer,
            url_path='select-list', filter_backends=[None])
    def product_option_select(self, request):
        """
        MEH: Tree-based OptionCategory list with active Option under each category for select
        in Page 6 of Product Edit
        """
        root_category_list = self.get_queryset().filter(parent_category__isnull=True).prefetch_related('sub_categories', 'option_list')
        return self.custom_get(root_category_list)


@extend_schema(tags=['Option'])
class OptionViewSet(CustomMixinModelViewSet):
    """
    MEH: Gallery Image Model viewset
    """
    queryset = Option.objects.select_related('parent_category').order_by('parent_category', 'sort_number')
    serializer_class = OptionSerializer
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['title']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['option_manager'],
        'create': ['create_option'],
        'destroy': ['delete_option'],
        'copy_option': ['copy_option'],
        'product_option_select': ['product_manager', 'create_product', 'option_manager']
    }

    @action(detail=False, methods=['post'], serializer_class=CopyWithIdSerializer,
            url_path='copy', filter_backends=[None])
    def copy_option(self, request):
        """
        MEH: Copy an Option Object & Create (use POST ACTION for sending id in request body)
        """
        validated_data = self.get_validate_data(request.data)
        option_id = validated_data.get('id', None)
        try:
            original_option = Option.objects.get(pk=option_id)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        option_copy = original_option
        option_copy.pk = None
        option_copy.title += ' (Copy)'
        option_copy.save()
        return Response({"detail": TG_DATA_COPIED}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], serializer_class=OptionProductListSerializer,
            url_path='related-product', filter_backends=[None])
    def option_related_product(self, request, pk=None):
        """
        MEH: Full list of related Product to Option
        """
        option = self.get_object(pk=pk)
        return self.custom_get(option.product_list)


@extend_schema(tags=['Price-List'])
class PriceListCategoryViewSet(CustomMixinModelViewSet):
    """
    MEH: Price List Category Model viewset
    """
    queryset = PriceListCategory.objects.all().order_by('sort_number')
    serializer_class = PriceListCategorySerializer
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['title']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['price_list_manager']
    }

    @extend_schema(
        summary='Tree list of Both Categories & Tables',
        parameters=[
            OpenApiParameter(
                name='parent_id',
                type=int,
                required=False,
                description='ID of the parent Category'
            ),
        ],
    )
    @action(detail=False, methods=['get'],
            url_path='explorer', filter_backends=[None])
    def table_explore_view(self, request):
        """
        MEH: Return mixed list of Price List Category `type='dir'` and Option Item `type='OFF/LAR/...'`
        for parent_id = x or root level parent_id = None
        """
        return self.get_explorer_list(request=request, category_model=PriceListCategory, item_model=PriceListTable,
                                      category_serializer=PriceListCategoryBriefSerializer, item_serializer=PriceListTableBriefSerializer,
                                      item_filter_field='price_list_categories')

    @extend_schema(
        summary='Delete list of Categories & Tables',
        request=CombineBulkDeleteSerializer,
        responses={
            200: OpenApiResponse(description="Successfully deleted Categories & Tables."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkDeleteSerializer,
            url_path='bulk-delete', filter_backends=[None])
    def bulk_delete(self, request):
        """
        MEH: Delete List of Category & Option Item Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, cat_qs = self.explorer_bulk_queryset(request, PriceListCategory, PriceListTable)
        return self.custom_list_destroy([itm_qs, cat_qs])

    @extend_schema(
        summary='Change Activation list of Categories & Options',
        request=CombineBulkUpdateActivateSerializer,
        responses={
            200: OpenApiResponse(description="Successfully Change is_active in Categories & Options."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkUpdateActivateSerializer,
            url_path='bulk-update-activation', filter_backends=[None])
    def bulk_update_is_active(self, request):
        """
        MEH: Change is_active field in List of Category & Table Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, cat_qs = self.explorer_bulk_queryset(request, PriceListCategory, PriceListTable)
        update_field = self.explorer_bulk_update_fields(request, field_name='is_active')
        return self.custom_list_update([itm_qs, cat_qs], update_field, update_sub=True)


@extend_schema(tags=['Price-List'])
class PriceListTableViewSet(CustomMixinModelViewSet):
    """
    MEH: Price List Table Model viewset
    """
    queryset = PriceListTable.objects.select_related('product_category').prefetch_related('price_list_categories').order_by('sort_number')
    serializer_class = PriceListTableSerializer
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['title']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['price_list_manager']
    }
