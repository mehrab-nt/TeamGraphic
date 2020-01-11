from django.urls import path
from . import views
from django.conf.urls import url, include

app_name = 'product'
urlpatterns = [
    path('category/<str:category_id>/', views.category_show, name='category_show'),
]
