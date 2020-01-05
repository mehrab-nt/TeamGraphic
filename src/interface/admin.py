from django.contrib import admin
from .models import MainMenu, SlidShow, SpecialProductBox


class MainMenuAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'link', 'rank', 'active')
    list_editable = ('title', 'link', 'rank', 'active')


class SlidShowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'image', 'rank', 'active', 'description', 'time')
    list_editable = ('title', 'rank', 'active', 'description', 'time')


class SpecialProductBoxAdmin(admin.ModelAdmin):
    list_display = ('pk', 'rank', 'product')
    list_editable = ('rank', )


admin.site.register(MainMenu, MainMenuAdmin)
admin.site.register(SlidShow, SlidShowAdmin)
admin.site.register(SpecialProductBox, SpecialProductBoxAdmin)
