.. _troubleshooting:

===============================================================================
Troubleshooting Guide
===============================================================================

Solutions to common issues when using dj-payfast.

Quick Diagnosis
===============

Use this flowchart to quickly identify your issue:

.. code-block:: text

   Can't install dj-payfast?
   └─> See: Installation Issues
   
   Payment not creating?
   └─> See: Payment Creation Issues
   
   Can't reach PayFast?
   └─> See: Payment Processing Issues
   
   Webhook not firing?
   └─> See: Webhook Issues
   
   Signature errors?
   └─> See: Security/Signature Issues
   
   Database errors?
   └─> See: Database Issues

Installation Issues
===================

Issue: pip install fails
-------------------------

**Symptoms**:

.. code-block:: bash

   ERROR: Could not find a version that satisfies the requirement dj-payfast

**Solutions**:

1. **Update pip**:

   .. code-block:: bash
   
      python -m pip install --upgrade pip

2. **Check Python version**:

   .. code-block:: bash
   
      python --version  # Must be 3.8+

3. **Use specific version**:

   .. code-block:: bash
   
      pip install dj-payfast==0.1.8

4. **Install from GitHub**:

   .. code-block:: bash
   
      pip install git+https://github.com/carrington-dev/dj-payfast.git

Issue: Import error after installation
---------------------------------------

**Symptoms**:

.. code-block:: python

   ImportError: No module named 'payfast'

**Solutions**:

1. **Verify installation**:

   .. code-block:: bash
   
      pip list | grep dj-payfast

2. **Check virtual environment**:

   .. code-block:: bash
   
      which python
      # Should be in your project's venv

3. **Add to INSTALLED_APPS**:

   .. code-block:: python
   
      # settings.py
      INSTALLED_APPS = [
          # ...
          'payfast',  # Add this
      ]

4. **Run migrations**:

   .. code-block:: bash
   
      python manage.py migrate

Payment Creation Issues
========================

Issue: Payment form not displaying
-----------------------------------

**Symptoms**: Blank page or missing form

**Solutions**:

1. **Check template exists**:

   .. code-block:: python
   
      # Verify template path
      'payfast/checkout.html'

2. **Check context data**:

   .. code-block:: python
   
      def checkout_view(request):
          # Ensure you're passing these
          return render(request, 'payfast/checkout.html', {
              'form': form,
              'payment': payment,
          })

