from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import ProtectedError
from unittest.mock import patch, MagicMock
from decimal import Decimal

from .models import Brand, Car
from .forms import CarForm
from ai_api.client import get_ai_description

User = get_user_model()

class CarModelTest(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name='Toyota')
        self.car = Car.objects.create(
            model='Corolla',
            brand=self.brand,
            factory_year=2022,
            model_year=2023,
            color='Prata',
            transmission='Automático',
            mileage=15000,
            price=Decimal('120000.00'),
            is_new=False,
            is_available=True,
            highlighted=True
        )

    def test_car_creation_with_valid_data(self):
        self.assertEqual(Car.objects.count(), 1)
        self.assertEqual(self.car.model, 'Corolla')
        self.assertEqual(self.car.brand.name, 'Toyota')

    def test_car_str_method(self):
        expected_str = f'[{self.car.id}]Toyota Corolla (2023)'
        self.assertEqual(str(self.car), expected_str)

    def test_brand_str_method(self):
        self.assertEqual(str(self.brand), 'Toyota')

    def test_brand_name_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Brand.objects.create(name='Toyota')

    def test_car_mileage_allows_null_blank_with_default(self):
        car2 = Car.objects.create(
            model='Hilux',
            brand=self.brand,
            factory_year=2023,
            model_year=2024,
            color='Branco',
            transmission='Automático',
            price=Decimal('250000.00')
        )
        self.assertEqual(car2.mileage, 0)

    def test_car_brand_protect_on_delete(self):
        with self.assertRaises(ProtectedError):
            self.brand.delete()

class CarFormTest(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name='Honda')

    def test_valid_form_submission(self):
        data = {
            'model': 'Civic',
            'brand': self.brand.id,
            'factory_year': 2022,
            'model_year': 2023,
            'color': 'Preto',
            'transmission': 'Automático',
            'mileage': 10000,
            'price': '130000.00',
            'is_new': False,
            'is_available': True,
            'highlighted': False
        }
        form = CarForm(data=data)
        self.assertTrue(form.is_valid())

    def test_is_new_with_mileage_greater_than_zero(self):
        data = {
            'model': 'Civic',
            'brand': self.brand.id,
            'factory_year': 2023,
            'model_year': 2024,
            'color': 'Preto',
            'transmission': 'Automático',
            'mileage': 100,
            'price': '150000.00',
            'is_new': True,
            'is_available': True,
            'highlighted': False
        }
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('mileage', form.errors)
        self.assertEqual(form.errors['mileage'][0], 'Carros novos não podem ter quilometragem maior que zero.')

    def test_is_new_with_mileage_zero(self):
        data = {
            'model': 'Civic',
            'brand': self.brand.id,
            'factory_year': 2023,
            'model_year': 2024,
            'color': 'Preto',
            'transmission': 'Automático',
            'mileage': 0,
            'price': '150000.00',
            'is_new': True,
            'is_available': True,
            'highlighted': False
        }
        form = CarForm(data=data)
        self.assertTrue(form.is_valid())

    def test_is_new_with_mileage_none(self):
        data = {
            'model': 'Civic',
            'brand': self.brand.id,
            'factory_year': 2023,
            'model_year': 2024,
            'color': 'Preto',
            'transmission': 'Automático',
            'mileage': None,
            'price': '150000.00',
            'is_new': True,
            'is_available': True,
            'highlighted': False
        }
        form = CarForm(data=data)
        self.assertTrue(form.is_valid())

    def test_factory_year_and_model_year_difference_greater_than_1(self):
        data = {
            'model': 'Civic',
            'brand': self.brand.id,
            'factory_year': 2020,
            'model_year': 2024,
            'color': 'Preto',
            'transmission': 'Automático',
            'mileage': 50000,
            'price': '100000.00',
            'is_new': False,
            'is_available': True,
            'highlighted': False
        }
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('factory_year', form.errors)
        self.assertEqual(form.errors['factory_year'][0], 'Ano de fabricação e modelo inválidos.')

    def test_factory_year_equal_to_model_year(self):
        data = {
            'model': 'Civic',
            'brand': self.brand.id,
            'factory_year': 2023,
            'model_year': 2023,
            'color': 'Preto',
            'transmission': 'Automático',
            'mileage': 1000,
            'price': '140000.00',
            'is_new': False,
            'is_available': True,
            'highlighted': False
        }
        form = CarForm(data=data)
        self.assertTrue(form.is_valid())

    def test_highlighted_true_with_is_available_false(self):
        data = {
            'model': 'Civic',
            'brand': self.brand.id,
            'factory_year': 2023,
            'model_year': 2024,
            'color': 'Preto',
            'transmission': 'Automático',
            'mileage': 1000,
            'price': '140000.00',
            'is_new': False,
            'is_available': False,
            'highlighted': True
        }
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('highlighted', form.errors)
        self.assertEqual(form.errors['highlighted'][0], 'Carros destacados devem estar disponíveis.')


class CarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.brand = Brand.objects.create(name='Ford')
        self.car = Car.objects.create(
            model='Mustang',
            brand=self.brand,
            factory_year=2022,
            model_year=2023,
            color='Vermelho',
            transmission='Automático',
            mileage=5000,
            price=Decimal('350000.00'),
            is_available=True
        )

    def test_car_list_view_returns_200_and_uses_correct_template(self):
        response = self.client.get(reverse('list_cars'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cars_list.html')

    def test_car_detail_view_returns_200_for_existing_car(self):
        response = self.client.get(reverse('car_detail', args=[self.car.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_detail.html')

    def test_car_detail_view_returns_404_for_non_existing_car(self):
        response = self.client.get(reverse('car_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_car_create_view_requires_staff_login(self):
        response = self.client.get(reverse('create_car'))
        self.assertRedirects(response, '/usuarios/login/?next=/carros/cadastrar/')

    def test_car_create_view_accessible_by_staff_returns_200(self):
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('create_car'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_car.html')

    def test_car_delete_view_requires_staff_login(self):
        response = self.client.get(reverse('delete_car', args=[self.car.id]))
        self.assertRedirects(response, f'/admin/login/?next=/carros/deletar/{self.car.id}/')


class AIApiTest(TestCase):
    @patch('ai_api.client.os.getenv')
    def test_get_ai_description_empty_string_when_api_key_not_set(self, mock_getenv):
        mock_getenv.return_value = None
        description = get_ai_description('Corolla', 'Toyota', 2022)
        self.assertEqual(description, '')

    @patch('ai_api.client.os.getenv')
    @patch('ai_api.client.OpenAI')
    def test_get_ai_description_handles_api_exceptions_gracefully(self, mock_openai, mock_getenv):
        mock_getenv.return_value = 'fake_api_key'
        
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception('API Error')
        
        description = get_ai_description('Corolla', 'Toyota', 2022)
        self.assertEqual(description, '')
