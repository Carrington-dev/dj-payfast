.. _usage:

Usage Guide
===========

This guide covers common use cases and advanced features of dj-payfast.

Basic Payment Flow
------------------

The typical payment flow with dj-payfast follows these steps:

1. **Create Payment Record** - Store payment details in the database
2. **Generate Payment Form** - Create a secure PayFast form
3. **User Completes Payment** - User is redirected to PayFast
4. **Receive Webhook** - PayFast sends ITN notification
5. **Update Payment Status** - Payment is marked as complete
6. **Grant Access** - Your application grants the purchased service

Creating Payments
-----------------

Simple Payment
~~~~~~~~~~~~~~

Create a basic one-time payment:

.. code-block:: python

   from payfast.models import PayFastPayment
   import uuid

   payment = PayFastPayment.objects.create(
       user=request.user,
       m_payment_id=str(uuid.uuid4()),  # Unique payment ID
       amount=199.99,
       item_name='Django Course',
       item_description='Complete Django Web Development Course',
       email_address=request.user.email,
       name_first=request.user.first_name,
       name_last=request.user.last_name,
   )

Payment with Custom Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Store additional data with your payment:

.. code-block:: python

   payment = PayFastPayment.objects.create(
       user=request.user,
       m_payment_id=str(uuid.uuid4()),
       amount=499.00,
       item_name='Premium Plan',
       email_address=request.user.email,
       
       # Custom string fields (useful for order IDs, SKUs, etc.)
       custom_str1=f'order_{order.id}',
       custom_str2=product.sku,
       custom_str3='monthly_subscription',
       
       # Custom integer fields (useful for user IDs, quantities, etc.)
       custom_int1=request.user.id,
       custom_int2=subscription.duration_months,
       custom_int3=order.quantity,
   )

Payment for Guest Checkout
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handle payments without requiring login:

.. code-block:: python

   payment = PayFastPayment.objects.create(
       user=None,  # No user for guest checkout
       m_payment_id=str(uuid.uuid4()),
       amount=99.00,
       item_name='Guest Purchase',
       email_address=request.POST.get('email'),
       name_first=request.POST.get('first_name'),
       name_last=request.POST.get('last_name'),
       cell_number=request.POST.get('phone'),
   )

Generating Payment Forms
------------------------

Basic Form
~~~~~~~~~~

.. code-block:: python

   from payfast.forms import PayFastPaymentForm
   from django.urls import reverse

   form = PayFastPaymentForm(initial={
       'amount': payment.amount,
       'item_name': payment.item_name,
       'm_payment_id': payment.m_payment_id,
       'email_address': payment.email_address,
       'notify_url': request.build_absolute_uri(reverse('payfast:notify')),
   })

Form with All Callback URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   form = PayFastPaymentForm(initial={
       'amount': payment.amount,
       'item_name': payment.item_name,
       'item_description': payment.item_description,
       'm_payment_id': payment.m_payment_id,
       'email_address': payment.email_address,
       'name_first': payment.name_first,
       'name_last': payment.name_last,
       'cell_number': payment.cell_number,
       
       # Callback URLs
       'return_url': request.build_absolute_uri(reverse('payment_success')),
       'cancel_url': request.build_absolute_uri(reverse('payment_cancel')),
       'notify_url': request.build_absolute_uri(reverse('payfast:notify')),
       
       # Pass custom fields
       'custom_str1': payment.custom_str1,
       'custom_int1': payment.custom_int1,
   })

Rendering the Form
~~~~~~~~~~~~~~~~~~

**In your template:**

.. code-block:: html

   <form action="{{ form.get_action_url }}" method="post">
       {{ form.as_p }}
       <button type="submit">Pay Now</button>
   </form>

**Or with Bootstrap styling:**

.. code-block:: html

   <form action="{{ form.get_action_url }}" method="post" class="payfast-form">
       {% for field in form %}
           {{ field }}
       {% endfor %}
       <button type="submit" class="btn btn-primary btn-lg">
           <i class="fas fa-lock"></i> Secure Payment - R{{ payment.amount }}
       </button>
   </form>

   <div class="payment-info mt-3">
       <small class="text-muted">
           You will be redirected to PayFast to complete your payment securely.
       </small>
   </div>

Querying Payments
-----------------

