from rest_framework import serializers
from api.responses import *
from .models import Province, City
from api.mixins import CustomModelSerializer, CustomChoiceField


class ProvinceSerializer(CustomModelSerializer):
    """
    MEH: Province full Information
    """
    class Meta:
        model = Province
        fields = '__all__'
