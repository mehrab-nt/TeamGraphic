from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from datetime import timedelta, datetime, timezone
from financial.models import Company
from .models import User, UserProfile, Introduction, Role, Address, GENDER
from api.responses import *
from api.mixins import CustomModelSerializer, CustomChoiceField, CustomBulkListSerializer
from api.models import ApiItem
from file_manager.images import *
import random
from .tasks import send_phone_verification_code
from django.core.cache import cache


class UserSignUpManualSerializer(CustomModelSerializer):
    """
    MEH: Api for sign up user with phone number & first name (full name)
    with simple password (min 8) without code verification (in person)
    """
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    password = serializers.CharField(required=True, min_length=8, max_length=32, write_only=True,
                                     style={'input_type': 'password'})
    first_name = serializers.CharField(required=True, min_length=3, max_length=73)
    introduce_code = serializers.CharField(min_length=8, max_length=8, allow_blank=True, allow_null=True, write_only=True, required=False)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'first_name', 'introduce_from', 'introduce_code']

    def validate_phone_number(self, data): # MEH: Validate if Phone Number is new or not
        if self.Meta.model.objects.filter(phone_number=data).exists():
            raise serializers.ValidationError(TG_SIGNUP_INTEGRITY)
        return data

    def create(self, validated_data, **kwargs): # MEH: override create super method (POST)
        password = validated_data.pop('password') # MEH: Safe drop password from data
        code = validated_data.pop('introduce_code', None)
        if code:
            validated_data['introducer'] = User.objects.filter(public_key=code).first()
        user = User.objects.create_user(**validated_data, username=validated_data['phone_number'])
        user.set_password(password) # MEH: Set Password with Hashing
        user.save()
        return {
            'user': {
                'id': user.id,
                'phone_number': user.phone_number
            }
        }


class UserSignUpRequestSerializer(CustomModelSerializer):
    """
    MEH: Api for request sign up User with just phone number and wait for SMS code
    """
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])

    class Meta:
        model = User
        fields = ['phone_number']

    def validate_phone_number(self, data): # MEH: Validate if Phone Number is new or not
        if self.Meta.model.objects.filter(phone_number=data).exists():
            raise serializers.ValidationError(TG_SIGNUP_INTEGRITY)
        return data

    def create(self, validated_data, **kwargs):
        phone_number = validated_data['phone_number']
        code = str(random.randint(1000, 9999))
        cache.set(f"sms-code:{phone_number}", code, timeout=300) # MEH: 5 min verify code!
        send_phone_verification_code.delay(code, phone_number) # MEH: Celery task run in background
        return TG_VERIFICATION_CODE_SENT


class UserSignUpVerifySerializer(UserSignUpRequestSerializer):
    """
    MEH: Api for verify sign up user with phone number & SMS code & first name (full name)
    without password!
    """
    sms_code = serializers.CharField(min_length=4, max_length=4, required=True, allow_null=False, write_only=True)
    first_name = serializers.CharField(required=True, min_length=3, max_length=73)
    introduce_code = serializers.CharField(min_length=8, max_length=8, allow_blank=True, allow_null=True, write_only=True, required=False)

    class Meta:
        model = User
        fields = ['phone_number', 'sms_code', 'first_name', 'introduce_from', 'introduce_code']

    def validate(self, data):
        phone_number = data['phone_number']
        code = data['sms_code']
        cached_code = cache.get(f"sms-code:{phone_number}")
        if cached_code is None or str(cached_code) != str(code):
            raise serializers.ValidationError(TG_AUTH_INVALID_CODE)
        return data

    def create(self, validated_data, **kwargs): # MEH: override create super method (POST)
        phone_number = validated_data['phone_number']
        validated_data.pop('sms_code')
        cache.delete(f"sms-code:{phone_number}") # MEH: Delete sms code from cache
        introduce_code = validated_data.pop('introduce_code', None)
        if introduce_code:
            validated_data['introducer'] = User.objects.filter(public_key=introduce_code).first()
            if validated_data['introducer']:
                validated_data['introducer'].invite_user_count += 1
                validated_data['introducer'].save(update_fields=['invite_user_count'])
        user = User.objects.create_user(**validated_data, username=phone_number, phone_number_verified=True)
        user.save()
        refresh = RefreshToken.for_user(user) # MEH: Auto signed in
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'full_name': user.get_full_name(),
            }
        }