3. **Debug template**:

   .. code-block:: django
   
      {# In template #}
      {{ form.errors }}
      {{ payment }}

Issue: Missing required fields
-------------------------------

**Symptoms**:

.. code-block:: text

   IntegrityError: NOT NULL constraint failed

**Solution**:

Ensure all required fields are provided:

.. code-block:: python

   # Required fields
   payment = PayFastPayment.objects.create(
       m_payment_id=str(uuid.uuid4()),  # Required & unique
       amount=99.99,                     # Required
       item_name='Product Name',         # Required
       email_address='user@example.com', # Required
   )

Issue: Duplicate payment_id error
----------------------------------

**Symptoms**:

.. code-block:: text

   IntegrityError: UNIQUE constraint failed: payfast_payfastpayment.m_payment_id

**Solutions**:

1. **Generate unique IDs**:

   .. code-block:: python
   
      import uuid
      
      m_payment_id = str(uuid.uuid4())
      # Or timestamp-based:
      from django.utils import timezone
      m_payment_id = f"{user.id}_{int(timezone.now().timestamp())}"

2. **Check for existing payment**:

   .. code-block:: python
   
      if PayFastPayment.objects.filter(m_payment_id=payment_id).exists():
          # Reuse existing payment
          payment = PayFastPayment.objects.get(m_payment_id=payment_id)
      else:
          # Create new payment
          payment = PayFastPayment.objects.create(...)

Payment Processing Issues
==========================

Issue: Can't reach PayFast
---------------------------

**Symptoms**: Connection timeout or error

**Solutions**:

1. **Check internet connection**:

   .. code-block:: bash
   
      ping sandbox.payfast.co.za

2. **Verify PAYFAST_TEST_MODE**:

   .. code-block:: python
   
      # settings.py
      PAYFAST_TEST_MODE = True  # For sandbox
      # False for production

3. **Check firewall**:

   Ensure outbound HTTPS (port 443) is allowed

Issue: Redirect not working
----------------------------

**Symptoms**: Form submits but nothing happens

**Solutions**:

1. **Check form action URL**:

   .. code-block:: html
   
      <form action="{{ form.get_action_url }}" method="post">

2. **Verify merchant credentials**:

   .. code-block:: python
   
      # settings.py
      PAYFAST_MERCHANT_ID = '10000100'  # Check this is correct
      PAYFAST_MERCHANT_KEY = '46f0cd694581a'

3. **Check JavaScript errors**:

   Open browser console (F12) and look for errors

Issue: Payment stuck on "Processing"
-------------------------------------

**Symptoms**: Payment never completes or fails

**Solutions**:

1. **Check webhook configuration**:

   .. code-block:: python
   
      notify_url = request.build_absolute_uri(
          reverse('payfast:notify')
      )

2. **Verify webhook URL is accessible**:

   .. code-block:: bash
   
      curl -X POST https://yourdomain.com/payfast/notify/
      # Should return 405 "Method Not Allowed"

3. **Check PayFast ITN logs**:

   Login to PayFast dashboard → ITN History

Webhook Issues
==============

Issue: Webhook never fires
---------------------------

**Symptoms**: Payment completes but status stays "pending"

**Solutions**:

1. **Verify webhook URL is public**:

   .. code-block:: bash
   
      # Test from external server
      curl -X POST https://yourdomain.com/payfast/notify/

2. **Check CSRF exemption**:

   dj-payfast does this automatically, but verify:

   .. code-block:: python
   
      @csrf_exempt
      def webhook_view(request):
          pass

3. **Use ngrok for local testing**:

   .. code-block:: bash
   
      ngrok http 8000
      # Use ngrok URL as notify_url

4. **Check webhook logs**:

   .. code-block:: python
   
      from payfast.models import PayFastNotification
      
      # Check for recent notifications
      notifications = PayFastNotification.objects.all().order_by('-created_at')[:10]
      
      for notif in notifications:
          print(f"Valid: {notif.is_valid}")
          print(f"Errors: {notif.validation_errors}")

Issue: Webhook returns 403 Forbidden
-------------------------------------

**Symptoms**: Webhook fails with 403 error

**Solutions**:

1. **Disable authentication requirement**:

   .. code-block:: python
   
      # Don't require login for webhook
      # dj-payfast handles this automatically

2. **Check middleware**:

   Ensure no middleware is blocking the request

3. **Verify ALLOWED_HOSTS**:

   .. code-block:: python
   
      # settings.py (production)
      ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

Issue: Webhook timeout
----------------------

**Symptoms**: Webhook takes too long, PayFast retries

**Solutions**:

1. **Respond quickly**:

   .. code-block:: python
   
      def webhook_view(request):
          # Process quickly
          payment_id = request.POST.get('m_payment_id')
          
          # Update database (fast)
          payment = PayFastPayment.objects.get(m_payment_id=payment_id)
          payment.mark_complete()
          
          # Queue slow tasks
          send_email.delay(payment.id)
          
          return HttpResponse('OK')  # Respond fast!

2. **Use Celery for slow tasks**:

   .. code-block:: bash
   
      pip install celery redis

3. **Optimize database queries**:

   .. code-block:: python
   
      # Use select_related to reduce queries
      payment = PayFastPayment.objects.select_related('user').get(
          m_payment_id=payment_id
      )

Security/Signature Issues
==========================

Issue: Signature verification failed
-------------------------------------

**Symptoms**:

.. code-block:: text

   Invalid signature

**Solutions**:

1. **Check passphrase matches**:

   .. code-block:: python
   
      # settings.py
      PAYFAST_PASSPHRASE = 'YourExactPassphrase'
      
      # Must match PayFast dashboard exactly

2. **Verify you're using correct credentials**:

   .. code-block:: python
   
      # Sandbox
      if PAYFAST_TEST_MODE:
          PAYFAST_PASSPHRASE = 'SandboxPassphrase'
      # Production
      else:
          PAYFAST_PASSPHRASE = 'ProductionPassphrase'

3. **Debug signature generation**:

   .. code-block:: python
   
      from payfast.utils import generate_signature
      
      # Generate signature
      data = {
          'merchant_id': '10000100',
          'amount': '100.00',
          'item_name': 'Test',
      }
      
      signature = generate_signature(data, 'YourPassphrase')
      print(f"Generated: {signature}")

4. **Check for whitespace**:

   .. code-block:: python
   
      # Remove any whitespace from passphrase
      PAYFAST_PASSPHRASE = 'YourPassphrase'.strip()

Issue: IP validation failing
-----------------------------

**Symptoms**: Webhook rejected due to invalid IP

**Solutions**:

1. **Check if behind proxy**:

   .. code-block:: python
   
      def get_client_ip(request):
          x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
          if x_forwarded_for:
              ip = x_forwarded_for.split(',')[0]
          else:
              ip = request.META.get('REMOTE_ADDR')
          return ip

2. **Configure nginx for proxies**:

   .. code-block:: nginx
   
      location /payfast/ {
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_pass http://your-app;
      }

3. **Temporarily disable for testing**:

   .. code-block:: python
   
      # Only for debugging!
      # utils.py
      def validate_ip(ip_address):
          return True  # REMOVE THIS IN PRODUCTION!

Database Issues
===============

Issue: Migration errors
-----------------------

**Symptoms**:

.. code-block:: text

   django.db.utils.OperationalError: no such table

**Solutions**:

1. **Run migrations**:

   .. code-block:: bash
   
      python manage.py migrate payfast

2. **Check migrations exist**:

   .. code-block:: bash
   
      python manage.py showmigrations payfast

3. **Create missing migrations**:

   .. code-block:: bash
   
      python manage.py makemigrations payfast
      python manage.py migrate

Issue: Database locked
----------------------

**Symptoms** (SQLite):

.. code-block:: text

   database is locked

**Solutions**:

1. **Use PostgreSQL in production**:

   .. code-block:: python
   
      # settings.py
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.postgresql',
              'NAME': 'your_db',
          }
      }

