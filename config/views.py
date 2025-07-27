from drf_spectacular.utils import extend_schema
from api.mixins import CustomMixinModelViewSet
from api.permissions import ApiAccess
from .models import PriceListConfig
from .serializers import PriceListConfigSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.response import Response
from api.responses import *


@extend_schema(tags=['Price-List'])
class PriceListConfigViewSet(CustomMixinModelViewSet):
    """
    MEH: Price List Config Model viewset
    """
    queryset = PriceListConfig.objects.all()
    serializer_class = PriceListConfigSerializer
    http_method_names = ['head', 'option']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': [], # MEH: Only admin access if any
        'config_info': ['price_list_manager'],
        'generate_auto_pdf': ['price_list_generate_pdf']
    }

    @action(detail=False, methods=['get', 'put', 'patch'], http_method_names=['get', 'put', 'patch'],
            url_path='info')
    def config_info(self, request):
        obj = PriceListConfig.objects.first() # MEH: Only first obj (it's most contain only 1 obj anyway)
        if not obj:
            raise NotFound(TG_DATA_NOT_FOUND)
        if request.method in ['PUT', 'PATCH']:
            return self.custom_update(obj, request, partial=(request.method == 'PATCH'))
        return self.custom_get(obj)

    @action(detail=False, methods=['get'], http_method_names=['get'],
            url_path='generate-pdf')
    def generate_auto_pdf(self, request):
        # MEH todo: generate new pdf list from price_list_category (and set last_update_pdf)
        return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)
