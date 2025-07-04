from django.db import models
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .responses import *
from django.db import IntegrityError, DatabaseError
from django.db.models.deletion import ProtectedError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from rest_framework.exceptions import PermissionDenied, ValidationError


# MEH: Customize message error for all serializer Field...
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
                    'invalid': TG_DATA_MOST_DIGIT,
                })
            if isinstance(field, serializers.PrimaryKeyRelatedField):
                field.error_messages.update({
                    'required': TG_DATA_REQUIRED,
                    'invalid': TG_DATA_WRONG,
                    'does_not_exist': TG_DATA_NOT_FOUND,
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
    pagination_class.page_size = 20
    pagination_class.max_page_size = 100
    required_api_keys = None

    # MEH: Get Key for Action -> Check Access at the End
    def get_required_api_key(self):
        return self.required_api_keys.get(self.action)

    def retrieve(self, request, *args, **kwargs): # MEH: not change for now
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs): # MEH: not change for now
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs): # MEH: override -> user custom create for handle is_many & EXCEPTION response
        return self.custom_create(request.data)

    def update(self, request, *args, **kwargs): # MEH: override -> user custom update for handle is_many & EXCEPTION response
        instance = self.get_object()
        return self.custom_update(instance, request.data)

    def partial_update(self, request, *args, **kwargs): # MEH: override -> user custom partial update for handle is_many & EXCEPTION response
        instance = self.get_object()
        return self.custom_update(instance, request.data, partial=True)

    def destroy(self, request, *args, **kwargs): # MEH: override -> user custom destroy for handle is_many & EXCEPTION response
        instance = self.get_object()
        return self.custom_destroy(instance)

    def custom_get(self, queryset): # Mix retrieve & list method In 1
        is_many = not isinstance(queryset, models.Model)
        serializer = self.get_serializer(queryset, many=is_many)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def custom_create(self, data, many=False, **kwargs):
        # MEH: Many Post Handle from View Actions -> (many=T or F)...
        is_many = isinstance(data, list)
        if is_many and not many:
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data, many=many)
        try:
            print(data)
            serializer.is_valid(raise_exception=True)
            print(serializer.validated_data)
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

    def custom_update(self, instance, data, partial=False, **kwargs):
        # MEH: Many Update disable...
        is_many = isinstance(data, list)
        if is_many:
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=data, partial=partial)
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
        # MEH: Many destroy disable here -> (handle with custom_bulk_destroy)
        is_many = isinstance(instance, list)
        if is_many:
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(instance, 'is_default'):
            if instance.is_default:
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

    def custom_list_destroy(self, list_data): # MEH: Handle delete list of object with 1 request
        serializer = self.get_serializer(data=list_data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = self.queryset.filter(id__in=ids)
        default_objs = []
        if hasattr(queryset.model, 'is_default'):
            default_objs = queryset.filter(is_default=True)
            if default_objs.exists():
                skipped_ids = list(default_objs.values_list('id', flat=True))
                queryset = queryset.exclude(id__in=skipped_ids)
        try:
            deleted_count, _ = queryset.delete()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": TG_DATA_DELETED, "deleted_count": deleted_count}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer, **kwargs): # MEH: override for parse **kwargs if any data there
        serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs): # MEH: override for parse **kwargs if any data there
        serializer.save(**kwargs)

    def perform_destroy(self, instance): # MEH: not change for now
        instance.delete()
