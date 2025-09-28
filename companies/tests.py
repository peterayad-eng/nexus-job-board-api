from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobboard.test_utils import BaseAPITestCase
from .models import Company 

# Create your tests here.
User = get_user_model()

class CompanyPublicAPITests(BaseAPITestCase):
    """Test companies API (public endpoints - no authentication required)"""
    
    def setUp(self):
        super().setUp()
        # Create test companies
        self.company1 = Company.objects.create(
            name='Tech Innovations Inc',
            description='A technology innovation company',
            location='San Francisco, CA',
            website='https://techinnovations.com',
            contact_email='info@techinnovations.com',
            created_by=self.employer_user
        )
        self.company2 = Company.objects.create(
            name='Marketing Pros LLC',
            description='Digital marketing agency',
            location='New York, NY',
            website='https://marketingpros.com',
            created_by=self.employer_user
        )
        self.company3 = Company.objects.create(
            name='Design Studio Creative',
            description='Creative design agency',
            location='Austin, TX',
            created_by=self.admin_user
        )
        
        # Add managers to companies
        self.company1.managers.add(self.employer_user)
        self.company2.managers.add(self.employer_user)
    
    def test_list_companies(self):
        """Test retrieving list of companies"""
        response = self.client.get(reverse('company-list-create'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Verify company names
        company_names = [company['name'] for company in response.data]
        self.assertIn('Tech Innovations Inc', company_names)
        self.assertIn('Marketing Pros LLC', company_names)
        self.assertIn('Design Studio Creative', company_names)
    
    def test_retrieve_company_detail(self):
        """Test retrieving a single company detail"""
        response = self.client.get(reverse('company-detail', args=[self.company1.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tech Innovations Inc')
        self.assertEqual(response.data['location'], 'San Francisco, CA')
        self.assertEqual(response.data['website'], 'https://techinnovations.com')
    
    def test_company_summary_list(self):
        """Test retrieving company summary list"""
        response = self.client.get(reverse('company-summary'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Summary should include basic fields
        company = response.data[0]
        self.assertIn('name', company)
        self.assertIn('location', company)
        self.assertIn('website', company)
        self.assertIn('job_count', company)
    
    def test_search_companies(self):
        """Test searching companies by name and location"""
        # Search by name
        response = self.client.get(reverse('company-list-create') + '?search=Tech')
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Tech Innovations Inc')
        
        # Search by location
        response = self.client.get(reverse('company-list-create') + '?search=San Francisco')
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location'], 'San Francisco, CA')
    
    def test_company_not_found(self):
        """Test retrieving non-existent company returns 404"""
        response = self.client.get(reverse('company-detail', args=[999]))
        self.assertResponseError(response, status.HTTP_404_NOT_FOUND)

class CompanyCreateTests(BaseAPITestCase):
    """Test company creation functionality"""
    
    def test_create_company_authenticated_user(self):
        """Test that authenticated users can create companies"""
        self.authenticate_user(self.employer_user)
        
        company_data = {
            'name': 'New Startup Inc',
            'description': 'A new startup company',
            'location': 'Seattle, WA',
            'website': 'https://newstartup.com',
            'contact_email': 'hello@newstartup.com'
        }
        
        response = self.client.post(reverse('company-list-create'), company_data)
        self.assertResponseSuccess(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Startup Inc')
        
        # Verify company was created with correct creator
        company = Company.objects.get(name='New Startup Inc')
        self.assertEqual(company.created_by, self.employer_user)
        
        # Verify creator was added as manager
        self.assertTrue(company.managers.filter(id=self.employer_user.id).exists())
    
    def test_create_company_unauthenticated(self):
        """Test that unauthenticated users cannot create companies"""
        company_data = {
            'name': 'Unauthorized Company',
            'description': 'Should not be created'
        }
        
        response = self.client.post(reverse('company-list-create'), company_data)
        self.assertResponseError(response, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_company_duplicate_name(self):
        """Test that company names must be unique"""
        self.authenticate_user(self.employer_user)
        
        # Create first company
        company_data1 = {
            'name': 'Unique Company',
            'description': 'First company'
        }
        response1 = self.client.post(reverse('company-list-create'), company_data1)
        self.assertResponseSuccess(response1, status.HTTP_201_CREATED)
        
        # Try to create company with same name
        company_data2 = {
            'name': 'Unique Company',  # Same name
            'description': 'Second company'
        }
        response2 = self.client.post(reverse('company-list-create'), company_data2)
        self.assertResponseError(response2, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response2.data)
    
    def test_create_company_validation(self):
        """Test company creation validation"""
        self.authenticate_user(self.employer_user)
        
        # Test missing required field
        invalid_data = {
            'description': 'Company without name'
        }
        
        response = self.client.post(reverse('company-list-create'), invalid_data)
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

class CompanyUpdateTests(BaseAPITestCase):
    """Test company update functionality"""
    
    def setUp(self):
        super().setUp()
        self.company = Company.objects.create(
            name='Test Company',
            description='Original description',
            location='Original location',
            created_by=self.employer_user
        )
        self.company.managers.add(self.employer_user)
    
    def test_update_company_as_manager(self):
        """Test that company managers can update company information"""
        self.authenticate_user(self.employer_user)
        
        update_data = {
            'name': 'Updated Company Name',
            'description': 'Updated description',
            'location': 'Updated location',
            'website': 'https://updated.com'
        }
        
        response = self.client.put(
            reverse('company-update', args=[self.company.id]), 
            update_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Company Name')
        self.assertEqual(response.data['description'], 'Updated description')
        
        # Verify database was updated
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Updated Company Name')
    
    def test_update_company_as_admin(self):
        """Test that admins can update any company"""
        self.authenticate_user(self.admin_user)
        
        update_data = {
            'name': 'Admin Updated Company',
            'description': 'Updated by admin'
        }
        
        response = self.client.put(
            reverse('company-update', args=[self.company.id]), 
            update_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Admin Updated Company')
    
    def test_update_company_unauthorized(self):
        """Test that non-managers cannot update companies"""
        # Try as job seeker (not a manager)
        self.authenticate_user(self.job_seeker_user)
        
        update_data = {'name': 'Unauthorized Update'}
        response = self.client.put(
            reverse('company-update', args=[self.company.id]), 
            update_data
        )
        self.assertResponsePermissionDenied(response)
        
        # Verify company was not updated
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Test Company')
    
    def test_partial_update_company(self):
        """Test partial updates using PATCH"""
        self.authenticate_user(self.employer_user)
        
        update_data = {
            'description': 'Partially updated description'
        }
        
        response = self.client.patch(
            reverse('company-update', args=[self.company.id]), 
            update_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Partially updated description')
        self.assertEqual(response.data['name'], 'Test Company')  # Name should remain unchanged

class CompanyDeleteTests(BaseAPITestCase):
    """Test company deletion functionality"""
    
    def setUp(self):
        super().setUp()
        self.company = Company.objects.create(
            name='Company To Delete',
            description='This company will be deleted',
            created_by=self.employer_user
        )
    
    def test_delete_company_as_owner(self):
        """Test that company owner can delete company"""
        self.authenticate_user(self.employer_user)
        
        response = self.client.delete(
            reverse('company-delete', args=[self.company.id])
        )
        self.assertResponseSuccess(response, status.HTTP_204_NO_CONTENT)
        
        # Verify company was deleted
        self.assertFalse(Company.objects.filter(id=self.company.id).exists())
    
    def test_delete_company_as_admin(self):
        """Test that admins can delete any company"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.delete(
            reverse('company-delete', args=[self.company.id])
        )
        self.assertResponseSuccess(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(id=self.company.id).exists())
    
    def test_delete_company_unauthorized(self):
        """Test that non-owners cannot delete companies"""
        # Try as job seeker (not owner)
        self.authenticate_user(self.job_seeker_user)
        
        response = self.client.delete(
            reverse('company-delete', args=[self.company.id])
        )
        self.assertResponsePermissionDenied(response)
        
        # Verify company still exists
        self.assertTrue(Company.objects.filter(id=self.company.id).exists())
    
    def test_delete_company_as_manager_but_not_owner(self):
        """Test that managers (but not owners) cannot delete companies"""
        # Create a new user and add as manager
        manager_user = self.create_user(
            username='manageruser',
            user_type='employer'
        )
        self.company.managers.add(manager_user)
        
        # Try to delete as manager (but not owner)
        self.authenticate_user(manager_user)
        
        response = self.client.delete(
            reverse('company-delete', args=[self.company.id])
        )
        self.assertResponsePermissionDenied(response)
        
        # Verify company still exists
        self.assertTrue(Company.objects.filter(id=self.company.id).exists())

class CompanyManagerManagementTests(BaseAPITestCase):
    """Test company manager management functionality"""
    
    def setUp(self):
        super().setUp()
        self.company = Company.objects.create(
            name='Manager Test Company',
            description='Company for manager tests',
            created_by=self.employer_user
        )
        self.company.managers.add(self.employer_user)
        
        # Create additional test users
        self.new_manager = self.create_user(
            username='newmanager',
            user_type='employer',
            first_name='New',
            last_name='Manager'
        )
    
    def test_add_manager_as_owner(self):
        """Test that company owner can add managers"""
        self.authenticate_user(self.employer_user)
        
        manager_data = {
            'user_id': self.new_manager.id
        }
        
        response = self.client.post(
            reverse('company-add-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertIn('added as manager', response.data['message'])
        
        # Verify user was added as manager
        self.assertTrue(self.company.managers.filter(id=self.new_manager.id).exists())
    
    def test_add_manager_as_admin(self):
        """Test that admins can add managers to any company"""
        self.authenticate_user(self.admin_user)
        
        manager_data = {
            'user_id': self.new_manager.id
        }
        
        response = self.client.post(
            reverse('company-add-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertTrue(self.company.managers.filter(id=self.new_manager.id).exists())
    
    def test_add_manager_unauthorized(self):
        """Test that non-owners cannot add managers"""
        self.authenticate_user(self.job_seeker_user)
        
        manager_data = {
            'user_id': self.new_manager.id
        }
        
        response = self.client.post(
            reverse('company-add-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponsePermissionDenied(response)
        
        # Verify user was not added as manager
        self.assertFalse(self.company.managers.filter(id=self.new_manager.id).exists())
    
    def test_add_manager_duplicate(self):
        """Test that adding existing manager returns error"""
        self.authenticate_user(self.employer_user)
        
        # First, add the manager
        manager_data = {'user_id': self.new_manager.id}
        response1 = self.client.post(
            reverse('company-add-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseSuccess(response1, status.HTTP_200_OK)
        
        # Try to add same manager again
        response2 = self.client.post(
            reverse('company-add-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseError(response2, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already a manager', response2.data['error'])
    
    def test_add_job_seeker_as_manager(self):
        """Test that job seekers cannot be added as managers"""
        self.authenticate_user(self.employer_user)
        
        job_seeker = self.create_user(
            username='jobseeker2',
            user_type='job_seeker'
        )
        
        manager_data = {
            'user_id': job_seeker.id
        }
        
        response = self.client.post(
            reverse('company-add-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Only employer users', response.data['error'])
    
    def test_remove_manager_as_owner(self):
        """Test that company owner can remove managers"""
        # First add a manager
        self.company.managers.add(self.new_manager)
        self.assertTrue(self.company.managers.filter(id=self.new_manager.id).exists())
        
        self.authenticate_user(self.employer_user)
        
        manager_data = {
            'user_id': self.new_manager.id
        }
        
        response = self.client.post(
            reverse('company-remove-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertIn('removed from managers', response.data['message'])
        
        # Verify manager was removed
        self.assertFalse(self.company.managers.filter(id=self.new_manager.id).exists())
    
    def test_remove_nonexistent_manager(self):
        """Test that removing non-manager returns error"""
        self.authenticate_user(self.employer_user)
        
        manager_data = {
            'user_id': self.new_manager.id  # This user is not a manager
        }
        
        response = self.client.post(
            reverse('company-remove-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not a manager', response.data['error'])
    
    def test_remove_company_owner_as_manager(self):
        """Test that company owner cannot be removed from managers"""
        self.authenticate_user(self.employer_user)
        
        manager_data = {
            'user_id': self.employer_user.id  # This is the owner
        }
        
        response = self.client.post(
            reverse('company-remove-manager', args=[self.company.id]),
            manager_data
        )
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot remove company owner', response.data['error'])

class CompanyAdminAPITests(BaseAPITestCase):
    """Test admin-only company endpoints"""
    
    def setUp(self):
        super().setUp()
        self.company = Company.objects.create(
            name='Admin Test Company',
            description='Company for admin tests',
            created_by=self.employer_user
        )
    
    def test_admin_list_companies(self):
        """Test that admins can list all companies"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.get(reverse('admin-company-list'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Admin Test Company')
    
    def test_admin_list_companies_unauthorized(self):
        """Test that non-admins cannot access admin company list"""
        # Try as employer
        self.authenticate_user(self.employer_user)
        response = self.client.get(reverse('admin-company-list'))
        self.assertResponsePermissionDenied(response)
        
        # Try as job seeker
        self.authenticate_user(self.job_seeker_user)
        response = self.client.get(reverse('admin-company-list'))
        self.assertResponsePermissionDenied(response)

class CompanyJobRelationshipTests(BaseAPITestCase):
    """Test company-job relationships"""
    
    def setUp(self):
        super().setUp()
        self.company = Company.objects.create(
            name='Job Test Company',
            description='Company for job relationship tests',
            created_by=self.employer_user
        )
        
        # Create jobs for the company
        self.job1 = self.create_test_job(
            company=self.company,
            title='Senior Developer',
            is_active=True
        )
        self.job2 = self.create_test_job(
            company=self.company,
            title='Junior Developer',
            is_active=True
        )
        # Create an inactive job
        self.job3 = self.create_test_job(
            company=self.company,
            title='Inactive Job',
            is_active=False
        )
    
    def test_company_job_count(self):
        """Test that company detail includes job count"""
        response = self.client.get(reverse('company-detail', args=[self.company.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['job_count'], 2)  # Only active jobs
    
    def test_company_jobs_endpoint(self):
        """Test retrieving jobs for a specific company"""
        response = self.client.get(reverse('company-jobs', args=[self.company.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        
        # Should return only active jobs
        self.assertEqual(len(response.data), 2)
        job_titles = [job['title'] for job in response.data]
        self.assertIn('Senior Developer', job_titles)
        self.assertIn('Junior Developer', job_titles)
        self.assertNotIn('Inactive Job', job_titles)

