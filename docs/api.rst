.. _api:

API Reference
=============

This page provides detailed API documentation for all dj-payfast components.

Models
------

PayFastPayment
~~~~~~~~~~~~~~

.. class:: payfast.models.PayFastPayment

   Model representing a PayFast payment transaction.

   **Fields**

   .. attribute:: user

      :type: ForeignKey to User (nullable)
      
      The user who made the payment. Can be null for guest checkouts.

   .. attribute:: m_payment_id

      :type: CharField (max_length=100, unique)
      
      Unique merchant payment ID. Must be unique across all payments.

   .. attribute:: pf_payment_id

      :type: CharField (max_length=100, nullable)
      
      PayFast's internal payment ID. Populated after payment is processed.

   .. attribute:: amount

      :type: DecimalField (max_digits=10, decimal_places=2)
      
      Payment amount in South African Rand (ZAR).

   .. attribute:: amount_gross

      :type: DecimalField (max_digits=10, decimal_places=2, nullable)
      
      Gross amount including fees. Populated by webhook.

   .. attribute:: amount_fee

      :type: DecimalField (max_digits=10, decimal_places=2, nullable)
      
      PayFast transaction fee. Populated by webhook.

   .. attribute:: amount_net

      :type: DecimalField (max_digits=10, decimal_places=2, nullable)
      
      Net amount after fees. Populated by webhook.

   .. attribute:: item_name

      :type: CharField (max_length=255)
      
      Name of the item being purchased.

   .. attribute:: item_description

      :type: TextField (blank)
      
      Detailed description of the item.

   .. attribute:: name_first

      :type: CharField (max_length=100, blank)
      
      Customer's first name.

   .. attribute:: name_last

      :type: CharField (max_length=100, blank)
      
      Customer's last name.

   .. attribute:: email_address

      :type: EmailField
      
      Customer's email address.

   .. attribute:: cell_number

      :type: CharField (max_length=20, blank)
      
      Customer's cell phone number.

   .. attribute:: status

      :type: CharField (max_length=20)
      :choices: ``pending``, ``complete``, ``failed``, ``cancelled``
      :default: ``pending``
      
      Current status of the payment.

   .. attribute:: payment_status

      :type: CharField (max_length=50, blank)
      
      PayFast's payment status (e.g., 'COMPLETE'). Populated by webhook.

   .. attribute:: created_at

      :type: DateTimeField (auto_now_add)
      
      When the payment record was created.

   .. attribute:: updated_at

      :type: DateTimeField (auto_now)
      
      When the payment record was last updated.

   .. attribute:: completed_at

      :type: DateTimeField (nullable)
      
      When the payment was marked as complete.

   .. attribute:: custom_str1 through custom_str5

      :type: CharField (max_length=255, blank)
      
      Custom string fields for storing additional data.

   .. attribute:: custom_int1 through custom_int5

      :type: IntegerField (nullable)
      
      Custom integer fields for storing additional data.

   **Methods**

   .. method:: mark_complete()

      Mark the payment as complete and set completion timestamp.

      .. code-block:: python

         payment.mark_complete()

   .. method:: mark_failed()

      Mark the payment as failed.

      .. code-block:: python

         payment.mark_failed()

   .. method:: __str__()

      Return string representation of the payment.

      :returns: ``"Payment {m_payment_id} - {status}"``

   **Example Usage**

   .. code-block:: python

      from payfast.models import PayFastPayment
      import uuid

      # Create a payment
      payment = PayFastPayment.objects.create(
          user=request.user,
          m_payment_id=str(uuid.uuid4()),
          amount=199.99,
          item_name='Premium Subscription',
          email_address='user@example.com',
      )

      # Query payments
      completed = PayFastPayment.objects.filter(status='complete')

      # Update status
      payment.mark_complete()

PayFastNotification
~~~~~~~~~~~~~~~~~~~

