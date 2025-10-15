from django.contrib import admin
from .models import CounterReport, MonthlySaleReport


class CounterReportAdmin(admin.ModelAdmin):
    list_display = ['id']

admin.site.register(CounterReport, CounterReportAdmin)


class MonthlySaleReportAdmin(admin.ModelAdmin):
    list_display = ['id']

admin.site.register(MonthlySaleReport, MonthlySaleReportAdmin)
