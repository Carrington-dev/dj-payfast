"""
dj-payfast: Django PayFast Integration Library
A comprehensive Django library for PayFast payment gateway integration in South Africa

PROJECT STRUCTURE:
==================

dj-payfast/
├── README.md
├── LICENSE
├── setup.py
├── requirements.txt
├── MANIFEST.in
├── .gitignore
│
├── payfast/                          # Main package directory
│   ├── __init__.py                   # Package initialization, version info
│   ├── apps.py                       # Django app configuration
│   ├── conf.py                       # Settings and configuration
│   ├── models.py                     # Database models (Payment, Notification)
│   ├── forms.py                      # PayFast payment form
│   ├── views.py                      # Webhook handler views
│   ├── utils.py                      # Signature generation, validation
│   ├── admin.py                      # Django admin configuration
│   ├── urls.py                       # URL routing for webhooks
│   ├── signals.py                    # Django signals (optional)
│   ├── exceptions.py                 # Custom exceptions (optional)
│   │
│   ├── migrations/                   # Database migrations
│   │   └── __init__.py
│   │
│   ├── management/                   # Management commands
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── payfast_test.py       # Test payment command
│   │
│   └── templates/                    # Optional template examples
│       └── payfast/
│           └── payment_form.html     # Example payment template
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── test_models.py                # Model tests
│   ├── test_views.py                 # View/webhook tests
│   ├── test_forms.py                 # Form tests
│   ├── test_utils.py                 # Utility function tests
│   └── test_signals.py               # Signal tests
│
├── docs/                             # Documentation
│   ├── conf.py                       # Sphinx configuration
│   ├── index.rst
│   ├── installation.rst
│   ├── quickstart.rst
│   ├── configuration.rst
│   ├── usage.rst
│   └── api.rst
│
└── example_project/                  # Example Django project
    ├── manage.py
    ├── example_project/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    └── shop/                         # Example app using dj-payfast
        ├── __init__.py
        ├── views.py
        ├── urls.py
        └── templates/
            └── shop/
                ├── checkout.html
                ├── success.html
                └── cancel.html

INSTALLATION:
=============
pip install dj-payfast

SETTINGS.PY CONFIGURATION:
==========================
INSTALLED_APPS = [
    ...
    'payfast',
]

PAYFAST_MERCHANT_ID = 'your_merchant_id'
PAYFAST_MERCHANT_KEY = 'your_merchant_key'
PAYFAST_PASSPHRASE = 'your_passphrase'
PAYFAST_TEST_MODE = True

URLS.PY CONFIGURATION:
======================
urlpatterns = [
    ...
    path('payfast/', include('payfast.urls')),
]
"""