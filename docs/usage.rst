===============================================================================
USAGE.RST
===============================================================================

Usage Guide
===========

This comprehensive guide covers common use cases and advanced patterns for **dj-payfast**.

Basic Payment
-------------

Creating a Simple Payment
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from payfast.models import PayFastPayment
   from payfast.forms import PayFastPaymentForm
   import uuid

   def create_payment(request):
       payment = PayFastPayment.objects.create(
           user=request.user,
           m_payment_id=str(uuid.uuid4()),
           amount=99.99,
           item_name='Product Name',
           email_address=request.user.email,
       )
       
       form = PayFastPaymentForm(initial={
           'amount': payment.amount,
           'item_name': payment.item_name,
           'm_payment_id': payment.m_payment_id,
           'email_address': payment.email_address,
           'notify_url': request.build_absolute_uri('/payfast/notify/'),
       })
       
       return render(request, 'checkout.html', {'form': form})

Working with Custom Fields
---------------------------

PayFast supports 5 string and 5 integer custom fields:

.. code-block:: python

   payment = PayFastPayment.objects.create(
       user=request.user,
       m_payment_id=str(uuid.uuid4()),
       amount=199.99,
       item_name='Premium Plan',
       email_address=request.user.email,
       
       # Custom string fields
       custom_str1='subscription',
       custom_str2='monthly',
       custom_str3=request.user.username,
       
       # Custom integer fields
       custom_int1=30,  # days
       custom_int2=request.user.id,
   )

Querying Payments
-----------------

Get User's Payments
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from payfast.models import PayFastPayment

   # All payments for a user
   payments = PayFastPayment.objects.filter(user=request.user)

   # Completed payments only
   completed = PayFastPayment.objects.filter(
       user=request.user,
       status='complete'
   )

   # Pending payments
   pending = PayFastPayment.objects.filter(
       user=request.user,
       status='pending'
   )

Get Payment by ID
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # By merchant payment ID
   payment = PayFastPayment.objects.get(m_payment_id=payment_id)

   # By PayFast payment ID
   payment = PayFastPayment.objects.get(pf_payment_id=pf_id)

Filter by Date Range
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.utils import timezone
   from datetime import timedelta

   # Payments in last 30 days
   thirty_days_ago = timezone.now() - timedelta(days=30)
   recent = PayFastPayment.objects.filter(
       created_at__gte=thirty_days_ago,
       status='complete'
   )

   # Payments by month
   from django.db.models.functions import TruncMonth
   
   monthly = PayFastPayment.objects.filter(
       status='complete'
   ).annotate(
       month=TruncMonth('completed_at')
   ).values('month').annotate(
       total=Sum('amount'),
       count=Count('id')
   )

Payment Status Handling
-----------------------

Check Payment Status
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   payment = PayFastPayment.objects.get(m_payment_id=payment_id)

   if payment.status == 'complete':
       # Grant access
       grant_user_access(payment.user)
   elif payment.status == 'pending':
       # Still processing
       show_pending_message()
   elif payment.status == 'failed':
       # Payment failed
       show_failure_message()

Manual Status Updates
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Mark as complete
   payment.mark_complete()

   # Mark as failed
   payment.mark_failed()

   # Custom status update
   payment.status = 'cancelled'
   payment.save()

Subscriptions and Recurring Payments
-------------------------------------

One-Time Subscription
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def subscribe_monthly(request):
       payment = PayFastPayment.objects.create(
           user=request.user,
           m_payment_id=str(uuid.uuid4()),
           amount=299.99,
           item_name='Monthly Premium Subscription',
           item_description='30 days premium access',
           email_address=request.user.email,
           custom_str1='subscription',
           custom_str2='monthly',
           custom_int1=30,  # duration in days
       )
       
       # Create form and render
       form = PayFastPaymentForm(initial={...})
       return render(request, 'subscribe.html', {'form': form})

Processing After Payment
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from payfast.models import PayFastPayment

   @receiver(post_save, sender=PayFastPayment)
   def process_subscription(sender, instance, **kwargs):
       """Automatically process subscriptions when payment complet