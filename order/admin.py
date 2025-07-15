from django.contrib import admin
from .models import Cart, Order, OrderStatus


class CartAdmin(admin.ModelAdmin):
    list_display = ['id',]


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id',]


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['id',]


admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