Get User's Payments
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # All payments for a user
   payments = PayFastPayment.objects.filter(user=request.user)

   # Completed payments only
   completed = PayFastPayment.objects.filter(
       user=request.user,
       status='complete'
   )

   # Recent payments (last 30 days)
   from django.utils import timezone
   from datetime import timedelta

   recent = PayFastPayment.objects.filter(
       user=request.user,
       created_at__gte=timezone.now() - timedelta(days=30)
   )

Get Payment by ID
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.shortcuts import get_object_or_404

   # By merchant payment ID
   payment = get_object_or_404(
       PayFastPayment,
       m_payment_id=payment_id
   )

   # By PayFast payment ID (after payment completed)
   payment = get_object_or_404(
       PayFastPayment,
       pf_payment_id=pf_payment_id
   )

Calculate Revenue
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.db.models import Sum, Count, Avg

   # Total revenue
   total = PayFastPayment.objects.filter(
       status='complete'
   ).aggregate(Sum('amount'))

   # Revenue this month
   from django.utils import timezone
   import calendar

   now = timezone.now()
   month_start = now.replace(day=1, hour=0, minute=0, second=0)
   
   monthly_revenue = PayFastPayment.objects.filter(
       status='complete',
       completed_at__gte=month_start
   ).aggregate(Sum('amount'))

   # Average transaction value
   avg_payment = PayFastPayment.objects.filter(
       status='complete'
   ).aggregate(Avg('amount'))

   # Total number of transactions
   total_transactions = PayFastPayment.objects.filter(
       status='complete'
   ).count()

Handling Payment Status
-----------------------

Check Payment Status
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   payment = PayFastPayment.objects.get(m_payment_id=payment_id)

   if payment.status == 'complete':
       # Payment successful
       grant_access(request.user)
   elif payment.status == 'pending':
       # Payment still processing
       show_pending_message()
   elif payment.status == 'failed':
       # Payment failed
       show_error_message()

Manual Status Update
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Mark as complete
   payment.mark_complete()

   # Mark as failed
   payment.mark_failed()

   # Manual status change
   payment.status = 'cancelled'
   payment.save()

Using Django Signals
--------------------

Listen for Payment Events
~~~~~~~~~~~~~~~~~~~~~~~~~

Create a signals handler to respond to payment events:

.. code-block:: python

   # signals.py
   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from payfast.models import PayFastPayment
   from django.core.mail import send_mail

   @receiver(post_save, sender=PayFastPayment)
   def handle_payment_update(sender, instance, created, **kwargs):
       """Handle payment status changes"""
       
       if created:
           # New payment created
           print(f"New payment created: {instance.m_payment_id}")
       
       elif instance.status == 'complete' and instance.payment_status == 'COMPLETE':
           # Payment completed successfully
           handle_successful_payment(instance)

   def handle_successful_payment(payment):
       """Process successful payment"""
       
       # Grant access to user
       if payment.user:
           activate_premium(payment.user)
       
       # Send confirmation email
       send_mail(
           subject='Payment Confirmation',
           message=f'Thank you for your payment of R{payment.amount}',
           from_email='noreply@example.com',
           recipient_list=[payment.email_address],
       )
       
       # Log the event
       print(f"Payment {payment.m_payment_id} completed successfully")

Register signals in your app's ``apps.py``:

.. code-block:: python

   # apps.py
   from django.apps import AppConfig

   class MyAppConfig(AppConfig):
       default_auto_field = 'django.db.models.BigAutoField'
       name = 'myapp'

       def ready(self):
           import myapp.signals  # Register signals

Working with Webhooks
---------------------

Understanding ITN Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PayFast sends Instant Transaction Notifications (ITN) to your webhook URL when:

* Payment is completed
* Payment fails
* Payment is cancelled
* Subscription is created/cancelled
* Payment status changes

The webhook handler at ``/payfast/notify/`` automatically:

1. Validates the request signature
2. Verifies the request comes from PayFast
3. Validates with PayFast servers
4. Updates the payment record
5. Logs the notification

Accessing Notification History
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from payfast.models import PayFastNotification

   # Get all notifications for a payment
   notifications = PayFastNotification.objects.filter(
       payment=payment
   )

   # Get failed notifications
   failed = PayFastNotification.objects.filter(
       is_valid=False
   )

   # Check why validation failed
   for notification in failed:
       print(f"Error: {notification.validation_errors}")
       print(f"Data: {notification.raw_data}")

Custom Webhook Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to extend webhook handling, you can subclass the view:

