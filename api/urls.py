from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, RoleViewSet, IntroductionViewSet
from employee.views import EmployeeViewSet


router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'introduction', IntroductionViewSet, basename='introduction')
router.register(r'employee', EmployeeViewSet, basename='employee')
urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', include(router.urls)),
    path('', include('user.urls')),
]
