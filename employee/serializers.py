from rest_framework import serializers
from .models import Employee
from user.models import User
from user.serializers import UserSerializer
from rest_framework.exceptions import PermissionDenied
from api.mixins import CustomModelSerializer
from api.responses import *


# MEH: Handle important field for Employee
class UserEmployeeSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'email',
                  'is_active', 'invite_user_count', 'user_profile']
        read_only_fields = ['id', 'date_joined', 'is_active']


# MEH: Main Employee full information
class EmployeeSerializer(CustomModelSerializer):
    user = UserEmployeeSerializer(required=False)

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('level', 'rate')

    # MEH: Nested create employee with user information and profile (Just for Admin work) just single Employee
    def create(self, validated_data, **kwargs):
        if isinstance(validated_data, list): # MEH: ignore bulk create
            raise PermissionDenied(TG_PERMISSION_DENIED)
        else: # MEH: Handle single create
            user_data = validated_data.pop('user', {})
            if user_data:
                user_serializer = UserEmployeeSerializer(data=user_data)
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()
                user.is_employee=True
                user.save()
                employee = Employee.objects.create(**validated_data, user=user)
                return employee
            else:
                raise serializers.ValidationError({'user': TG_DATA_WRONG})

    # MEH: Nested update for employee with profile
    def update(self, instance, validated_data, **kwargs):
        user_data = validated_data.pop('user', {})
        if user_data:
            user_serializer = UserEmployeeSerializer(instance=instance.user, data=user_data, partial=(self.context.get('request').method == 'PATCH'))
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
