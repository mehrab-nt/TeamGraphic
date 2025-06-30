from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import IntegrityError
from .models import User, UserProfile, Introduction, Role, Address
from api.tg_massages import TG_SIGNUP_INTEGRITY, TG_SIGNIN_ERROR


# MEH: Api for sign up user with phone number & simple password (min:8) & first name (full name)
# SMS check phone number set in NUXT
class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    phone_number = serializers.CharField(min_length=11, max_length=11, required=True)
    first_name = serializers.CharField(min_length=3, max_length=73, required=True)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'first_name']

    # MEH: override create super method (POST)
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


# MEH: Api for validate user sign in with phone number and password -> return: Access Token & Refresh Token
class UserSignInSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if not user:
            raise serializers.ValidationError(TG_SIGNIN_ERROR)
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
            }
        }


# MEH: Profile information about user (Gender, Photo, Job, ...)
class UserProfileSerializer(serializers.ModelSerializer):
    introduce_from_display = serializers.StringRelatedField(source='introduce_from')
    class Meta:
        model = UserProfile
        fields = ['user', 'birth_date', 'description', 'introduce_from', 'introduce_from_display', 'job', 'gender']
        read_only_fields = ['id', 'user']

    # MEH: For gender Farsi show in Api form
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['gender_display'] = instance.get_gender_display()
        return data


# MEH: Main user full information
class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()
    is_active = serializers.BooleanField(read_only=True)
    role = serializers.StringRelatedField(read_only=True)
    national_id = serializers.CharField(default=None)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'email',
                  'is_active', 'role', 'user_profile',]
        read_only_fields = ['id', 'date_joined']

    # MEH: Nested update for user profile
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


# MEH: Public & Private key for user
class UserKeySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user', 'public_key', 'private_key']

    @staticmethod
    def get_user(instance):
        return str(instance)


# MEH: User accounting information
class UserAccountingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    role = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ['id', 'user', 'phone_number', 'national_id', 'email', 'first_name', 'last_name',
                  'role', 'accounting_id', 'accounting_name']
        read_only_fields = ['phone_number', 'role']

    @staticmethod
    def get_user(instance):
        return str(instance)


# MEH: User Role and is_active information
class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    role_display = serializers.StringRelatedField(source='role')

    class Meta:
        model = User
        fields = ['id', 'user', 'role', 'role_display', 'is_active']

    @staticmethod
    def get_user(instance):
        return str(instance)


# MEH: User Address information
class AddressSerializer(serializers.ModelSerializer):
    submit_date = serializers.HiddenField(default=timezone.now) # MEH: Set date time to now every time address change!

    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']

    # MEH: For display Farsi name in Api alongside id
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['province_display'] = instance.province.__str__()
        data['city_display'] = instance.city.__str__()
        return data


# MEH: Introduction list (Instagram, Telegram, Google, ...)
class IntroductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Introduction
        fields = '__all__'


# MEH: Role list (Customer, Co-Worker, ...)
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
