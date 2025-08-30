from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        # Profile should be created automatically via signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_str_method(self):
        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.user.profile), expected_str)


class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form_password_mismatch(self):
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_invalid_form_missing_email(self):
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_valid_profile_form(self):
        form_data = {
            'phone': '+1234567890',
            'address_line_1': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'US'
        }
        form = UserProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())


class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_login_view_get(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')
    
    def test_login_view_post_valid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Please enter a correct username and password')
    
    def test_register_view_get(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')
    
    def test_register_view_post_valid(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_edit_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:edit_profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_profile_view_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone': '+1234567890',
            'address_line_1': '123 Updated Street',
            'city': 'Updated City',
            'state': 'Updated State',
            'postal_code': '54321',
            'country': 'US'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Check if user was updated
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.email, 'updated@example.com')
    
    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_order_history_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:order_history'))
        self.assertEqual(response.status_code, 200)
    
    def test_order_history_view_unauthenticated(self):
        response = self.client.get(reverse('accounts:order_history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class UserProfileSignalTest(TestCase):
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(
            username='signaltest',
            email='signal@example.com',
            password='testpass123'
        )
        # Profile should be created automatically
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
    
    def test_profile_saved_on_user_save(self):
        user = User.objects.create_user(
            username='signaltest2',
            email='signal2@example.com',
            password='testpass123'
        )
        
        # Update user
        user.first_name = 'Updated'
        user.save()
        
        # Profile should still exist
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