class UserSignInRequestSerializer(UserSignUpRequestSerializer):
    """
    MEH: Inherit from UserSignUpRequestSerializer to request SMS code -> just change validate_phone_number
    """
    def validate_phone_number(self, data): # MEH: Validate if Phone Number is exist or not
        if self.Meta.model.objects.filter(phone_number=data).exists():
            return data
        raise serializers.ValidationError(TG_SIGNIN_ERROR)

    @staticmethod
    def increase_refresh_exp_date(refresh, user, days=30):
        now = datetime.now(timezone.utc)
        custom_lifetime = timedelta(days=days)
        refresh.set_exp(from_time=now, lifetime=custom_lifetime)
        try:
            db_token = OutstandingToken.objects.get(jti=refresh['jti'])
            db_token.expires_at = now + custom_lifetime
            db_token.save()
        except OutstandingToken.DoesNotExist:
            OutstandingToken.objects.create(
                user=user,
                jti=refresh['jti'],
                token=str(refresh),
                created_at=now,
                expires_at=now + custom_lifetime
            )
        return refresh


class UserSignInWithCodeSerializer(UserSignInRequestSerializer):
    """
    MEH: Api for validate user sign in with phone number and verify SMS code
    return: Access Token & Refresh Token
    """
    sms_code = serializers.CharField(min_length=4, max_length=4, required=True, allow_null=False, write_only=True)
    keep_me_signed_in = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ['phone_number', 'sms_code', 'keep_me_signed_in']

    def validate(self, data):
        phone_number = data['phone_number']
        cached_code = cache.get(f"sms-code:{phone_number}")
        code = data.pop('sms_code', None)
        if cached_code is None or str(cached_code) != str(code):
            raise serializers.ValidationError(TG_AUTH_INVALID_CODE)
        cache.delete(f"sms-code:{phone_number}") # MEH: Delete sms code from cache
        user = User.objects.get(phone_number=phone_number)
        data['user'] = user
        return data

    def create(self, validated_data, **kwargs):
        user = validated_data['user']
        if not user.phone_number_verified:
            user.phone_number_verified = True
            user.save(update_fields=['phone_number_verified'])
        refresh = RefreshToken.for_user(user)
        keep_signed_in = validated_data.get('keep_me_signed_in', False)
        if keep_signed_in:
            refresh = self.increase_refresh_exp_date(refresh, user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'full_name': user.get_full_name(),
            }
        }


