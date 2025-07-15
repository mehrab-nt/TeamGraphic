from rest_framework import status, filters
from rest_framework.response import Response
from api.permissions import ApiAccess
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import FileDirectory, FileItem, ClearFileHistory
from .serializers import FileDirectorySerializer, FileItemSerializer, ClearFileSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from api.responses import *
from api.mixins import CustomMixinModelViewSet
from api.serializers import CombineBulkDeleteSerializer
from django.core.cache import cache


@extend_schema(tags=['File-Manager'])
class FileDirectoryViewSet(CustomMixinModelViewSet):
    """
    MEH: File Directory Model viewset
    """
    queryset = FileDirectory.objects.all()
    serializer_class = FileDirectorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['name']
    ordering_fields = ['create_date', 'name']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['file_manager'],
        **dict.fromkeys(['retrieve', 'update', 'partial_update'], []), # MEH: Admin User
    }

    @extend_schema(exclude=True)  # MEH: Hidden GET <pk> from Api Documentation (only Admin work!)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)  # MEH: Hidden PUT from Api Documentation (only Admin work!)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)  # MEH: Hidden PATCH from Api Documentation (only Admin work!)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="MEH: Use `parent_id` in query or body to assign a parent_directory. If omitted, Directory will be created at root level.",
        parameters=[
            OpenApiParameter(
                name='parent_id',
                description='ID of the parent_directory. If omitted, creates root Directory.',
                type=int,
                required=False,
                location=OpenApiParameter.QUERY
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        parent_id = request.query_params.get('parent_id')
        if not parent_id: # MEH: it can be in body
            parent_id = request.data.get('parent_id')
        if parent_id in ['', 'None', None]:
            parent_directory = None
        else:
            try:
                parent_directory = FileDirectory.objects.get(pk=parent_id)
            except FileDirectory.DoesNotExist:
                return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        return self.custom_create(request.data, parent_directory=parent_directory)

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
            url_path='explorer', filter_backends=[None])
    def file_explore_view(self, request):
        """
        MEH: Return mixed list of Directory `type='dir'` and File Item `type='else'`
        for parent_id = x or root level parent_id = None
        """
        parent_id = request.query_params.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = FileDirectory.objects.get(pk=parent_id)
            except FileDirectory.DoesNotExist:
                return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        directories = FileDirectory.objects.filter(parent_directory=parent).order_by('-create_date', 'name')
        files = FileItem.objects.filter(parent_directory=parent).order_by('-create_date', 'name')
        dir_data = FileDirectorySerializer(directories, many=True).data
        file_data = FileItemSerializer(files, many=True).data
        return Response(dir_data + file_data, status=status.HTTP_200_OK)

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
        MEH: Delete List of File Item Objects (use POST ACTION for sending last_date in request body)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_ids = serializer.validated_data.get('item_ids', [])
        dir_ids = serializer.validated_data.get('layer_ids', [])
        file_qs = FileItem.objects.filter(id__in=file_ids)
        dir_qs = FileDirectory.objects.filter(id__in=dir_ids)
        self.serializer_class = FileDirectorySerializer # MEH: Just for drf view
        return self.custom_list_destroy([file_qs, dir_qs])


@extend_schema(tags=['File-Manager'])
class FileItemViewSet(CustomMixinModelViewSet):
    """
    MEH: File Item Model viewset
    """
    queryset = FileItem.objects.all()
    serializer_class = FileItemSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['name']
    ordering_fields = ['create_date', 'name', 'type', 'volume']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['file_manager'],
        'clear_old_files': ['clear_old_files'],
        **dict.fromkeys(['retrieve', 'update', 'partial_update'], []), # MEH: Admin User
    }

    @extend_schema(exclude=True)  # MEH: Hidden GET <pk> from Api Documentation (only Admin work!)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True) # MEH: Hidden PUT from Api Documentation (only Admin work!)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True) # MEH: Hidden PATCH from Api Documentation (only Admin work!)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="MEH: Use `parent_id` in query or body to assign a parent_directory. If omitted, File will be uploaded at root level.",
        parameters=[
            OpenApiParameter(
                name='parent_id',
                description='ID of the parent_directory. If omitted, uploaded File at root level.',
                type=int,
                required=False,
                location=OpenApiParameter.QUERY
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return FileDirectoryViewSet.create(self, request, *args, **kwargs)

    @extend_schema(summary = "Related to Clear old file from Orders")
    @action(detail=False, methods=['get', 'post'],
            url_path='clear-old-files', serializer_class=ClearFileSerializer, filter_backends=[None])
    def clear_old_files(self, request):
        cache_key = 'clear_old_files'
        if request.method == 'POST':
            cache.delete(cache_key)
            return self.custom_create(request.data)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        histories = ClearFileHistory.objects.select_related('employee').order_by('-submit_date')
        res = self.custom_get(histories)
        cache.set(cache_key, res.data, timeout=60 * 60 * 24 * 365)
        return res
