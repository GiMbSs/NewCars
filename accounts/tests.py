from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username='staff_user', password='testpassword', is_staff=True)
        self.regular_user = User.objects.create_user(username='regular_user', password='testpassword', is_staff=False)

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_successful_login_redirects_staff_to_admin(self):
        response = self.client.post(reverse('login'), {
            'username': 'staff_user',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('admin:index'))

    def test_successful_login_redirects_non_staff_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'regular_user',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_with_invalid_credentials_shows_form_again(self):
        response = self.client.post(reverse('login'), {
            'username': 'regular_user',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(response.context['user'].is_authenticated)

    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'StrongP@ssw0rd!',
            'password2': 'StrongP@ssw0rd!'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='newuser').pk)

    def test_logout_via_post_redirects_to_home(self):
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_via_get_does_not_log_out(self):
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)
