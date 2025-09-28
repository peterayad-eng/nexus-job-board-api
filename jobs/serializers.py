from rest_framework import serializers
from categories.serializers import CategorySerializer, SkillSerializer
from companies.serializers import CompanySerializer
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    company_details = CompanySerializer(source='company', read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.username', read_only=True)
    categories_details = CategorySerializer(source='categories', many=True, read_only=True)
    skills_details = SkillSerializer(source='required_skills', many=True, read_only=True)
    application_count = serializers.IntegerField(read_only=True)
    is_owner = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'company', 'company_details',
            'posted_by', 'posted_by_name', 'location', 'job_type',
            'salary_range', 'categories', 'categories_details',
            'required_skills', 'skills_details', 'is_active',
            'application_count', 'is_owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'posted_by', 'created_at', 'updated_at']

class JobCreateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'company', 'location', 'job_type',
            'salary_range', 'categories', 'required_skills', 'is_active'
        ]
    
    def validate_company(self, value):
        # Check if user is associated with the company
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if not (value.created_by == request.user or value.managers.filter(id=request.user.id).exists()):
                raise serializers.ValidationError("You must be a manager of this company to post jobs.")
        return value

class JobUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'location', 'job_type',
            'salary_range', 'categories', 'required_skills', 'is_active'
        ]

class JobSummarySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)
    category_names = serializers.SerializerMethodField()
    skill_names = serializers.SerializerMethodField()
    application_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'company_logo', 'location',
            'job_type', 'salary_range', 'category_names', 'skill_names',
            'application_count', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_category_names(self, obj):
        return [category.name for category in obj.categories.all()]
    
    def get_skill_names(self, obj):
        return [skill.name for skill in obj.required_skills.all()]

class JobSearchSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    application_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'location', 'job_type',
            'salary_range', 'application_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

