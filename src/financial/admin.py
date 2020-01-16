from django.contrib import admin
from .models import Transaction, FinancialType, Financial, Salary,\
    PrintingHouse, PrintingHouseIncome, PrintingHousePayment


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'amount', 'type', 'record_date', 'confirm', 'confirm_date', 'record_user')
    list_editable = ('confirm', )


class FinancialTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'mode')
    list_editable = ('title', 'mode')


class FinancialAdmin(admin.ModelAdmin):
    list_display = ('pk', 'amount', 'type', 'record_date', 'record_user')


class SalaryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'for_user', 'base_salary', 'reduce_salary', 'amount', 'payment_date', 'record_user')


class PrintingHouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'record_date')
    list_editable = ('title', )


class PrintingHousePaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'record_date', 'order', 'printing_house', 'record_user')


class PrintingHouseIncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'record_date', 'printing_house', 'record_user')


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(FinancialType, FinancialTypeAdmin)
admin.site.register(Financial, FinancialAdmin)
admin.site.register(Salary, SalaryAdmin)
admin.site.register(PrintingHouse, PrintingHouseAdmin)
admin.site.register(PrintingHousePayment, PrintingHousePaymentAdmin)
admin.site.register(PrintingHouseIncome, PrintingHouseIncomeAdmin)

