from django.contrib import admin
from .models import CounterReport, MonthlySaleReport, NotifReport


class NotifReportAdmin(admin.ModelAdmin):
    list_display = ['id']

admin.site.register(NotifReport, NotifReportAdmin)


class CounterReportAdmin(admin.ModelAdmin):
    list_display = ['id']

admin.site.register(CounterReport, CounterReportAdmin)


class MonthlySaleReportAdmin(admin.ModelAdmin):
    list_display = ['id']

admin.site.register(MonthlySaleReport, MonthlySaleReportAdmin)
