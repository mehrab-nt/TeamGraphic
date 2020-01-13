from django.contrib import admin
from .models import *


class SellingOptionInline(admin.TabularInline):
    model = SellingOption
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'preview', 'category', 'brief_intro', 'guidance', 'design_base')
    list_editable = ('title', 'category')
    # fieldsets = (
    #
    # )
    inlines = [
        SellingOptionInline,
    ]


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'cost', 'description')
    list_editable = ('title', 'cost', 'description')


class ProductServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'service', 'difference', 'active')
    list_editable = ('product', 'service', 'difference', 'active')


class OrderProductServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_service', 'number')
    list_editable = ('order', 'product_service', 'number')


class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'icon', 'preview', 'description', 'order')
    list_editable = ('title', 'order')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'icon', 'classification', 'preview', 'description', 'order', 'main')
    list_editable = ('title', 'classification', 'order', 'main')


class DesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'preview', 'vector', 'category', 'price', 'max_time', 'duration')
    list_editable = ('title', 'category', 'price', 'max_time', 'duration')


admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TemplateFile)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(OrderProductServices, OrderProductServicesAdmin)
admin.site.register(ProductServices, ProductServicesAdmin)
admin.site.register(Size)
admin.site.register(Cut)
admin.site.register(Ready)
admin.site.register(Color)
admin.site.register(Quality)
admin.site.register(Design, DesignAdmin)
admin.site.register(Discount)
admin.site.register(SellingOption)
