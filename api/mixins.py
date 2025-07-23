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


class CustomModelSerializer(serializers.ModelSerializer):
    """
    MEH: Customize message error for common serializer Field...
    """
    def get_fields(self):
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
                raise serializers.ValidationError(
                    f"{TG_MAX_IMAGE_DIMENSIONS}({max_width}x{max_height}px)")
        return optimize_image(image, size=size)


class CustomChoiceField(serializers.ChoiceField):
    """
    MEH: Customize message error for common serializer Field...
    """
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            raise serializers.ValidationError(TG_DATA_WRONG)


class CustomMixinModelViewSet(viewsets.ModelViewSet):
    """
    MEH: Custom ModelViewSet for get, put, post, delete -> Reduce Code Line & Repeat in all Viewset
    """
    pagination_class = PageNumberPagination # MEH: Custom Pagination :) even LimitOffsetPagination
    pagination_class.page_size_query_param = 'size'
    pagination_class.page_size = 20
    pagination_class.max_page_size = 100
    required_api_keys = None # MEH: Override this In each model view set for handle Access

    def get_required_api_key(self): # MEH: Custom Pagination :) even LimitOffsetPagination
        return self.required_api_keys.get(self.action) or self.required_api_keys.get('__all__')

    @staticmethod
    def get_parent_id(request):
        parent_id = request.query_params.get('parent_id')
        if not parent_id: # MEH: it can be in body
            parent_id = request.data.get('parent_id')
        if parent_id in ['', 'None', None]:
            return None
        return parent_id

    def get_serializer_fields(self, serializer: Optional[serializers.BaseSerializer] = None,
                              parent_prefix: str = '') -> Dict[str, serializers.Field]:
        fields = {} # MEH: For get valid field from serializer (nested included)
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

    def get_object(self, *args, **kwargs): # MEH: Override get single obj (with pk) (DEFAULT GET OBJECT ACTION) also use auto for PUT & DELETE
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field, '')
        try:
            obj = queryset.get(pk=int(lookup_value))
            return obj # MEH: Object Access check again after In has_object_permission
        except ObjectDoesNotExist:
            raise NotFound(TG_DATA_NOT_FOUND)
        except ValueError:
            raise NotFound(TG_EXPECTED_ID_NUMBER)

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

    def custom_get(self, data, request=None): # Mix retrieve & list method In 1
        is_many = not isinstance(data, models.Model)
        if request:
            serializer = self.get_serializer(data, many=is_many, context={'request': request})
        else:
            serializer = self.get_serializer(data, many=is_many)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def custom_create(self, data, many=False, customize_response=None, **kwargs):
        is_many = isinstance(data, list)
        if is_many and not many: # MEH: Many Post Handle from View Actions -> (many=T or F)...
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data, many=many)
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
        if customize_response:
            return Response({'detail': created_data}, status=status.HTTP_202_ACCEPTED)
        return Response({"detail": TG_DATA_CREATED}, status=status.HTTP_201_CREATED)

    def custom_update(self, instance, data, partial=False, customize_response=None, **kwargs):
        is_many = isinstance(data, list)
        if is_many: # MEH: Many Update disable...
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=data, partial=partial)
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
        if customize_response:
            return Response({'detail': updated_data}, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def custom_destroy(self, instance):
        is_many = isinstance(instance, list)
        if is_many: # MEH: Many destroy disable here -> (handle with custom_bulk_destroy)
            return Response({'detail': TG_MANY_DATA_DENIED}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(instance, 'is_default'):
            if instance.is_default:
                raise PermissionDenied(TG_PREVENT_DELETE_DEFAULT)
        try:
            deleted_count = 0
            if hasattr(instance, 'delete_recursive'):
                with transaction.atomic():
                    deleted_count = instance.delete_recursive()
            else:
                self.perform_destroy(instance)
        except ProtectedError: # Model on-delete=PROTECT
            raise PermissionDenied(TG_PREVENT_DELETE_PROTECTED)
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if deleted_count:
            return Response({"detail": TG_DATA_DELETED, "deleted_count": deleted_count,}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": TG_DATA_DELETED}, status=status.HTTP_204_NO_CONTENT)

    def get_validate_data(self, data, many=False):
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @staticmethod
    def explorer_bulk_queryset(validated_data, category_model, item_model, field=None):
        cat_ids = validated_data.get('layer_ids', [])
        itm_ids = validated_data.get('item_ids', [])
        cat_qs = category_model.objects.filter(id__in=cat_ids)
        itm_qs = item_model.objects.filter(id__in=itm_ids)
        field_value = validated_data.get(field, None)
        update_fields = None
        if field_value:
            update_fields = {
                field: field_value,
            }
        elif field_value is None and field:
            raise NotFound(TG_DATA_EMPTY)
        return itm_qs, cat_qs, update_fields

    @staticmethod
    def custom_list_destroy(queryset_list: list): # MEH: Handle bulk delete list of object with 1 request
        total_delete = 0
        skipped_ids = []
        try:
            with transaction.atomic():
                for qs in queryset_list:
                    model = qs.model
                    if hasattr(model, 'is_default'):
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
    def custom_list_update(queryset_list: list, update_fields: dict, update_sub=False): # MEH: Handle bulk update list of fields in list of object with 1 request
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
    def get_explorer_list(request, category_model, item_model, category_serializer, item_serializer, # MEH: Handle mixed list of category and item for explorer view
                              parent_field='parent_category', category_filter_extra=None, item_filter_field='parent_category'):
        parent_id = request.query_params.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = category_model.objects.get(pk=parent_id)
            except category_model.DoesNotExist:
                return Response({'detail': TG_DATA_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
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

    def perform_create(self, serializer, **kwargs): # MEH: override for parse **kwargs if any data there
        with transaction.atomic(): # MEH: With transaction if anything wrong, Everything in DB roll back to first place
            return serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs): # MEH: override for parse **kwargs if any data there
        with transaction.atomic():
            return serializer.save(**kwargs)

    def perform_destroy(self, instance): # MEH: not change for now
        with transaction.atomic():
            instance.delete()


class CustomBulkListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        """
        # MEH: Handle bulk create (1 by 1) (instead of .bulk_create: because 1 by 1 maybe slower but safer!)
        Used for import data with Excel
        """
        data_list = []
        for i, data in enumerate(validated_data): # MEH: First Validate data 1 by 1 if anything wrong, No Data Create at all
            try:
                self.child.validate_filed(data)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({f"item-{i+1}": e.detail})
        for data in validated_data: # MEH: Now Create 1 by 1
            data_list.append(self.child.create(data))
        return data_list
