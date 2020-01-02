from django.contrib import admin
from .models import User, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class UserAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'first_name', 'last_name',
                    'email', 'Profile', 'confirm_code', 'reg_time', 'last_edit_time')
    # list_display_links = ('user_addresses',)
    list_editable = ('first_name', 'last_name',
                     'email', 'confirm_code')
    readonly_fields = ('last_edit_time',)
    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name'),)
        }),
        (None, {
            'fields': ('email', 'Profile', )
        }),
        ('Security', {
            'classes': ('collapse',),
            'fields': (('confirm_code', 'password',),'reg_time', 'last_edit_time',),
        })
    )
    inlines = [
        AddressInline,
    ]


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


admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
