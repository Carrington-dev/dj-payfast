.. _faq:

===============================================================================
Frequently Asked Questions (FAQ)
===============================================================================

Quick answers to common questions about dj-payfast.

General Questions
=================

What is dj-payfast?
-------------------

dj-payfast is a Django library that provides complete integration with PayFast, South Africa's leading payment gateway. It handles payment creation, webhook processing, signature verification, and payment tracking.

Is dj-payfast production-ready?
--------------------------------

Yes! dj-payfast is used in production by multiple companies and includes:

* ✅ Complete security implementation
* ✅ Comprehensive error handling
* ✅ Thorough testing suite
* ✅ Production-tested code
* ✅ Active maintenance

What Django versions are supported?
------------------------------------

dj-payfast supports Django 3.2 through 5.0+.

Supported versions:
* Django 3.2 (LTS)
* Django 4.0
* Django 4.1
* Django 4.2 (LTS)
* Django 5.0+

What Python versions are supported?
------------------------------------

Python 3.8 and above:
* Python 3.8
* Python 3.9
* Python 3.10
* Python 3.11
* Python 3.12

Do I need a PayFast account?
-----------------------------

Yes, you need:

* **Development**: Sandbox account (free) at https://sandbox.payfast.co.za
* **Production**: Verified merchant account at https://www.payfast.co.za

Installation & Setup
====================

How do I install dj-payfast?
-----------------------------

.. code-block:: bash

   pip install dj-payfast

Then add to ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       # ...
       'payfast',
   ]

Do I need to install any other packages?
-----------------------------------------

dj-payfast requires:

* Django >= 3.2
* djangorestframework (included automatically)
* requests >= 2.25.0 (included automatically)

All dependencies are installed automatically.

How do I get my PayFast credentials?
-------------------------------------

**For Sandbox (Testing)**:

1. Sign up at https://sandbox.payfast.co.za
2. Go to **Settings → Integration**
3. Copy Merchant ID and Merchant Key
4. Generate a passphrase

**For Production**:

1. Sign up at https://www.payfast.co.za
2. Complete merchant verification
3. Go to **Settings → Integration**
4. Copy production credentials

Payment & Integration
=====================

Can I use dj-payfast without user authentication?
--------------------------------------------------

Yes! The ``user`` field is optional:

.. code-block:: python

   payment = PayFastPayment.objects.create(
       user=None,  # No user required
       m_payment_id=str(uuid.uuid4()),
       amount=99.99,
       item_name='Guest Purchase',
       email_address='guest@example.com',
   )

How do I store additional data with payments?
----------------------------------------------

Use custom fields (``custom_str1-5`` and ``custom_int1-5``):

.. code-block:: python

   payment = PayFastPayment.objects.create(
       # ... standard fields ...
       custom_str1='order_123',      # Order reference
       custom_str2='premium_plan',   # Plan type
       custom_int1=user.id,          # User ID
       custom_int2=12,               # Subscription months
   )

Then retrieve them:

.. code-block:: python

   order_id = payment.custom_str1
   plan_type = payment.custom_str2

Can I customize the checkout page?
-----------------------------------

Yes, in two ways:

**1. Override Template** (Easiest):

.. code-block:: bash

   # Create this file:
   templates/payfast/checkout.html

**2. Custom View** (More Control):

.. code-block:: python

   def custom_checkout(request):
       # Your custom logic
       return render(request, 'my_checkout.html', {
           'form': form,
           'payment': payment,
       })

How do I process different types of payments?
----------------------------------------------

Use custom fields to identify payment types:

.. code-block:: python

   # One-time purchase
   payment.custom_str1 = 'purchase'
   
   # Subscription
   payment.custom_str1 = 'subscription'
   
   # Donation
   payment.custom_str1 = 'donation'

Then in your webhook handler:

.. code-block:: python

   payment_type = payment.custom_str1
   
   if payment_type == 'purchase':
       process_purchase(payment)
   elif payment_type == 'subscription':
       activate_subscription(payment)
   elif payment_type == 'donation':
       process_donation(payment)

Webhooks
========

What is a webhook?
------------------

A webhook is a callback URL that PayFast POSTs to when payment events occur (completion, failure, etc.). It allows your server to receive real-time payment updates.

Why are webhooks important?
----------------------------

Webhooks are **critical** because:

* ✅ You get instant payment updates
* ✅ Works even if user closes browser
* ✅ Enables automation (grant access, send emails)
* ✅ Keeps your database synchronized
* ✅ Required for reliable payment processing

