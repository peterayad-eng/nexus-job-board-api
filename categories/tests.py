from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from jobboard.test_utils import BaseAPITestCase
from .models import Category, Skill
from jobs.models import Job
from companies.models import Company

# Create your tests here.
User = get_user_model()

class CategoryPublicAPITests(BaseAPITestCase):
    """Test categories API (public endpoints - no authentication required)"""
    
    def setUp(self):
        super().setUp()
        # Create test categories
        self.category1 = Category.objects.create(
            name='Technology',
            description='Technology related jobs'
        )
        self.category2 = Category.objects.create(
            name='Marketing',
            description='Marketing related jobs'
        )
        self.category3 = Category.objects.create(
            name='Design',
            description='Design related jobs'
        )
    
    def test_list_categories(self):
        """Test retrieving list of categories"""
        response = self.client.get(reverse('category-list'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Verify category names
        category_names = [cat['name'] for cat in response.data]
        self.assertIn('Technology', category_names)
        self.assertIn('Marketing', category_names)
        self.assertIn('Design', category_names)
    
    def test_retrieve_category_detail(self):
        """Test retrieving a single category detail"""
        response = self.client.get(reverse('category-detail', args=[self.category1.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology')
        self.assertEqual(response.data['description'], 'Technology related jobs')
    
    def test_categories_with_jobs_empty(self):
        """Test categories with jobs when no jobs exist"""
        response = self.client.get(reverse('category-with-jobs'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No jobs yet
    
    def test_search_categories(self):
        """Test searching categories by name"""
        response = self.client.get(reverse('category-list') + '?search=tech')
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Technology')
    
    def test_category_not_found(self):
        """Test retrieving non-existent category returns 404"""
        response = self.client.get(reverse('category-detail', args=[999]))
        self.assertResponseError(response, status.HTTP_404_NOT_FOUND)

class SkillPublicAPITests(BaseAPITestCase):
    """Test skills API (public endpoints)"""
    
    def setUp(self):
        super().setUp()
        # Create test skills
        self.skill1 = Skill.objects.create(
            name='Python',
            description='Python programming language'
        )
        self.skill2 = Skill.objects.create(
            name='JavaScript',
            description='JavaScript programming'
        )
        self.skill3 = Skill.objects.create(
            name='Project Management',
            description='Project management skills'
        )
    
    def test_list_skills(self):
        """Test retrieving list of skills"""
        response = self.client.get(reverse('skill-list'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        skill_names = [skill['name'] for skill in response.data]
        self.assertIn('Python', skill_names)
        self.assertIn('JavaScript', skill_names)
        self.assertIn('Project Management', skill_names)
    
    def test_retrieve_skill_detail(self):
        """Test retrieving a single skill detail"""
        response = self.client.get(reverse('skill-detail', args=[self.skill1.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Python')
        self.assertEqual(response.data['description'], 'Python programming language')
    
    def test_skills_with_jobs_empty(self):
        """Test skills with jobs when no jobs exist"""
        response = self.client.get(reverse('skill-with-jobs'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_search_skills(self):
        """Test searching skills by name"""
        response = self.client.get(reverse('skill-list') + '?search=python')
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Python')

class CategoryAdminAPITests(BaseAPITestCase):
    """Test categories API (admin endpoints - require authentication)"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )
    
    def test_create_category_as_admin(self):
        """Test creating a category as admin user"""
        self.authenticate_user(self.admin_user)
        
        category_data = {
            'name': 'New Category',
            'description': 'New category description'
        }
        
        response = self.client.post(reverse('admin-category-create'), category_data)
        self.assertResponseSuccess(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Category')
        self.assertTrue(Category.objects.filter(name='New Category').exists())
    
    def test_create_category_duplicate_name(self):
        """Test creating category with duplicate name should fail"""
        self.authenticate_user(self.admin_user)
        
        category_data = {
            'name': 'Test Category',  # Same as existing category
            'description': 'Duplicate category'
        }
        
        response = self.client.post(reverse('admin-category-create'), category_data)
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)  # Should have name validation error
    
    def test_create_category_unauthenticated(self):
        """Test that unauthenticated users cannot create categories"""
        category_data = {
            'name': 'Unauthorized Category',
            'description': 'Should not be created'
        }
        
        response = self.client.post(reverse('admin-category-create'), category_data)
        self.assertResponseError(response, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_category_non_admin(self):
        """Test that non-admin users cannot create categories"""
        self.authenticate_user(self.employer_user)
        
        category_data = {
            'name': 'Employer Category',
            'description': 'Should be forbidden'
        }
        
        response = self.client.post(reverse('admin-category-create'), category_data)
        self.assertResponsePermissionDenied(response)
    
    def test_update_category_as_admin(self):
        """Test updating a category as admin"""
        self.authenticate_user(self.admin_user)
        
        update_data = {
            'name': 'Updated Category',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            reverse('admin-category-update', args=[self.category.id]), 
            update_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Category')
        
        # Verify the category was updated in database
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')
    
    def test_delete_category_as_admin(self):
        """Test deleting a category as admin"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.delete(
            reverse('admin-category-delete', args=[self.category.id])
        )
        self.assertResponseSuccess(response, status.HTTP_204_NO_CONTENT)
        
        # Verify the category was deleted
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
    
    def test_delete_category_non_admin(self):
        """Test that non-admin users cannot delete categories"""
        self.authenticate_user(self.employer_user)
        
        response = self.client.delete(
            reverse('admin-category-delete', args=[self.category.id])
        )
        self.assertResponsePermissionDenied(response)
        
        # Verify the category still exists
        self.assertTrue(Category.objects.filter(id=self.category.id).exists())

class SkillAdminAPITests(BaseAPITestCase):
    """Test skills API (admin endpoints)"""
    
    def setUp(self):
        super().setUp()
        self.skill = Skill.objects.create(
            name='Test Skill',
            description='Test skill description'
        )
    
    def test_create_skill_as_admin(self):
        """Test creating a skill as admin user"""
        self.authenticate_user(self.admin_user)
        
        skill_data = {
            'name': 'New Skill',
            'description': 'New skill description'
        }
        
        response = self.client.post(reverse('admin-skill-create'), skill_data)
        self.assertResponseSuccess(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Skill')
        self.assertTrue(Skill.objects.filter(name='New Skill').exists())
    
    def test_update_skill_as_admin(self):
        """Test updating a skill as admin"""
        self.authenticate_user(self.admin_user)
        
        update_data = {
            'name': 'Updated Skill',
            'description': 'Updated skill description'
        }
        
        response = self.client.put(
            reverse('admin-skill-update', args=[self.skill.id]), 
            update_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Skill')
    
    def test_delete_skill_as_admin(self):
        """Test deleting a skill as admin"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.delete(
            reverse('admin-skill-delete', args=[self.skill.id])
        )
        self.assertResponseSuccess(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Skill.objects.filter(id=self.skill.id).exists())

class CategoryJobRelationshipTests(BaseAPITestCase):
    """Test categories with job relationships"""
    
    def setUp(self):
        super().setUp()
        # Create categories
        self.tech_category = Category.objects.create(name='Technology')
        self.marketing_category = Category.objects.create(name='Marketing')
        
        # Create a company and job
        self.company = self.create_test_company()
        self.job = self.create_test_job(title='Tech Job')
        self.job.categories.add(self.tech_category)
    
    def test_category_job_count(self):
        """Test that category detail includes job count"""
        response = self.client.get(reverse('category-detail', args=[self.tech_category.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['job_count'], 1)  # Should have 1 job
    
    def test_categories_with_jobs(self):
        """Test categories with jobs endpoint shows only categories with jobs"""
        response = self.client.get(reverse('category-with-jobs'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        
        # Should only show Technology category (has jobs), not Marketing (no jobs)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Technology')
        self.assertEqual(response.data[0]['job_count'], 1)
    
    def test_skill_job_count(self):
        """Test that skill detail includes job count"""
        # Add skill to job
        python_skill, created = Skill.objects.get_or_create(
            name='Python-Test', 
            defaults={'description': 'Test Python skill'}
        )
        self.job.required_skills.add(python_skill)
        
        response = self.client.get(reverse('skill-detail', args=[python_skill.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['job_count'], 1)

class CategoryValidationTests(BaseAPITestCase):
    """Test category and skill validation"""
    
    def test_category_name_uniqueness(self):
        """Test that category names must be unique"""
        self.authenticate_user(self.admin_user)
        
        # Create first category
        response1 = self.client.post(reverse('admin-category-create'), {
            'name': 'Unique Category',
            'description': 'First category'
        })
        self.assertResponseSuccess(response1, status.HTTP_201_CREATED)
        
        # Try to create category with same name
        response2 = self.client.post(reverse('admin-category-create'), {
            'name': 'Unique Category',  # Same name
            'description': 'Second category'
        })
        self.assertResponseError(response2, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response2.data)
    
    def test_skill_name_uniqueness(self):
        """Test that skill names must be unique"""
        self.authenticate_user(self.admin_user)
        
        # Create first skill
        response1 = self.client.post(reverse('admin-skill-create'), {
            'name': 'Unique Skill',
            'description': 'First skill'
        })
        self.assertResponseSuccess(response1, status.HTTP_201_CREATED)
        
        # Try to create skill with same name
        response2 = self.client.post(reverse('admin-skill-create'), {
            'name': 'Unique Skill',  # Same name
            'description': 'Second skill'
        })
        self.assertResponseError(response2, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response2.data)
    
    def test_category_name_required(self):
        """Test that category name is required"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(reverse('admin-category-create'), {
            'description': 'Category without name'  # Missing name
        })
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

class SkillJobRelationshipTests(BaseAPITestCase):
    """Test relationship between skills and jobs"""

    def setUp(self):
        super().setUp()
        self.skill = Skill.objects.create(name="Python")
        # Create a job with the skill using your existing helper
        self.job = self.create_test_job(title="Backend Developer")
        self.job.required_skills.add(self.skill)

    def test_skill_with_jobs(self):
        """Test skill includes job count"""
        response = self.client.get(reverse('skill-detail', args=[self.skill.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['job_count'], 1)

    def test_skill_with_no_jobs(self):
        """Test skill returns job_count = 0 if no jobs exist"""
        # Create a skill with no jobs
        empty_skill = Skill.objects.create(name="Empty Skill")
        
        response = self.client.get(reverse('skill-detail', args=[empty_skill.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['job_count'], 0)

