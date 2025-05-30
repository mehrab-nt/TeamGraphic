from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['phone_number', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_filter = ['is_active', 'is_staff']

    fieldsets = UserAdmin.fieldsets + (
        ('TeamGraphic', {'fields': ('phone_number', 'national_id', 'public_key', 'private_key')}),
    )

admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date', 'gender']
    search_fields = ['user__phone_number', 'user__first_name']
