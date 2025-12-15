.. dj-payfast documentation master file

Welcome to dj-payfast's documentation!
=======================================

**dj-payfast** is a comprehensive Django library for integrating PayFast payment gateway into your Django applications. It provides a simple, secure, and Pythonic way to accept payments from South African customers.

.. image:: https://img.shields.io/pypi/v/dj-payfast.svg
   :target: https://pypi.org/project/dj-payfast/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/dj-payfast.svg
   :target: https://pypi.org/project/dj-payfast/
   :alt: Python versions

.. image:: https://img.shields.io/pypi/djversions/dj-payfast.svg
   :target: https://pypi.org/project/dj-payfast/
   :alt: Django versions

.. image:: https://img.shields.io/github/license/carrington-dev/dj-payfast.svg
   :target: https://github.com/carrington-dev/dj-payfast/blob/main/LICENSE
   :alt: License

Overview
--------

PayFast is South Africa's leading payment gateway, trusted by thousands of businesses to process online payments securely. **dj-payfast** makes it easy to integrate PayFast into your Django projects with minimal configuration.

Key Features
~~~~~~~~~~~~

*  **Secure**: Built-in signature verification and validation
*  **Easy to Use**: Simple API similar to dj-stripe and dj-paypal
*  **Complete**: Models, forms, views, and webhooks included
*  **Test Mode**: Sandbox support for development and testing
*  **Admin Interface**: Full Django admin integration
*  **Webhooks**: Automatic ITN (Instant Transaction Notification) handling
*  **Database Tracking**: Complete payment history and audit trail
*  **Customizable**: Support for custom fields and metadata
*  **Mobile Ready**: Works with PayFast's mobile payment options

Quick Example
~~~~~~~~~~~~~

Install using pip:

.. code-block:: bash

   pip install dj-payfast

Add payfast to your main projects:

.. code-block:: bash
   
   INSTALLED_APPS += [
      'payfast'
   ]
   
Add App to Main Projects urls.py:

.. code-block:: bash
   urlpatterns += [
      path('payfast/', include("payfast.urls"))
   ]

Added payfast application ( /payfast/payments ), perform a post request on, some fields are not required, This is a post request:

.. code-block:: json
   {
      "m_payment_id": "",
      "user": null,
      "amount": null,
      "item_name": "",
      "item_description": "",
      "name_first": "",
      "name_last": "",
      "email_address": "",
      "cell_number": "", # optional field
      "custom_str1": "", # optional field
      "custom_str2": "", # optional field
      "custom_str3": "", # optional field
      "custom_str4": "", # optional field
      "custom_str5": "", # optional field
      "custom_int1": null, # optional field
      "custom_int2": null, # optional field
      "custom_int3": null, # optional field
      "custom_int4": null, # optional field
      "custom_int5": null # optional field
   }

# Expected Response
.. code-block:: json
   {
      "amount": "99.99",
      "item_name": "Premium Subscription",
      "item_description": "1 month premium access",
      "name_first": "",
      "name_last": "",
      "email_address": "your.email@gmail.com",
      "m_payment_id": "3a280ceb-344c-48d1-8e9c-7945f3f1194a",
      "payfast_url": "http://127.0.0.1:2000/payfast/checkout/2"
   }


Using Payfast within React or Android
~~~~~~~~~~~~~~~
To use the above Response just redirect to the payfast_url and pay.


Why dj-payfast?
~~~~~~~~~~~~~~~

**PayFast Integration Made Simple**

While PayFast provides excellent documentation, integrating it into Django applications requires handling:

- Secure signature generation and verification
- ITN webhook processing and validation
- Payment tracking and database storage
- Admin interface for payment management
- Test and production environment configuration

**dj-payfast** handles all of this for you, letting you focus on building your application instead of dealing with payment gateway integration details.

Requirements
------------

* Python 3.8+
* Django 3.2+
* requests 2.25.0+
* A PayFast merchant account (get one at `payfast.co.za <https://www.payfast.co.za>`_)

Installation
------------

Install using pip:

.. code-block:: bash

   pip install dj-payfast

Or install from source:

.. code-block:: bash

   git clone https://github.com/carrington-dev/dj-payfast.git
   cd dj-payfast
   pip install -e .

Quick Start
-----------

1. **Add to INSTALLED_APPS**

   .. code-block:: python

      INSTALLED_APPS = [
          ...
          'payfast',
      ]

2. **Configure Settings**

   .. code-block:: python

      # PayFast Configuration
      PAYFAST_MERCHANT_ID = 'your_merchant_id'
      PAYFAST_MERCHANT_KEY = 'your_merchant_key'
      PAYFAST_PASSPHRASE = 'your_passphrase'  # Optional but recommended
      PAYFAST_TEST_MODE = True  # Set to False for production

3. **Add URLs**

   .. code-block:: python

      urlpatterns = [
          ...
          path('payfast/', include('payfast.urls')),
      ]

4. **Run Migrations**

   .. code-block:: bash

      python manage.py migrate

5. **Start Accepting Payments!**

   See the :doc:`usage` guide for detailed examples.

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   configuration

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   usage
   webhooks
   testing
   security

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   models
   forms
   views
   utils
   signals

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   changelog
   contributing
   faq
   troubleshooting
   support

PayFast Resources
-----------------

* `PayFast Website <https://www.payfast.co.za>`_
* `PayFast API Documentation <https://developers.payfast.co.za>`_
* `PayFast Integration Guide <https://developers.payfast.co.za/docs#integration>`_
* `PayFast Sandbox <https://sandbox.payfast.co.za>`_

Community & Support
-------------------

* **GitHub**: `github.com/carrington-dev/dj-payfast <https://github.com/carrington-dev/dj-payfast>`_
* **Issues**: `GitHub Issue Tracker <https://github.com/carrington-dev/dj-payfast/issues>`_
* **PyPI**: `pypi.org/project/dj-payfast <https://pypi.org/project/dj-payfast>`_
* **Email**: carrington.muleya@outlook.com

Contributing
------------

We welcome contributions! Please see our :doc:`contributing` guide for details on:

* Reporting bugs
* Suggesting features
* Submitting pull requests
* Running tests
* Code style guidelines

License
-------

**dj-payfast** is released under the MIT License. See the LICENSE file for details.

Acknowledgments
---------------

This library is inspired by other excellent Django payment libraries:

* `dj-stripe <https://github.com/dj-stripe/dj-stripe>`_
* `dj-paypal <https://github.com/dj-paypal/dj-paypal>`_
* `django-paypal <https://github.com/spookylukey/django-paypal>`_

Special thanks to PayFast for providing a reliable payment gateway for South African businesses.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`