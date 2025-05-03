from django.contrib.auth.models import Group, User
from rest_framework import serializers
from django.core import validators
from .models import UserProfile, GENDER


class UserSerializer(serializers.ModelSerializer):
    user_profile = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_profile']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'user', 'national_id', 'gender', 'description', 'public_key', 'private_key',
                  'accounting_id', 'company', 'last_order_date', 'how_to', 'job', 'credit']
    # id = serializers.IntegerField(read_only=True)
    # phone_number = serializers.CharField(max_length=11, validators=[validators.MinLengthValidator(11)],
    #                                      required=True, allow_blank=False)
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # national_id = serializers.CharField(max_length=10, validators=[validators.MinLengthValidator(10)],
    #                                     required=True, allow_blank=False)
    # birth_date = serializers.DateField(required=False)
    # gender = serializers.ChoiceField(choices=GENDER.choices, default=GENDER.UNDEFINED)
    # description = serializers.CharField(style={'base_template': 'textarea.html'})
    # public_key = serializers.CharField(max_length=8, validators=[validators.MinLengthValidator(8)],
    #                                    required=True, allow_blank=False)
    # private_key = serializers.CharField(max_length=20, required=True, allow_blank=False)
    # accounting_id = serializers.IntegerField(read_only=True)
    # company = serializers.CharField(read_only=True)
    # last_order_date = serializers.DateField(read_only=True)
    # how_to = serializers.CharField(read_only=True)
    # job = serializers.CharField(read_only=True)
    # credit = serializers.CharField(read_only=True)
    #
    # def create(self, validated_data):
    #     """
    #     Create and return a new `User` instance, given the validated data.
    #     """
    #     return Users.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     """
    #     Update and return an existing `User` instance, given the validated data.
    #     """
    #     instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    #     instance.national_id = validated_data.get('national_id', instance.national_id)
    #     instance.birth_date = validated_data.get('birth_date', instance.birth_date)
    #     instance.gender = validated_data.get('gender', instance.gender)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.public_key = validated_data.get('public_key', instance.public_key)
    #     instance.private_key = validated_data.get('private_key', instance.private_key)
    #     instance.save()
    #     return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
