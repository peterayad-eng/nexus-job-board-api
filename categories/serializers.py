from rest_framework import serializers
from .models import Category, Skill

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class CategoryDetailSerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'job_count', 'created_at']
        read_only_fields = ['id', 'job_count', 'created_at']
    
class SkillDetailSerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'job_count', 'created_at']
        read_only_fields = ['id', 'job_count', 'created_at']

