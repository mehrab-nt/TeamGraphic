from django.contrib import admin
from .models import MainMenu, MainImage, SlideShow, SpecialProductBox


class MainMenuAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'link', 'rank', 'active')
    list_editable = ('title', 'link', 'rank', 'active')


class MainImageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title')


class SlideShowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'image', 'rank', 'active', 'description', 'time')
    list_editable = ('title', 'rank', 'active', 'description', 'time')


class SpecialProductBoxAdmin(admin.ModelAdmin):
    list_display = ('pk', 'rank', 'product')
    list_editable = ('rank', )


admin.site.register(MainMenu, MainMenuAdmin)
admin.site.register(MainImage, MainImageAdmin)
admin.site.register(SlideShow, SlideShowAdmin)
admin.site.register(SpecialProductBox, SpecialProductBoxAdmin)
