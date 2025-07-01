from django.db import models
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .responses import TG_DATA_CREATED, TG_DATA_DELETED, TG_PREVENT_DELETE_DEFAULT
from django.db import transaction, IntegrityError, DatabaseError
from rest_framework.exceptions import PermissionDenied

# MEH: Custom get, put, post, delete for Reduce Code Line & Repeat
class CustomMixinModelViewSet(viewsets.ModelViewSet):
    # MEH: Custom Pagination :) even LimitOffsetPagination
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'size'
    pagination_class.page_size = 100
    pagination_class.max_page_size = 1000

    def custom_get(self, queryset):
        is_many = not isinstance(queryset, models.Model)
        return Response(self.get_serializer(queryset, many=is_many).data, status=status.HTTP_200_OK)

    def custom_update(self, instance, request):
        serializer = self.get_serializer(instance, data=request.data, partial=(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def custom_create(self, request, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, **kwargs)
        return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)

    def custom_destroy(self, instance, **kwargs):
        if kwargs.get('is_default'):
            raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
        self.perform_destroy(instance)
        return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer, **kwargs):
        try:
            return serializer.save(**kwargs)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        try:
            return serializer.save()
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        try:
            return instance.delete()
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

