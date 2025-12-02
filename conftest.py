"""
conftest.py - Configure Django for tests
Place this file in the root directory (same level as tests/ folder)
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

# Setup Django
if not settings.configured:
    django.setup()