How do I set up webhooks?
--------------------------

Webhooks are automatically configured:

1. Include payfast URLs:

   .. code-block:: python
   
      # urls.py
      urlpatterns = [
          path('payfast/', include('payfast.urls')),
      ]

2. This creates: ``https://yourdomain.com/payfast/notify/``

3. dj-payfast handles everything else automatically!

How do I test webhooks locally?
--------------------------------

Use ngrok:

.. code-block:: bash

   # Start Django
   python manage.py runserver
   
   # Start ngrok in another terminal
   ngrok http 8000
   
   # Use ngrok URL in notify_url:
   notify_url = 'https://abc123.ngrok.io/payfast/notify/'

Do I need to validate webhooks?
--------------------------------

dj-payfast does all validation automatically:

* ✅ IP address validation
* ✅ Signature verification
* ✅ Server-side validation with PayFast
* ✅ Notification logging

You don't need to implement validation yourself!

How do I add custom logic when payment completes?
--------------------------------------------------

Use Django signals (recommended):

.. code-block:: python

   # signals.py
   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from payfast.models import PayFastPayment
   
   @receiver(post_save, sender=PayFastPayment)
   def handle_payment(sender, instance, **kwargs):
       if instance.status == 'complete':
           # Your custom logic here
           grant_access(instance.user)
           send_email(instance)

Security
========

Is dj-payfast secure?
----------------------

Yes! dj-payfast implements all PayFast security requirements:

* ✅ Signature verification
* ✅ IP validation
* ✅ Server-side validation
* ✅ HTTPS enforcement (production)
* ✅ Secure credential storage

Should I use a passphrase?
---------------------------

**Yes, absolutely!** Passphrases add cryptographic security to signature verification.

Generate a secure passphrase:

.. code-block:: python

   import secrets
   passphrase = secrets.token_urlsafe(32)
   print(passphrase)

Then add to settings:

.. code-block:: python

   PAYFAST_PASSPHRASE = 'your_secure_passphrase'

How do I store credentials securely?
-------------------------------------

**Never hardcode credentials!** Use environment variables:

.. code-block:: python

   # settings.py
   import os
   
   PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
   PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
   PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')

Create ``.env`` file (add to ``.gitignore``):

.. code-block:: bash

   PAYFAST_MERCHANT_ID=10000100
   PAYFAST_MERCHANT_KEY=46f0cd694581a
   PAYFAST_PASSPHRASE=your_passphrase

Is HTTPS required?
------------------

* **Development**: No, HTTP is fine with ngrok
* **Production**: **Yes, absolutely required!** PayFast requires HTTPS for production webhooks.

Testing
=======

Can I test without processing real payments?
---------------------------------------------

Yes! Use PayFast sandbox:

.. code-block:: python

   # settings.py
   PAYFAST_TEST_MODE = True  # Sandbox mode

Use test card: ``4242 4242 4242 4242``

How do I test webhooks?
------------------------

1. Use ngrok to expose localhost
2. PayFast will send test webhooks to ngrok URL
3. Check Django admin for webhook logs: ``/admin/payfast/payfastnotification/``

What test data should I use?
-----------------------------

**Successful Payment**:

.. code-block:: text

   Card: 4242 4242 4242 4242
   Expiry: 12/25
   CVV: 123

**Failed Payment**:

.. code-block:: text

   Card: 4000 0000 0000 0002
   Expiry: 12/25
   CVV: 123

Pricing & Fees
==============

Does dj-payfast cost money?
----------------------------

No! dj-payfast is **free and open source** (MIT License).

You only pay PayFast's transaction fees (typically 2.9% + R2.90).

What are PayFast's fees?
-------------------------

PayFast charges (as of 2025):

* **Standard**: 2.9% + R2.90 per transaction
* **Premium**: Lower rates for high volume
* **No setup fees**
* **No monthly fees**

Check current rates at: https://www.payfast.co.za/fees

Production
==========

How do I switch to production?
-------------------------------

1. **Get production credentials** from https://www.payfast.co.za

2. **Update settings**:

   .. code-block:: python
   
      PAYFAST_TEST_MODE = False  # Production mode
      PAYFAST_MERCHANT_ID = 'production_merchant_id'
      PAYFAST_MERCHANT_KEY = 'production_merchant_key'
      PAYFAST_PASSPHRASE = 'production_passphrase'

3. **Enable HTTPS**:

   .. code-block:: python
   
      SECURE_SSL_REDIRECT = True
      SESSION_COOKIE_SECURE = True
      CSRF_COOKIE_SECURE = True

