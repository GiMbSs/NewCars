from django.urls import path
from .views import Home, Logs

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('logs/', Logs.as_view(), name='logs'),
]