2. **Increase SQLite timeout**:

   .. code-block:: python
   
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.sqlite3',
              'NAME': 'db.sqlite3',
              'OPTIONS': {
                  'timeout': 20,
              }
          }
      }

Configuration Issues
====================

Issue: Settings not found
-------------------------

**Symptoms**:

.. code-block:: text

   AttributeError: 'Settings' object has no attribute 'PAYFAST_MERCHANT_ID'

**Solution**:

Add required settings:

.. code-block:: python

   # settings.py
   PAYFAST_MERCHANT_ID = '10000100'
   PAYFAST_MERCHANT_KEY = '46f0cd694581a'
   PAYFAST_PASSPHRASE = 'your_passphrase'
   PAYFAST_TEST_MODE = True

Issue: Environment variables not loading
-----------------------------------------

**Symptoms**: Settings show ``None`` or empty values

**Solutions**:

1. **Install python-decouple**:

   .. code-block:: bash
   
      pip install python-decouple

2. **Create .env file**:

   .. code-block:: bash
   
      # .env
      PAYFAST_MERCHANT_ID=10000100
      PAYFAST_MERCHANT_KEY=46f0cd694581a
      PAYFAST_PASSPHRASE=your_passphrase

3. **Load in settings**:

   .. code-block:: python
   
      # settings.py
      from decouple import config
      
      PAYFAST_MERCHANT_ID = config('PAYFAST_MERCHANT_ID')
      PAYFAST_MERCHANT_KEY = config('PAYFAST_MERCHANT_KEY')

4. **Add .env to .gitignore**:

   .. code-block:: text
   
      # .gitignore
      .env
      *.env

Template Issues
===============

Issue: Template not found
-------------------------

**Symptoms**:

.. code-block:: text

   TemplateDoesNotExist: payfast/checkout.html

**Solutions**:

1. **Check INSTALLED_APPS order**:

   .. code-block:: python
   
      INSTALLED_APPS = [
          'payfast',  # Should be here
          # Your apps can override templates if listed after
      ]

2. **Verify APP_DIRS**:

   .. code-block:: python
   
      TEMPLATES = [{
          'APP_DIRS': True,  # Must be True
      }]

3. **Create custom template**:

   .. code-block:: bash
   
      mkdir -p templates/payfast
      cp venv/lib/python3.x/site-packages/payfast/templates/payfast/checkout.html \
         templates/payfast/

Issue: Static files not loading
--------------------------------

**Symptoms**: CSS/images missing

**Solutions**:

1. **Collect static files**:

   .. code-block:: bash
   
      python manage.py collectstatic

2. **Configure static settings**:

   .. code-block:: python
   
      # settings.py
      STATIC_URL = '/static/'
      STATIC_ROOT = BASE_DIR / 'staticfiles'

Performance Issues
==================

Issue: Slow payment creation
-----------------------------

**Solutions**:

1. **Optimize database queries**:

   .. code-block:: python
   
      # Use select_related for foreign keys
      payment = PayFastPayment.objects.select_related('user').get(id=1)

2. **Add database indexes**:

   .. code-block:: python
   
      class PayFastPayment(models.Model):
          m_payment_id = models.CharField(max_length=100, db_index=True)

3. **Use connection pooling**:

   .. code-block:: bash
   
      pip install django-db-connection-pool

Issue: Webhook processing slow
-------------------------------

**Solutions**:

1. **Use async tasks**:

   .. code-block:: python
   
      from celery import shared_task
      
      @shared_task
      def process_webhook(payment_id):
          # Process in background
          pass

2. **Optimize validation**:

   .. code-block:: python
   
      # Cache PayFast IP addresses
      from django.core.cache import cache
      
      def get_payfast_ips():
          ips = cache.get('payfast_ips')
          if not ips:
              ips = resolve_payfast_hosts()
              cache.set('payfast_ips', ips, 3600)
          return ips

Getting Help
============

If you can't solve your issue:

1. **Check Existing Issues**:

   https://github.com/carrington-dev/dj-payfast/issues

2. **Enable Debug Logging**:

   .. code-block:: python
   
      # settings.py
      LOGGING = {
          'version': 1,
          'handlers': {
              'console': {
                  'class': 'logging.StreamHandler',
              },
          },
          'loggers': {
              'payfast': {
                  'handlers': ['console'],
                  'level': 'DEBUG',
              },
          },
      }

3. **Gather Information**:

   - Django version: ``python manage.py --version``
   - dj-payfast version: ``pip show dj-payfast``
   - Python version: ``python --version``
   - Error messages and stack traces
   - Relevant configuration (without credentials!)

4. **Create Issue**:

   https://github.com/carrington-dev/dj-payfast/issues/new

Next Steps
==========

* :doc:`security` - Security best practices
* :doc:`api` - Complete API reference
* :doc:`faq` - Frequently asked questions