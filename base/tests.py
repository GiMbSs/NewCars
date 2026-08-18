from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cars.models import Brand, Car
from decimal import Decimal

User = get_user_model()

class BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.regular_user = User.objects.create_user(username='user', password='password', is_staff=False)
        
        self.brand = Brand.objects.create(name='Chevrolet')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        
        # Highlighted and available
        self.car1 = Car.objects.create(
            model='Onix', brand=self.brand, factory_year=2022, model_year=2023,
            color='Preto', transmission='Manual', price=Decimal('80000.00'),
            is_available=True, highlighted=True, image='test.jpg'
        )
        
        # Available but not highlighted
        self.car2 = Car.objects.create(
            model='Cruze', brand=self.brand, factory_year=2022, model_year=2023,
            color='Prata', transmission='Automático', price=Decimal('120000.00'),
            is_available=True, highlighted=False, image='test.jpg'
        )
        
        # Highlighted but not available (invalid according to form, but let's test view filtering anyway)
        self.car3 = Car.objects.create(
            model='Tracker', brand=self.brand, factory_year=2022, model_year=2023,
            color='Branco', transmission='Automático', price=Decimal('140000.00'),
            is_available=False, highlighted=True, image='test.jpg'
        )

    def test_home_page_returns_200_and_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_shows_only_highlighted_and_available_cars(self):
        response = self.client.get(reverse('home'))
        cars = response.context.get('cars', response.context.get('object_list'))
        self.assertIsNotNone(cars)
        
        # Should contain car1 (highlighted + available)
        self.assertIn(self.car1, cars)
        
        # Should NOT contain car2 (not highlighted)
        self.assertNotIn(self.car2, cars)
        
        # Should NOT contain car3 (not available)
        self.assertNotIn(self.car3, cars)

    def test_logs_page_requires_staff_login(self):
        response = self.client.get(reverse('logs'))
        # Using login required decorator might redirect to /usuarios/login/
        self.assertRedirects(response, '/usuarios/login/?next=/logs/')

    def test_logs_page_accessible_by_staff_returns_200(self):
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('logs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logs.html')
