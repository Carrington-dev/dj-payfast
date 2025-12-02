===============================================================================
INSTALLATION.RST
===============================================================================

Installation
============

This guide will help you install and set up **dj-payfast** in your Django project.

Requirements
------------

Before installing dj-payfast, ensure you have:

* Python 3.8 or higher
* Django 3.2 or higher
* A PayFast merchant account
* pip package manager

Installing dj-payfast
---------------------

Using pip (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

Install the latest stable version from PyPI:

.. code-block:: bash

   pip install dj-payfast

Installing from GitHub
~~~~~~~~~~~~~~~~~~~~~~

To install the latest development version:

.. code-block:: bash

   pip install git+https://github.com/yourusername/dj-payfast.git

Or clone and install locally:

.. code-block:: bash

   git clone https://github.com/yourusername/dj-payfast.git
   cd dj-payfast
   pip install -e .

Installing for Development
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to contribute or modify the library:

.. code-block:: bash

   git clone https://github.com/yourusername/dj-payfast.git
   cd dj-payfast
   pip install -e ".[dev]"

This installs additional development dependencies like pytest, black, and flake8.

Verifying Installation
----------------------

Verify the installation by importing the package:

.. code-block:: python

   import payfast
   print(payfast.__version__)

Django Configuration
--------------------

1. Add to INSTALLED_APPS
~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``'payfast'`` to your ``INSTALLED_APPS`` in ``settings.py``:

.. code-block:: python

   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       
       # Your apps
       'myapp',
       
       # Third-party apps
       'payfast',  # Add this
   ]

2. Configure PayFast Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add your PayFast credentials to ``settings.py``:

.. code-block:: python

   # PayFast Configuration
   PAYFAST_MERCHANT_ID = '10000100'  # Your merchant ID
   PAYFAST_MERCHANT_KEY = '46f0cd694581a'  # Your merchant key
   PAYFAST_PASSPHRASE = 'your_secure_passphrase'  # Optional but recommended
   PAYFAST_TEST_MODE = True  # False for production

.. warning::
   Never commit your production credentials to version control!
   Use environment variables or a secrets management system.

Using Environment Variables (Recommended):

.. code-block:: python

   import os
   
   PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
   PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
   PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
   PAYFAST_TEST_MODE = os.environ.get('PAYFAST_TEST_MODE', 'True') == 'True'

3. Include URLs
~~~~~~~~~~~~~~~

Add PayFast URLs to your main ``urls.py``:

.. code-block:: python

   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('payfast/', include('payfast.urls')),
       # Your other URLs
   ]

4. Run Migrations
~~~~~~~~~~~~~~~~~

Create the necessary database tables:

.. code-block:: bash

   python manage.py migrate

You should see output like:

.. code-block:: text

   Running migrations:
     Applying payfast.0001_initial... OK

Getting PayFast Credentials
----------------------------

Sandbox (Testing)
~~~~~~~~~~~~~~~~~

1. Sign up for a sandbox account at https://sandbox.payfast.co.za
2. Log in to your sandbox dashboard
3. Navigate to **Settings → Integration**
4. Copy your Merchant ID and Merchant Key
5. Generate a passphrase (recommended)

Production
~~~~~~~~~~

1. Sign up at https://www.payfast.co.za
2. Complete the merchant verification process
3. Log in to your PayFast dashboard
4. Navigate to **Settings → Integration**
5. Copy your Merchant ID and Merchant Key
6. Generate a secure passphrase

Next Steps
----------

Now that you have dj-payfast installed, proceed to:

* :doc:`quickstart` - Create your first payment
* :doc:`configuration` - Advanced configuration options
* :doc:`usage` - Detailed usage examples


