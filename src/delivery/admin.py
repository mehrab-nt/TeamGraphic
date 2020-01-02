from django.contrib import admin
from .models import Delivery


class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cost', 'description', 'duration')
    list_editable = ('name', 'cost', 'duration')


admin.site.register(Delivery, DeliveryAdmin)
