from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('carros/', include('cars.urls')),
    path('usuarios/', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
