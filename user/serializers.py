from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import IntegrityError
from .models import User, UserProfile, Introduction, Role, Address
from api.responses import *


# MEH: Api for sign up user with phone number & simple password (min:8) & first name (full name)
# SMS check phone number set in NUXT
class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=32, required=True,
                                     error_messages={'blank': TG_DATA_EMPTY})
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    first_name = serializers.CharField(min_length=3, max_length=73, required=True)
    introduce_code = serializers.CharField(write_only=True, min_length=8, max_length=8, allow_null=True)

    def validate_phone_number(self, data):
        if self.Meta.model.objects.filter(phone_number=data).exists():
            raise serializers.ValidationError(TG_UNIQUE_PROTECT)
        return data

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'first_name', 'introduce_from', 'introduce_code']

    # MEH: override create super method (POST)
    def create(self, validated_data, **kwargs):
        try:
            code = validated_data.pop('introduce_code', None)
            if code:
                validated_data['introducer'] = User.objects.filter(public_key=code).first()
            user = User.objects.create_user(**validated_data, username=validated_data['phone_number'])
        except IntegrityError:
            raise serializers.ValidationError(TG_SIGNUP_INTEGRITY)
        return user


# MEH: Api for validate user sign in with phone number and password -> return: Access Token & Refresh Token
class UserSignInSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    password = serializers.CharField(write_only=True, min_length=8, max_length=32, required=True,
                                     error_messages={'blank': TG_DATA_EMPTY})
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
    user = serializers.SerializerMethodField()
    gender_display = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'birth_date', 'description', 'job', 'gender', 'gender_display']

    @staticmethod
    def get_user(obj):
        return str(obj)

    @staticmethod
    def get_gender_display(obj):
        return obj.get_gender_display()


# MEH: Main user full information
class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    national_id = serializers.CharField(required=False, allow_null=True,
                                        validators=[RegexValidator(regex='^\d{10}$', message=TG_INCORRECT_NATIONAL_ID)])
    user_profile = UserProfileSerializer(required=False)
    introduce_from_display = serializers.StringRelatedField(source='introduce_from')
    invite_user_count = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_invite_user_count(obj):
        try:
            return obj.invite_user_list.all().count()
        except AttributeError:
            return None

    @staticmethod
    def validate_filed(user_data, pk=None):
        if 'phone_number' in user_data:
            if User.objects.exclude(pk=pk).filter(phone_number=user_data['phone_number']).exists():
                raise serializers.ValidationError({'phone_number': TG_UNIQUE_PROTECT})
        if 'national_id' in user_data:
            if user_data['national_id']:
                if User.objects.exclude(pk=pk).filter(national_id=user_data['national_id']).exists():
                    raise serializers.ValidationError({'national_id': TG_UNIQUE_PROTECT})

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'email',
                  'is_active', 'role', 'introduce_from', 'introduce_from_display', 'introducer', 'invite_user_count', 'user_profile']
        read_only_fields = ['id', 'date_joined', 'is_active', 'role']

    # MEH: Nested create user with profile (Just for Admin work) example like from file... Single or Bulk
    def create(self, validated_data, **kwargs):
        if isinstance(validated_data, list): # MEH: Handle bulk create
            user_list = []
            for user_data in validated_data:
                self.validate_filed(user_data)
                profile_data = user_data.pop('user_profile', {})
                user_profile = UserProfile.objects.create(**profile_data)
                user = User.objects.create_user(**user_data, username=user_data['phone_number'], user_profile=user_profile)
                user_list.append(user)
            return user_list
        else: # MEH: Handle single create
            self.validate_filed(validated_data)
            profile_data = validated_data.pop('user_profile', {})
            user_profile = UserProfile.objects.create(**profile_data)
            user = User.objects.create_user(**validated_data, username=validated_data['phone_number'], user_profile=user_profile)
            return user

    # MEH: Nested update for user profile
    def update(self, instance, validated_data, **kwargs):
        self.validate_filed(validated_data, instance.pk)
        profile_data = validated_data.pop('user_profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.user_profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance


# MEH: Handle important field for Employee
class UserEmployeeSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'email',
                  'is_active', 'invite_user_count', 'user_profile']
        read_only_fields = ['id', 'date_joined', 'is_active']


# MEH: Public & Private key for user
class UserKeySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user', 'public_key', 'private_key']

    @staticmethod
    def get_user(obj):
        return str(obj)


# MEH: User accounting information
class UserAccountingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    role = serializers.StringRelatedField()
    accounting_id = serializers.IntegerField(allow_null=True,
                                             validators=[RegexValidator(regex=r'^\d{1,16}$', message=TG_DATA_WRONG)])

    def validate_accounting_id(self, data):
        if not data:
            return data
        if self.instance:
            if User.objects.exclude(pk=self.instance.id).filter(accounting_id=data).exists():
                raise serializers.ValidationError(TG_UNIQUE_PROTECT)
        return data

    class Meta:
        model = User
        fields = ['id', 'user', 'phone_number', 'national_id', 'first_name', 'last_name',
                  'role', 'accounting_id', 'accounting_name']
        read_only_fields = ['phone_number', 'role', 'national_id']

    @staticmethod
    def get_user(obj):
        return str(obj)


# MEH: User Role and is_active information
class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    role_display = serializers.StringRelatedField(source='role')

    class Meta:
        model = User
        fields = ['id', 'user', 'role', 'role_display', 'is_active']

    @staticmethod
    def get_user(obj):
        return str(obj)


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

    def create(self, validated_data, **kwargs):
        if isinstance(validated_data, list): # MEH: Handle bulk create
            address_list = []
            for address_data in validated_data:
                address = Address(**address_data, **kwargs)
                address.save()
                address_list.append(address)
            return address_list
        else:
            address = Address(**validated_data, **kwargs)
            address.save()
            return address


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
