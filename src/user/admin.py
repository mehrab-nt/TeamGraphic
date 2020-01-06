from django.contrib import admin
from .models import UserTG, Address, Introduction


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class UserTGAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_full_name', 'user_email_address', 'role',
                    'profile', 'introduction', 'confirm_code', 'address_count', 'is_active')
    # list_display_links = ('user_addresses',)
    list_editable = ('confirm_code', )
    # readonly_fields = ('last_edit_time',)
    # fieldsets = (
    #     (None, {
    #         'fields': ('mobile', ('first_name', 'last_name'),)
    #     }),
    #     (None, {
    #         'fields': ('email', 'Profile', )
    #     }),
    #     ('Security', {
    #         'classes': ('collapse',),
    #         'fields': (('confirm_code', 'password',),'reg_time', 'last_edit_time',),
    #     })
    # )
    inlines = [
        AddressInline,
    ]


class IntroductionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'number')


class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'state', 'detail', 'user')
    list_editable = ('country', 'state', 'detail', 'user')
    fieldsets = [
        (None, {
            'fields': (('country', 'state'), 'detail')
        }),
        (None, {
            'fields': ('user',)
        })
    ]


admin.site.register(UserTG, UserTGAdmin)
admin.site.register(Address, AddressAdmin)
