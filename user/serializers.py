from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, UserProfile, Introduction, Role, Address, GENDER
from api.responses import *
from api.mixins import CustomModelSerializer, CustomChoiceField, CustomBulkListSerializer
from api.models import ApiItem, ApiCategory


class UserSignUpSerializer(CustomModelSerializer):
    """
    MEH: Api for sign up user with phone number & simple password (min:8) & first name (full name)
    SMS check phone number set in NUXT front end
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
        return user


class UserSignInSerializer(CustomModelSerializer):
    """
    MEH: Api for validate user sign in with phone number and password
    return: Access Token & Refresh Token
    """
    phone_number = serializers.CharField(required=True,
                                         validators=[RegexValidator(regex=r'^09\d{9}$', message=TG_INCORRECT_PHONE_NUMBER)])
    password = serializers.CharField(required=True, min_length=8, max_length=32, write_only=True,
                                     style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['phone_number', 'password']

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


class UserProfileSerializer(CustomModelSerializer):
    """
    MEH: Profile information about user (Gender, Photo, Job, ...)
    """
    user = serializers.SerializerMethodField()
    gender = CustomChoiceField(choices=GENDER.choices, initial=GENDER.UNDEFINED)
    gender_display = serializers.SerializerMethodField()
    description = serializers.CharField(default=None, allow_null=True, style={'base_template': 'textarea.html'})
    job = serializers.CharField(default=None, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'birth_date', 'description', 'job', 'gender', 'gender_display']

    @staticmethod
    def get_user(obj):
        return str(obj)

    @staticmethod
    def get_gender_display(obj):
        return obj.get_gender_display()


class UserSerializer(CustomModelSerializer):
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
    role_display = serializers.StringRelatedField(source='role')
    introduce_from_display = serializers.StringRelatedField(source='introduce_from')
    invite_user_count = serializers.SerializerMethodField()
    introducer = serializers.StringRelatedField()
    province = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'national_id', 'date_joined', 'order_count', 'last_order_date', 'email', 'province',
                  'is_active', 'role', 'role_display', 'introduce_from', 'introduce_from_display', 'introducer', 'invite_user_count', 'user_profile']
        read_only_fields = ['date_joined', 'is_active']
        list_serializer_class = CustomBulkListSerializer

    @staticmethod
    def get_invite_user_count(obj): # MEH: get Count of invite_user_list (in user list QS)
        try:
            return obj.invite_user_count
        except AttributeError:
            return 0

    @staticmethod
    def get_province(obj): # MEH: Get default province from user address list if any (To show and filter in user list QS)
        try:
            return obj.default_province
        except AttributeError:
            return None

    @staticmethod
    def validate_filed(user_data, pk=None): # MEH: validate phone or national_id is not in DB (except self data for update)
        if 'phone_number' in user_data:
            if User.objects.exclude(pk=pk).filter(phone_number=user_data['phone_number']).exists():
                raise serializers.ValidationError({'phone_number': TG_UNIQUE_PROTECT})
        if 'national_id' in user_data:
            if user_data['national_id']:
                if User.objects.exclude(pk=pk).filter(national_id=user_data['national_id']).exists():
                    raise serializers.ValidationError({'national_id': TG_UNIQUE_PROTECT})

    def create(self, validated_data, **kwargs): # MEH: Nested create a User with Profile (Just for Admin work) example like from Excel file...
        self.validate_filed(validated_data)
        profile_data = validated_data.pop('user_profile', {})
        user_profile = UserProfile.objects.create(**profile_data)
        user = User.objects.create_user(**validated_data, username=validated_data['phone_number'], user_profile=user_profile)
        return user

    def update(self, instance, validated_data, **kwargs): # MEH: Nested update for User Profile
        self.validate_filed(validated_data, instance.pk)
        profile_data = validated_data.pop('user_profile', {})
        for attr, value in validated_data.items():
            if attr == 'phone_number' and instance.phone_number != value:
                instance.phone_number_verified = False
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.user_profile
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
        list_serializer_class = CustomBulkListSerializer


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


class AddressSerializer(CustomModelSerializer):
    """
    MEH: User Address full information
    """
    submit_date = serializers.HiddenField(default=timezone.now) # MEH: Set date time to now every time address change!
    postal_code = serializers.CharField(default=None)
    location = GeometryField()
    user = serializers.SerializerMethodField()

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

    def create(self, validated_data, **kwargs):
        address = Address(**validated_data, **kwargs) # MEH: for parse User in **kwargs
        address.save()
        return address


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
