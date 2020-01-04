from django.urls import path
from . import views
from django.conf.urls import url, include

app_name = 'user'
urlpatterns = [
    # path('', views.home_view, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    # url(r'^register/$', views.register, name='register'),
    # url(r'^user_login/$', views.user_login, name='user_login'),
    path('index/', views.index, name='index'),
    path('logout/', views.user_logout, name='logout'),
    # url(r'^$', views.index, name='index'),
    # url(r'^special/', views.special, name='special'),
    # url(r'^user/', include('user.urls')),
    # url(r'^logout/$', views.user_logout, name='logout'),
]