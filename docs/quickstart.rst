.. _quickstart:

Quick Start Guide
=================

This guide will help you integrate PayFast into your Django application in under 10 minutes.

Prerequisites
-------------

Before you begin, make sure you have:

* A Django project (3.2 or higher)
* Python 3.8 or higher installed
* A PayFast merchant account (sign up at `payfast.co.za <https://www.payfast.co.za>`_)
* Your PayFast credentials (Merchant ID, Merchant Key, and Passphrase)

Step 1: Installation
---------------------

Install dj-payfast using pip:

.. code-block:: bash

   pip install dj-payfast

Or add it to your ``requirements.txt``:

.. code-block:: text

   dj-payfast>=0.1.0

Step 2: Add to Django Settings
-------------------------------

Add ``payfast`` to your ``INSTALLED_APPS`` in ``settings.py``:

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
       
       # dj-payfast
       'payfast',
   ]

Step 3: Configure PayFast Credentials
--------------------------------------

Add your PayFast credentials to ``settings.py``:

**For Testing (Sandbox)**

.. code-block:: python

   # PayFast Configuration
   PAYFAST_MERCHANT_ID = '10000100'  # Sandbox merchant ID
   PAYFAST_MERCHANT_KEY = '46f0cd694581a'  # Sandbox merchant key
   PAYFAST_PASSPHRASE = 'jt7NOE43FZPn'  # Your passphrase (optional but recommended)
   PAYFAST_TEST_MODE = True  # Always True for sandbox

**For Production**

.. code-block:: python

   # PayFast Configuration
   PAYFAST_MERCHANT_ID = 'your_live_merchant_id'
   PAYFAST_MERCHANT_KEY = 'your_live_merchant_key'
   PAYFAST_PASSPHRASE = 'your_secure_passphrase'
   PAYFAST_TEST_MODE = False  # False for live payments

.. warning::
   Never commit your production credentials to version control!
   Use environment variables:

   .. code-block:: python

      import os
      
      PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
      PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
      PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
      PAYFAST_TEST_MODE = os.environ.get('PAYFAST_TEST_MODE', 'True') == 'True'

Step 4: Configure URLs
-----------------------

Add PayFast URLs to your ``urls.py``:

.. code-block:: python

   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('payfast/', include('payfast.urls')),  # Add this line
       # Your other URLs
   ]

This creates the webhook endpoint at ``/payfast/notify/`` which PayFast will use to send payment notifications.

Step 5: Run Migrations
-----------------------

Create the necessary database tables:

.. code-block:: bash

   python manage.py migrate

This creates two tables:
   * ``payfast_payfastpayment`` - Stores payment records
   * ``payfast_payfastnotification`` - Logs webhook notifications

Step 6: Create Your First Payment
----------------------------------

Create a view to handle the checkout process:

.. code-block:: python

   # views.py
   from django.shortcuts import render, redirect
   from django.urls import reverse
   from django.contrib.auth.decorators import login_required
   from payfast.models import PayFastPayment
   from payfast.forms import PayFastPaymentForm
   import uuid

   @login_required
   def checkout_view(request):
       """Display checkout page with PayFast payment form"""
       
       # Create a unique payment ID
       payment_id = str(uuid.uuid4())
       
       # Create payment record in database
       payment = PayFastPayment.objects.create(
           user=request.user,
           m_payment_id=payment_id,
           amount=99.00,  # R99.00
           item_name='Premium Membership',
           item_description='1 month of premium access',
           email_address=request.user.email,
           name_first=request.user.first_name,
           name_last=request.user.last_name,
       )
       
       # Build absolute URLs for callbacks
       return_url = request.build_absolute_uri(reverse('payment_success'))
       cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
       notify_url = request.build_absolute_uri(reverse('payfast:notify'))
       
       # Create PayFast form with payment data
       form = PayFastPaymentForm(initial={
           'amount': payment.amount,
           'item_name': payment.item_name,
           'item_description': payment.item_description,
           'm_payment_id': payment.m_payment_id,
           'email_address': payment.email_address,
           'name_first': payment.name_first,
           'name_last': payment.name_last,
           'return_url': return_url,
           'cancel_url': cancel_url,
           'notify_url': notify_url,
       })
       
       context = {
           'form': form,
           'payment': payment,
       }
       
       return render(request, 'checkout.html', context)

   def payment_success_view(request):
       """Handle successful payment return"""
       return render(request, 'payment_success.html')

   def payment_cancel_view(request):
       """Handle cancelled payment"""
       return render(request, 'payment_cancel.html')

Step 7: Create the Template
----------------------------

Create ``templates/checkout.html``:

