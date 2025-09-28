import django_filters
from .models import Job
from categories.models import Category, Skill

class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains", label="Job Title"
    )
    location = django_filters.CharFilter(
        field_name="location", lookup_expr="icontains", label="Location"
    )
    company = django_filters.CharFilter(
        field_name="company__name", lookup_expr="icontains", label="Company Name"
    )
    job_type = django_filters.ChoiceFilter(
        field_name="job_type", choices=Job.JOB_TYPES, label="Job Type"
    )
    salary_min = django_filters.NumberFilter(
        field_name="salary_range", lookup_expr="gte", label="Minimum Salary"
    )
    salary_max = django_filters.NumberFilter(
        field_name="salary_range", lookup_expr="lte", label="Maximum Salary"
    )
    categories = django_filters.ModelMultipleChoiceFilter(
        field_name="categories", queryset=Category.objects.all(), label="Categories"
    )
    skills = django_filters.ModelMultipleChoiceFilter(
        field_name="required_skills", queryset=Skill.objects.all(), label="Skills"
    )
    is_active = django_filters.BooleanFilter(field_name="is_active")
    
    class Meta:
        model = Job
        fields = ['title', 'location', 'company', 'job_type', 'salary_min', 'salary_max', 'categories', 'skills', 'is_active']

