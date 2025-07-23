from rest_framework import serializers
from .models import PriceListConfig


class PriceListConfigSerializer(serializers.ModelSerializer):
    """
    MEH: Price List Config full information
    """
    block_role_display = serializers.StringRelatedField(source='block_role', many=True)

    class Meta:
        model = PriceListConfig
        read_only_fields = ['last_update']
        exclude = ['id']
