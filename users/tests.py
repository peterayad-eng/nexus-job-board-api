from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobboard.test_utils import BaseAPITestCase

# Create your tests here.
User = get_user_model()

class AuthenticationTests(BaseAPITestCase):
    def test_user_registration_workflow(self):
        """Test complete user registration and login workflow"""
        # Test registration
        reg_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'password_confirmation': 'newpass123',
            'user_type': 'job_seeker',
            'first_name': 'New',
            'last_name': 'User'
        }

        # Use the correct URL name from your users/urls.py
        reg_response = self.client.post(reverse('register'), reg_data)
        self.assertResponseSuccess(reg_response, status.HTTP_201_CREATED)

        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.user_type, 'job_seeker')

        # Test login with new user
        login_data = self.api_login(username='newuser', password='newpass123')
        self.assertIsNotNone(login_data)
        self.assertIn('access', login_data)
        self.assertIn('refresh', login_data)

    def test_employer_registration(self):
        """Test employer registration with required fields"""
        reg_data = {
            'username': 'newemployer',
            'email': 'employer@company.com',
            'password': 'employerpass123',
            'password_confirmation': 'employerpass123',
            'user_type': 'employer',
            'first_name': 'Company',
            'last_name': 'Owner'
        }

        response = self.client.post(reverse('register'), reg_data)
        self.assertResponseSuccess(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['user_type'], 'employer')

    def test_registration_validation(self):
        """Test registration validation errors"""
        # Test missing required fields
        invalid_data = {
            'username': 'invaliduser',
            'password': 'short',
            'password_confirmation': 'short'
        }

        response = self.client.post(reverse('register'), invalid_data)
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)  # Should have password validation error

    def test_user_login_success(self):
        """Test successful user login"""
        login_data = {
            'username': 'jobseeker1',
            'password': 'testpass123'
        }

        response = self.client.post(reverse('login'), login_data)
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'jobseeker1')

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'jobseeker1',
            'password': 'wrongpassword'
        }

        response = self.client.post(reverse('login'), login_data)
        self.assertResponseError(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_token_refresh(self):
        """Test JWT token refresh functionality"""
        # First login to get tokens
        login_response = self.client.post(reverse('login'), {
            'username': 'jobseeker1',
            'password': 'testpass123'
        })
        refresh_token = login_response.data['refresh']

        # Refresh the token
        refresh_response = self.client.post(reverse('token-refresh'), {
            'refresh': refresh_token
        })

        self.assertResponseSuccess(refresh_response, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

class UserProfileTests(BaseAPITestCase):
    def test_get_user_profile_authenticated(self):
        """Test retrieving user profile when authenticated"""
        self.authenticate_user(self.job_seeker_user)

        response = self.client.get(reverse('user-profile'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'jobseeker1')
        self.assertEqual(response.data['user_type'], 'job_seeker')

    def test_get_user_profile_unauthenticated(self):
        """Test that unauthenticated users cannot access profile"""
        response = self.client.get(reverse('user-profile'))
        self.assertResponseError(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile(self):
        """Test updating user profile information"""
        self.authenticate_user(self.job_seeker_user)

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'This is my updated bio',
            'phone_number': '+14155552671'
        }

        response = self.client.put(reverse('user-profile'), update_data)
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['bio'], 'This is my updated bio')

    def test_password_update(self):
        """Test user password update functionality"""
        self.authenticate_user(self.job_seeker_user)

        password_data = {
            'current_password': 'testpass123',
            'new_password': 'newsecurepassword456',
            'confirm_password': 'newsecurepassword456'
        }

        response = self.client.put(reverse('user-password-update'), password_data)
        self.assertResponseSuccess(response, status.HTTP_200_OK)

        # Verify new password works by logging in with it
        self.remove_authentication()
        login_response = self.client.post(reverse('login'), {
            'username': 'jobseeker1',
            'password': 'newsecurepassword456'
        })
        self.assertResponseSuccess(login_response, status.HTTP_200_OK)

class UserPermissionTests(BaseAPITestCase):
    def test_admin_user_list_access(self):
        """Test that only admins can access user list"""
        # Try without authentication
        response = self.client.get(reverse('admin-user-list'))
        self.assertResponseError(response, status.HTTP_401_UNAUTHORIZED)

        # Try as job seeker (should be denied)
        self.authenticate_user(self.job_seeker_user)
        response = self.client.get(reverse('admin-user-list'))
        self.assertResponsePermissionDenied(response)

        # Try as employer (should be denied)
        self.authenticate_user(self.employer_user)
        response = self.client.get(reverse('admin-user-list'))
        self.assertResponsePermissionDenied(response)

        # Try as admin (should succeed)
        self.authenticate_user(self.admin_user)
        response = self.client.get(reverse('admin-user-list'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)

    def test_user_search_admin_only(self):
        """Test that user search is admin-only"""
        self.authenticate_user(self.job_seeker_user)
        response = self.client.get(reverse('admin-user-search') + '?search=test')
        self.assertResponsePermissionDenied(response)

        self.authenticate_user(self.admin_user)
        response = self.client.get(reverse('admin-user-search') + '?search=jobseeker')
        self.assertResponseSuccess(response, status.HTTP_200_OK)

    def test_user_activation_admin_only(self):
        """Test that only admins can activate/deactivate users"""
        # Create a test user to activate/deactivate
        test_user = self.create_user(username='testuser')

        self.authenticate_user(self.employer_user)
        response = self.client.patch(reverse('admin-user-activation', args=[test_user.id]))
        self.assertResponsePermissionDenied(response)

        self.authenticate_user(self.admin_user)
        response = self.client.patch(reverse('admin-user-activation', args=[test_user.id]))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertIn('is_active', response.data)

class UserStatsTests(BaseAPITestCase):
    def test_user_stats_admin_only(self):
        """Test that user statistics are admin-only"""
        self.authenticate_user(self.job_seeker_user)
        response = self.client.get(reverse('admin-user-stats'))
        self.assertResponsePermissionDenied(response)

        self.authenticate_user(self.admin_user)
        response = self.client.get(reverse('admin-user-stats'))
        self.assertResponseSuccess(response, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('job_seekers', response.data)
        self.assertIn('employers', response.data)

