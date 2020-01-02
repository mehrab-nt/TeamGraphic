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


admin.site.register(Classification)
admin.site.register(Category)
admin.site.register(Template_File)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size)
admin.site.register(Cut)
admin.site.register(Ready)
admin.site.register(Color)
admin.site.register(Quality)
admin.site.register(Design)
admin.site.register(Discount)
admin.site.register(Selling_Option)
