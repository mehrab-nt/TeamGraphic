from .models import Province, City
from .serializers import ProvinceSerializer, CitySerializer
from drf_spectacular.utils import extend_schema
from api.mixins import CustomMixinModelViewSet
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CustomerFilter


@extend_schema(tags=['Province'])
class ProvinceViewSet(CustomMixinModelViewSet):
    """
    MEH: Province Model viewset
    """
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 50
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ['name']
    http_method_names = ['get', 'head', 'options']
    cache_key = 'province'

    def list(self, request, *args, **kwargs): # MEH: for set time out to 1 year (always!)
        return super().list(request, timeout=60 * 60 * 24 * 365)


@extend_schema(tags=['Province'])
class CityViewSet(CustomMixinModelViewSet):
    """
    MEH: City Model viewset
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 200
    filterset_class = CustomerFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = ['name']
    http_method_names = ['get', 'head', 'options']
    cache_key = 'city'

    def list(self, request, *args, **kwargs): # MEH: for set time out to 1 year (always!)
        return super().list(request, timeout=60 * 60 * 24 * 365)