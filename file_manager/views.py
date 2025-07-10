from rest_framework import status, filters
from datetime import datetime, date
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from api.permissions import ApiAccess, IsNotAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import FileDirectory, FileItem
from api.models import ApiCategory
from django.db.models import Subquery, OuterRef, Count, Prefetch
from .serializers import FileDirectorySerializer, FileItemSerializer
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
    ordering_fields = ['create_date', 'name', 'type']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': 'allow_any',
        'list': ''
    }

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
        data = request.data.copy()
        parent_id = request.query_params.get('parent_id')
        if not parent_id: # MEH: it can be in body
            parent_id = data.get('parent_id')
        if parent_id in ['', 'None', None]:
            data['parent_directory'] = None
        else:
            try:
                parent_directory = FileDirectory.objects.get(pk=parent_id)
                data['parent_directory'] = parent_directory.pk
            except FileDirectory.DoesNotExist:
                return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        return self.custom_create(data, *args, **kwargs)

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
        directories = FileDirectory.objects.filter(parent_directory=parent).order_by('-create_date', 'name').prefetch_related('sub_dirs')
        files = FileItem.objects.filter(parent_directory=parent).order_by('-create_date', 'name')
        dir_data = FileDirectorySerializer(directories, many=True).data
        file_data = FileItemSerializer(files, context={'request': request}, many=True).data
        return Response(dir_data + file_data, status=status.HTTP_200_OK)


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
        '__all__': 'allow_any',
        'update': '',
        'partial_update': '',
    }

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