class UserResendCodeSerializer(UserSignUpRequestSerializer):
    """
    MEH: Api for request re-send code for sign-up or sign-in
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


class UserSignInWithPasswordSerializer(UserSignInRequestSerializer):
    """
    MEH: Api for validate user sign in with phone number and password
    return: Access Token & Refresh Token
    """
    password = serializers.CharField(required=True, min_length=8, max_length=32, write_only=True,
                                     style={'input_type': 'password'})
    keep_me_signed_in = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'keep_me_signed_in']

    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if not user:
            raise serializers.ValidationError(TG_SIGNIN_ERROR)
        data['user'] = user
        return data

    def create(self, validated_data, **kwargs):
        user = validated_data['user']
        keep_signed_in = validated_data.get('keep_me_signed_in', False)
        refresh = RefreshToken.for_user(user)
        if keep_signed_in:
            refresh = self.increase_refresh_exp_date(refresh, user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'full_name': user.get_full_name(),
            }
        }


class UserSignOutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, data):
        try:
            token = RefreshToken(data.get('refresh'))
            token.blacklist()
            return data
        except TokenError as e:
            raise serializers.ValidationError(e.args[0])


class UserChangePasswordSerializer(CustomModelSerializer):
    """
    MEH: Api for validate user old Password & change it (or set New pass for first time)
    """
    old_password = serializers.CharField(default=None, required=False, min_length=8, max_length=32, write_only=True, allow_null=True,
                                         style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, min_length=8, max_length=32, write_only=True,
                                         style={'input_type': 'password'})
    new_password_repeat = serializers.CharField(required=True, min_length=8, max_length=32, write_only=True,
                                                style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'new_password_repeat']

    def validate(self, data):
        request_user = self.context['request'].user
        if data['new_password'] != data['new_password_repeat']:
            raise serializers.ValidationError(TG_WRONG_REPEAT_PASSWORD)
        if request_user.has_usable_password(): # MEH: User has a Password already
            if not data['old_password'] or not request_user.check_password(data['old_password']):
                raise serializers.ValidationError(TG_WRONG_PASSWORD)
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return TG_PASSWORD_CHANGED


class UserProfileSerializer(CustomModelSerializer):
    """
    MEH: Profile information about user (Gender, Photo, Job, ...)
    """
    user = serializers.SerializerMethodField()
    gender = CustomChoiceField(choices=GENDER.choices, initial=GENDER.UNDEFINED)
    gender_display = serializers.SerializerMethodField()
    description = serializers.CharField(default=None, allow_null=True, style={'base_template': 'textarea.html'})
    job = serializers.CharField(default=None, allow_null=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'profile_image', 'birth_date', 'description', 'job', 'gender', 'gender_display']

    @staticmethod
    def get_user(obj):
        return str(obj)

    @staticmethod
    def get_gender_display(obj):
        return obj.get_gender_display()

    def validate_profile_image(self, image): # MEH: Check uploaded Image for profile (Optimize in filemanager.images.py)
        if image:
            validate_image = self.validate_upload_image(image, max_image_size=2, max_width=1024, max_height=1024)
            if validate_image:
                return optimize_image(validate_image)
        return None


class UserBriefSerializer(CustomModelSerializer):
    """
    MEH: Brief User information for list
    """
    company = serializers.SerializerMethodField()
    credit = serializers.SerializerMethodField()
    role_display = serializers.StringRelatedField(source='role')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'order_count', 'last_order_date', 'company', 'credit', 'role_display']
        read_only_fields = ['id', 'first_name', 'last_name', 'phone_number', 'order_count', 'last_order_date', 'company', 'credit', 'role_display']

    @staticmethod
    def get_company(obj):
        company = getattr(obj, 'company', None)
        if company:
            return company.name
        return None

    @staticmethod
    def get_credit(obj):
        credit = getattr(obj, 'credit', None)
        if credit:
            return credit.total_amount
        return 0


class UserSerializer(UserBriefSerializer):
    """
    MEH: Main User full information
    """
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    first_name = serializers.CharField(required=True, min_length=3, max_length=73)
    last_name = serializers.CharField(min_length=3, max_length=73, allow_blank=True, allow_null=False)
    national_id = serializers.CharField(required=False, allow_null=True,
                                        validators=[RegexValidator(regex='^\d{10}$', message=TG_INCORRECT_NATIONAL_ID)])
    user_profile = UserProfileSerializer(required=False)
    introduce_from_display = serializers.StringRelatedField(source='introduce_from')
    introducer = serializers.StringRelatedField()
    province = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'order_count', 'last_order_date', 'email', 'province',
                  'is_active', 'role', 'role_display', 'introduce_from', 'introduce_from_display', 'introducer', 'invite_user_count', 'user_profile', 'company', 'credit']
        read_only_fields = ['date_joined', 'is_active', 'invite_user_count', 'company', 'credit']

    @staticmethod
    def get_province(obj): # MEH: Get default province from user address list if any (To show and filter in user list QS)
        try:
            return obj.default_province
        except AttributeError:
            return None

    def validate_phone_number(self, value):
        if self.instance and self.instance.phone_number == value:
            return value
        if User.objects.exclude(pk=self.instance.pk if self.instance else None).filter(phone_number=value).exists():
            raise serializers.ValidationError(TG_UNIQUE_PROTECT)
        return value

    def validate_national_id(self, value):
        if self.instance and self.instance.national_id == value:
            return value
        if User.objects.exclude(pk=self.instance.pk if self.instance else None).filter(national_id=value).exists():
            raise serializers.ValidationError(TG_UNIQUE_PROTECT)
        return value

    def create(self, validated_data, **kwargs): # MEH: Nested create a User with Profile (Just for Admin work) example like from Excel file...
        profile_data = validated_data.pop('user_profile', {})
        user_profile = UserProfile.objects.create(**profile_data)
        user = User.objects.create_user(**validated_data, username=validated_data['phone_number'], user_profile=user_profile)
        return user

    def update(self, instance, validated_data, **kwargs): # MEH: Nested update for User Profile
        profile_data = validated_data.pop('user_profile', {})
        for attr, value in validated_data.items():
            if attr == 'phone_number' and instance.phone_number != value:
                instance.phone_number_verified = False
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.user_profile
            new_image = profile_data.get('profile_image', None)
            if new_image: # MEH: check if new valid image here, delete old image
                if profile.profile_image:
                    profile.profile_image.delete(save=False)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance


class UserProfileImportDataSerializer(UserSerializer):
    """
    MEH: for handle User-Profile field -> Excel import user list
    """
    class Meta:
        model = UserProfile
        fields = ['gender', 'job', 'description']


class UserImportDataSerializer(UserSerializer):
    """
    MEH: for handle User field -> Excel import user list
    """
    user_profile = UserProfileImportDataSerializer(required=False)
    class Meta:
        model = User
        fields = ['phone_number', 'first_name', 'last_name', 'national_id', 'order_count', 'last_order_date', 'email', 'province',
                  'is_active', 'role', 'introduce_from', 'accounting_id', 'accounting_name', 'user_profile']
        list_serializer_class = CustomBulkListSerializer # MEH: for validate all data and response with number


class UserImportFieldDataSerializer(CustomModelSerializer):
    """
    MEH: temporary Serializer Class for handle Excel & user role -> (User import list)
    """
    excel_file = serializers.FileField(required=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['role', 'excel_file']


class UserDownloadDataSerializer(UserSerializer):
    """
    MEH: for handle User list field for write in Excel file -> (User download list)
    """
    role = serializers.StringRelatedField()
    gender = serializers.CharField(source='user_profile.gender')
    job = serializers.CharField(source='user_profile.job')
    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['phone_number', 'first_name', 'last_name', 'date_joined', 'national_id', 'order_count', 'last_order_date', 'email', 'province',
                  'is_active', 'invite_user_count', 'role', 'introduce_from', 'accounting_id', 'accounting_name', 'gender', 'job']
        read_only_fields = ['phone_number', 'first_name', 'last_name', 'national_id', 'order_count', 'last_order_date', 'email', 'province',
                  'is_active', 'invite_user_count', 'introduce_from', 'accounting_id', 'accounting_name', 'gender', 'job']

    @staticmethod
    def get_date_joined(obj):
        if obj.date_joined:
            return obj.date_joined.strftime('%Y-%m-%d %H:%M')
        return None


class UserKeySerializer(CustomModelSerializer):
    """
    MEH: Public & Private key form user (Sub serializer from User)
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user', 'public_key', 'private_key']
        read_only_fields = ['public_key', 'private_key']

    @staticmethod
    def get_user(obj):
        return str(obj)


