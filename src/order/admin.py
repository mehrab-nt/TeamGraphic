from django.contrib import admin
from .models import Cart, Order, Status


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user', 'status', 'total_cost', 'create_date', 'duration', 'delivery_date')
    list_editable = ('status', 'total_cost', 'duration')
    # fieldsets = (
    #
    # )
    inlines = [
        OrderInline,
    ]


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'cart', 'status', 'design_feature', 'count',
                    'description', 'cost', 'duration', 'ready_date')
    list_editable = ('status', 'design_feature', 'description', 'cost', 'duration')


class StatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'title', 'vector', 'type')
    list_editable = ('title', 'vector', 'type')


admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Status, StatusAdmin)
