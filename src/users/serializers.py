from django.contrib.auth.models import Group, User
from rest_framework import serializers
from django.core import validators
from .models import UserProfile, GENDER


class UserProfileSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()
    # highlight = serializers.HyperlinkedIdentityField(view_name='user-base', format='html')
    class Meta:
        model = UserProfile
        fields = [
            'phone_number',
            'national_id',
            'gender',
            'description',
            'public_key',
            'private_key',
            'accounting_id',
            'company',
            'last_order_date',
            'how_to',
            'job',
            'credit',
        ]


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    # user_profile = serializers.HyperlinkedRelatedField(read_only=True, view_name='user_profile_details')
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'user_profile',
            'is_staff'
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = [
            'url',
            'name'
        ]
