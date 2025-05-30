from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims if you want
        token['role'] = user.role.title if user.role else None
        return token

    def validate(self, attrs):
        attrs['username'] = attrs.get('phone_number')
        return super().validate(attrs)
