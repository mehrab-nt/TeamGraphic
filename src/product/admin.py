from django.contrib import admin
from .models import *


class Selling_OptionInline(admin.TabularInline):
    model = Selling_Option
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'preview', 'category', 'brief_intro', 'guidance', 'design_feature')
    list_editable = ('title', 'category', 'design_feature')
    # fieldsets = (
    #
    # )
    inlines = [
        Selling_OptionInline,
    ]


class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'icon', 'preview', 'description', 'order')
    list_editable = ('title', 'order')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'icon', 'classification', 'preview', 'description', 'order')
    list_editable = ('title', 'classification', 'order')


class DesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'preview', 'vector', 'category', 'price', 'low_price', 'min_time', 'duration')
    list_editable = ('title', 'category', 'price', 'low_price', 'min_time', 'duration')


admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Template_File)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size)
admin.site.register(Cut)
admin.site.register(Ready)
admin.site.register(Color)
admin.site.register(Quality)
admin.site.register(Design, DesignAdmin)
admin.site.register(Discount)
admin.site.register(Selling_Option)
