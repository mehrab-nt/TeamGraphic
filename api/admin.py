from django.contrib import admin
from .models import ApiItem, ApiCategory


class ApiCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'sort_number', 'role_base']


class ApiItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category' , 'key']
    list_filter = ['category']
    search_fields = ['key', 'title']


admin.site.register(ApiCategory, ApiCategoryAdmin)
admin.site.register(ApiItem, ApiItemAdmin)
