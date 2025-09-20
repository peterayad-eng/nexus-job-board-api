from django.contrib import admin
from .models import Company

# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'contact_email', 'website',
                   'created_by', 'employee_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'location', 'contact_email')
    ordering = ('-created_at',)

    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'description', 'location')
        }),
        ('Contact Details', {
            'fields': ('website', 'contact_email', 'logo')
        }),
        ('Management', {
            'fields': ('created_by', 'managers')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('managers',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_by',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # if creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = "Employees"

