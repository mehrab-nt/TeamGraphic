from django.contrib import admin
from .models import FileDirectory, FileItem, ClearFileHistory
from mptt.admin import DraggableMPTTAdmin


class FileDirectoryAdmin(DraggableMPTTAdmin):
    mptt_level_indent = 20
    list_display = ['tree_actions', 'id', 'indented_title', 'name', 'create_date']
    list_display_links = ['indented_title']
    search_fields = ['name']


class FileItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'volume', 'create_date', 'parent_directory']
    search_fields = ['name']
    list_filter = ['parent_directory', 'type']


class ClearFileHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_date', 'until_date', 'employee', 'submit_date']


admin.site.register(FileDirectory, FileDirectoryAdmin)
admin.site.register(FileItem, FileItemAdmin)
admin.site.register(ClearFileHistory, ClearFileHistoryAdmin)