.. class:: payfast.models.PayFastNotification

   Model for logging PayFast ITN (Instant Transaction Notification) webhooks.

   **Fields**

   .. attribute:: payment

      :type: ForeignKey to PayFastPayment (nullable)
      
      The associated payment record, if found.

   .. attribute:: raw_data

      :type: JSONField
      
      Complete raw POST data from PayFast.

   .. attribute:: is_valid

      :type: BooleanField (default=False)
      
      Whether the notification passed all validation checks.

   .. attribute:: validation_errors

      :type: TextField (blank)
      
      Error messages if validation failed.

   .. attribute:: ip_address

      :type: GenericIPAddressField (nullable)
      
      IP address of the webhook request.

   .. attribute:: created_at

      :type: DateTimeField (auto_now_add)
      
      When the notification was received.

   **Methods**

   .. method:: __str__()

      Return string representation of the notification.

      :returns: ``"Notification {id} - {'Valid' if is_valid else 'Invalid'}"``

   **Example Usage**

   .. code-block:: python

      from payfast.models import PayFastNotification

      # Get all notifications for a payment
      notifications = PayFastNotification.objects.filter(
          payment=payment
      )

      # Check for validation failures
      failed = PayFastNotification.objects.filter(
          is_valid=False
      )

      for notification in failed:
          print(notification.validation_errors)
          print(notification.raw_data)

Forms
-----

PayFastPaymentForm
~~~~~~~~~~~~~~~~~~

.. class:: payfast.forms.PayFastPaymentForm

   Django form for generating PayFast payment requests.

   **Fields**

   All fields are hidden inputs that will be submitted to PayFast:

   .. attribute:: merchant_id

      PayFast merchant ID (auto-populated from settings).

   .. attribute:: merchant_key

      PayFast merchant key (auto-populated from settings).

   .. attribute:: amount

      Payment amount (required).

   .. attribute:: item_name

      Item name (required).

   .. attribute:: item_description

      Item description (optional).

   .. attribute:: m_payment_id

      Unique payment ID (required).

   .. attribute:: name_first

      Customer first name (optional).

   .. attribute:: name_last

      Customer last name (optional).

   .. attribute:: email_address

      Customer email (required).

   .. attribute:: cell_number

      Customer phone number (optional).

   .. attribute:: return_url

      URL to redirect after successful payment (optional).

   .. attribute:: cancel_url

      URL to redirect if payment is cancelled (optional).

   .. attribute:: notify_url

      Webhook URL for ITN notifications (required).

   .. attribute:: custom_str1 through custom_str5

      Custom string fields (optional).

   .. attribute:: custom_int1 through custom_int5

      Custom integer fields (optional).

   .. attribute:: signature

      MD5 signature for security (auto-generated).

   **Methods**

   .. method:: __init__(*args, **kwargs)

      Initialize form and generate signature from initial data.

   .. method:: get_action_url()

      Get the PayFast form submission URL (sandbox or production).

      :returns: PayFast processing URL

   **Example Usage**

   .. code-block:: python

      from payfast.forms import PayFastPaymentForm

      # Create form
      form = PayFastPaymentForm(initial={
          'amount': 99.99,
          'item_name': 'Premium Plan',
          'm_payment_id': 'unique-payment-id',
          'email_address': 'user@example.com',
          'notify_url': 'https://example.com/payfast/notify/',
      })

      # In template
      # <form action="{{ form.get_action_url }}" method="post">
      #     {{ form.as_p }}
      #     <button type="submit">Pay</button>
      # </form>

Views
-----

PayFastNotifyView
~~~~~~~~~~~~~~~~~