4. **Test thoroughly** with small transactions first!

What should I monitor in production?
-------------------------------------

Monitor these metrics:

* **Payment success rate** (should be > 95%)
* **Webhook delivery rate** (should be 100%)
* **Failed signature verifications** (should be 0)
* **Payment processing time**
* **Error rates**

Check Django admin regularly:

* ``/admin/payfast/payfastpayment/``
* ``/admin/payfast/payfastnotification/``

Database
========

What database should I use?
----------------------------

**Development**: SQLite (Django default)

**Production**: PostgreSQL (strongly recommended)

.. code-block:: python

   # Production settings
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db',
           'USER': 'your_user',
           'PASSWORD': os.environ.get('DB_PASSWORD'),
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }

Can I store payment data in a separate database?
-------------------------------------------------

Yes, use database routers:

.. code-block:: python

   # settings.py
   DATABASES = {
       'default': {...},
       'payments': {...},  # Separate database
   }
   
   DATABASE_ROUTERS = ['myapp.routers.PaymentRouter']

Advanced Features
=================

Can I use dj-payfast with Django REST Framework?
-------------------------------------------------

Yes! dj-payfast includes full DRF support:

.. code-block:: python

   # urls.py
   from payfast.views import PayFastPaymentModelViewSet
   from rest_framework.routers import DefaultRouter
   
   router = DefaultRouter()
   router.register('payments', PayFastPaymentModelViewSet)
   
   urlpatterns = [
       path('api/', include(router.urls)),
   ]

This provides REST endpoints:

* ``GET /api/payments/`` - List payments
* ``POST /api/payments/`` - Create payment
* ``GET /api/payments/{id}/`` - Get payment
* ``PATCH /api/payments/{id}/`` - Update payment

Can I use dj-payfast with React/Vue/Angular?
---------------------------------------------

Yes! Create payments via API:

.. code-block:: javascript

   // React example
   const response = await fetch('/api/payments/', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
           amount: 99.99,
           item_name: 'Premium Plan',
           email_address: 'user@example.com',
       })
   });
   
   const data = await response.json();
   window.location.href = data.payfast_url;  // Redirect to PayFast

Does dj-payfast support subscriptions?
---------------------------------------

Currently dj-payfast focuses on one-time payments. Subscription support is planned for future releases.

For now, you can:

* Process monthly payments manually
* Use custom fields to track subscription status
* Implement renewal logic in your application

How do I handle refunds?
-------------------------

Refunds are processed through PayFast dashboard:

1. Log in to PayFast
2. Find the transaction
3. Click "Refund"

To track refunds in dj-payfast:

.. code-block:: python

   # Create custom model
   class PayFastRefund(models.Model):
       payment = models.ForeignKey(PayFastPayment, on_delete=models.CASCADE)
       amount = models.DecimalField(max_digits=10, decimal_places=2)
       reason = models.TextField()
       refunded_at = models.DateTimeField(auto_now_add=True)

Support & Community
===================

Where can I get help?
---------------------

1. **Documentation**: https://carrington-dev.github.io/dj-payfast/
2. **GitHub Issues**: https://github.com/carrington-dev/dj-payfast/issues
3. **PayFast Support**: https://www.payfast.co.za/support

How do I report bugs?
----------------------

1. Check existing issues: https://github.com/carrington-dev/dj-payfast/issues
2. Create new issue with:
   * Django version
   * dj-payfast version
   * Python version
   * Error message
   * Steps to reproduce

How can I contribute?
---------------------

Contributions are welcome! See: :doc:`contributing`

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit pull request

Common Errors
=============

"No module named 'payfast'"
----------------------------

**Solution**: 

.. code-block:: bash

   pip install dj-payfast
   # Add 'payfast' to INSTALLED_APPS
   # Run: python manage.py migrate

"Invalid signature"
-------------------

**Solution**: Check passphrase matches PayFast dashboard exactly

"Method Not Allowed" on webhook
--------------------------------

**Solution**: This is **correct**! Webhook URL should only accept POST requests.

"Payment not found"
-------------------

**Solution**: Ensure payment was created with correct ``m_payment_id``

Still Have Questions?
=====================

* Check :doc:`troubleshooting` for solutions
* Read :doc:`usage` for detailed examples
* See :doc:`api` for complete API reference
* Open an issue on GitHub

Next Steps
==========

* :doc:`quickstart` - Get started in 10 minutes
* :doc:`usage` - Learn advanced features
* :doc:`security` - Security best practices