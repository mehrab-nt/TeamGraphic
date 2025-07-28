from django.contrib import admin
from .models import Company, Credit, Deposit, BankAccount


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'agent']


class CreditAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'total_amount', 'total_coin']


class DepositAdmin(admin.ModelAdmin):
    list_display = ['id', 'credit', 'display_price', 'submit_date', 'transaction_type', 'deposit_type', 'confirm_status']


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active', 'is_online']


admin.site.register(Company, CompanyAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
