from django.contrib import admin
from .models import ProductCategory, Product, OffsetProduct, LargeFormatProduct, SolidProduct, DigitalProduct, \
    GalleryCategory, GalleryImage, OptionCategory, Option, ProductOption, SheetPaper, Size, Paper, Banner


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sort_number', 'status']
    search_fields = ['title']
    list_filter = ['is_landing', 'status']
    ordering = ['sort_number']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'parent_category', 'sort_number', 'alt', 'status']
    search_fields = ['title']
    list_filter = ['type', 'status']
    ordering = ['sort_number', 'parent_category', 'total_order']


class OffsetProductAdmin(admin.ModelAdmin):
    list_display = ['product_info']
    ordering = ['product_info']


class LargeFormatProductAdmin(admin.ModelAdmin):
    list_display = ['product_info']
    ordering = ['product_info']


class SolidProductAdmin(admin.ModelAdmin):
    list_display = ['product_info']
    ordering = ['product_info']


class DigitalProductAdmin(admin.ModelAdmin):
    list_display = ['product_info']
    ordering = ['product_info']


class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent_category', 'sort_number']
    search_fields = ['name']


class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'image_file', 'parent_category', 'sort_number', 'alt']
    search_fields = ['name']
    list_filter = ['parent_category']


class OptionCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'parent_category', 'sort_number', 'is_active']
    search_fields = ['title']


class OptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'parent_category', 'sort_number', 'is_active']
    search_fields = ['title']


class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'option']


class SheetPaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'material', 'display_name', 'length', 'width']


class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'display_name', 'length', 'width', 'base_cutting_edge']


class PaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'sheet_paper', 'size', 'per_paper_price']


class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'width']


admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OffsetProduct, OffsetProductAdmin)
admin.site.register(LargeFormatProduct, LargeFormatProductAdmin)
admin.site.register(SolidProduct, SolidProductAdmin)
admin.site.register(DigitalProduct, DigitalProductAdmin)
admin.site.register(GalleryCategory, GalleryCategoryAdmin)
admin.site.register(GalleryImage, GalleryImageAdmin)
admin.site.register(OptionCategory, OptionCategoryAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(ProductOption, ProductOptionAdmin)
admin.site.register(SheetPaper, SheetPaperAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Banner, BannerAdmin)
