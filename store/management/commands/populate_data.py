from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.files.base import ContentFile
from store.models import Category, Product
from decimal import Decimal
import random
from io import BytesIO
from PIL import Image


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def create_placeholder_image(self, product_name, category_name):
        """Create a simple placeholder image for the product"""
        try:
            # Define colors for different categories
            category_colors = {
                'Electronics': '#3B82F6',      # Blue
                'Clothing': '#EF4444',         # Red
                'Books': '#10B981',            # Green
                'Home & Garden': '#F59E0B',    # Yellow
                'Sports & Outdoors': '#8B5CF6', # Purple
                'Health & Beauty': '#EC4899'   # Pink
            }

            # Get color for category or default to gray
            color = category_colors.get(category_name, '#6B7280')

            # Create a simple colored image
            img = Image.new('RGB', (400, 400), color=color)

            # Save to BytesIO
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)

            # Create filename
            filename = f"{slugify(product_name)}.jpg"

            return ContentFile(img_io.getvalue(), name=filename)
        except Exception as e:
            self.stdout.write(f'Error creating image for {product_name}: {e}')
            return None

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create categories
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Latest electronic gadgets and devices'
            },
            {
                'name': 'Clothing',
                'description': 'Fashion and apparel for all occasions'
            },
            {
                'name': 'Books',
                'description': 'Books, magazines, and educational materials'
            },
            {
                'name': 'Home & Garden',
                'description': 'Home improvement and garden supplies'
            },
            {
                'name': 'Sports & Outdoors',
                'description': 'Sports equipment and outdoor gear'
            },
            {
                'name': 'Health & Beauty',
                'description': 'Health, wellness, and beauty products'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products_data = [
            # Electronics
            {
                'name': 'Wireless Bluetooth Headphones',
                'description': 'High-quality wireless headphones with noise cancellation and long battery life.',
                'price': Decimal('99.99'),
                'stock': 50,
                'category': 'Electronics',
                'is_featured': True
            },
            {
                'name': 'Smartphone Case',
                'description': 'Durable protective case for smartphones with shock absorption.',
                'price': Decimal('24.99'),
                'stock': 100,
                'category': 'Electronics'
            },
            {
                'name': 'Portable Charger',
                'description': '10000mAh portable power bank with fast charging capability.',
                'price': Decimal('39.99'),
                'stock': 75,
                'category': 'Electronics'
            },
            
            # Clothing
            {
                'name': 'Cotton T-Shirt',
                'description': 'Comfortable 100% cotton t-shirt available in multiple colors.',
                'price': Decimal('19.99'),
                'stock': 200,
                'category': 'Clothing',
                'is_featured': True
            },
            {
                'name': 'Denim Jeans',
                'description': 'Classic fit denim jeans made from premium quality fabric.',
                'price': Decimal('59.99'),
                'stock': 80,
                'category': 'Clothing'
            },
            {
                'name': 'Winter Jacket',
                'description': 'Warm and stylish winter jacket with water-resistant coating.',
                'price': Decimal('129.99'),
                'stock': 30,
                'category': 'Clothing'
            },
            
            # Books
            {
                'name': 'Python Programming Guide',
                'description': 'Comprehensive guide to Python programming for beginners and experts.',
                'price': Decimal('34.99'),
                'stock': 60,
                'category': 'Books'
            },
            {
                'name': 'Science Fiction Novel',
                'description': 'Bestselling science fiction novel with thrilling adventures.',
                'price': Decimal('14.99'),
                'stock': 90,
                'category': 'Books'
            },
            
            # Home & Garden
            {
                'name': 'LED Desk Lamp',
                'description': 'Adjustable LED desk lamp with multiple brightness levels.',
                'price': Decimal('45.99'),
                'stock': 40,
                'category': 'Home & Garden'
            },
            {
                'name': 'Plant Pot Set',
                'description': 'Set of 3 ceramic plant pots with drainage holes.',
                'price': Decimal('29.99'),
                'stock': 70,
                'category': 'Home & Garden',
                'is_featured': True
            },
            
            # Sports & Outdoors
            {
                'name': 'Yoga Mat',
                'description': 'Non-slip yoga mat with extra cushioning for comfort.',
                'price': Decimal('35.99'),
                'stock': 85,
                'category': 'Sports & Outdoors'
            },
            {
                'name': 'Water Bottle',
                'description': 'Stainless steel insulated water bottle keeps drinks cold for 24 hours.',
                'price': Decimal('22.99'),
                'stock': 120,
                'category': 'Sports & Outdoors'
            },
            
            # Health & Beauty
            {
                'name': 'Vitamin C Serum',
                'description': 'Anti-aging vitamin C serum for brighter, healthier skin.',
                'price': Decimal('49.99'),
                'stock': 55,
                'category': 'Health & Beauty'
            },
            {
                'name': 'Essential Oil Set',
                'description': 'Set of 6 pure essential oils for aromatherapy and relaxation.',
                'price': Decimal('39.99'),
                'stock': 45,
                'category': 'Health & Beauty'
            }
        ]
        
        for product_data in products_data:
            category = Category.objects.get(name=product_data['category'])
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'slug': slugify(product_data['name']),
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'category': category,
                    'is_featured': product_data.get('is_featured', False)
                }
            )

            # Add placeholder image if product was created and doesn't have an image
            if created or not product.image:
                placeholder_image = self.create_placeholder_image(product.name, category.name)
                if placeholder_image:
                    product.image.save(placeholder_image.name, placeholder_image, save=True)
                    self.stdout.write(f'Added image to product: {product.name}')

            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create a test user
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(f'Created test user: {user.username}')
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created admin user: {admin_user.username}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
        self.stdout.write(
            self.style.WARNING('Test user credentials: testuser / testpass123')
        )
        self.stdout.write(
            self.style.WARNING('Admin credentials: admin / admin123')
        )
