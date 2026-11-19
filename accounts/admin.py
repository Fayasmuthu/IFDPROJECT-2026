from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for User accounts with email / Gmail prominently displayed,
    searchable, and editable.
    """
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'usertype',
        'phone_number',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
    )
    list_display_links = ('username', 'email')
    list_filter = (
        'usertype',
        'is_staff',
        'is_superuser',
        'is_active',
        'is_customer',
        'date_joined',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone_number',
    )
    ordering = ('-date_joined',)
    readonly_fields = ('enc_key', 'last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Information & Gmail'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'photo')
        }),
        (_('Account Type & Role'), {
            'fields': ('usertype', 'is_customer')
        }),
        (_('Permissions & Access'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Security & Dates'), {
            'fields': ('enc_key', 'last_login', 'date_joined')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Account Details & Gmail'), {
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'usertype')
        }),
    )
