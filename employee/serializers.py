from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import IntegrityError
from .models import Employee
from user.models import User, UserProfile
from user.serializers import UserEmployeeSerializer
from rest_framework.exceptions import PermissionDenied

from api.responses import *


# MEH: Main user full information
class EmployeeSerializer(serializers.ModelSerializer):
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
