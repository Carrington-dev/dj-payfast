.. _testing:

===============================================================================
Testing Guide
===============================================================================

Comprehensive guide to testing PayFast integrations in your Django application.

Overview
========

Testing payment systems is crucial for:

* **Preventing Production Issues**: Catch bugs before they affect real payments
* **Regulatory Compliance**: Ensure PCI DSS compliance
* **User Experience**: Verify smooth payment flows
* **Business Continuity**: Avoid revenue loss from broken payments

Testing Environments
====================

PayFast Sandbox
---------------

PayFast provides a sandbox environment for testing without processing real money.

**Sandbox URL**: https://sandbox.payfast.co.za

**Getting Sandbox Credentials**:

1. Sign up at https://sandbox.payfast.co.za
2. Navigate to **Settings → Integration**
3. Copy your sandbox credentials
4. Generate a test passphrase

**Sandbox vs Production Differences**:

+------------------+--------------------------------+--------------------------------+
| Feature          | Sandbox                        | Production                     |
+==================+================================+================================+
| URL              | sandbox.payfast.co.za          | www.payfast.co.za              |
+------------------+--------------------------------+--------------------------------+
| Real Money       | No charges                     | Real payments                  |
+------------------+--------------------------------+--------------------------------+
| Test Cards       | Use test card numbers          | Real card numbers only         |
+------------------+--------------------------------+--------------------------------+
| Webhooks         | Same as production             | Same as sandbox                |
+------------------+--------------------------------+--------------------------------+

Configuring Test Mode
----------------------

.. code-block:: python

   # settings.py
   
   # Sandbox Configuration
   PAYFAST_MERCHANT_ID = '10000100'  # Sandbox merchant ID
   PAYFAST_MERCHANT_KEY = '46f0cd694581a'  # Sandbox merchant key
   PAYFAST_PASSPHRASE = 'jt7NOE43FZPn'  # Test passphrase
   PAYFAST_TEST_MODE = True  # Enable sandbox

**Using Environment Variables**:

.. code-block:: python

   # settings.py
   import os
   
   PAYFAST_TEST_MODE = os.environ.get('PAYFAST_TEST_MODE', 'True') == 'True'
   
   if PAYFAST_TEST_MODE:
       # Sandbox credentials
       PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_SANDBOX_MERCHANT_ID')
       PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_SANDBOX_MERCHANT_KEY')
       PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_SANDBOX_PASSPHRASE')
   else:
       # Production credentials
       PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
       PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
       PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')

Unit Testing
============

Testing Models
--------------

.. code-block:: python

   # tests/test_models.py
   from django.test import TestCase
   from django.contrib.auth import get_user_model
   from payfast.models import PayFastPayment, PayFastNotification
   import uuid
   
   User = get_user_model()
   
   class PayFastPaymentModelTests(TestCase):
       
       def setUp(self):
           """Create test user and payment"""
           self.user = User.objects.create_user(
               username='testuser',
               email='test@example.com',
               password='testpass123'
           )
           
           self.payment = PayFastPayment.objects.create(
               user=self.user,
               m_payment_id=str(uuid.uuid4()),
               amount=99.99,
               item_name='Test Product',
               email_address=self.user.email,
           )
       
       def test_payment_creation(self):
           """Test payment is created with correct defaults"""
           self.assertEqual(self.payment.status, 'pending')
           self.assertEqual(self.payment.amount, 99.99)
           self.assertEqual(self.payment.user, self.user)
           self.assertIsNotNone(self.payment.m_payment_id)
       
       def test_mark_complete(self):
           """Test marking payment as complete"""
           self.payment.mark_complete()
           
           self.assertEqual(self.payment.status, 'complete')
           self.assertIsNotNone(self.payment.completed_at)
       
       def test_mark_failed(self):
           """Test marking payment as failed"""
           self.payment.mark_failed()
           
           self.assertEqual(self.payment.status, 'failed')
       
       def test_string_representation(self):
           """Test __str__ method"""
           expected = f'Payment {self.payment.m_payment_id} - pending'
           self.assertEqual(str(self.payment), expected)
       
       def test_custom_fields(self):
           """Test custom fields storage"""
           payment = PayFastPayment.objects.create(
               m_payment_id=str(uuid.uuid4()),
               amount=199.99,
               item_name='Premium Plan',
               email_address='user@example.com',
               custom_str1='order_123',
               custom_int1=5,
           )
           
           self.assertEqual(payment.custom_str1, 'order_123')
           self.assertEqual(payment.custom_int1, 5)

Testing Forms
-------------