.. code-block:: python

   # views.py
   from payfast.views import PayFastNotifyView

   class CustomPayFastNotifyView(PayFastNotifyView):
       
       def post(self, request, *args, **kwargs):
           # Call parent processing
           response = super().post(request, *args, **kwargs)
           
           # Add custom logic
           if response.status_code == 200:
               post_data = request.POST.dict()
               m_payment_id = post_data.get('m_payment_id')
               
               # Your custom logic here
               self.send_custom_notifications(m_payment_id)
           
           return response
       
       def send_custom_notifications(self, payment_id):
           """Send custom notifications"""
           # Your implementation
           pass

Then update your URLs:

.. code-block:: python

   from .views import CustomPayFastNotifyView

   urlpatterns = [
       path('payfast/notify/', CustomPayFastNotifyView.as_view(), name='payfast_notify'),
   ]

Advanced Use Cases
------------------

Dynamic Pricing
~~~~~~~~~~~~~~~

Calculate prices based on user input:

.. code-block:: python

   def checkout_view(request):
       # Get selected plan
       plan = request.POST.get('plan')
       
       # Calculate amount
       prices = {
           'basic': 99.00,
           'pro': 199.00,
           'enterprise': 499.00,
       }
       amount = prices.get(plan, 99.00)
       
       # Apply discount if applicable
       if request.user.has_discount():
           amount = amount * 0.9  # 10% discount
       
       payment = PayFastPayment.objects.create(
           user=request.user,
           m_payment_id=str(uuid.uuid4()),
           amount=amount,
           item_name=f'{plan.title()} Plan',
           email_address=request.user.email,
           custom_str1=plan,
       )

Multiple Items Checkout
~~~~~~~~~~~~~~~~~~~~~~~

Handle cart checkout with multiple items:

.. code-block:: python

   def cart_checkout(request):
       cart = get_cart(request)
       
       # Calculate total
       total = sum(item.price * item.quantity for item in cart.items.all())
       
       # Create item description
       items_desc = ', '.join([
           f"{item.quantity}x {item.product.name}"
           for item in cart.items.all()
       ])
       
       payment = PayFastPayment.objects.create(
           user=request.user,
           m_payment_id=str(uuid.uuid4()),
           amount=total,
           item_name='Shopping Cart',
           item_description=items_desc,
           email_address=request.user.email,
           custom_str1=f'cart_{cart.id}',
           custom_int1=cart.items.count(),  # Number of items
       )

Refund Tracking
~~~~~~~~~~~~~~~

While dj-payfast doesn't process refunds (done via PayFast dashboard), you can track them:

.. code-block:: python

   # Create a custom model for refunds
   from django.db import models

   class PayFastRefund(models.Model):
       payment = models.ForeignKey(PayFastPayment, on_delete=models.CASCADE)
       amount = models.DecimalField(max_digits=10, decimal_places=2)
       reason = models.TextField()
       refunded_at = models.DateTimeField(auto_now_add=True)
       processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

   # Create refund record
   refund = PayFastRefund.objects.create(
       payment=payment,
       amount=payment.amount,
       reason='Customer request',
       processed_by=request.user,
   )

Best Practices
--------------

1. **Always Use HTTPS in Production**
   
   PayFast requires HTTPS for live payments.

2. **Generate Unique Payment IDs**
   
   Use UUIDs or combine timestamp + user ID:

   .. code-block:: python

      import uuid
      m_payment_id = str(uuid.uuid4())
      
      # Or
      from django.utils import timezone
      m_payment_id = f"{request.user.id}_{int(timezone.now().timestamp())}"

3. **Store Original Request Data**
   
   Use custom fields to store important metadata:

   .. code-block:: python

      payment.custom_str1 = f'order_{order.id}'
      payment.custom_int1 = request.user.id

4. **Handle All Payment States**
   
   Don't assume payments will always complete:

   .. code-block:: python

      if payment.status == 'complete':
          grant_access()
      elif payment.status == 'pending':
          show_pending_message()
      else:
          show_error_message()

5. **Use Absolute URLs for Callbacks**
   
   Always use ``build_absolute_uri()``:

   .. code-block:: python

      notify_url = request.build_absolute_uri(reverse('payfast:notify'))

6. **Monitor Webhook Failures**
   
   Regularly check ``PayFastNotification`` for validation errors.

7. **Test Thoroughly**
   
   Always test in sandbox before going live. See :doc:`testing`.

Next Steps
----------

* :doc:`webhooks` - Deep dive into webhook handling
* :doc:`testing` - Learn testing strategies
* :doc:`security` - Security best practices
* :doc:`api` - Complete API reference