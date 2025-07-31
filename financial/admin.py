from django.contrib import admin
from .models import Company, Credit, Deposit, BankAccount, CashBackPercent, CashBack


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'agent']


class CreditAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'total_amount', 'last_update']


class DepositAdmin(admin.ModelAdmin):
    list_display = ['id', 'credit', 'display_price', 'submit_date', 'transaction_type', 'deposit_type', 'confirm_status', 'official_invoice']


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active', 'is_online']


class CashBackPercentAdmin(admin.ModelAdmin):
    list_display = ['id', 'percent', 'min_amount', 'max_amount']


class CashBackAdmin(admin.ModelAdmin):
    list_display = ['id', 'tmp_cashback', 'tmp_total_order_amount', 'now_cashback', 'now_total_order_amount', 'is_active']


admin.site.register(Company, CompanyAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(CashBackPercent, CashBackPercentAdmin)
admin.site.register(CashBack, CashBackAdmin)
