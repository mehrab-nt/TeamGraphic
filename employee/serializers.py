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


class EmployeeBriefSerializer(CustomModelSerializer):
    """
    MEH: Brief Employee information for list
    """
    phone_number = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    level_display = serializers.StringRelatedField(source='level')

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'phone_number', 'email', 'level_display', 'is_active']

    @staticmethod
    def get_phone_number(obj):
        return obj.user.phone_number

    @staticmethod
    def get_email(obj):
        return obj.user.email

    @staticmethod
    def get_is_active(obj):
        return obj.user.is_active


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
            user = user_serializer.save() # MEH: Inner Nested create user with profile data
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
    all_api_items = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeLevel
        fields = ['id', 'title', 'description', 'is_active', 'manager', 'api_items', 'all_api_items']

    def get_all_api_items(self, obj): # MEH: Provide all api-item list for UI form generate
        if self.context.get('view').action == 'retrieve': # MEH: Only for get single obj
            items = ApiItem.objects.select_related('category').filter(category__role_base=False)
            return [
                {"id": item.id, "title": item.title, "category": item.category.title}
                for item in items
            ]
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action != 'retrieve': # MEH: Drop all-api-item list if request action not retrieve
            data.pop('all_api_items', None)
        if self.context.get('view').action == 'list': # MEH: api-item in list view
            data.pop('api_items', None)
        return data
