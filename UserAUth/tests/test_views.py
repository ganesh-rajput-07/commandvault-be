from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserRegistrationTests(APITestCase):
    """Test user registration functionality"""
    
    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        # Check user is created but not verified
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_email_verified)
        self.assertIsNotNone(user.email_verification_token)
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email fails"""
        User.objects.create_user(
            email='test@example.com',
            username='existing',
            password='pass123'
        )
        data = {
            'email': 'test@example.com',
            'username': 'newuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_weak_password(self):
        """Test registration with weak password - currently no validation"""
        # Note: Password validation is not enforced in current implementation
        # This test documents current behavior
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'weak'
        }
        response = self.client.post('/api/auth/register/', data)
        # TODO: Add password validation in future
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_register_missing_fields(self):
        """Test registration with missing fields fails"""
        data = {'email': 'test@example.com'}
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """Test user login functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_login_success(self):
        """Test successful login"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_wrong_password(self):
        """Test login with wrong password fails"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user fails"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailVerificationTests(APITestCase):
    """Test email verification functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        # Simulate verification email sent
        from UserAUth.utils import generate_verification_token
        self.user.email_verification_token = generate_verification_token()
        from django.utils import timezone
        self.user.email_verification_sent_at = timezone.now()
        self.user.save()
    
    def test_verify_email_success(self):
        """Test successful email verification"""
        token = self.user.email_verification_token
        response = self.client.get(f'/api/auth/verify-email/{token}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user is now verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        self.assertIsNone(self.user.email_verification_token)
    
    def test_verify_email_invalid_token(self):
        """Test verification with invalid token fails"""
        response = self.client.get('/api/auth/verify-email/invalid-token/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_resend_verification(self):
        """Test resending verification email"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/auth/resend-verification/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileTests(APITestCase):
    """Test user profile functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Test bio'
        }
        response = self.client.patch('/api/auth/user/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.bio, 'Test bio')
    
    def test_profile_unauthenticated(self):
        """Test accessing profile without authentication fails"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
