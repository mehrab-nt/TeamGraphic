from rest_framework import serializers
from .mixins import CustomModelSerializer


class BulkDeleteSerializer(CustomModelSerializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, required=True)
