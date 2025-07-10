from rest_framework import status, filters
from datetime import datetime, date
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from api.permissions import ApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, Product
from api.models import ApiCategory
from django.db.models import Subquery, OuterRef, Count, Prefetch
from .serializers import ProductCategorySerializer, ProductCategoryBriefSerializer, ProductBriefSerializer
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
# from .filters import CustomerFilter
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkDeleteSerializer, ApiCategorySerializer
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
    required_api_keys = {}

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset().select_related('gallery', 'landing')
        return qs

    @extend_schema(
        description="MEH: Use `parent_id` in query or body to assign a parent_category. If omitted, category will be created at root level.",
        parameters=[
            OpenApiParameter(
                name='parent_id',
                description='ID of the parent_category. If omitted, creates root category.',
                type=int,
                required=False,
                location=OpenApiParameter.QUERY
            ),
        ]
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
        parameters=[
            OpenApiParameter(name='parent_id', type=int, required=False, description='ID of the parent category')
        ],
        tags=['Products'],
    )
    @action(detail=False, methods=['get'],
            url_path='explorer')
    def product_explore_view(self, request):
        """
        MEH: Return mixed list of category (list_type=category) and product (list_type=product)
        for (parent_id = x) or root level (parent_category = None)
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
