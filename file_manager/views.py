from rest_framework import filters
from rest_framework.response import Response
from api.permissions import ApiAccess
from rest_framework.decorators import action
from .filters import TypeFilter
from .models import FileDirectory, FileItem, ClearFileHistory
from .serializers import FileDirectorySerializer, FileItemSerializer, ClearFileSerializer, FileDirectoryTreeSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from api.mixins import CustomMixinModelViewSet
from api.serializers import CombineBulkDeleteSerializer
from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend


@extend_schema(tags=['File-Manager'])
class FileDirectoryViewSet(CustomMixinModelViewSet):
    """
    MEH: File Directory Model viewset
    """
    queryset = FileDirectory.objects.all().order_by('-create_date')
    serializer_class = FileDirectorySerializer
    http_method_names = ['get', 'head', 'option', 'post', 'delete']
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['name']
    ordering_fields = ['create_date', 'name']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['file_manager'],
       'retrieve': [] # MEH: Admin User
    }

    @action(detail=False, methods=['get'], pagination_class=None,
            serializer_class=FileDirectoryTreeSerializer)
    def tree(self, request):
        # Get only root categories
        roots = FileDirectory.objects.root_nodes()
        return self.custom_get(roots)

    @extend_schema(
        summary='Tree list of Both Directories & Files',
        parameters=[
            OpenApiParameter(
                name='parent_id',
                type=int,
                required=False,
                description='ID of the parent Directory'
            ),
        ],
    )
    @action(detail=False, methods=['get'],
            url_path='explorer')
    def file_explore_view(self, request):
        """
        MEH: Return mixed list of Directory `type='dir'` and File Item `type='else'`
        for parent_id = x or root level parent_id = None
        """
        return self.get_explorer_list(request=request, category_model=FileDirectory, item_model=FileItem,
                                      category_serializer=FileDirectorySerializer, item_serializer=FileItemSerializer,
                                      parent_field='parent_directory', item_filter_field='parent_directory',
                                      filter_backends=self.filter_backends, paginate=True)

    @extend_schema(
        summary='Delete list of Directories & Files',
        request=CombineBulkDeleteSerializer,
        responses={
            200: OpenApiResponse(description="Successfully deleted Directories & Files."),
            400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], serializer_class=CombineBulkDeleteSerializer,
            url_path='bulk-delete', filter_backends=[None])
    def bulk_delete(self, request):
        """
        MEH: Delete List of Directory & File Item Objects (use POST ACTION for sending ids list in request body)
        """
        itm_qs, dir_qs = self.explorer_bulk_queryset(request, FileDirectory, FileItem)
        return self.custom_list_destroy([itm_qs, dir_qs])

@extend_schema(tags=['File-Manager'])
class FileItemViewSet(CustomMixinModelViewSet):
    """
    MEH: File Item Model viewset
    """
    queryset = FileItem.objects.all().order_by('-create_date')
    serializer_class = FileItemSerializer
    http_method_names = ['get', 'head', 'option', 'post', 'delete']
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['name']
    ordering_fields = ['create_date', 'name', 'type', 'volume']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['file_manager'],
        'clear_old_files': ['clear_old_files'],
        'retrieve': [] # MEH: Admin User
    }

    @extend_schema(summary = "Related to Clear old file from Orders")
    @action(detail=False, methods=['get', 'post'],
            url_path='clear-old-files', serializer_class=ClearFileSerializer, filter_backends=[None])
    def clear_old_files(self, request):
        cache_key = 'clear_old_files'
        if not hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            raise PermissionDenied
        if request.method == 'POST':
            cache.delete(cache_key)
            return self.custom_create(request, employee=request.user.employee_profile)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        histories = ClearFileHistory.objects.select_related('employee').order_by('-submit_date')
        res = self.custom_get(histories)
        cache.set(cache_key, res.data, timeout=60 * 60 * 24 * 365) # MEH: 1 year (always) until change
        return res
