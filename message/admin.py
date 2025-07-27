from django.contrib import admin
from .models import SmsMessage, Department, WebMessage, WebMessageContent, AlarmMessage


class AlarmMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'end_date', 'employee']

class SmsMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'receiver', 'panel', 'tracking_code']

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

class WebMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'status', 'create_date', 'department', 'employee']

class WebMessageContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'type']


admin.site.register(AlarmMessage, AlarmMessageAdmin)
admin.site.register(SmsMessage, SmsMessageAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(WebMessage, WebMessageAdmin)
admin.site.register(WebMessageContent, WebMessageContentAdmin)

