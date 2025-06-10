from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Role, Introduction, Address


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['phone_number', 'first_name', 'last_name', 'email', 'is_employee', 'is_active', 'role']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_filter = ['is_active', 'is_employee']

    fieldsets = UserAdmin.fieldsets + (
        ('TeamGraphic', {'fields': ('phone_number', 'national_id', 'public_key', 'private_key', 'accounting_id', 'accounting_name', 'role', 'is_employee')}),
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date', 'gender']
    search_fields = ['user__phone_number', 'user__first_name']


class RoleAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'sort_number']


class IntroductionAdmin(admin.ModelAdmin):
    list_display = ['title', 'number', 'sort_number']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'state', 'city', 'content', 'plate_number', 'unit_number']
    list_display_links = ['title']


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Introduction, IntroductionAdmin)
admin.site.register(Address, AddressAdmin)
