from django.db import models
from django.db import IntegrityError, DatabaseError
from django.db.models.deletion import ProtectedError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from .responses import *
from file_manager.images import *
from typing import Optional, Dict
from django.db import transaction
from drf_spectacular.utils import extend_schema
from django.core.cache import cache
import hashlib


class CustomModelSerializer(serializers.ModelSerializer):
    """
    MEH: for handle same logic for all serializer class
    """
    def get_fields(self):
        """
        MEH: Override get_fields to Customize message error for common serializer Field...
        """
        fields = super().get_fields()
        for name, field in fields.items():
            if isinstance(field, serializers.CharField):
                field.error_messages.update({
                    'blank': TG_DATA_BLANK, 'required': TG_DATA_REQUIRED, 'invalid': TG_DATA_WRONG,
                })
            if isinstance(field, serializers.IntegerField):
                field.error_messages.update({
                    'blank': TG_DATA_BLANK, 'required': TG_DATA_REQUIRED, 'invalid': TG_DATA_MOST_DIGIT,
                })
            if isinstance(field, serializers.PrimaryKeyRelatedField):
                field.error_messages.update({
                    'required': TG_DATA_REQUIRED, 'invalid': TG_DATA_WRONG, 'does_not_exist': TG_DATA_NOT_FOUND,
                })
            for validator in getattr(field, 'validators', []):
                if isinstance(validator, MinLengthValidator):
                    validator.message = TG_DATA_TOO_SHORT + str(validator.limit_value)
                if isinstance(validator, MaxLengthValidator):
                    validator.message = TG_DATA_TOO_LONG + str(validator.limit_value)
        return fields

    @staticmethod
    def validate_upload_image(image, max_image_size=10, max_width=1024, max_height=1024, size=(256, 256)):
        """
        MEH: Validate uploaded image for type, size, volume
        """
        try:
            size_mb = image.size / (1024 * 1024)
            if size_mb > max_image_size:
                raise serializers.ValidationError(f"{TG_MAX_IMAGE_SIZE} ({max_image_size} MB)")
        except (AttributeError, TypeError):
            raise serializers.ValidationError(TG_INVALID_IMAGE)
        try:
            img = Image.open(image)
        except (UnidentifiedImageError, OSError):
            raise serializers.ValidationError(TG_INVALID_IMAGE)
        img_format = img.format.upper()
        if img_format not in ALLOWED_IMAGE_FORMATS:
            raise serializers.ValidationError(f"{TG_UNSUPPORTED_FORMAT} ({img_format})")
        width, height = img.size
        if max_width and max_height:
            if width > max_width or height > max_height:
                raise serializers.ValidationError(f"{TG_MAX_IMAGE_DIMENSIONS}({max_width}x{max_height}px)")
        return optimize_image(image, size=size)


class CustomChoiceField(serializers.ChoiceField):
    """
    MEH: Customize message error for char choice serializer Field...
    """
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            raise serializers.ValidationError(TG_DATA_WRONG)


