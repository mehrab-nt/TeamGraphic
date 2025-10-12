from .models import Province
from .serializers import ProvinceSerializer
from drf_spectacular.utils import extend_schema
from api.mixins import CustomMixinModelViewSet
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination


@extend_schema(tags=['Province'])
class ProvinceViewSet(CustomMixinModelViewSet):
    """
    MEH: Department Model viewset
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
