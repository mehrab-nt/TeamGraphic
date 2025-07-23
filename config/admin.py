from django.contrib import admin
from .models import PriceListConfig


class PriceListConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'view_type', 'auth_need', 'last_update', 'pdf_file']


admin.site.register(PriceListConfig, PriceListConfigAdmin)