class UserAccountingSerializer(CustomModelSerializer):
    """
    MEH: User accounting information (Sub serializer from User)
    """
    user = serializers.SerializerMethodField()
    role = serializers.StringRelatedField()
    first_name = serializers.CharField(required=True, min_length=3, max_length=73)
    last_name = serializers.CharField(min_length=3, max_length=73, allow_blank=True, allow_null=False)
    accounting_id = serializers.IntegerField(default=None,
                                             validators=[RegexValidator(regex=r'^\d{1,16}$', message=TG_DATA_WRONG)])
    accounting_name = serializers.CharField(default=None)

    class Meta:
        model = User
        fields = ['id', 'user', 'phone_number', 'national_id', 'first_name', 'last_name',
                  'role', 'accounting_id', 'accounting_name']
        read_only_fields = ['phone_number', 'national_id']

    def validate_accounting_id(self, data): # Make sure is Unique
        if not data:
            return data
        if self.instance:
            if User.objects.exclude(pk=self.instance.id).filter(accounting_id=data).exists():
                raise serializers.ValidationError(TG_UNIQUE_PROTECT)
        return data

    @staticmethod
    def get_user(obj):
        return str(obj)


class UserActivationSerializer(CustomModelSerializer):
    """
    MEH: User Role and is_active information (Sub serializer from User)
    """
    user = serializers.SerializerMethodField()
    role_display = serializers.StringRelatedField(source='role')

    class Meta:
        model = User
        fields = ['id', 'user', 'role_display', 'is_active']

    @staticmethod
    def get_user(obj):
        return str(obj)


class UserManualVerifyPhoneSerializer(CustomModelSerializer):
    """
    MEH: for Manually verified User phone number (Sub serializer from User)
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user', 'phone_number', 'phone_number_verified']
        read_only_fields = ['phone_number']

    @staticmethod
    def get_user(obj):
        return str(obj)


class AddressBriefSerializer(CustomModelSerializer):
    """
    MEH: User Address brief information
    """
    class Meta:
        model = Address
        fields = ['id', 'receiver_name', 'province', 'city', 'content', 'plate_number', 'unit_number']

    def to_representation(self, instance): # MEH: for display Farsi name in Api alongside id
        data = super().to_representation(instance)
        data['province_display'] = instance.province.__str__()
        data['city_display'] = instance.city.__str__()
        return data


class AddressSerializer(CustomModelSerializer):
    """
    MEH: User Address full information
    """
    postal_code = serializers.CharField(default=None)
    location = GeometryField()
    user = serializers.SerializerMethodField()
    receiver_phone_number = serializers.CharField(required=True,
                                                  validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    sender_phone_number = serializers.CharField(required=False,
                                                validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])

    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']

    @staticmethod
    def get_user(obj):
        return obj.user.get_full_name()

    def to_representation(self, instance): # MEH: for display Farsi name in Api alongside id
        data = super().to_representation(instance)
        data['province_display'] = instance.province.__str__()
        data['city_display'] = instance.city.__str__()
        return data


class IntroductionSerializer(CustomModelSerializer):
    """
    MEH: Introduction full Information (Instagram, Telegram, Google, ...)
    """
    class Meta:
        model = Introduction
        fields = '__all__'


class RoleSerializer(CustomModelSerializer):
    """
    MEH: Role full Information (Customer, Co-Worker, ...)
    """
    description = serializers.CharField(default=None, style={'base_template': 'textarea.html'})
    api_items = serializers.PrimaryKeyRelatedField(many=True, queryset=ApiItem.objects.filter(category__role_base=True))

    class Meta:
        model = Role
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action == 'list': # MEH: api-item in list view
            data.pop('api_items', None)
        return data
