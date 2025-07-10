from django.contrib import admin
from .models import ProductCategory, Product


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sort_number']
    search_fields = ['title']
    list_filter = ['is_landing']
    ordering = ['sort_number']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'parent_category', 'sort_number', 'alt', 'price']
    search_fields = ['title']
    list_filter = ['is_landing', 'type', 'status']


admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
