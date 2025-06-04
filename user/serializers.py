from rest_framework import serializers
from .models import User, UserProfile, Role, Introduction


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'title', 'description', 'sort_number']


class IntroductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Introduction
        fields = ['id', 'title', 'number', 'sort_number']


class UserProfileSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source='get_gender_display')  # Show gender display value

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'birth_date', 'gender', 'description', 'job']


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)  # Nested UserProfile serializer
    role = RoleSerializer(read_only=True)  # Nested Role serializer

    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'email', 'first_name', 'last_name', 'user_profile', 'role']


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        # Use Django's built-in method to hash the password
        user = User(
            phone_number=validated_data['phone_number'],
            username=validated_data['phone_number'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