.. code-block:: python

   # tests/test_forms.py
   from django.test import TestCase
   from payfast.forms import PayFastPaymentForm
   from payfast import conf
   
   class PayFastPaymentFormTests(TestCase):
       
       def test_form_initialization(self):
           """Test form creates with initial data"""
           initial_data = {
               'amount': 99.99,
               'item_name': 'Test Item',
               'm_payment_id': 'test-123',
               'email_address': 'test@example.com',
               'notify_url': 'https://example.com/notify/',
           }
           
           form = PayFastPaymentForm(initial=initial_data)
           
           self.assertIsNotNone(form.fields['signature'].initial)
           self.assertEqual(form.fields['merchant_id'].initial, conf.PAYFAST_MERCHANT_ID)
       
       def test_signature_generation(self):
           """Test signature is generated correctly"""
           initial_data = {
               'amount': 100.00,
               'item_name': 'Test',
               'm_payment_id': 'test-456',
               'email_address': 'test@example.com',
               'notify_url': 'https://example.com/notify/',
           }
           
           form = PayFastPaymentForm(initial=initial_data)
           signature = form.fields['signature'].initial
           
           self.assertIsNotNone(signature)
           self.assertEqual(len(signature), 32)  # MD5 hash length
       
       def test_get_action_url(self):
           """Test form action URL"""
           form = PayFastPaymentForm()
           action_url = form.get_action_url()
           
           if conf.PAYFAST_TEST_MODE:
               self.assertIn('sandbox', action_url)
           else:
               self.assertNotIn('sandbox', action_url)

Testing Utilities
-----------------

.. code-block:: python

   # tests/test_utils.py
   from django.test import TestCase
   from payfast.utils import (
       generate_signature,
       verify_signature,
       validate_ip
   )
   
   class UtilityTests(TestCase):
       
       def test_generate_signature(self):
           """Test signature generation"""
           data = {
               'merchant_id': '10000100',
               'merchant_key': '46f0cd694581a',
               'amount': '100.00',
               'item_name': 'Test',
           }
           
           signature = generate_signature(data, 'testpass')
           
           self.assertIsNotNone(signature)
           self.assertEqual(len(signature), 32)
       
       def test_verify_signature_valid(self):
           """Test signature verification with valid signature"""
           data = {
               'merchant_id': '10000100',
               'amount': '100.00',
               'item_name': 'Test',
           }
           
           # Generate signature
           signature = generate_signature(data, 'testpass')
           data['signature'] = signature
           
           # Verify
           is_valid = verify_signature(data, 'testpass')
           self.assertTrue(is_valid)
       
       def test_verify_signature_invalid(self):
           """Test signature verification with invalid signature"""
           data = {
               'merchant_id': '10000100',
               'amount': '100.00',
               'signature': 'invalid_signature',
           }
           
           is_valid = verify_signature(data, 'testpass')
           self.assertFalse(is_valid)
       
       def test_validate_ip(self):
           """Test IP validation"""
           # Valid PayFast IP (simplified test)
           is_valid = validate_ip('127.0.0.1')
           self.assertIsNotNone(is_valid)

Integration Testing
===================

Testing Views
-------------

.. code-block:: python

   # tests/test_views.py
   from django.test import TestCase, Client
   from django.urls import reverse
   from django.contrib.auth import get_user_model
   from payfast.models import PayFastPayment, PayFastNotification
   import uuid
   
   User = get_user_model()
   
   class CheckoutViewTests(TestCase):
       
       def setUp(self):
           self.client = Client()
           self.user = User.objects.create_user(
               username='testuser',
               email='test@example.com',
               password='testpass123'
           )
           self.client.login(username='testuser', password='testpass123')
       
       def test_checkout_view_requires_login(self):
           """Test checkout requires authentication"""
           self.client.logout()
           response = self.client.get(reverse('payfast:checkout'))
           
           self.assertEqual(response.status_code, 302)  # Redirect to login
       
       def test_checkout_view_creates_payment(self):
           """Test checkout creates payment record"""
           response = self.client.get(
               reverse('payfast:checkout'),
               {
                   'amount': 99.99,
                   'item_name': 'Test Item',
                   'email_address': 'test@example.com',
               }
           )
           
           self.assertEqual(response.status_code, 200)
           
           # Check payment was created
           payment_exists = PayFastPayment.objects.filter(
               user=self.user,
               amount=99.99
           ).exists()
           
           self.assertTrue(payment_exists)
   
   class WebhookViewTests(TestCase):
       
       def setUp(self):
           self.client = Client()
           self.payment = PayFastPayment.objects.create(
               m_payment_id='test-123',
               amount=99.99,
               item_name='Test',
               email_address='test@example.com',
           )
       
       def test_webhook_post_creates_notification(self):
           """Test webhook creates notification record"""
           webhook_data = {
               'm_payment_id': 'test-123',
               'pf_payment_id': '1234567',
               'payment_status': 'COMPLETE',
               'amount_gross': '99.99',
               'amount_fee': '5.75',
               'amount_net': '94.24',
               'item_name': 'Test',
               'email_address': 'test@example.com',
           }
           
           response = self.client.post(
               reverse('payfast:notify'),
               data=webhook_data
           )
           
           # Check notification was created
           notification_exists = PayFastNotification.objects.filter(
               payment=self.payment
           ).exists()
           
           self.assertTrue(notification_exists)

Testing Signals
---------------

