from rest_framework import serializers
from .models import Employee, EmployeeLevel
from user.models import User
from api.models import ApiItem
from user.serializers import UserSerializer
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
                  'is_active', 'is_employee', 'user_profile']
        read_only_fields = ['id', 'date_joined', 'is_active']


class EmployeeSerializer(CustomModelSerializer):
    """
    MEH: Main Employee full information
    """
    user = UserEmployeeSerializer(required=False) # MEH: Nested (User Model) Information
    level_display = serializers.StringRelatedField(source='level')

    class Meta:
        model = Employee
        fields = ['id', 'user', 'level', 'level_display', 'rate']
        read_only_fields = ['rate']

    def create(self, validated_data, **kwargs): # MEH: Nested create Employee with User information and Profile, just single Employee per req
        user_data = validated_data.pop('user', {})
        if user_data:
            user_serializer = UserEmployeeSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            employee = Employee.objects.create(**validated_data, user=user, full_name=user.get_full_name())
            return employee
        else:
            raise serializers.ValidationError({'employee': TG_DATA_WRONG})

    def update(self, instance, validated_data, **kwargs): # MEH: Nested update for Employee with User & Profile
        user_data = validated_data.pop('user', {})
        if user_data:
            user_serializer = UserEmployeeSerializer(instance=instance.user, data=user_data, partial=(self.context.get('request').method == 'PATCH'))
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            setattr(instance, 'full_name', user.get_full_name())
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmployeeLevelSerializer(CustomModelSerializer):
    """
    MEH: Main Employee level full information
    """
    manager = serializers.StringRelatedField()
    api_items = serializers.PrimaryKeyRelatedField(many=True, queryset=ApiItem.objects.filter(category__role_base=False))

    class Meta:
        model = EmployeeLevel
        fields = ['id', 'title', 'description', 'is_active', 'manager', 'api_items']

    def create(self, validated_data, **kwargs):
        employee_level = EmployeeLevel(**validated_data, **kwargs) # MEH: for parse manager in **kwargs
        employee_level.save()
        return employee_level
