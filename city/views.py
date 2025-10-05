from .models import Province
from .serializers import ProvinceSerializer
from drf_spectacular.utils import extend_schema
from api.mixins import CustomMixinModelViewSet


@extend_schema(tags=['Province'])
class ProvinceViewSet(CustomMixinModelViewSet):
    """
    MEH: Department Model viewset
    """
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    pagination_class = None
    http_method_names = ['get', 'head', 'options']
    cache_key = 'province'

    def list(self, request, *args, **kwargs): # MEH: for set time out to 1 year (always!)
        return super().list(request, timeout=60 * 60 * 24 * 365)
