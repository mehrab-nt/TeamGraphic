from rest_framework import serializers

from api.models import ApiItem
from .models import Employee, EmployeeLevel
from user.models import User
from user.serializers import UserSerializer
from rest_framework.exceptions import PermissionDenied
from api.mixins import CustomModelSerializer
from api.responses import *


class UserEmployeeSerializer(UserSerializer):
    """
    MEH: Handle important field form User model in Employee Serializer
    Create & Update Handle in UserSerializer...
    """
    is_employee = serializers.HiddenField(default=True)
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'email',
                  'is_active', 'is_employee', 'invite_user_count', 'user_profile']
        read_only_fields = ['id', 'date_joined', 'is_active']


class EmployeeSerializer(CustomModelSerializer):
    """
    MEH: Main Employee full information
    """
    user = UserEmployeeSerializer(required=False) # MEH: Nested (User Model) Information
    level = serializers.StringRelatedField()

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('rate',)

    def create(self, validated_data, **kwargs): # MEH: Nested create Employee with User information and Profile (Just for Admin work) just single Employee
        user_data = validated_data.pop('user', {})
        if user_data:
            user_serializer = UserEmployeeSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            employee = Employee.objects.create(**validated_data, user=user)
            return employee
        else:
            raise serializers.ValidationError({'employee': TG_DATA_WRONG})

    def update(self, instance, validated_data, **kwargs): # MEH: Nested update for Employee with User & Profile
        user_data = validated_data.pop('user', {})
        if user_data:
            user_serializer = UserEmployeeSerializer(instance=instance.user, data=user_data, partial=(self.context.get('request').method == 'PATCH'))
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmployeeLevelSerializer(CustomModelSerializer):
    """
    MEH: Main Employee level full information
    """
    manager = serializers.StringRelatedField()
    class Meta:
        model = EmployeeLevel
        fields = ['id', 'title', 'description', 'is_active', 'manager']

    def create(self, validated_data, **kwargs):
        employee_level = EmployeeLevel(**validated_data, **kwargs) # MEH: for parse manager in **kwargs
        employee_level.save()
        return employee_level


class EmployeeLevelSetSerializer(CustomModelSerializer):
    """
    MEH: Handle Post Employee to Level for Set that Level on Employee
    """
    full_name = serializers.SerializerMethodField()
    level_display = serializers.StringRelatedField(source='level')
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'level', 'level_display']

    @staticmethod
    def get_full_name(obj):
        return str(obj)