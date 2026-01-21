.. _webhooks:

===============================================================================
Webhooks Guide
===============================================================================

Understanding PayFast Webhooks
===============================

PayFast uses webhooks (also called ITN - Instant Transaction Notifications) to notify your application about payment events in real-time. This guide covers everything you need to know about implementing and handling webhooks effectively.

What are Webhooks?
------------------

Webhooks are HTTP callbacks that PayFast sends to your server when a payment event occurs. These events include:

* Payment completion
* Payment failure
* Payment cancellation
* Subscription updates
* Refund notifications

Why Webhooks are Important
---------------------------

Webhooks are **critical** for your payment system because:

1. **Real-time Updates**: Get instant notification when payments complete
2. **Reliability**: Even if users close their browser, you still receive updates
3. **Automation**: Automatically grant access, send emails, update inventory
4. **Reconciliation**: Keep your database synchronized with PayFast
5. **Security**: Server-side validation ensures payment authenticity

How Webhooks Work
-----------------

The webhook flow follows these steps:

.. code-block:: text

   1. User completes payment on PayFast
   2. PayFast sends POST request to your webhook URL
   3. Your server validates the request
   4. Your server updates payment status
   5. Your server responds with HTTP 200
   6. PayFast marks notification as delivered

**Important**: You must respond with HTTP 200 within 10 seconds, or PayFast will retry.

Setting Up Webhooks
====================

Step 1: Configure Webhook URL
------------------------------

Your webhook URL must be:

