from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'company',
                   'is_active', 'is_staff', 'last_login', 'date_joined', 'application_count')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined', 'company')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'company__name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Profile Details', {
            'fields': ('user_type', 'bio', 'profile_picture')
        }),
        ('Contact Info', {
            'fields': ('phone_number',)
        }),
        ('Professional Info', {
            'fields': ('resume', 'experience', 'education', 'company')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'company')
        }),
    )

    readonly_fields = ('date_joined', 'last_login', 'application_count')
    autocomplete_fields = ('company',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_application_count=Count('applications'))

    def application_count(self, obj):
        return obj._application_count
    application_count.admin_order_field = '_application_count'
    application_count.short_description = 'Applications'

