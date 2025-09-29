from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    manager_count = serializers.IntegerField(read_only=True)
    employee_count = serializers.IntegerField(read_only=True)
    job_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'location', 'website', 
            'logo', 'contact_email', 'managers', 'created_by', 
            'created_by_name', 'manager_count', 'employee_count', 
            'job_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', 'description', 'location', 'website', 'logo', 'contact_email']
    
    def validate_name(self, value):
        if Company.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A company with this name already exists.")
        return value

class CompanySummarySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'location', 'website', 'job_count']
        read_only_fields = ['id', 'job_count']

class DeleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class AddManagerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="ID of the user to add as manager")

class RemoveManagerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class ManagerResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

