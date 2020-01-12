from django.contrib import admin
from .models import Cart, Order, Status, OrderAction, CartAction


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0


class CartAdmin(admin.ModelAdmin):
    # list_display = ('cart_id', 'user', 'status', 'total_cost', 'create_date', 'duration', 'delivery_date')
    # list_editable = ('status', 'total_cost', 'duration')
    # fieldsets = (
    #
    # )
    inlines = [
        OrderInline,
    ]


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'cart', 'status', 'design_feature', 'count',
                    'description', 'product_cost', 'design_cost', 'tot_cost', 'duration', 'ready_date')
    list_editable = ('status', 'design_feature', 'description', 'duration')


class StatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'title', 'vector', 'type')
    list_editable = ('title', 'vector', 'type')


class OrderActionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'order', 'user', 'old_status', 'new_status', 'data')


class CartActionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'cart', 'old_status', 'new_status', 'data')


admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(OrderAction, OrderActionAdmin)
admin.site.register(CartAction, CartActionAdmin)

