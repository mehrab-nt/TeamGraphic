from rest_framework import status, filters
from datetime import datetime, date
from rest_framework.response import Response
from api.permissions import ApiAccess
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import CombineBulkDeleteSerializer
from .models import ProductCategory, Product, GalleryCategory, GalleryImage
from .serializers import ProductSerializer, ProductCategorySerializer, ProductCategoryBriefSerializer, ProductBriefSerializer, \
    GalleryCategorySerializer, GalleryImageSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from file_manager.excel_handler import ExcelHandler


@extend_schema(tags=['Products'])
class ProductCategoryViewSet(CustomMixinModelViewSet):
    """
    MEH: Product Category Model viewset
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title']
    ordering_fields = ['parent_category_display', 'sort_number', 'title']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['allow_any'],
    }

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related('gallery', 'image', 'landing')

    @extend_schema(
        description="MEH: Use `parent_id` in query or body to assign a parent_category. If omitted, category will be created at root level.",
        parameters=[
            OpenApiParameter(
                name='parent_id',
                description='ID of the parent_category. If omitted, creates root Category.',
                type=int,
                required=False,
                location='query'
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        parent_id = request.query_params.get('parent_id')
        if not parent_id: # MEH: it can be in body
            parent_id = data.get('parent_id')
        if parent_id in ['', 'None', None]:
            data['parent_category'] = None
        else:
            try:
                parent_category = ProductCategory.objects.get(pk=parent_id)
                data['parent_category'] = parent_category.pk
            except ProductCategory.DoesNotExist:
                return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        return self.custom_create(data, *args, **kwargs)

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
        tags=['Products'],
    )
    @action(detail=False, methods=['get'],
            url_path='explorer')
    def product_explore_view(self, request):
        """
        MEH: Return mixed list of Category `type='CAT'` & Product `type in ['OFF','LAR',...]`
        for parent_id = x or root level parent_id = None
        """
        parent_id = request.query_params.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = ProductCategory.objects.get(pk=parent_id)
            except ProductCategory.DoesNotExist:
                return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        categories = ProductCategory.objects.filter(parent_category=parent).order_by('sort_number', 'title').prefetch_related('sub_categories')
        products = Product.objects.filter(parent_category=parent).order_by('sort_number', 'title')
        category_data = ProductCategoryBriefSerializer(categories, many=True).data
        product_data = ProductBriefSerializer(products, many=True).data
        return Response(category_data + product_data, status=status.HTTP_200_OK)


@extend_schema(tags=['Products'])
class ProductViewSet(CustomMixinModelViewSet):
    """
    MEH: Product Model viewset
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title']
    ordering_fields = ['parent_category_display', 'sort_number', 'title']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['allow_any'],
    }

    @extend_schema(exclude=True) # MEH: Hidden list from Api Documentation (only Admin work)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="MEH: Use `parent_id` in query or body to assign a parent_category. If omitted, Product will be created at root level.",
        parameters=[
            OpenApiParameter(
                name='parent_id',
                description='ID of the parent_category. If omitted, creates Product at root level.',
                type=int,
                required=False,
                location='query'
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return ProductCategoryViewSet.create(self, request, *args, **kwargs)


@extend_schema(tags=['Gallery'])
class GalleryCategoryViewSet(CustomMixinModelViewSet):
    """
    MEH: Gallery Category Model viewset
    """
    queryset = GalleryCategory.objects.all().order_by('sort_number', 'name')
    serializer_class = GalleryCategorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = ['name']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['gallery_manager'],
        **dict.fromkeys(['gallery_explore_view', 'list', 'retrieve'], ['gallery_list', 'gallery_manager'])
    }

    @extend_schema(
        description="MEH: Use `parent_id` in query or body to assign a parent_category. If omitted, Directory will be created at root level.",
        parameters=[
            OpenApiParameter(
                name='parent_id',
                description='ID of the parent_category. If omitted, creates root Directory.',
                type=int,
                required=False,
                location='query'
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        parent_id = request.query_params.get('parent_id')
        if not parent_id: # MEH: it can be in body
            parent_id = request.data.get('parent_id')
        if parent_id in ['', 'None', None]:
            parent_category = None
        else:
            try:
                parent_category = GalleryCategory.objects.get(pk=parent_id)
            except GalleryCategory.DoesNotExist:
                return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        return self.custom_create(request.data, parent_category=parent_category)

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
    def gallery_explore_view(self, request):
        """
        MEH: Return mixed list of Category `type='dir'` and Image Item `type='webp'`
        for parent_id = x or root level parent_id = None
        """
        parent_id = request.query_params.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = GalleryCategory.objects.get(pk=parent_id)
            except GalleryCategory.DoesNotExist:
                return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        categories = GalleryCategory.objects.filter(parent_category=parent).order_by('sort_number', 'name')
        images = GalleryImage.objects.filter(parent_category=parent).order_by('sort_number', 'name')
        cat_data = GalleryCategorySerializer(categories, many=True).data
        img_data = GalleryImageSerializer(images, many=True).data
        return Response(cat_data + img_data, status=status.HTTP_200_OK)

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        img_ids = serializer.validated_data.get('item_ids', [])
        cat_ids = serializer.validated_data.get('layer_ids', [])
        img_qs = GalleryImage.objects.filter(id__in=img_ids)
        cat_qs = GalleryCategory.objects.filter(id__in=cat_ids)
        self.serializer_class = GalleryCategorySerializer # MEH: Just for drf view
        return self.custom_list_destroy([img_qs, cat_qs])


@extend_schema(tags=['Gallery'])
class GalleryImageViewSet(CustomMixinModelViewSet):
    """
    MEH: Gallery Image Model viewset
    """
    queryset = GalleryImage.objects.all().order_by('sort_number', 'name')
    serializer_class = GalleryImageSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = ['name']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['gallery_manager'],
        **dict.fromkeys(['list', 'retrieve'], ['gallery_list', 'gallery_manager'])
    }

    @extend_schema(
        description="MEH: Use `parent_id` in query or body to assign a parent_category. If omitted, Image will be uploaded at root level.",
        parameters=[
            OpenApiParameter(
                name='parent_id',
                description='ID of the parent_category. If omitted, uploaded Image at root level.',
                type=int,
                required=False,
                location='query'
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return GalleryCategoryViewSet.create(self, request, *args, **kwargs)
