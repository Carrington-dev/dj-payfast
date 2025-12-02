===============================================================================
QUICKSTART.RST
===============================================================================

Quick Start Guide
=================

This guide will walk you through creating your first payment with **dj-payfast**.

Prerequisites
-------------

* dj-payfast installed (:doc:`installation`)
* Django project configured
* PayFast credentials set up

Basic Payment Flow
------------------

The typical payment flow with PayFast consists of:

1. **Create Payment**: Store payment details in your database
2. **Generate Form**: Create a PayFast payment form
3. **Redirect to PayFast**: User completes payment on PayFast
4. **Receive Notification**: PayFast sends ITN to your webhook
5. **Process Payment**: Update payment status in your database

Step 1: Create a Payment View
------------------------------

Create a view to handle the checkout process:

.. code-block:: python

   # views.py
   from django.shortcuts import render, redirect
   from django.contrib.auth.decorators import login_required
   from django.urls import reverse
   from payfast.models import PayFastPayment
   from payfast.forms import PayFastPaymentForm
   import uuid

   @login_required
   def checkout_view(request):
       # Create a unique payment ID
       payment_id = str(uuid.uuid4())
       
       # Create payment record
       payment = PayFastPayment.objects.create(
           user=request.user,
           m_payment_id=payment_id,
           amount=299.99,
           item_name='Premium Subscription',
           item_description='1 month access to premium features',
           email_address=request.user.email,
           name_first=request.user.first_name,
           name_last=request.user.last_name,
       )
       
       # Prepare form data
       form_data = {
           'amount': payment.amount,
           'item_name': payment.item_name,
           'item_description': payment.item_description,
           'm_payment_id': payment.m_payment_id,
           'email_address': payment.email_address,
           'name_first': payment.name_first,
           'name_last': payment.name_last,
           'return_url': request.build_absolute_uri(reverse('payment_success')),
           'cancel_url': request.build_absolute_uri(reverse('payment_cancel')),
           'notify_url': request.build_absolute_uri(reverse('payfast:notify')),
       }
       
       # Create PayFast form
       form = PayFastPaymentForm(initial=form_data)
       
       return render(request, 'checkout.html', {
           'form': form,
           'payment': payment,
       })

Step 2: Create the Checkout Template
-------------------------------------

Create ``templates/checkout.html``:

.. code-block:: html

   {% extends 'base.html' %}

   {% block content %}
   <div class="checkout-container">
       <h1>Complete Your Purchase</h1>
       
       <div class="payment-details">
           <h2>Order Summary</h2>
           <p><strong>Item:</strong> {{ payment.item_name }}</p>
           <p><strong>Description:</strong> {{ payment.item_description }}</p>
           <p><strong>Amount:</strong> R{{ payment.amount }}</p>
       </div>

       <form action="{{ form.get_action_url }}" method="post" class="payfast-form">
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

Step 3: Create Success and Cancel Views
----------------------------------------

.. code-block:: python

   # views.py
   from django.shortcuts import render
   from payfast.models import PayFastPayment

   def payment_success_view(request):
       """Handle successful payment return"""
       return render(request, 'payment_success.html')

   def payment_cancel_view(request):
       """Handle cancelled payment"""
       return render(request, 'payment_cancel.html')

Step 4: Configure URLs
-----------------------

.. code-block:: python

   # urls.py
   from django.urls import path
   from . import views

   urlpatterns = [
       path('checkout/', views.checkout_view, name='checkout'),
       path('payment/success/', views.payment_success_view, name='payment_success'),
       path('payment/cancel/', views.payment_cancel_view, name='payment_cancel'),
   ]

Step 5: Test Your Integration
------------------------------

1. **Start your development server**:

   .. code-block:: bash

      python manage.py runserver

2. **Expose your local server** (for webhook testing):

   Use ngrok or a similar service:

   .. code-block:: bash

      ngrok http 8000

3. **Update your notify_url** to use the ngrok URL:

   .. code-block:: python

      notify_url = 'https://your-ngrok-url.ngrok.io/payfast/notify/'

4. **Visit the checkout page** and complete a test payment

5. **Use PayFast sandbox test credentials**:

   * Card Number: 4000 0000 0000 0002
   * CVV: 123
   * Expiry: Any future date

Checking Payment Status
------------------------

View payments in Django admin:

.. code-block:: python

   # Navigate to: http://localhost:8000/admin/payfast/payfastpayment/

Or query programmatically:

.. code-block:: python

   from payfast.models import PayFastPayment

   # Get all completed payments
   completed = PayFastPayment.objects.filter(status='complete')

   # Get user's payments
   user_payments = PayFastPayment.objects.filter(user=request.user)

   # Get specific payment
   payment = PayFastPayment.objects.get(m_payment_id=payment_id)
   if payment.status == 'complete':
       # Grant access to user
       grant_premium_access(payment.user)

Complete Example
----------------

Here's a complete working example combining all the pieces:

.. code-block:: python

   # views.py
   from django.shortcuts import render, redirect, get_object_or_404
   from django.contrib.auth.decorators import login_required
   from django.urls import reverse
   from django.contrib import messages
   from payfast.models import PayFastPayment
   from payfast.forms import PayFastPaymentForm
   import uuid

   @login_required
   def subscribe_view(request):
       """Handle subscription checkout"""
       
       # Create payment
       payment = PayFastPayment.objects.create(
           user=request.user,
           m_payment_id=str(uuid.uuid4()),
           amount=299.99,
           item_name='Premium Monthly Subscription',
           item_description='Access to all premium features for 30 days',
           email_address=request.user.email,
           name_first=request.user.first_name,
           name_last=request.user.last_name,
           custom_str1='subscription',  # Custom field for tracking
           custom_int1=30,  # Days of subscription
       )
       
       # Generate form
       form = PayFastPaymentForm(initial={
           'amount': payment.amount,
           'item_name': payment.item_name,
           'item_description': payment.item_description,
           'm_payment_id': payment.m_payment_id,
           'email_address': payment.email_address,
           'name_first': payment.name_first,
           'name_last': payment.name_last,
           'return_url': request.build_absolute_uri(
               reverse('subscription_success')
           ),
           'cancel_url': request.build_absolute_uri(
               reverse('subscription_cancel')
           ),
           'notify_url': request.build_absolute_uri(
               reverse('payfast:notify')
           ),
           'custom_str1': payment.custom_str1,
           'custom_int1': payment.custom_int1,
       })
       
       return render(request, 'subscribe.html', {
           'form': form,
           'payment': payment,
       })

   def subscription_success_view(request):
       """Show success message"""
       messages.success(request, 'Payment successful! Processing your subscription...')
       return render(request, 'subscription_success.html')

   def subscription_cancel_view(request):
       """Show cancellation message"""
       messages.warning(request, 'Payment was cancelled.')
       return redirect('home')

Next Steps
----------

* :doc:`usage` - Advanced usage patterns
* :doc:`webhooks` - Understanding webhook processing
* :doc:`testing` - Testing your integration
* :doc:`security` - Security best practices