* **Publicly accessible** (not localhost)
* **HTTPS** (required for production)
* **POST-enabled** (GET requests will fail)
* **Not behind authentication** (PayFast can't log in)

Example webhook URL:

.. code-block:: text

   https://yourdomain.com/payfast/notify/

**For Local Development**:

Use ngrok to expose your local server:

.. code-block:: bash

   # Install ngrok
   brew install ngrok  # macOS
   # or download from https://ngrok.com
   
   # Start ngrok
   ngrok http 8000
   
   # Use the generated URL
   # Example: https://abc123.ngrok.io/payfast/notify/

Step 2: Add URL to Django
--------------------------

The webhook URL is automatically configured when you include payfast URLs:

.. code-block:: python

   # urls.py
   from django.urls import path, include
   
   urlpatterns = [
       path('payfast/', include('payfast.urls')),
   ]

This creates the endpoint: ``/payfast/notify/``

Step 3: Configure in PayFast Form
----------------------------------

Include the webhook URL when generating payment forms:

.. code-block:: python

   from django.urls import reverse
   
   notify_url = request.build_absolute_uri(
       reverse('payfast:notify')
   )
   
   form = PayFastPaymentForm(initial={
       'amount': 99.99,
       'item_name': 'Premium Plan',
       'm_payment_id': payment_id,
       'email_address': user.email,
       'notify_url': notify_url,  # Webhook URL
   })

Webhook Security
================

dj-payfast implements multiple security layers to protect your webhooks.

1. IP Address Validation
-------------------------

Webhooks only come from PayFast servers:

Valid PayFast IPs:

* ``www.payfast.co.za``
* ``sandbox.payfast.co.za``
* ``w1w.payfast.co.za``
* ``w2w.payfast.co.za``

The library validates these automatically:

.. code-block:: python

   from payfast.utils import validate_ip
   
   ip_address = get_client_ip(request)
   if not validate_ip(ip_address):
       return HttpResponseForbidden('Invalid IP')

2. Signature Verification
--------------------------

Every webhook includes a cryptographic signature:

.. code-block:: python

   from payfast.utils import verify_signature
   
   post_data = request.POST.dict()
   
   if not verify_signature(post_data, PAYFAST_PASSPHRASE):
       return HttpResponseBadRequest('Invalid signature')

**How Signatures Work**:

1. PayFast generates MD5 hash of payment data + passphrase
2. Signature is included in webhook POST data
3. Your server recalculates the signature
4. If signatures match, request is authentic

3. Server-Side Validation
--------------------------

The final security layer validates with PayFast servers:

.. code-block:: python

   import requests
   from payfast.conf import PAYFAST_VALIDATE_URL
   
   response = requests.post(
       PAYFAST_VALIDATE_URL,
       data=post_data,
       timeout=10
   )
   
   if response.text != 'VALID':
       return HttpResponseBadRequest('Validation failed')

Webhook Data Structure
=======================

PayFast sends the following data in webhook requests:

Standard Fields
---------------

.. code-block:: python

   {
       # Payment Identifiers
       'm_payment_id': 'your-unique-id',       # Your payment ID
       'pf_payment_id': '1234567',             # PayFast's payment ID
       
       # Payment Status
       'payment_status': 'COMPLETE',            # COMPLETE, FAILED, PENDING, CANCELLED
       
       # Amount Details
       'amount_gross': '100.00',                # Gross amount
       'amount_fee': '5.75',                    # PayFast fee
       'amount_net': '94.25',                   # Net amount (what you receive)
       
       # Item Information
       'item_name': 'Premium Plan',
       'item_description': '1 month subscription',
       
       # Customer Details
       'name_first': 'John',
       'name_last': 'Doe',
       'email_address': 'john@example.com',
       
       # Security
       'signature': 'abc123def456...',          # MD5 signature
       
       # Custom Fields (if provided)
       'custom_str1': 'order_123',
       'custom_int1': '5',
   }

Payment Status Values
---------------------

PayFast sends one of these statuses:

+---------------+--------------------------------------------------+
| Status        | Description                                      |
+===============+==================================================+
| ``COMPLETE``  | Payment successfully completed                   |
+---------------+--------------------------------------------------+
| ``FAILED``    | Payment failed (insufficient funds, etc.)        |
+---------------+--------------------------------------------------+
| ``PENDING``   | Payment initiated but not yet complete           |
+---------------+--------------------------------------------------+
| ``CANCELLED`` | User cancelled the payment                       |
+---------------+--------------------------------------------------+

Handling Webhooks
=================

Built-in Webhook Handler
------------------------

dj-payfast includes a complete webhook handler:

.. code-block:: python

   # payfast/views.py
   from payfast.views import PayFastNotifyView
   
   # Already included in payfast.urls
   # Available at: /payfast/notify/

The built-in handler automatically:

1. ✅ Validates IP address
2. ✅ Verifies signature
3. ✅ Validates with PayFast servers
4. ✅ Updates payment record
5. ✅ Logs notification
6. ✅ Returns appropriate response

Custom Webhook Processing
--------------------------

To add custom logic, subclass the view:

.. code-block:: python

   # myapp/views.py
   from payfast.views import PayFastNotifyView
   from django.core.mail import send_mail
   
   class CustomPayFastNotifyView(PayFastNotifyView):
       
       def post(self, request, *args, **kwargs):
           # Call parent processing first
           response = super().post(request, *args, **kwargs)
           
           # Only run custom logic if validation passed
           if response.status_code == 200:
               post_data = request.POST.dict()
               payment_status = post_data.get('payment_status')
               m_payment_id = post_data.get('m_payment_id')
               
               # Your custom logic
               if payment_status == 'COMPLETE':
                   self.handle_successful_payment(m_payment_id)
               elif payment_status == 'FAILED':
                   self.handle_failed_payment(m_payment_id)
           
           return response
       
       def handle_successful_payment(self, payment_id):
           """Process successful payment"""
           payment = PayFastPayment.objects.get(m_payment_id=payment_id)
           
           # Grant access
           if payment.user:
               self.activate_subscription(payment.user)
           
           # Send email
           send_mail(
               subject='Payment Confirmed!',
               message=f'Your payment of R{payment.amount} was successful.',
               from_email='noreply@example.com',
               recipient_list=[payment.email_address],
           )
           
           # Update inventory
           self.update_stock(payment)
       
       def handle_failed_payment(self, payment_id):
           """Handle failed payment"""
           payment = PayFastPayment.objects.get(m_payment_id=payment_id)
           
           # Send notification
           send_mail(
               subject='Payment Failed',
               message='Your payment was unsuccessful. Please try again.',
               from_email='noreply@example.com',
               recipient_list=[payment.email_address],
           )

Register your custom view:

.. code-block:: python

   # myapp/urls.py
   from django.urls import path
   from .views import CustomPayFastNotifyView
   
   urlpatterns = [
       path('payfast/notify/', CustomPayFastNotifyView.as_view()),
   ]

Using Django Signals
--------------------

**Recommended approach** for handling payment events:

.. code-block:: python

   # myapp/signals.py
   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from payfast.models import PayFastPayment
   from django.core.mail import send_mail
   
   @receiver(post_save, sender=PayFastPayment)
   def handle_payment_update(sender, instance, created, **kwargs):
       """Handle payment status changes"""
       
       # Only process completed payments
       if instance.status == 'complete' and instance.payment_status == 'COMPLETE':
           handle_successful_payment(instance)
   
   def handle_successful_payment(payment):
       """Process completed payment"""
       
       # 1. Grant access to user
       if payment.user:
           payment.user.profile.is_premium = True
           payment.user.profile.save()
       
       # 2. Send confirmation email
       send_mail(
           subject='Payment Confirmed',
           message=f'''
               Thank you for your payment of R{payment.amount}.
               Transaction ID: {payment.m_payment_id}
               
               Your premium access has been activated!
           ''',
           from_email='noreply@example.com',
           recipient_list=[payment.email_address],
       )
       
       # 3. Process custom fields
       if payment.custom_str1:
           process_order(payment.custom_str1)
       
       # 4. Log the event
       logger.info(f'Payment completed: {payment.m_payment_id}')

Register signals in ``apps.py``:

.. code-block:: python

   # myapp/apps.py
   from django.apps import AppConfig
   
   class MyAppConfig(AppConfig):
       name = 'myapp'
       
       def ready(self):
           import myapp.signals  # Register signals

Webhook Debugging
=================

Logging Webhooks
----------------

All webhook attempts are logged in ``PayFastNotification`` model:

.. code-block:: python

   from payfast.models import PayFastNotification
   
   # Get all notifications
   notifications = PayFastNotification.objects.all()
   
   # Get failed notifications
   failed = PayFastNotification.objects.filter(is_valid=False)
   
   # Check errors
   for notification in failed:
       print(f"Error: {notification.validation_errors}")
       print(f"Data: {notification.raw_data}")
       print(f"IP: {notification.ip_address}")

View in Django Admin
--------------------

Navigate to: ``/admin/payfast/payfastnotification/``

You'll see:

* All webhook attempts
* Validation status
* Error messages
* Raw POST data
* IP addresses
* Timestamps

Testing Webhooks Locally
-------------------------

**Method 1: ngrok (Recommended)**

.. code-block:: bash

   # Start Django
   python manage.py runserver
   
   # In another terminal, start ngrok
   ngrok http 8000
   
   # Use the ngrok URL in your payment form
   notify_url = 'https://abc123.ngrok.io/payfast/notify/'

**Method 2: Manual Testing**

Send a test POST request:

.. code-block:: python

   import requests
   
   test_data = {
       'm_payment_id': 'test-123',
       'pf_payment_id': '1234567',
       'payment_status': 'COMPLETE',
       'amount_gross': '100.00',
       'amount_fee': '5.75',
       'amount_net': '94.25',
       'item_name': 'Test Item',
       'email_address': 'test@example.com',
   }
   
   response = requests.post(
       'http://localhost:8000/payfast/notify/',
       data=test_data
   )
   
   print(response.status_code)
   print(response.text)

Common Webhook Issues
=====================

Issue 1: Webhook Not Receiving Notifications
---------------------------------------------

**Symptoms**: Payments complete on PayFast but webhook never fires.

**Causes & Solutions**:

1. **URL Not Accessible**

   .. code-block:: bash
   
      # Test if your webhook is accessible
      curl -X POST https://yourdomain.com/payfast/notify/
      
      # Should return: "Method Not Allowed" (405) - This is correct!
      # Means the endpoint exists and can receive POST requests

2. **Using localhost**

   PayFast can't reach ``http://localhost:8000``
   
   **Solution**: Use ngrok for local development

3. **Firewall Blocking**

   Check server firewall allows incoming connections
   
   **Solution**: Whitelist PayFast IP addresses

4. **Wrong URL in Form**

   .. code-block:: python
   
      # ❌ WRONG - Relative URL
      notify_url = '/payfast/notify/'
      
      # ✅ CORRECT - Absolute URL
      notify_url = request.build_absolute_uri(
          reverse('payfast:notify')
      )

Issue 2: Signature Verification Failing
----------------------------------------

**Symptoms**: Webhook returns "Invalid signature"

**Causes & Solutions**:

1. **Passphrase Mismatch**

   .. code-block:: python
   
      # settings.py
      PAYFAST_PASSPHRASE = 'YourExactPassphrase'  # Must match PayFast dashboard

2. **Test vs Production Passphrase**

   .. code-block:: python
   
      # Use different passphrases for test and production
      if PAYFAST_TEST_MODE:
          PAYFAST_PASSPHRASE = 'SandboxPassphrase'
      else:
          PAYFAST_PASSPHRASE = 'ProductionPassphrase'

3. **Debug Signature**

   .. code-block:: python
   
      from payfast.utils import generate_signature
      
      data = request.POST.dict()
      calculated = generate_signature(data, PAYFAST_PASSPHRASE)
      received = data.get('signature')
      
      print(f"Calculated: {calculated}")
      print(f"Received: {received}")
      print(f"Match: {calculated == received}")

Issue 3: Payment Status Not Updating
-------------------------------------

**Symptoms**: Webhook fires but payment stays "pending"

**Solution**: Check webhook logs for errors

.. code-block:: python

   from payfast.models import PayFastNotification
   
   # Get recent failed notifications
   failed = PayFastNotification.objects.filter(
       is_valid=False,
       created_at__gte=timezone.now() - timedelta(hours=1)
   )
   
   for notification in failed:
       print(notification.validation_errors)

Issue 4: Duplicate Webhooks
----------------------------

**Symptoms**: Same webhook received multiple times

**Causes**: 

* PayFast retries if you don't respond with HTTP 200
* Network issues
* Slow processing

**Solution**: Implement idempotency

.. code-block:: python

   from django.db import transaction
   
   @transaction.atomic
   def process_webhook(post_data):
       m_payment_id = post_data.get('m_payment_id')
       
       # Get payment with lock to prevent race conditions
       payment = PayFastPayment.objects.select_for_update().get(
           m_payment_id=m_payment_id
       )
       
       # Only process if still pending
       if payment.status == 'pending':
           payment.status = 'complete'
           payment.save()
           
           # Process additional logic
           grant_access(payment)
       
       # Always return success if payment exists
       return True

Webhook Best Practices
=======================

1. Respond Quickly
------------------

PayFast expects response within 10 seconds:

.. code-block:: python

   def post(self, request):
       # ✅ GOOD - Quick processing
       payment_id = request.POST.get('m_payment_id')
       
       # Update database (fast)
       payment = PayFastPayment.objects.get(m_payment_id=payment_id)
       payment.mark_complete()
       
       # Queue slow tasks (email, API calls) for later
       send_confirmation_email.delay(payment.id)
       
       return HttpResponse('OK', status=200)

2. Use Background Tasks
-----------------------

For slow operations, use Celery:

.. code-block:: python

   # tasks.py
   from celery import shared_task
   
   @shared_task
   def send_confirmation_email(payment_id):
       payment = PayFastPayment.objects.get(id=payment_id)
       # Send email (slow)
       send_mail(...)
   
   @shared_task
   def update_external_system(payment_id):
       # Call external API (slow)
       requests.post(...)

3. Implement Idempotency
------------------------

Handle duplicate webhooks gracefully:

.. code-block:: python

   def process_payment(payment_id):
       payment = PayFastPayment.objects.get(m_payment_id=payment_id)
       
       # Check if already processed
       if payment.status == 'complete':
           logger.info(f"Payment {payment_id} already processed")
           return True
       
       # Process payment
       payment.mark_complete()
       grant_access(payment.user)
       
       return True

4. Log Everything
-----------------

.. code-block:: python

   import logging
   
   logger = logging.getLogger('payfast.webhooks')
   
   def handle_webhook(request):
       logger.info(f"Webhook received from {request.META.get('REMOTE_ADDR')}")
       
       try:
           # Process webhook
           logger.info("Webhook processed successfully")
       except Exception as e:
           logger.error(f"Webhook processing failed: {e}")
           raise

5. Monitor Webhook Health
--------------------------

.. code-block:: python

   from payfast.models import PayFastNotification
   from django.utils import timezone
   from datetime import timedelta
   
   def check_webhook_health():
       """Check for webhook issues in last hour"""
       
       one_hour_ago = timezone.now() - timedelta(hours=1)
       
       total = PayFastNotification.objects.filter(
           created_at__gte=one_hour_ago
       ).count()
       
       failed = PayFastNotification.objects.filter(
           created_at__gte=one_hour_ago,
           is_valid=False
       ).count()
       
       success_rate = ((total - failed) / total * 100) if total > 0 else 100
       
       if success_rate < 90:
           send_alert(f"Webhook success rate: {success_rate}%")

Production Checklist
====================

Before going live:

.. code-block:: text

   ☐ Webhook URL is HTTPS
   ☐ Webhook URL is publicly accessible
   ☐ Passphrase is configured correctly
   ☐ Signature verification is enabled
   ☐ IP validation is enabled
   ☐ Server-side validation is enabled
   ☐ Webhook logging is configured
   ☐ Error monitoring is set up
   ☐ Background task processing is configured
   ☐ Idempotency is implemented
   ☐ Tested with real PayFast account
   ☐ Monitoring alerts are configured

Next Steps
==========

* :doc:`security` - Security best practices
* :doc:`testing` - Testing webhooks thoroughly
* :doc:`troubleshooting` - Solutions to common issues
* :doc:`api` - API reference for webhook handler