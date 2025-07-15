from django.contrib import admin
from .models import FileDirectory, FileItem, ClearFileHistory


class FileDirectoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'create_date']
    search_fields = ['name']
    ordering = ['-create_date']


class FileItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'volume', 'create_date', 'parent_directory']
    search_fields = ['name']
    list_filter = ['parent_directory', 'type']


class ClearFileHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_date', 'until_date', 'employee', 'submit_date']


admin.site.register(FileDirectory, FileDirectoryAdmin)
admin.site.register(FileItem, FileItemAdmin)
admin.site.register(ClearFileHistory, ClearFileHistoryAdmin)
