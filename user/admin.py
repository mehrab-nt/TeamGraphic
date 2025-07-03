from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from .models import User, UserProfile, Role, Introduction, Address
from api.responses import TG_PREVENT_DELETE_DEFAULT


class CustomModelAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        if obj.is_default:
            self.message_user(request, TG_PREVENT_DELETE_DEFAULT, level=messages.ERROR)
        else:
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        if queryset.filter(is_default=True).exists():
            self.message_user(request, TG_PREVENT_DELETE_DEFAULT, level=messages.ERROR)
            queryset = queryset.exclude(is_default=True)
        super().delete_queryset(request, queryset)


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['phone_number', 'first_name', 'last_name', 'email', 'is_employee', 'is_active', 'role', 'introduce_from']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_filter = ['is_active', 'is_employee']

    fieldsets = UserAdmin.fieldsets + (
        ('TeamGraphic', {'fields': ('phone_number', 'phone_number_verified', 'national_id', 'user_profile', 'public_key', 'private_key', 'introducer', 'introduce_from', 'accounting_id', 'accounting_name', 'role', 'is_employee')}),
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'birth_date', 'gender', 'job']
    search_fields = ['user__phone_number', 'user__first_name']


class RoleAdmin(CustomModelAdmin):
    list_display = ['title', 'description', 'is_default', 'sort_number']


class IntroductionAdmin(admin.ModelAdmin):
    list_display = ['title', 'number', 'sort_number']


class AddressAdmin(CustomModelAdmin):
    list_display = ['title', 'user', 'province', 'city', 'content', 'plate_number', 'unit_number', 'is_default']
    list_display_links = ['title']
    list_filter = ['is_default']


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Introduction, IntroductionAdmin)
admin.site.register(Address, AddressAdmin)
