from django.contrib import admin
from .models import ProductCategory, Product, GalleryCategory, GalleryImage


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sort_number']
    search_fields = ['title']
    list_filter = ['is_landing']
    ordering = ['sort_number']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'parent_category', 'sort_number', 'alt', 'price']
    search_fields = ['title']
    list_filter = ['is_landing', 'type', 'status']


class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent_category', 'sort_number']
    search_fields = ['name']


class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'image_file', 'parent_category', 'sort_number', 'alt']
    search_fields = ['name']
    list_filter = ['parent_category']


admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(GalleryCategory, GalleryCategoryAdmin)
admin.site.register(GalleryImage, GalleryImageAdmin)

