import django_filters
from .models import Job

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
    categories = django_filters.CharFilter(
        field_name="categories__name", lookup_expr="icontains", label="Category"
    )
    skills = django_filters.CharFilter(
        field_name="required_skills__name", lookup_expr="icontains", label="Skill"
    )
    is_active = django_filters.BooleanFilter(field_name="is_active")
    
    class Meta:
        model = Job
        fields = ['title', 'location', 'company', 'job_type', 'salary_min', 'salary_max', 'categories', 'skills', 'is_active']

