from rest_framework import serializers
from .mixins import CustomModelSerializer, CustomChoiceField
from .models import ApiItem, ApiCategory
from product.models import ProductStatus
from .responses import TG_DATA_EMPTY


class CopyWithIdSerializer(serializers.Serializer):
    """
    MEH: Get an ID for copy that object
    """
    id = serializers.IntegerField(allow_null=False, required=True)


class BulkDeleteSerializer(serializers.Serializer):
    """
    MEH: Get a list of IDs for bulk delete
    """
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, required=True)


class CombineBulkDeleteSerializer(serializers.Serializer):
    """
    MEH: Get 2 list of IDs for bulk delete
    in explorer page (file-manager, product-cat, ...)
    """
    item_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=False)
    layer_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=False)

    def validate(self, attrs):
        if not attrs.get('item_ids') and not attrs.get('layer_ids'):
            raise serializers.ValidationError(TG_DATA_EMPTY)
        return attrs


class CombineBulkUpdateProductStatusSerializer(CombineBulkDeleteSerializer):
    """
    MEH: Get 2 list of IDs and (status) field for bulk update
    in explorer page (product-cat, ...)
    """
    status = CustomChoiceField(choices=ProductStatus.choices, initial=ProductStatus.ACTIVE, default=ProductStatus.ACTIVE)


class CombineBulkUpdateActivateSerializer(CombineBulkDeleteSerializer):
    """
    MEH: Get 2 list of IDs and (is_active) field for bulk update
    in explorer page (option-cat, ...)
    """
    is_active = serializers.BooleanField(required=True)


class ApiItemSerializer(CustomModelSerializer):
    """
    MEH: Api Item nested data
    """
    class Meta:
        model = ApiItem
        fields = ['id', 'title']


class ApiCategorySerializer(CustomModelSerializer):
    """
    MEH: Api Category full list with nested Api Items
    (Role and Employee Level - Handle both)
    """
    api_items = ApiItemSerializer(many=True, read_only=True)

    class Meta:
        model = ApiCategory
        fields = ['id', 'title', 'api_items']


class AdminApiCategorySerializer(CustomModelSerializer):
    """
    MEH: Api Category information without Api-Items
    for Admin work
    """
    class Meta:
        model = ApiCategory
        fields = ['id', 'title', 'sort_number']


class AdminApiItemSerializer(CustomModelSerializer):
    """
    MEH: Api Item detail full information (with changing category)
    for Admin work
    """
    category_display = serializers.StringRelatedField(source='category')

    class Meta:
        model = ApiItem
        fields = ['id', 'category', 'category_display', 'title', 'sort_number', 'key']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action == 'api_item_list': # MEH: Drop Category
            data.pop('category', None)
        return data