.. class:: payfast.views.PayFastNotifyView

   Class-based view for handling PayFast ITN webhook notifications.

   **Decorators**

   * ``@csrf_exempt`` - CSRF protection disabled (PayFast can't send CSRF token)
   * ``@require_POST`` - Only POST requests allowed

   **Methods**

   .. method:: post(request, *args, **kwargs)

      Handle incoming webhook notification.

      **Process:**

      1. Extract POST data
      2. Validate IP address
      3. Verify signature
      4. Validate with PayFast server
      5. Find payment record
      6. Update payment status
      7. Log notification

      :param request: Django HttpRequest object
      :returns: HttpResponse with status 200 if valid, 400 if invalid

   .. method:: validate_with_payfast(post_data)

      Validate notification data with PayFast servers.

      :param post_data: Dictionary of POST data
      :returns: Boolean indicating validation success

   **Example Custom View**

   .. code-block:: python

      from payfast.views import PayFastNotifyView

      class CustomNotifyView(PayFastNotifyView):
          
          def post(self, request, *args, **kwargs):
              response = super().post(request, *args, **kwargs)
              
              if response.status_code == 200:
                  # Add custom logic
                  self.send_notifications(request.POST)
              
              return response
          
          def send_notifications(self, data):
              # Your custom implementation
              pass

Utility Functions
-----------------

generate_signature
~~~~~~~~~~~~~~~~~~

.. function:: payfast.utils.generate_signature(data_dict, passphrase=None)

   Generate MD5 signature for PayFast request.

   :param data_dict: Dictionary of payment data
   :param passphrase: PayFast passphrase (optional, uses settings if not provided)
   :returns: MD5 signature as hex string

   **Example**

   .. code-block:: python

      from payfast.utils import generate_signature

      data = {
          'merchant_id': '10000100',
          'merchant_key': '46f0cd694581a',
          'amount': '100.00',
          'item_name': 'Test Product',
      }

      signature = generate_signature(data, passphrase='MyPassphrase')

verify_signature
~~~~~~~~~~~~~~~~

.. function:: payfast.utils.verify_signature(data_dict, passphrase=None)

   Verify PayFast signature from webhook data.

   :param data_dict: Dictionary containing payment data and signature
   :param passphrase: PayFast passphrase (optional)
   :returns: Boolean indicating if signature is valid

   **Example**

   .. code-block:: python

      from payfast.utils import verify_signature

      webhook_data = request.POST.dict()
      
      if verify_signature(webhook_data):
          # Signature is valid
          process_payment(webhook_data)
      else:
          # Invalid signature
          log_security_alert()

validate_ip
~~~~~~~~~~~

.. function:: payfast.utils.validate_ip(ip_address)

   Validate that request comes from PayFast servers.

   :param ip_address: IP address to validate
   :returns: Boolean indicating if IP is valid

   **Example**

   .. code-block:: python

      from payfast.utils import validate_ip

      ip = request.META.get('REMOTE_ADDR')
      
      if validate_ip(ip):
          # Request from PayFast
          process_webhook()
      else:
          # Invalid IP
          return HttpResponseForbidden()

Configuration
-------------

Settings
~~~~~~~~

All settings are configured in your Django ``settings.py``:

.. attribute:: PAYFAST_MERCHANT_ID

   :type: str
   :required: Yes
   
   Your PayFast merchant ID.

   .. code-block:: python

      PAYFAST_MERCHANT_ID = '10000100'

.. attribute:: PAYFAST_MERCHANT_KEY

   :type: str
   :required: Yes
   
   Your PayFast merchant key.

   .. code-block:: python

      PAYFAST_MERCHANT_KEY = '46f0cd694581a'

.. attribute:: PAYFAST_PASSPHRASE

   :type: str
   :required: No (but recommended)
   :default: ``''``
   
   Your PayFast passphrase for enhanced security.

   .. code-block:: python

      PAYFAST_PASSPHRASE = 'MySecurePassphrase123'

.. attribute:: PAYFAST_TEST_MODE

   :type: bool
   :required: No
   :default: ``True``
   
   Enable sandbox/test mode. Set to ``False`` for production.

   .. code-block:: python

      PAYFAST_TEST_MODE = False  # Production mode

URLs
~~~~

.. data:: payfast.urls

   URL configuration for dj-payfast.

   **Patterns:**

   * ``notify/`` - Webhook endpoint (name: ``payfast:notify``)

   **Usage:**

   .. code-block:: python

      # urls.py
      from django.urls import path, include

      urlpatterns = [
          path('payfast/', include('payfast.urls')),
      ]

   This creates the endpoint: ``/payfast/notify/``

Admin
-----

PayFastPaymentAdmin
~~~~~~~~~~~~~~~~~~~

.. class:: payfast.admin.PayFastPaymentAdmin

   Django admin configuration for PayFastPayment model.

   **Features:**

   * List display with key fields
   * Filters by status, dates
   * Search by payment IDs and email
   * Read-only timestamp fields
   * Organized fieldsets
   * Collapsible custom fields section

   **List Display:**

   * ``m_payment_id``
   * ``user``
   * ``amount``
   * ``status``
   * ``email_address``
   * ``created_at``
   * ``completed_at``

   **Filters:**

   * ``status``
   * ``created_at``
   * ``completed_at``

   **Search Fields:**

   * ``m_payment_id``
   * ``pf_payment_id``
   * ``email_address``
   * ``item_name``

PayFastNotificationAdmin
~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: payfast.admin.PayFastNotificationAdmin

   Django admin configuration for PayFastNotification model.

   **Features:**

   * List display with validation status
   * Filter by validity and date
   * Search by payment ID and IP
   * Read-only raw data field

   **List Display:**

   * ``id``
   * ``payment``
   * ``is_valid``
   * ``ip_address``
   * ``created_at``

Exceptions
----------

While dj-payfast uses standard Django exceptions, you may want to create custom exceptions:

.. code-block:: python

   # payfast/exceptions.py
   class PayFastError(Exception):
       """Base exception for PayFast errors"""
       pass

   class SignatureVerificationError(PayFastError):
       """Signature verification failed"""
       pass

   class PayFastValidationError(PayFastError):
       """PayFast validation failed"""
       pass

Constants
---------

Payment Status Choices
~~~~~~~~~~~~~~~~~~~~~~

.. data:: payfast.models.PayFastPayment.STATUS_CHOICES

   Available payment status values:

   * ``'pending'`` - Payment initiated but not complete
   * ``'complete'`` - Payment successfully completed
   * ``'failed'`` - Payment failed
   * ``'cancelled'`` - Payment cancelled by user

PayFast URLs
~~~~~~~~~~~~

.. data:: payfast.conf.PAYFAST_URL

   PayFast payment processing URL (sandbox or production).

.. data:: payfast.conf.PAYFAST_VALIDATE_URL

   PayFast validation endpoint (sandbox or production).

Version Information
-------------------

.. data:: payfast.__version__

   Current version of dj-payfast.

   .. code-block:: python

      import payfast
      print(payfast.__version__)  # '0.1.0'

Type Hints
----------

For better IDE support and type checking, you can use type hints:

.. code-block:: python

   from typing import Optional, Dict, Any
   from decimal import Decimal
   from django.http import HttpRequest, HttpResponse
   from payfast.models import PayFastPayment

   def create_payment(
       user_id: int,
       amount: Decimal,
       item_name: str,
       email: str
   ) -> PayFastPayment:
       payment = PayFastPayment.objects.create(
           user_id=user_id,
           m_payment_id=str(uuid.uuid4()),
           amount=amount,
           item_name=item_name,
           email_address=email,
       )
       return payment

   def process_webhook(
       request: HttpRequest,
       data: Dict[str, Any]
   ) -> HttpResponse:
       # Process webhook
       pass

See Also
--------

* :doc:`usage` - Usage examples and patterns
* :doc:`webhooks` - Webhook handling guide
* :doc:`models` - Detailed model documentation
* :doc:`security` - Security best practices