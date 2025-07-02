from django.urls import path
from .views import CustomTokenRefreshView, CustomTokenVerifyView


urlpatterns = [
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
]
