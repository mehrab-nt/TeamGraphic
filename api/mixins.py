from django.db import models
from rest_framework import serializers
from user.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .responses import *
from django.db import transaction, IntegrityError, DatabaseError
from django.db.models.deletion import ProtectedError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import BulkDeleteSerializer


class CustomModelSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for name, field in fields.items():
            if isinstance(field, serializers.CharField):
                field.error_messages.update({
                    'blank': TG_DATA_BLANK,
                    'required': TG_DATA_REQUIRED,
                })
            if isinstance(field, serializers.IntegerField):
                field.error_messages.update({
                    'blank': TG_DATA_BLANK,
                    'required': TG_DATA_REQUIRED,
                    'invalid': TG_DATA_MOST_DIGIT
                })
            for validator in getattr(field, 'validators', []):
                if isinstance(validator, MinLengthValidator):
                    validator.message = TG_DATA_TOO_SHORT + str(validator.limit_value)
                if isinstance(validator, MaxLengthValidator):
                    validator.message = TG_DATA_TOO_LONG + str(validator.limit_value)
        return fields


# MEH: Custom get, put, post, delete for Reduce Code Line & Repeat
class CustomMixinModelViewSet(viewsets.ModelViewSet):
    # MEH: Custom Pagination :) even LimitOffsetPagination
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'size'
    pagination_class.page_size = 100
    pagination_class.max_page_size = 1000
    required_api_keys = None

    def get_object(self, **kwargs):
        return super().get_object()

    # MEH: Override post single or Bulk list
    def create(self, request, *args, **kwargs):
        return self.custom_create(request)

    def update(self, request, *args, **kwargs):
        queryset = self.get_object(**kwargs)
        return self.custom_update(queryset, request)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, 'is_default'):
            return self.custom_destroy(instance, is_default=instance.is_default)
        return self.custom_destroy(instance)

    def custom_get(self, queryset):
        is_many = not isinstance(queryset, models.Model)
        serializer = self.get_serializer(queryset, many=is_many)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def custom_create(self, request, **kwargs):
        # MEH: Many Create disable... (Customize when Its need)
        is_many = isinstance(request.data, list)
        if is_many:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer, **kwargs)
        except ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)

    def custom_update(self, instance, request, **kwargs):
        # MEH: Many Update disable...
        is_many = isinstance(request.data, list)
        if is_many:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        serializer = self.get_serializer(instance, data=request.data, partial=(request.method == 'PATCH'))
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer, **kwargs)
        except ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def custom_destroy(self, instance, **kwargs):
        if kwargs.get('is_default'):
            raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
        try:
            self.perform_destroy(instance)
        except ProtectedError: # Model on-delete=PROTECT
            raise PermissionDenied(TG_PREVENT_DELETE_PROTECTED)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)

    def custom_bulk_destroy(self, request):
        serializer = BulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = self.queryset.filter(id__in=ids)
        model = queryset.model
        default_obj = []
        if hasattr(model, 'is_default'):
            default_obj = queryset.filter(is_default=True)
            if default_obj.exists():
                raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
        try:
            queryset.delete()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer, **kwargs):
        return serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):
        serializer.save(**kwargs)

    def perform_destroy(self, instance):
        return instance.delete()

    # MEH: Get Key for Action -> Check Access at the End
    def get_required_api_key(self):
        return self.required_api_keys.get(self.action)
