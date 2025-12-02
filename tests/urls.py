"""
URL configuration for tests
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payfast/', include('payfast.urls')),
]