from rest_framework import filters
from api.permissions import ApiAccess
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductReportFilter
from .serializers import ProductReportSerializer, CounterReportSerializer, MonthlySaleReportSerializer, \
    NotifReportSerializer
from product.models import Product
from drf_spectacular.utils import extend_schema
from api.mixins import CustomMixinModelViewSet
from .models import CounterReport, MonthlySaleReport

@extend_schema(tags=['Report'])
class ProductReportViewSet(CustomMixinModelViewSet):
    """
    MEH: Report Product sale Viewset (READ-Only)
    """
    queryset = Product.objects.select_related('parent_category')
    serializer_class = ProductReportSerializer
    http_method_names = ['get', 'head', 'options']
    filterset_class = ProductReportFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title', 'parent_category__title']
    ordering_fields = ['total_order', 'last_order', 'total_main_sale', 'total_option_sale']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['allow_any']
    }


@extend_schema(tags=['Report'])
class CounterReportViewSet(CustomMixinModelViewSet):
    """
    MEH: Counter Report Viewset (READ-Only)
    """
    queryset = CounterReport.objects.all()
    serializer_class = CounterReportSerializer
    http_method_names = ['get', 'head', 'options']
    permission_classes = [ApiAccess]
    pagination_class = None
    required_api_keys = {
        '__all__': ['allow_any']
    }


@extend_schema(tags=['Report'])
class MonthlySaleReportViewSet(CustomMixinModelViewSet):
    """
    MEH: Counter Report Viewset (READ-Only)
    """
    queryset = MonthlySaleReport.objects.all()
    serializer_class = MonthlySaleReportSerializer
    http_method_names = ['get', 'head', 'options']
    permission_classes = [ApiAccess]
    pagination_class = None
    required_api_keys = {
        '__all__': ['allow_any']
    }


@extend_schema(tags=['Report'])
class NotifReportViewSet(CustomMixinModelViewSet):
    """
    MEH: Notif Report Viewset (READ-Only)
    """
    queryset = NotifReport.objects.all()
    serializer_class = NotifReportSerializer
    http_method_names = ['get', 'head', 'options']
    permission_classes = [ApiAccess]
    pagination_class = None
    required_api_keys = {
        '__all__': ['allow_any']
    }