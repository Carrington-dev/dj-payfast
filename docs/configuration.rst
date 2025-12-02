===============================================================================
CONFIGURATION.RST
===============================================================================

Configuration
=============

This guide covers all configuration options for **dj-payfast**.

Basic Settings
--------------

Required Settings
~~~~~~~~~~~~~~~~~

These settings must be configured in your ``settings.py``:

.. code-block:: python

   # PayFast Merchant Credentials
   PAYFAST_MERCHANT_ID = 'your_merchant_id'
   PAYFAST_MERCHANT_KEY = 'your_merchant_key'
   
   # Test or Production Mode
   PAYFAST_TEST_MODE = True  # Set to False for production

Optional Settings
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Security passphrase (highly recommended)
   PAYFAST_PASSPHRASE = 'your_secure_passphrase'

Environment Variables
---------------------

**Recommended**: Store credentials as environment variables:

.. code-block:: python

   import os
   
   PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
   PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
   PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
   PAYFAST_TEST_MODE = os.environ.get('PAYFAST_TEST_MODE', 'True') == 'True'

Using python-decouple:

.. code-block:: bash

   pip install python-decouple

.. code-block:: python

   from decouple import config
   
   PAYFAST_MERCHANT_ID = config('PAYFAST_MERCHANT_ID')
   PAYFAST_MERCHANT_KEY = config('PAYFAST_MERCHANT_KEY')
   PAYFAST_PASSPHRASE = config('PAYFAST_PASSPHRASE', default='')
   PAYFAST_TEST_MODE = config('PAYFAST_TEST_MODE', default=True, cast=bool)

Create a ``.env`` file:

.. code-block:: text

   PAYFAST_MERCHANT_ID=10000100
   PAYFAST_MERCHANT_KEY=46f0cd694581a
   PAYFAST_PASSPHRASE=your_secure_passphrase
   PAYFAST_TEST_MODE=True

Test vs Production Mode
------------------------

Test Mode (Sandbox)
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   PAYFAST_TEST_MODE = True

* Uses sandbox.payfast.co.za
* Test credentials required
* No real money processed
* Perfect for development

Production Mode
~~~~~~~~~~~~~~~

.. code-block:: python

   PAYFAST_TEST_MODE = False

* Uses www.payfast.co.za
* Production credentials required
* Real money processed
* Requires verified merchant account

URL Configuration
-----------------

PayFast URLs are automatically configured based on ``PAYFAST_TEST_MODE``:

**Test Mode URLs:**

* Payment: ``https://sandbox.payfast.co.za/eng/process``
* Validation: ``https://sandbox.payfast.co.za/eng/query/validate``

**Production URLs:**

* Payment: ``https://www.payfast.co.za/eng/process``
* Validation: ``https://www.payfast.co.za/eng/query/validate``

Custom Configuration
--------------------

Advanced users can override default URLs:

.. code-block:: python

   # Custom PayFast URLs (not recommended)
   PAYFAST_URL = 'https://custom.payfast.url/process'
   PAYFAST_VALIDATE_URL = 'https://custom.payfast.url/validate'

Database Configuration
----------------------

dj-payfast creates two models:

* ``PayFastPayment`` - Stores payment records
* ``PayFastNotification`` - Logs webhook notifications

Default settings work for most cases. For high-volume sites:

.. code-block:: python

   # Add database indexes
   DATABASES = {
       'default': {
           # ... your database config
       }
   }
   
   # Consider separate database for payments
   DATABASE_ROUTERS = ['myapp.routers.PaymentRouter']

Webhook Configuration
---------------------

The webhook URL is automatically configured at:

.. code-block:: text

   https://yourdomain.com/payfast/notify/

Ensure this URL is:

1. Publicly accessible
2. Uses HTTPS (required for production)
3. Not behind authentication
4. Can receive POST requests

For local development, use ngrok:

.. code-block:: bash

   ngrok http 8000

Then use the ngrok URL in your notify_url:

.. code-block:: python

   notify_url = 'https://abc123.ngrok.io/payfast/notify/'

Security Settings
-----------------

Passphrase
~~~~~~~~~~

**Highly recommended** for production:

.. code-block:: python

   PAYFAST_PASSPHRASE = 'your_very_secure_random_passphrase_here'

Generate a secure passphrase:

.. code-block:: python

   import secrets
   passphrase = secrets.token_urlsafe(32)
   print(passphrase)

IP Validation
~~~~~~~~~~~~~

PayFast webhook requests come from specific IPs. The library validates these automatically.

Valid PayFast hosts:

* ``www.payfast.co.za``
* ``sandbox.payfast.co.za``
* ``w1w.payfast.co.za``
* ``w2w.payfast.co.za``

HTTPS Configuration
~~~~~~~~~~~~~~~~~~~

**Required for production**:

.. code-block:: python

   # Ensure HTTPS in production
   SECURE_SSL_REDIRECT = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True

Logging Configuration
---------------------

Configure logging to track payments:

.. code-block:: python

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': 'payfast.log',
           },
       },
       'loggers': {
           'payfast': {
               'handlers': ['file'],
               'level': 'INFO',
               'propagate': True,
           },
       },
   }

Multi-Environment Setup
-----------------------

Example configuration for multiple environments:

.. code-block:: python

   # settings/base.py
   INSTALLED_APPS = [
       # ...
       'payfast',
   ]

.. code-block:: python

   # settings/development.py
   from .base import *
   
   PAYFAST_TEST_MODE = True
   PAYFAST_MERCHANT_ID = '10000100'  # Sandbox ID
   PAYFAST_MERCHANT_KEY = '46f0cd694581a'  # Sandbox key

.. code-block:: python

   # settings/production.py
   from .base import *
   
   PAYFAST_TEST_MODE = False
   PAYFAST_MERCHANT_ID = os.environ['PAYFAST_MERCHANT_ID']
   PAYFAST_MERCHANT_KEY = os.environ['PAYFAST_MERCHANT_KEY']
   PAYFAST_PASSPHRASE = os.environ['PAYFAST_PASSPHRASE']

Configuration Checklist
-----------------------

Before going to production:

.. code-block:: text

   ☐ Set PAYFAST_TEST_MODE = False
   ☐ Use production credentials
   ☐ Set secure PAYFAST_PASSPHRASE
   ☐ Enable HTTPS
   ☐ Configure proper logging
   ☐ Test webhook URL is accessible
   ☐ Set up error monitoring
   ☐ Review security settings
   ☐ Test with small transaction
   ☐ Monitor first few transactions

Next Steps
----------

* :doc:`usage` - Learn advanced usage patterns
* :doc:`security` - Security best practices
* :doc:`webhooks` - Understanding webhooks


