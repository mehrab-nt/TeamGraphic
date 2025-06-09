from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile, Role, Introduction, Address


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'first_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            username=validated_data['phone_number'],
            first_name=validated_data['first_name'],
            password=validated_data['password']
        )
        return user


class UserSignInSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid phone number or password!')
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
            }
        }


class UserProfileSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source='get_gender_display')  # Show gender display value

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'birth_date', 'gender', 'description', 'introduce_from', 'job']


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'national_id', 'email', 'first_name', 'last_name', 'is_active', 'is_employee', 'user_profile', 'role']


class UserKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'public_key', 'private_key']


class UserAccountingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'national_id', 'email', 'first_name', 'last_name', 'role', 'accounting_id', 'accounting_name']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'title', 'description', 'sort_number']


class IntroductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Introduction
        fields = ['id', 'title', 'number', 'sort_number']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'