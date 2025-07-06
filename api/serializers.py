from rest_framework import serializers
from .mixins import CustomModelSerializer
from .models import ApiItem, ApiCategory


class BulkDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, required=True)


class ApiCategorySerializer(CustomModelSerializer):
    """
    MEH: Api Category information without Api-Items
    """
    class Meta:
        model = ApiCategory
        fields = ['id', 'title', 'sort_number']


class ApiCategoryItemSerializer(CustomModelSerializer):
    """
    MEH: Api Item list full information in Api Category
    """
    category_display = serializers.StringRelatedField(source='category')

    class Meta:
        model = ApiItem
        fields = ['id', 'category_display', 'title', 'sort_number', 'key']

    def create(self, validated_data, **kwargs):
        api_item = ApiItem(**validated_data, **kwargs)
        api_item.save()
        return api_item


class ApiItemSerializer(CustomModelSerializer):
    """
    MEH: Api Item detail full information (with changing category)
    """
    category_display = serializers.StringRelatedField(source='category')

    class Meta:
        model = ApiItem
        fields = ['id', 'category', 'category_display', 'title', 'sort_number', 'key']
