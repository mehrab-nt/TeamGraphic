from django.contrib import admin
from .models import PriceListConfig, MessageConfig


class PriceListConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'view_type', 'auth_need', 'last_update', 'pdf_file']

class MessageConfigAdmin(admin.ModelAdmin):
    list_display = ['id']


admin.site.register(PriceListConfig, PriceListConfigAdmin)
admin.site.register(MessageConfig, MessageConfigAdmin)
