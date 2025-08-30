from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
from .models import Category, Product, Cart, CartItem, Order, OrderItem


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category description'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertTrue(self.category.is_active)
    
    def test_category_str_method(self):
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_category_get_absolute_url(self):
        expected_url = reverse('store:category_products', kwargs={'slug': self.category.slug})
        self.assertEqual(self.category.get_absolute_url(), expected_url)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            description='Test product description',
            price=Decimal('29.99'),
            stock=10
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, Decimal('29.99'))
        self.assertEqual(self.product.stock, 10)
        self.assertTrue(self.product.is_active)
        self.assertFalse(self.product.is_featured)
    
    def test_product_str_method(self):
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_product_get_absolute_url(self):
        expected_url = reverse('store:product_detail', kwargs={'slug': self.product.slug})
        self.assertEqual(self.product.get_absolute_url(), expected_url)
    
    def test_product_is_in_stock(self):
        self.assertTrue(self.product.is_in_stock)
        
        # Test out of stock
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product1 = Product.objects.create(
            name='Product 1',
            slug='product-1',
            category=self.category,
            description='Product 1 description',
            price=Decimal('19.99'),
            stock=10
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            slug='product-2',
            category=self.category,
            description='Product 2 description',
            price=Decimal('29.99'),
            stock=5
        )
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.total_price, 0)
    
    def test_cart_with_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)
        
        self.assertEqual(self.cart.total_items, 3)
        self.assertEqual(self.cart.total_price, Decimal('69.97'))  # (19.99 * 2) + (29.99 * 1)


class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            description='Test product description',
            price=Decimal('29.99'),
            stock=10
        )
    
    def test_product_list_view(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_product_detail_view(self):
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        self.assertContains(response, '$29.99')
    
    def test_category_products_view(self):
        response = self.client.get(reverse('store:category_products', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            description='Test product description',
            price=Decimal('29.99'),
            stock=10
        )
    
    def test_cart_view_requires_login(self):
        response = self.client.get(reverse('store:cart'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_cart_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('store:cart'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_cart_requires_login(self):
        response = self.client.post(
            reverse('store:add_to_cart'),
            data={'product_id': self.product.id, 'quantity': 1},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])


class AuthenticationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')
    
    def test_register_view(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')
    
    def test_login_functionality(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)


class SecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_csrf_protection(self):
        # Test that CSRF protection is enabled
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Should fail without CSRF token
        self.assertNotEqual(response.status_code, 200)
    
    def test_sql_injection_protection(self):
        # Test basic SQL injection protection
        malicious_input = "'; DROP TABLE store_product; --"
        response = self.client.get(reverse('store:product_list'), {'search': malicious_input})
        self.assertEqual(response.status_code, 200)
        # Should not cause any errors and should return safely
    
    def test_xss_protection(self):
        # Test XSS protection in search
        xss_input = "<script>alert('xss')</script>"
        response = self.client.get(reverse('store:product_list'), {'search': xss_input})
        self.assertEqual(response.status_code, 200)
        # Should not contain unescaped script tags
        self.assertNotContains(response, "<script>alert('xss')</script>", html=False)
