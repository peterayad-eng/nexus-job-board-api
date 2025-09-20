from django.contrib import admin
from .models import Category, Skill

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'created_at')
    list_display = ('name', 'description', 'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'created_at')
    list_display = ('name', 'description', 'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('name',)

