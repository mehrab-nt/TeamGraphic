from django.urls import path
from . import views
from django.conf.urls import url, include

app_name = 'user'
urlpatterns = [
    path('signup/', views.user_signup, name='user_signup'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.user_profile, name='user_profile'),
]
