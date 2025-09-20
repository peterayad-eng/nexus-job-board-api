from rest_framework import serializers
from jobs.serializers import JobSummarySerializer
from users.serializers import UserSerializer
from .models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    job_details = JobSummarySerializer(source='job', read_only=True)
    applicant_details = UserSerializer(source='applicant', read_only=True)
    can_manage = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_details', 'applicant', 'applicant_details',
            'cover_letter', 'resume', 'status', 'notes',
            'can_manage', 'applied_date', 'updated_date'
        ]
        read_only_fields = ['id', 'applicant', 'applied_date', 'updated_date']

class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['job', 'cover_letter', 'resume']
    
    def validate(self, data):
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to apply for jobs.")
        
        # Check if user already applied for this job
        if Application.objects.filter(job=data['job'], applicant=request.user).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        
        # Check if user is a job seeker
        if not request.user.is_job_seeker():
            raise serializers.ValidationError("Only job seekers can apply for jobs.")
        
        # Check if job is active
        if not data['job'].is_active:
            raise serializers.ValidationError("Cannot apply to an inactive job.")
        
        return data

class ApplicationStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Application
        fields = ['status', 'status_display', 'notes']
    
    def validate_status(self, value):
        valid_transitions = {
            'applied': ['reviewed', 'rejected'],
            'reviewed': ['interview', 'rejected'],
            'interview': ['accepted', 'rejected'],
            'rejected': [],
            'accepted': []
        }
        
        current_status = self.instance.status if self.instance else 'applied'
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}"
            )
        return value

class ApplicationSummarySerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job_title', 'company_name', 'applicant_name', 'applicant_email',
            'status', 'applied_date', 'updated_date'
        ]
        read_only_fields = ['id', 'applied_date', 'updated_date']

class ApplicationDetailSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)
    company_id = serializers.IntegerField(source='job.company.id', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    applicant_phone = serializers.CharField(source='applicant.phone_number', read_only=True)
    can_manage = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job_title', 'company_name', 'company_id',
            'applicant_name', 'applicant_email', 'applicant_phone',
            'cover_letter', 'resume', 'status', 'notes',
            'can_manage', 'applied_date', 'updated_date'
        ]
        read_only_fields = ['id', 'applied_date', 'updated_date']

class ApplicationBulkStatusSerializer(serializers.Serializer):
    application_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of application IDs to update"
    )
    status = serializers.ChoiceField(choices=Application.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_application_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one application ID is required.")
        
        # Check if all applications exist
        existing_count = Application.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError("One or more application IDs are invalid.")
        
        return value

