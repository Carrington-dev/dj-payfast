#!/usr/bin/env python
"""
setup_and_test.py - Setup and run tests
Usage: python setup_and_test.py
"""
import os
import sys
import django
import subprocess

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

from django.core.management import call_command

def main():
    print("=" * 60)
    print("dj-payfast Test Setup and Execution")
    print("=" * 60)
    print()
    
    # Step 1: Create migrations
    print("Step 1: Creating migrations...")
    try:
        call_command('makemigrations', 'payfast', verbosity=1)
        print("✓ Migrations created successfully")
    except Exception as e:
        print(f"✗ Error creating migrations: {e}")
        return 1
    
    print()
    
    # Step 2: Run migrations
    print("Step 2: Running migrations...")
    try:
        call_command('migrate', verbosity=1, run_syncdb=True)
        print("✓ Migrations applied successfully")
    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        return 1
    
    print()
    
    # Step 3: Run tests
    print("Step 3: Running tests...")
    print("-" * 60)
    try:
        call_command('test', 'tests', verbosity=2)
        print()
        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        return 0
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Tests failed: {e}")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())