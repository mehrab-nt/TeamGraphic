from rest_framework import viewsets, mixins, status, filters
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomModelViewSet(viewsets.ModelViewSet):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default:
            raise PermissionDenied("This object is protected and cannot be deleted.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
