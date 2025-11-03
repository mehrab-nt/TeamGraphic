from rest_framework import serializers
from .models import Employee, EmployeeLevel
from user.models import User
from api.models import ApiItem
from user.serializers import UserSerializer, UserSignInWithPasswordSerializer, authenticate
from api.mixins import CustomModelSerializer
from api.responses import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator
import random
from user.tasks import send_phone_verification_code
from django.core.cache import cache


class EmployeeSignInWithPasswordSerializer(UserSignInWithPasswordSerializer):
    """
    MEH: Api for validate user sign in with phone number and password
    return: Access Token & Refresh Token
    """
    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if user:
            if getattr(user, 'is_employee', False):
                data['user'] = user
                return data
        raise serializers.ValidationError(TG_SIGNIN_ERROR)


class UserEmployeeSerializer(UserSerializer):
    """
    MEH: Handle important field form User model in Employee Serializer
    Create & Update Handle in UserSerializer...
    """
    is_employee = serializers.HiddenField(default=True)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'email',
                  'is_active', 'is_employee', 'user_profile']
        read_only_fields = ['id', 'date_joined']


class EmployeeBriefSerializer(CustomModelSerializer):
    """
    MEH: Brief Employee information for list
    """
    phone_number = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    level_display = serializers.StringRelatedField(source='level')
    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'phone_number', 'email', 'level', 'level_display', 'is_active', 'rate', 'date_joined']
        read_only_fields = ['id', 'rate']

    @staticmethod
    def get_phone_number(obj):
        return obj.user.phone_number

    @staticmethod
    def get_email(obj):
        return obj.user.email

    @staticmethod
    def get_is_active(obj):
        return obj.user.is_active

    @staticmethod
    def get_date_joined(obj):
        return obj.user.date_joined


class EmployeeSerializer(CustomModelSerializer):
    """
    MEH: Main Employee full information
    """
    user = UserEmployeeSerializer(required=False) # MEH: Nested (User Model) Information
    phone_number = serializers.CharField(required=True, write_only=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    national_id = serializers.CharField(required=True, write_only=True,
                                        validators=[RegexValidator(regex='^\d{10}$', message=TG_INCORRECT_NATIONAL_ID)])
    level_display = serializers.StringRelatedField(source='level')

    class Meta:
        model = Employee
        fields = ['id', 'user', 'level', 'level_display', 'rate', 'phone_number', 'national_id']
        read_only_fields = ['id', 'rate']

    def validate_phone_number(self, value):
        if self.instance and self.instance.user.phone_number == value:
            return value
        if User.objects.exclude(pk=self.instance.user.pk if self.instance else None).filter(phone_number=value).exists():
            raise serializers.ValidationError('شماره موبایل ' + TG_UNIQUE_PROTECT)
        return value

    def validate_national_id(self, value):
        if self.instance and self.instance.user.national_id == value:
            return value
        if User.objects.exclude(pk=self.instance.user.pk if self.instance else None).filter(national_id=value).exists():
            raise serializers.ValidationError('کد ملی ' + TG_UNIQUE_PROTECT)
        return value

    def create(self, validated_data, **kwargs): # MEH: Nested create Employee with User information and Profile, just single Employee per req
        user_data = validated_data.pop('user', {})
        if user_data:
            user_data['phone_number'] = validated_data.pop('phone_number')
            user_data['national_id'] = validated_data.pop('national_id')
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
            user_data['phone_number'] = validated_data.pop('phone_number')
            user_data['national_id'] = validated_data.pop('national_id')
            user_serializer = UserEmployeeSerializer(instance=instance.user, data=user_data, partial=(self.context.get('request').method == 'PATCH'))
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            setattr(instance, 'full_name', user.get_full_name())
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmployeeChoiceListSerializer(CustomModelSerializer):
    """
    MEH: Employee brief Information for Choice List
    """
    class Meta:
        model = Employee
        fields = ['id', 'full_name']


class EmployeeResetPasswordRequestSerializer(serializers.Serializer):
    """
    MEH: Api for request reset password with phone number
    """
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])

    @staticmethod
    def validate_phone_number(data): # MEH: Validate if Phone Number is new or not
        if User.objects.filter(phone_number=data, is_employee=True).exists():
            return data
        raise serializers.ValidationError(TG_USER_NOT_FOUND_BY_PHONE)

    def create(self, validated_data, **kwargs):
        phone_number = validated_data['phone_number']
        code = str(random.randint(1000, 9999))
        cache.set(f"sms-code:{phone_number}", code, timeout=300) # MEH: 5 min verify code!
        send_phone_verification_code.delay(code, phone_number) # MEH: Celery task run in background
        return TG_VERIFICATION_CODE_SENT


class EmployeeResendResetPasswordRequestSerializer(EmployeeResetPasswordRequestSerializer):
    """
    MEH: Api for request re-send code for reset password
    """
    def validate_phone_number(self, data): # MEH: Override Validate phone_number for both exist or not
        cache_key = f'sms-code:{data}'
        cached_code = cache.get(cache_key)
        if not cached_code: # MEH: Check if this phone number really want resend code, or it's a new request!
            raise serializers.ValidationError(TG_VERIFICATION_CODE_RESENT_DENIED)
        return data

    def create(self, validated_data, **kwargs):
        super().create(validated_data, **kwargs)
        return TG_VERIFICATION_CODE_RESENT


class EmployeeChangeVerifySerializer(EmployeeResetPasswordRequestSerializer):
    """
    MEH: Api for verify sign up user with phone number & SMS code & first name (full name)
    without password!
    """
    sms_code = serializers.CharField(min_length=4, max_length=4, required=True, allow_null=False, write_only=True)
    new_password = serializers.CharField(required=True, min_length=8, max_length=32, write_only=True,
                                         style={'input_type': 'password'})
    new_password_repeat = serializers.CharField(required=True, min_length=8, max_length=32, write_only=True,
                                                style={'input_type': 'password'})

    def validate(self, data):
        phone_number = data['phone_number']
        code = data['sms_code']
        cached_code = cache.get(f"sms-code:{phone_number}")
        if cached_code is None or str(cached_code) != str(code):
            raise serializers.ValidationError(TG_AUTH_INVALID_CODE)
        if data['new_password'] != data['new_password_repeat']:
            raise serializers.ValidationError(TG_WRONG_REPEAT_PASSWORD)
        return data


    def create(self, validated_data, **kwargs): # MEH: override create super method (POST)
        employee = Employee.objects.get(user__phone_number=validated_data['phone_number'])
        employee.user.set_password(validated_data['new_password'])
        employee.user.save()
        return TG_PASSWORD_CHANGED


class EmployeeApiList(CustomModelSerializer):
    """
    MEH: Employee API List for check permissions
    """
    api_items = serializers.StringRelatedField(many=True)

    class Meta:
        model = EmployeeLevel
        fields = ['id', 'api_items']


class EmployeeLevelSerializer(CustomModelSerializer):
    """
    MEH: Main Employee level full information
    """
    manager_display = serializers.StringRelatedField(source='manager')
    api_items = serializers.PrimaryKeyRelatedField(many=True, queryset=ApiItem.objects.filter(category__role_base=False))

    class Meta:
        model = EmployeeLevel
        fields = ['id', 'title', 'description', 'is_active', 'manager', 'manager_display', 'api_items']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action == 'list': # MEH: api-item in list view
            data.pop('api_items', None)
        return data
