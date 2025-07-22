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
from rest_framework.exceptions import MethodNotAllowed


@extend_schema(tags=['File-Manager'])
class FileDirectoryViewSet(CustomMixinModelViewSet):
    """
    MEH: File Directory Model viewset
    """
    queryset = FileDirectory.objects.all().order_by('-create_date')
    serializer_class = FileDirectorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['name']
    ordering_fields = ['create_date', 'name']
    pagination_class = None
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
        raise MethodNotAllowed('PUT')

    @extend_schema(exclude=True)  # MEH: Hidden PATCH from Api Documentation (only Admin work!)
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

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
        dir_data = FileDirectorySerializer(directories, many=True, context={'request': request}).data
        file_data = FileItemSerializer(files, many=True, context={'request': request}).data
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
        MEH: Delete List of Directory & File Item Objects (use POST ACTION for sending ids list in request body)
        """
        validated_data = self.get_validated_ids_list(request.data)
        file_ids = validated_data.get('item_ids', [])
        dir_ids = validated_data.get('layer_ids', [])
        file_qs = FileItem.objects.filter(id__in=file_ids)
        dir_qs = FileDirectory.objects.filter(id__in=dir_ids)
        self.serializer_class = FileDirectorySerializer # MEH: Just for drf view
        return self.custom_list_destroy([file_qs, dir_qs])


@extend_schema(tags=['File-Manager'])
class FileItemViewSet(CustomMixinModelViewSet):
    """
    MEH: File Item Model viewset
    """
    queryset = FileItem.objects.all().order_by('-create_date')
    serializer_class = FileItemSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['name']
    ordering_fields = ['create_date', 'name', 'type', 'volume']
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['file_manager'],
        'clear_old_files': ['clear_old_files'],
        **dict.fromkeys(['retrieve', 'update', 'partial_update'], []), # MEH: Admin User
    }

    @extend_schema(exclude=True)  # MEH: Hidden GET <pk> from Api Documentation (only Admin work!)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True) # MEH: Hidden PUT from Api Documentation (MethodNotAllowed)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    @extend_schema(exclude=True) # MEH: Hidden PATCH from Api Documentation (MethodNotAllowed)
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

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
