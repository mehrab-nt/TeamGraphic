from django.urls import path
from . import views
from django.conf.urls import url, include

app_name = 'order'
urlpatterns = [
    path('cart/', views.cart_show, name='cart_show'),
]
