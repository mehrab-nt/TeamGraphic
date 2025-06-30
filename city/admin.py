from django.contrib import admin
from .models import Province, City


class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']


class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'province']
    list_filter = ['province']


admin.site.register(Province, ProvinceAdmin)
admin.site.register(City, CityAdmin)
