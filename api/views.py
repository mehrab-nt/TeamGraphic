from drf_spectacular.utils import extend_schema
from rest_framework import filters
from rest_framework.decorators import action
from .mixins import CustomMixinModelViewSet
from .models import ApiItem, ApiCategory
from .permissions import ApiAccess
from .serializers import AdminApiCategorySerializer, AdminApiItemSerializer
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from .responses import *
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.response import Response


@extend_schema(tags=['Api-Access'])
class ApiCategoryViewSet(ReadOnlyModelViewSet):
    """
    MEH: Api Category Model viewset
    """
    queryset = ApiCategory.objects.all()
    serializer_class = AdminApiCategorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title'] # MEH: Get search query
    ordering_fields = ['sort_number', 'title']
    permission_classes = [ApiAccess]
    required_api_keys = {} # MEH: Empty mean just Admin can Access

    def get_queryset(self):
        qs = super().get_queryset().filter(role_base=False).order_by('sort_number')
        if action == 'api_item_list':
            qs = qs.prefetch_related('api_items')
        return qs

    @action(detail=True, methods=['get'],
            url_path='item-list', serializer_class=AdminApiItemSerializer)
    def api_item_list(self, request, pk=None):
        """
        MEH: Get Api-Category (with pk) Api-Item List (GET/POST ACTION)
        """
        api_category = self.get_object()
        if getattr(api_category, 'api_items', None):
            serializer = self.get_serializer(api_category.api_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotFound


@extend_schema(tags=['Api-Access'])
class ApiItemViewSet(ReadOnlyModelViewSet):
    """
    MEH: Api Item Model viewset
    """
    queryset = (ApiItem.objects.prefetch_related('category')
                .order_by('sort_number'))
    serializer_class = AdminApiItemSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title']  # MEH: Get search query
    ordering_fields = ['sort_number', 'category']
    permission_classes = [ApiAccess]
    required_api_keys = {} # MEH: Empty mean just Admin can Access
