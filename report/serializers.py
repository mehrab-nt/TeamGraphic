from rest_framework import serializers
from .models import DailySaleReport
from product.models import Product
from api.mixins import CustomModelSerializer
from django.core.cache import cache


class ProductReportSerializer(CustomModelSerializer):
    """
    MEH: Product brief sale Report
    """
    parent_category_display = serializers.StringRelatedField(source='parent_category', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'type', 'status', 'parent_category', 'parent_category_display', 'total_order', 'last_order', 'total_main_sale', 'total_option_sale']
