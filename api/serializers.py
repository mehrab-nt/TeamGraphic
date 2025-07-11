from rest_framework import serializers
from .mixins import CustomModelSerializer
from .models import ApiItem, ApiCategory
from .responses import TG_DATA_EMPTY


class BulkDeleteSerializer(serializers.Serializer):
    """
    MEH: Get a list of Ids for bulk delete
    """
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, required=True)


class CombineBulkDeleteSerializer(serializers.Serializer):
    """
    MEH: Get 2 list of Ids for bulk delete in explorer page (file-manager, product-cat, ...)
    """
    item_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=False)
    layer_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=False)

    def validate(self, attrs):
        if not attrs.get('item_ids') and not attrs.get('layer_ids'):
            raise serializers.ValidationError(TG_DATA_EMPTY)
        return attrs


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


class AdminApiCategoryItemSerializer(CustomModelSerializer):
    """
    MEH: Api Item list full information in Api Category
    for Admin work
    """
    category_display = serializers.StringRelatedField(source='category')

    class Meta:
        model = ApiItem
        fields = ['id', 'category_display', 'title', 'sort_number', 'key']

    def create(self, validated_data, **kwargs):
        api_item = ApiItem(**validated_data, **kwargs)
        api_item.save()
        return api_item


class AdminApiItemSerializer(CustomModelSerializer):
    """
    MEH: Api Item detail full information (with changing category)
    for Admin work
    """
    category_display = serializers.StringRelatedField(source='category')

    class Meta:
        model = ApiItem
        fields = ['id', 'category', 'category_display', 'title', 'sort_number', 'key']
