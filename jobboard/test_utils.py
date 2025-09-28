from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Create test data that will be available for all test methods"""
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            user_type='admin'
        )
        
        cls.employer_user = User.objects.create_user(
            username='employer1',
            email='employer@test.com',
            password='testpass123',
            user_type='employer',
            first_name='Employer',
            last_name='User'
        )
        
        cls.job_seeker_user = User.objects.create_user(
            username='jobseeker1',
            email='seeker@test.com',
            password='testpass123',
            user_type='job_seeker',
            first_name='Job',
            last_name='Seeker'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user using JWT tokens"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def remove_authentication(self):
        """Helper method to remove authentication"""
        self.client.credentials()
    
    def create_user(self, **kwargs):
        """Helper method to create a user with default values"""
        defaults = {
            "username": f"testuser{User.objects.count() + 1}",  
            "email": f"test{User.objects.count() + 1}@test.com",
            "password": "testpass123",
            "user_type": "job_seeker",
            "first_name": "Test",
            "last_name": "User"
        }
        defaults.update(kwargs)
        
        user = User.objects.create_user(**defaults)
        if 'password' in defaults:
            user.raw_password = defaults['password']  # Store for later use
        return user
    
    def api_login(self, username=None, password="testpass123", user=None):
        """
        Helper method to login via API and get JWT token
        Can accept either a user object or username/password
        """
        if user and not username:
            username = user.username
            password = getattr(user, 'raw_password', 'testpass123')
        
        login_url = reverse("login")  
        response = self.client.post(login_url, {  
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            token = response.data["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
            return response.data
        else:
            # For debugging failed logins
            print(f"Login failed: {response.data}")
            return None
    
    def assertResponseSuccess(self, response, status_code=200):
        """Helper to assert response success with optional status code"""
        self.assertEqual(response.status_code, status_code)
        return response  # Return response for chaining
    
    def assertResponseError(self, response, status_code=400):
        """Helper to assert response error with optional status code"""
        self.assertEqual(response.status_code, status_code)
        return response  # Return response for chaining
    
    def assertResponsePermissionDenied(self, response):
        """Helper specifically for permission denied errors - allow 403 or 404"""
        self.assertTrue(
            response.status_code in [403, 404],
            f"Expected 403 or 404, got {response.status_code}. Response: {response.data}"
        )
        return response
    
    def create_test_company(self, **kwargs):
        """Helper to create a test company"""
        from companies.models import Company
        
        defaults = {
            "name": f"Test Company {Company.objects.count() + 1}",
            "description": "A test company",
            "location": "Test City",
            "website": "https://testcompany.com",
            "contact_email": "info@testcompany.com",
            "created_by": self.employer_user
        }
        defaults.update(kwargs)
        
        company = Company.objects.create(**defaults)
        if 'managers' not in kwargs:  # Add creator as manager by default
            company.managers.add(defaults['created_by'])
        return company
    
    def create_test_job(self, **kwargs):
        """Helper to create a test job"""
        from jobs.models import Job
        from categories.models import Category, Skill
        
        # Create default company if not provided
        if 'company' not in kwargs:
            kwargs['company'] = self.create_test_company()
        
        if 'posted_by' not in kwargs:
            kwargs['posted_by'] = self.employer_user
        
        defaults = {
            "title": f"Test Job {Job.objects.count() + 1}",
            "description": "A test job description",
            "location": "Remote",
            "job_type": "full_time",
            "salary_range": "$50,000-$70,000",
            "is_active": True
        }
        defaults.update(kwargs)
        
        job = Job.objects.create(**defaults)
        
        # Add default category and skill if they exist
        try:
            category, _ = Category.objects.get_or_create(name="Technology")
            skill, _ = Skill.objects.get_or_create(name="Python")
            job.categories.add(category)
            job.required_skills.add(skill)
        except:
            pass  # Categories app might not be available in all tests
        
        return job
    
    def create_test_application(self, **kwargs):
        """Helper to create a test application"""
        from applications.models import Application
        
        if 'job' not in kwargs:
            kwargs['job'] = self.create_test_job()
        
        if 'applicant' not in kwargs:
            kwargs['applicant'] = self.job_seeker_user
        
        defaults = {
            "cover_letter": "I am interested in this position",
            "status": "applied"
        }
        defaults.update(kwargs)
        
        application = Application.objects.create(**defaults)
        return application