.. code-block:: html

   {% extends 'base.html' %}

   {% block content %}
   <div class="container">
       <h1>Complete Your Payment</h1>
       
       <div class="payment-details">
           <h2>{{ payment.item_name }}</h2>
           <p>{{ payment.item_description }}</p>
           <h3>Amount: R{{ payment.amount }}</h3>
       </div>

       <form action="{{ form.get_action_url }}" method="post" id="payfast-form">
           {{ form.as_p }}
           <button type="submit" class="btn btn-primary">
               Pay with PayFast
           </button>
       </form>

       <div class="payment-info">
           <p>You will be redirected to PayFast to complete your payment securely.</p>
       </div>
   </div>
   {% endblock %}

Step 8: Add URL Patterns
-------------------------

Add the views to your ``urls.py``:

.. code-block:: python

   from django.urls import path
   from . import views

   urlpatterns = [
       path('checkout/', views.checkout_view, name='checkout'),
       path('payment/success/', views.payment_success_view, name='payment_success'),
       path('payment/cancel/', views.payment_cancel_view, name='payment_cancel'),
   ]

Step 9: Test Your Integration
------------------------------

1. Start your development server:

   .. code-block:: bash

      python manage.py runserver

2. Visit ``http://localhost:8000/checkout/``

3. Fill in the payment form and click "Pay with PayFast"

4. You'll be redirected to PayFast sandbox

5. Use test card details:

   * **Card Number**: 4242 4242 4242 4242
   * **Expiry**: Any future date
   * **CVV**: Any 3 digits

6. Complete the payment

7. Check the Django admin at ``/admin/payfast/payfastpayment/`` to see your payment record

.. note::
   In sandbox mode, payments are simulated. No real money is charged.

Step 10: Handle Webhooks (Important!)
--------------------------------------

PayFast sends ITN (Instant Transaction Notification) webhooks when payment status changes. dj-payfast handles these automatically, but you need to ensure your webhook URL is accessible.

**For Local Development**

Use a tool like ngrok to expose your local server:

.. code-block:: bash

   ngrok http 8000

Then update your ``notify_url`` to use the ngrok URL:

.. code-block:: python

   notify_url = 'https://your-ngrok-url.ngrok.io/payfast/notify/'

**For Production**

Make sure your domain is accessible and HTTPS is enabled (required by PayFast).

Next Steps
----------

You now have a working PayFast integration! Here's what to explore next:

* :doc:`usage` - Learn about advanced features
* :doc:`webhooks` - Understand webhook processing in detail
* :doc:`testing` - Learn how to test payments
* :doc:`security` - Best practices for secure payments
* :doc:`api` - Complete API reference

Common Next Features
~~~~~~~~~~~~~~~~~~~~

**Add Custom Fields**

.. code-block:: python

   payment = PayFastPayment.objects.create(
       # ... other fields ...
       custom_str1='order_123',  # Your order ID
       custom_int1=request.user.id,  # User ID for reference
   )

**Handle Payment Completion**

Use Django signals to trigger actions when payments complete:

.. code-block:: python

   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from payfast.models import PayFastPayment

   @receiver(post_save, sender=PayFastPayment)
   def payment_completed(sender, instance, **kwargs):
       if instance.status == 'complete' and instance.payment_status == 'COMPLETE':
           # Grant access, send email, etc.
           activate_premium_membership(instance.user)

**Query Payments**

.. code-block:: python

   # Get all completed payments for a user
   payments = PayFastPayment.objects.filter(
       user=request.user,
       status='complete'
   )

   # Get pending payments
   pending = PayFastPayment.objects.filter(status='pending')

   # Get total revenue
   from django.db.models import Sum
   total = PayFastPayment.objects.filter(
       status='complete'
   ).aggregate(Sum('amount'))

Troubleshooting
---------------

**Webhook not receiving notifications?**

* Check that your ``notify_url`` is publicly accessible
* For local development, use ngrok
* Check PayFast ITN logs in the admin: ``/admin/payfast/payfastnotification/``

**Signature validation failing?**

* Make sure your passphrase matches exactly
* Check that ``PAYFAST_TEST_MODE`` is set correctly
* Verify your merchant credentials

**Payment status not updating?**

* Check the ``payfast_payfastnotification`` table for validation errors
* Ensure your webhook endpoint is working: visit ``/payfast/notify/`` (should show "Method Not Allowed")

Getting Help
------------

* Check the :doc:`faq` for common questions
* See :doc:`troubleshooting` for solutions to common issues
* Open an issue on `GitHub <https://github.com/yourusername/dj-payfast/issues>`_

Congratulations! 🎉
-------------------

You've successfully integrated PayFast into your Django application. Your users can now make secure payments directly from your website.