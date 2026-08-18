import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.test_settings')
django.setup()
from django.test import Client
from django.urls import reverse
client = Client()
response = client.post(reverse('register'), {'username': 'newuser123', 'password1': 'StrongP@ssw0rd!', 'password2': 'StrongP@ssw0rd!'})
print("STATUS:", response.status_code)
if response.status_code == 200:
    print(response.context['user_form'].errors)
