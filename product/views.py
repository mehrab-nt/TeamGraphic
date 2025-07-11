from rest_framework import status, filters
from datetime import datetime, date
from rest_framework.response import Response
from api.permissions import ApiAccess
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, Product
from .serializers import ProductSerializer, ProductCategorySerializer, ProductCategoryBriefSerializer, ProductBriefSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from file_manager.apps import ExcelHandler


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
        '__all__': 'allow_any',
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
                location=OpenApiParameter.QUERY
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
        '__all__': 'allow_any',
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
                location=OpenApiParameter.QUERY
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return ProductCategoryViewSet.create(self, request, *args, **kwargs)
