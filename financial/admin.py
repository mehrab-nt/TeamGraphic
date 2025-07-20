from django.contrib import admin
from .models import Credit


class CreditAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'total_amount', 'total_coin']


admin.site.register(Credit, CreditAdmin)
