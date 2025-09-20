from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from .models import Application

# Register your models here.
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_date', 'updated_date')
    list_filter = (
        'status',
        ('job', RelatedOnlyFieldListFilter),
        ('applicant', RelatedOnlyFieldListFilter),
        'applied_date',
        'updated_date',
    )
    search_fields = ('job__title', 'applicant__username', 'cover_letter')
    ordering = ('-applied_date',)

    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'applicant', 'cover_letter', 'resume')
        }),
        ('Status Management', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('applied_date', 'updated_date'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('applied_date', 'updated_date')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('job', 'applicant')
        return self.readonly_fields