.. code-block:: python

   # tests/test_signals.py
   from django.test import TestCase
   from payfast.models import PayFastPayment
   from unittest.mock import patch, MagicMock
   
   class SignalTests(TestCase):
       
       @patch('myapp.signals.grant_access')
       def test_payment_complete_signal(self, mock_grant_access):
           """Test signal fires on payment completion"""
           
           # Create payment
           payment = PayFastPayment.objects.create(
               m_payment_id='test-123',
               amount=99.99,
               item_name='Test',
               email_address='test@example.com',
               status='pending',
           )
           
           # Mark as complete
           payment.mark_complete()
           payment.save()
           
           # Check signal handler was called
           mock_grant_access.assert_called_once()

Testing Webhooks
================

Mocking PayFast Webhooks
-------------------------

.. code-block:: python

   # tests/test_webhooks.py
   from django.test import TestCase, Client
   from django.urls import reverse
   from payfast.models import PayFastPayment
   from payfast.utils import generate_signature
   
   class WebhookTests(TestCase):
       
       def setUp(self):
           self.client = Client()
           self.payment = PayFastPayment.objects.create(
               m_payment_id='test-123',
               amount=99.99,
               item_name='Test Product',
               email_address='test@example.com',
           )
       
       def _generate_webhook_data(self, payment_status='COMPLETE'):
           """Helper to generate valid webhook data"""
           data = {
               'm_payment_id': self.payment.m_payment_id,
               'pf_payment_id': '1234567',
               'payment_status': payment_status,
               'amount_gross': str(self.payment.amount),
               'amount_fee': '5.75',
               'amount_net': '94.24',
               'item_name': self.payment.item_name,
               'email_address': self.payment.email_address,
           }
           
           # Generate valid signature
           from django.conf import settings
           signature = generate_signature(data, settings.PAYFAST_PASSPHRASE)
           data['signature'] = signature
           
           return data
       
       def test_webhook_successful_payment(self):
           """Test webhook processes successful payment"""
           webhook_data = self._generate_webhook_data('COMPLETE')
           
           response = self.client.post(
               reverse('payfast:notify'),
               data=webhook_data
           )
           
           self.assertEqual(response.status_code, 200)
           
           # Verify payment was updated
           self.payment.refresh_from_db()
           self.assertEqual(self.payment.status, 'complete')
           self.assertEqual(self.payment.payment_status, 'COMPLETE')
       
       def test_webhook_failed_payment(self):
           """Test webhook processes failed payment"""
           webhook_data = self._generate_webhook_data('FAILED')
           
           response = self.client.post(
               reverse('payfast:notify'),
               data=webhook_data
           )
           
           self.assertEqual(response.status_code, 200)
           
           # Verify payment was marked as failed
           self.payment.refresh_from_db()
           self.assertEqual(self.payment.status, 'failed')

Manual Testing
==============

Test Card Numbers
-----------------

Use these test cards in PayFast sandbox:

**Successful Payment**:

.. code-block:: text

   Card Number: 4242 4242 4242 4242
   Expiry: Any future date
   CVV: Any 3 digits

**Insufficient Funds**:

.. code-block:: text

   Card Number: 4000 0000 0000 0002
   Expiry: Any future date
   CVV: Any 3 digits

Testing Payment Flow
--------------------

**Step-by-Step Manual Test**:

1. **Start Test Server**

   .. code-block:: bash
   
      python manage.py runserver

2. **Start ngrok** (for webhook testing)

   .. code-block:: bash
   
      ngrok http 8000

3. **Create Test Payment**

   Navigate to: http://localhost:8000/payfast/checkout/?amount=99.99&item_name=Test

4. **Complete Payment**

   * Use test card: 4242 4242 4242 4242
   * Expiry: 12/25
   * CVV: 123

5. **Verify Webhook**

   Check Django admin: /admin/payfast/payfastnotification/

6. **Verify Payment Status**

   Check: /admin/payfast/payfastpayment/

Testing Checklist
=================

Before Production
-----------------

.. code-block:: text

   Unit Tests:
   ☐ Model creation and methods
   ☐ Form validation and signature generation
   ☐ Utility functions
   ☐ Signal handlers
   
   Integration Tests:
   ☐ View endpoints
   ☐ Webhook processing
   ☐ Database transactions
   ☐ Authentication/authorization
   
   Manual Tests:
   ☐ Complete payment flow (sandbox)
   ☐ Failed payment handling
   ☐ Cancelled payment handling
   ☐ Webhook delivery
   ☐ Email notifications
   ☐ User interface flows
   
   Security Tests:
   ☐ Signature verification
   ☐ IP validation
   ☐ CSRF protection
   ☐ SQL injection prevention
   ☐ XSS prevention
   
   Production Readiness:
   ☐ HTTPS enabled
   ☐ Production credentials configured
   ☐ PAYFAST_TEST_MODE = False
   ☐ Webhook URL accessible
   ☐ Error monitoring configured
   ☐ Logging enabled
   ☐ Backup strategy in place

Next Steps
==========

* :doc:`webhooks` - Understanding webhooks in detail
* :doc:`security` - Security best practices
* :doc:`troubleshooting` - Solving common issues