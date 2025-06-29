from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile, GENDER, Introduction, Role, Address
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from backend.tg_massages import TG_SIGNUP_INTEGRITY, TG_SIGN_ERROR


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    phone_number = serializers.CharField(min_length=11, max_length=11, required=True)
    first_name = serializers.CharField(min_length=3, max_length=73, required=True)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'first_name']

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                phone_number=validated_data['phone_number'],
                username=validated_data['phone_number'],
                first_name=validated_data['first_name'],
                password=validated_data['password']
            )
        except IntegrityError:
            raise serializers.ValidationError(TG_SIGNUP_INTEGRITY)
        return user


class UserSignInSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if not user:
            raise serializers.ValidationError(TG_SIGN_ERROR)
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
            }
        }


class UserProfileSerializer(serializers.ModelSerializer):
    introduce_from_display = serializers.StringRelatedField(source='introduce_from')
    class Meta:
        model = UserProfile
        fields = ['user', 'birth_date', 'description', 'introduce_from', 'introduce_from_display', 'job', 'gender']
        read_only_fields = ['id', 'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['gender_display'] = instance.get_gender_display()
        return data


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()
    is_active = serializers.BooleanField(read_only=True)
    role_display = serializers.StringRelatedField(source='role')

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'email',
                  'is_active', 'role', 'role_display', 'user_profile',]
        read_only_fields = ['id', 'date_joined']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('user_profile', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.user_profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance


class UserKeySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user', 'public_key', 'private_key']
        read_only_fields = ['id']

    @staticmethod
    def get_user(instance):
        return str(instance)


class UserAccountingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    role_display = serializers.StringRelatedField(source='role')

    class Meta:
        model = User
        fields = ['id', 'user', 'phone_number', 'national_id', 'email', 'first_name', 'last_name',
                  'role', 'role_display', 'accounting_id', 'accounting_name']
        read_only_fields = ['id', 'phone_number']

    @staticmethod
    def get_user(instance):
        return str(instance)


class IntroductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Introduction
        fields = '__all__'
        read_only_fields = ['id']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['id']


class AddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    submit_date = serializers.HiddenField(default=timezone.now)
    # user = serializers.RelatedField(queryset=User.objects.all())

    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['id', 'user']