class CustomMixinModelViewSet(viewsets.ModelViewSet):
    """
    MEH: Custom ModelViewSet for get, put, patch, post, delete -> single obj & bulk
    Reduce Code Line & Repeat in all Viewset
    """
    pagination_class = PageNumberPagination # MEH: Custom Pagination :) even LimitOffsetPagination
    pagination_class.page_size_query_param = 'size'
    pagination_class.page_size = 20
    pagination_class.max_page_size = 100
    required_api_keys = None # MEH: Override this In each model view set for handle Access
    cache_key = None # MEH: Override this if used cached for list

    def get_required_api_key(self):
        """
        MEH: get required key for check in permission class
        """
        return self.required_api_keys.get(self.action) or self.required_api_keys.get('__all__')

    def get_cache_key(self, request):
        """
        MEH: for pagination & filtering cached
        """
        query_string = request.GET.urlencode()
        hashed = hashlib.md5(query_string.encode()).hexdigest()
        return f"{self.cache_key}_{hashed}"

    def get_serializer_fields(self, serializer: Optional[serializers.BaseSerializer] = None,
                              parent_prefix: str = '') -> Dict[str, serializers.Field]:
        """
        MEH: for get valid field from serializer (nested included)
        show in schema or UI
        """
        fields = {}
        if serializer is None:
            serializer = self.get_serializer()
        for name, field in serializer.fields.items():
            full_name = f"{parent_prefix}{name}" if parent_prefix else name
            if isinstance(field, serializers.BaseSerializer):
                nested_fields = self.get_serializer_fields(serializer=field)
                fields.update(nested_fields)
            else:
                fields[full_name] = field
        return fields

    def get_object(self, *args, **kwargs):
        """
        MEH: Override get single obj (with pk) (DEFAULT GET OBJECT ACTION)
        also use auto for PUT & DELETE obj
        """
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field, '')
        try:
            obj = queryset.get(pk=int(lookup_value))
            return obj # MEH: Object Access check again after In has_object_permission (Just in main action, for custom action most call manual)
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        except ValueError:
            raise NotFound(TG_EXPECTED_ID_NUMBER)

    def list(self, request, timeout=60 * 60 * 24, *args, **kwargs):
        """
        MEH: Override list (GET) ViewSet logic for Cached data
        """
        if self.cache_key:
            full_cache_key = self.get_cache_key(request) # MEH: different cache key for different request
            cached_data = cache.get(full_cache_key)
            if cached_data:
                return Response(cached_data)
            res = super().list(request, *args, **kwargs)
            cache.set(self.cache_key, res.data, timeout=timeout) # MEH: Default 1 day!
            return res
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        MEH: for override retrieve (GET) ViewSet logic, noting change for now
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs): # MEH: override ->
        """
        MEH: for override create (POST) ViewSet logic,
        user custom create for handle is_many & EXCEPTION response
        """
        return self.custom_create(request, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        MEH: for override update (PUT) ViewSet logic,
        user custom update for handle is_many & EXCEPTION response
        """
        instance = self.get_object()
        return self.custom_update(instance, request, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        MEH: for override partial update (PATCH) ViewSet logic,
        user custom update for handle is_many & EXCEPTION response
        """
        instance = self.get_object()
        return self.custom_update(instance, request, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        MEH: for override destroy (DELETE) ViewSet logic,
        user custom destroy for handle is_many & EXCEPTION response
        """
        instance = self.get_object()
        return self.custom_destroy(instance)

    def custom_get(self, data):
        """
        MEH: Mix retrieve & list method In 1 logic
        """
        is_many = not isinstance(data, models.Model)
        if is_many:
            page = self.paginate_queryset(data)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(data, many=is_many)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def custom_create(self, request, many=False, response_data_back=None, **kwargs):
        """
        MEH: Handle single or list obj create & handle Exception response,
        send manual field data that not in the request with **kwargs
        """
        is_many = isinstance(request.data, list)
        if is_many and not many: # MEH: Many Post most Handle from View Actions -> (many=T or F)...
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data, many=many)
        try:
            serializer.is_valid(raise_exception=True)
            created_data = self.perform_create(serializer, **kwargs)
        except ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if response_data_back: # MEH: If wanting data in response
            return Response({'detail': created_data}, status=status.HTTP_202_ACCEPTED)
        return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)

    def custom_update(self, instance, request, partial=False, response_data_back=None, **kwargs):
        """
        MEH: Handle only single obj update & handle Exception response,
        send manual field data that not in the request with **kwargs
        """
        is_many = isinstance(request.data, list)
        if is_many: # MEH: Many Update disable here -> (handle with custom_list_update)
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            updated_data = self.perform_update(serializer, **kwargs)
        except ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(instance, '_prefetched_objects_cache', None):  # MEH: Invalidate prefetch cache if needed
            instance._prefetched_objects_cache = {}
        if response_data_back:
            return Response({'detail': updated_data}, status=status.HTTP_200_OK)
        return Response({'detail': TG_DATA_UPDATED}, status=status.HTTP_200_OK)

    def custom_destroy(self, instance):
        """
        MEH: Handle only single obj delete & handle Exception response,
        """
        is_many = isinstance(instance, list)
        if is_many: # MEH: Many destroy disable here -> (handle with custom_list_destroy)
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(instance, 'is_default'): # MEH: Don't let default obj destroy
            if instance.is_default:
                raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
        try:
            if hasattr(instance, 'delete_recursive'): # MEH: for handle delete M2M child (FK child delete auto with on_delete=CASCADE)
                with transaction.atomic():
                    deleted_child_count = instance.delete_recursive()
            else:
                deleted_child_count, _ = self.perform_destroy(instance)
        except ProtectedError: # Model on_delete=PROTECT
            raise PermissionDenied(TG_PREVENT_DELETE_PROTECTED)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if deleted_child_count > 1:
            return Response({"detail": TG_DATA_DELETED, "deleted_count": deleted_child_count}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)

    def get_validate_data(self, data, many=False):
        """
        MEH: Get validate data from serializer (obj or qs)
        only for use data manually in viewset (create/update)
        """
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def explorer_bulk_queryset(self, request, category_model, item_model):
        """
        MEH: Handle selected list of cat & item in explorer view
        """
        validated_ids = self.get_validate_data(request.data) # MEH: Get 2 ids list
        cat_ids = validated_ids.get('layer_ids', [])
        itm_ids = validated_ids.get('item_ids', [])
        cat_qs = category_model.objects.filter(id__in=cat_ids)
        itm_qs = item_model.objects.filter(id__in=itm_ids)
        return itm_qs, cat_qs

    def explorer_bulk_update_fields(self, request, field_name=None):
        """
        MEH: Handle 1 field bulk-update with value in explorer view
        """
        validated_ids = self.get_validate_data(request.data)
        field_value = validated_ids.get(field_name, None) # MEH: Only for update some fields in all list
        update_field = None
        if field_value is not None:
            update_field = {
                field_name: field_value,
            }
        elif field_value is None and field_name:
            raise NotFound(TG_DATA_EMPTY)
        return update_field

    @staticmethod
    def custom_list_destroy(queryset_list: list):
        """
        MEH: Handle bulk delete list of object with 1 request
        """
        total_delete = 0
        skipped_ids = []
        try:
            with transaction.atomic():
                for qs in queryset_list:
                    model = qs.model
                    if hasattr(model, 'is_default'): # MEH: In any case, just skipped is_default
                        default_objs = qs.filter(is_default=True)
                        if default_objs.exists():
                            ids = list(default_objs.values_list('id', flat=True))
                            skipped_ids.extend(ids)
                            qs = qs.exclude(id__in=ids)
                    if not qs.exists():
                        continue
                    if model.delete is models.Model.delete: # MEH: Safe to do bulk delete
                        deleted_count, _ = qs.delete()
                        total_delete += deleted_count
                    else: # MEH: Delete obj 1 by 1 (for M2M sub child)
                        for obj in qs:
                            sub_delete, _ = obj.delete()
                            total_delete += sub_delete
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if total_delete == 0:
            return Response({"detail": TG_DATA_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": TG_DATA_DELETED, "deleted_count": total_delete, "skipped_ids": skipped_ids,}, status=status.HTTP_200_OK)

    @staticmethod
    def custom_list_update(queryset_list: list, update_fields: dict, update_sub=False):
        """
        MEH: Handle bulk update list of fields in list of object with 1 request,
        for simplify, handle here instead of ListSerializer update method
        """
        try:
            with transaction.atomic():
                for qs in queryset_list:
                    if not qs.exists():
                        continue
                    for obj in qs:
                        for field_name, field_value in update_fields.items():
                            if hasattr(obj, field_name):
                                setattr(obj, field_name, field_value)
                        obj.save(update_fields=list(update_fields.keys()))
                        if update_sub and hasattr(obj, 'update_all_subcategories_and_items'):
                            obj.update_all_subcategories_and_items() # MEH: Nested update until the end!
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": TG_DATA_UPDATED}, status=status.HTTP_200_OK)

    @staticmethod
    def get_parent_with_id(request, category_model):
        """
        MEH: Get parent object from category model with ID
        """
        parent_id = request.query_params.get('parent_id')
        if not parent_id: # MEH: it can be in body
            parent_id = request.data.get('parent_id')
        if parent_id in ['', 'None', None]:
            return None
        try:
            return category_model.objects.get(pk=parent_id)
        except category_model.DoesNotExist:
            return Response({'detail': TG_DATA_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

    def get_explorer_list(self, request, category_model, item_model, category_serializer, item_serializer,
                          parent_field='parent_category', category_filter_extra=None, item_filter_field='parent_category'):
        """
        MEH: Handle mixed list of category and item for explorer view
        """
        parent = self.get_parent_with_id(request, category_model)
        category_filter = {parent_field: parent}
        if category_filter_extra:
            category_filter.update(category_filter_extra)
        categories = category_model.objects.filter(**category_filter)
        if hasattr(category_model, 'sort_number'):
            categories = categories.order_by('sort_number')
        items = item_model.objects.filter(**{item_filter_field: parent})
        if hasattr(item_model, 'sort_number'):
            items = items.order_by('sort_number')
        cat_data = category_serializer(categories, many=True, context={'request': request}).data
        item_data = item_serializer(items, many=True, context={'request': request}).data
        return Response(cat_data + item_data, status=status.HTTP_200_OK)

    def perform_create(self, serializer, **kwargs):
        """
        MEH: override for parse **kwargs if any data there & handle transaction
        """
        with transaction.atomic(): # MEH: With transaction if anything wrong, Everything in DB roll back to first place
            res = serializer.save(**kwargs)
        if self.cache_key:
            cache.delete_pattern(f'{self.cache_key}*')
        return res

    def perform_update(self, serializer, **kwargs):
        """
        MEH: override for parse **kwargs if any data there & handle transaction
        """
        with transaction.atomic():
            res = serializer.save(**kwargs)
        if self.cache_key:
            cache.delete_pattern(f'{self.cache_key}*') # MEH: Delete all cache begin with this key
        return res

    def perform_destroy(self, instance):
        """
        MEH: override just for handle transaction
        """
        with transaction.atomic():
            res = instance.delete()
        if self.cache_key:
            cache.delete_pattern(f'{self.cache_key}*')
        return res


class CustomBulkListSerializer(serializers.ListSerializer):
    """
    MEH: for Override ListSerializer behavior
    most be set in serializer class Meta -> list_serializer_class = CustomBulkListSerializer
    """
    def create(self, validated_data):
        """
        MEH: Override bulk create to (1 by 1) (instead of .bulk_create: because 1 by 1 maybe slower but safer!)
        if in custom_create, parse many=True, perform_create, use this method instead of serializer default create method...
        Used for import data with Excel
        """
        data_list = []
        for i, data in enumerate(validated_data): # MEH: First Validate data 1 by 1 if anything wrong, No Data Create at all
            try:
                self.child.validate_filed(data)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({f"item-{i+1}": e.detail})
        for data in validated_data: # MEH: Now Create 1 by 1 (nested create, most handle in serializer create method)
            data_list.append(self.child.create(data))
        return data_list
