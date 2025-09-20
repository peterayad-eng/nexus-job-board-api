from django.contrib import admin
from .models import Job

# Register your models here.
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type',
                   'salary_range', 'is_active', 'application_count', 'created_at')
    list_filter = ('job_type', 'is_active', 'created_at', 'updated_at', 'categories')
    search_fields = ('title', 'description', 'location', 'company__name')
    ordering = ('-created_at',)

    fieldsets = (
        ('Job Details', {
            'fields': ('title', 'description', 'company', 'posted_by')
        }),
        ('Job Specifications', {
            'fields': ('location', 'job_type', 'salary_range')
        }),
        ('Classifications', {
            'fields': ('categories', 'required_skills')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('categories', 'required_skills')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('posted_by',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # if creating a new object
            obj.posted_by = request.user
        super().save_model(request, obj, form, change)

    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = "Applications"

