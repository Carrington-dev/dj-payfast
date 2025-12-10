# dj-payfast - Django + Payfast Made Easy

[![payfast Verified Partner](https://img.shields.io/static/v1?label=payfast&message=Verified%20Partner&color=red&style=for-the-badge)](https://payfast.com/docs/libraries#community-libraries)
<br>

[![CI tests](./assets/img/badge.svg)](https://github.com/dj-payfast/dj-payfast/actions/workflows/ci.yml)
[![Package Downloads](https://img.shields.io/pypi/dm/dj-payfast)](https://pypi.org/project/dj-payfast/)
[![Documentation](https://img.shields.io/static/v1?label=Docs&message=READ&color=informational&style=plastic)](https://carrington-dev.github.io/dj-payfast/)
[![Sponsor dj-payfast](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=red&style=plastic)](https://github.com/sponsors/dj-payfast)
[![MIT License](https://img.shields.io/static/v1?label=License&message=MIT&color=informational&style=plastic)](https://github.com/sponsors/dj-payfast)

PayFast Models for Django.

## Introduction

dj-payfast implements all of the Payfast models intergration, for Django. Set up your
webhook endpoint and start receiving model updates. You will then have
a copy of all the payfast models available in Django models, as soon as
they are updated!

The full documentation is available [on Read the Docs](https://carrington-dev.github.io/dj-payfast/).

## Features

-   Payfast Core
-   Payfast Billing
-   Payfast Cards (JS v2) and Sources (JS v3)
-   Payment Methods and Payment Intents (SCA support)
-   Support for multiple accounts and API keys
-   Payfast Connect (partial support)
-   Tested with Payfast API `2020-08-27` (see [API versions](api_versions.md#dj-payfast_latest_tested_version))

## Requirements

-   Django >=4.2
-   Python >=3.9
-   PostgreSQL engine (recommended) >=12
-   MySQL engine: MariaDB >=10.5 or MySQL >=8.0
-   SQLite: Not recommended in production. Version >=3.26 required.
-   Nginx, Gunicorn, Docker
-   Celery is included
-   Email setup

## Installation

See [installation](https://dj-payfast.dev/dj-payfast/2.7/installation/) instructions.


### 1. Install via pip

```bash
pip install dj-payfast
```

### 2. Add to `INSTALLED_APPS`

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',  # Optional, for API support
    'payfast',         # Add this
    
    # Your apps
    'myapp',
]
```

### 3. Configure URLs

```python
# urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payfast/', include('payfast.urls')),  # Add this
    # Your other URLs
]
```

This creates the webhook endpoint at: `/payfast/notify/`

### 4. Run Migrations

```bash
python manage.py migrate
```

---

## Configuration

### Basic Configuration

Add your PayFast credentials to `settings.py`:

```python
# settings.py

# PayFast Configuration
PAYFAST_MERCHANT_ID = '10023192'           # Your merchant ID
PAYFAST_MERCHANT_KEY = 'ecs5ue9vb4i70'     # Your merchant key
PAYFAST_PASSPHRASE = 'jt7NOE43FZPn'        # Your passphrase (recommended)
PAYFAST_TEST_MODE = True                    # False for production
```

### Environment Variables (Recommended)

**Never commit credentials to version control!** Use environment variables:

```python
# settings.py
import os

PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
PAYFAST_TEST_MODE = os.environ.get('PAYFAST_TEST_MODE', 'True') == 'True'
```

Create a `.env` file:

```bash
# .env
PAYFAST_MERCHANT_ID=10023192
PAYFAST_MERCHANT_KEY=ecs5ue9vb4i70
PAYFAST_PASSPHRASE=jt7NOE43FZPn
PAYFAST_TEST_MODE=True
```

### Getting PayFast Credentials

**Sandbox (Testing):**
1. Sign up at [sandbox.payfast.co.za](https://sandbox.payfast.co.za)
2. Navigate to **Settings → Integration**
3. Copy your Merchant ID and Merchant Key
4. Generate a passphrase

**Production:**
1. Sign up at [www.payfast.co.za](https://www.payfast.co.za)
2. Complete merchant verification
3. Navigate to **Settings → Integration**
4. Copy your credentials

---


## Usage Examples
### Steps Taken When Using API Calls (To make it dynamic)

Create a payment (post) endpoint at: `/payfast/payments/`

```json
// some fields are not required
// This is a post request
{
    "m_payment_id": "",
    "user": null,
    "amount": null,
    "item_name": "",
    "item_description": "",
    "name_first": "",
    "name_last": "",
    "email_address": "",
    "cell_number": "",
    "custom_str1": "",
    "custom_str2": "",
    "custom_str3": "",
    "custom_str4": "",
    "custom_str5": "",
    "custom_int1": null,
    "custom_int2": null,
    "custom_int3": null,
    "custom_int4": null,
    "custom_int5": null
}
```
This request returns something like this
```json
{
    "amount": "99.99",
    "item_name": "Premium Subscription",
    "item_description": "1 month premium access",
    "name_first": "",
    "name_last": "",
    "email_address": "crn96m@gmail.com",
    "m_payment_id": "3a280ceb-344c-48d1-8e9c-7945f3f1194a",
    "payfast_url": "http://127.0.0.1:2000/payments/checkout/2"
}
```

__if you are using a frontend app like REACTJS just redirect to 'payfast_url'__

After the completion of this payment payfast will redirect to complete endpoint or cancelled endpoint


### Steps Taken Using Query Parameters (To make it dynamic)

#### Example 1: E-commerce Checkout

```python
# views.py
from django.shortcuts import redirect, reverse
from urllib.parse import urlencode
from .models import Order

def process_order_checkout(request, order_id):
    """
    Process order and redirect to PayFast checkout
    """
    order = Order.objects.get(id=order_id, user=request.user)
    
    # Calculate total
    total = order.calculate_total()
    
    # Build item description
    items = ', '.join([f"{item.quantity}x {item.product.name}" 
                       for item in order.items.all()])
    
    params = urlencode({
        'amount': total,
        'item_name': f'Order #{order.id}',
        'item_description': items,
        'custom_str1': f'order_{order.id}',
        'custom_int1': order.items.count(),
        'email_address': request.user.email,
    })
    
    url = f"{reverse('payfast:checkout')}?{params}"
    return redirect(url)
```

## Changelog

[See release notes on Read the Docs](history/2_7_0/).

<!-- This link *will* get stale again eventually. There should be an index page for the
     changelog that can be linked to.

     For example:
     https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#section-index-pages -->

## Funding and Support

<a href="https://payfast.io">
  <img alt="Payfast Logo" src="https://github.com/Carrington-dev/dj-payfast/blob/main/assets/img/payfast.webp" width="250px" />
</a>

You can now become a sponsor to dj-payfast with [GitHub Sponsors](https://github.com/sponsors/dj-payfast).

We've been bringing dj-payfast to the world for over 10 years and are excited to be able to start
dedicating some real resources to the project.

Your sponsorship helps us keep a team of maintainers actively working to improve dj-payfast and
ensure it stays up-to-date with the latest payfast changes. If you use dj-payfast commercially, we would encourage you to invest in its continued
development by [signing up for a paid plan](https://github.com/sponsors/dj-payfast).
Corporate sponsors [receive priority support and development time](project/support.md).

All contributions through GitHub sponsors flow into our [Open Collective](https://opencollective.com/dj-payfast), which holds our funds and keeps
an open ledger on how donations are spent.

## Our Gold sponsors

<a href="https://payfast.io">
<!--   <img alt="Stemgon Logo" src="./logos/payfast_blurple.svg" width="250px" /> -->
  <img alt="Payfast Logo" src="https://github.com/Carrington-dev/dj-payfast/blob/main/assets/img/payfast.webp" width="250px" />
</a>

## Similar libraries

-   [dj-paypal](https://github.com/HearthSim/dj-paypal)
    ([PayPal](https://www.paypal.com/))
-   [dj-paddle](https://github.com/paddle-python/dj-paddle)
    ([Paddle](https://paddle.com/))
