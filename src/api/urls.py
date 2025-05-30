from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'user', UserList.queryset)
# router.register(r'groups', GroupList.queryset)

urlpatterns = [
    # path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('user/', UserListApiView.as_view(), name='user'),
    path('user/p/', UserProfileApiView.as_view(), name='user_profiles'),
    path('user/<str:public_key>/', UserDetailsApiView.as_view(), name='user_profile_details'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
