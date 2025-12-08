# dj-payfast Documentation

## Complete Integration Guide for Django PayFast Payment Gateway

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Quick Start](#quick-start)
7. [Usage Examples](#usage-examples)
8. [API Reference](#api-reference)
9. [Security](#security)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## Introduction

**dj-payfast** is a comprehensive Django library for integrating PayFast, South Africa's leading payment gateway, into your Django applications. It provides a simple, secure, and Pythonic way to accept online payments.

### What is PayFast?

PayFast is South Africa's most trusted payment gateway, allowing businesses to accept payments via:
- Credit/Debit Cards (Visa, Mastercard)
- Instant EFT
- Bitcoin
- SnapScan
- Zapper
- Mobicred

---

## Features

✅ **Easy Integration** - Get started in under 10 minutes  
✅ **Secure** - Built-in signature verification, IP validation, and server-side validation  
✅ **Complete** - Models, forms, views, and webhooks included  
✅ **Test Mode** - Sandbox support for development  
✅ **Admin Interface** - Full Django admin integration  
✅ **Webhooks** - Automatic ITN (Instant Transaction Notification) handling  
✅ **Database Tracking** - Complete payment history and audit trail  
✅ **Customizable** - Support for custom fields and metadata  
✅ **REST API** - Optional DRF integration for API-first applications  

---

## Requirements

- **Python**: 3.8+
- **Django**: 3.2+
- **djangorestframework**: Latest version
- **requests**: 2.25.0+
- **PayFast Account**: Sign up at [payfast.co.za](https://www.payfast.co.za)

---

## Installation

### 1. Install via pip

```bash
pip install dj-payfast
```

### 2. Add to `INSTALLED_APPS`

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',  # Optional, for API support
    'payfast',         # Add this
    
    # Your apps
    'myapp',
]
```

### 3. Configure URLs

```python
# urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payfast/', include('payfast.urls')),  # Add this
    # Your other URLs
]
```

This creates the webhook endpoint at: `/payfast/notify/`

### 4. Run Migrations

```bash
python manage.py migrate
```

---

## Configuration

### Basic Configuration

Add your PayFast credentials to `settings.py`:

```python
# settings.py

# PayFast Configuration
PAYFAST_MERCHANT_ID = '10023192'           # Your merchant ID
PAYFAST_MERCHANT_KEY = 'ecs5ue9vb4i70'     # Your merchant key
PAYFAST_PASSPHRASE = 'jt7NOE43FZPn'        # Your passphrase (recommended)
PAYFAST_TEST_MODE = True                    # False for production
```

### Environment Variables (Recommended)

**Never commit credentials to version control!** Use environment variables:

```python
# settings.py
import os

PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
PAYFAST_TEST_MODE = os.environ.get('PAYFAST_TEST_MODE', 'True') == 'True'
```

Create a `.env` file:

```bash
# .env
PAYFAST_MERCHANT_ID=10023192
PAYFAST_MERCHANT_KEY=ecs5ue9vb4i70
PAYFAST_PASSPHRASE=jt7NOE43FZPn
PAYFAST_TEST_MODE=True
```

### Getting PayFast Credentials

**Sandbox (Testing):**
1. Sign up at [sandbox.payfast.co.za](https://sandbox.payfast.co.za)
2. Navigate to **Settings → Integration**
3. Copy your Merchant ID and Merchant Key
4. Generate a passphrase

**Production:**
1. Sign up at [www.payfast.co.za](https://www.payfast.co.za)
2. Complete merchant verification
3. Navigate to **Settings → Integration**
4. Copy your credentials

---

## Quick Start

### Method 1: Direct Checkout (Your Example)

This is the pattern you showed - redirecting directly to checkout with query parameters:

```python
# views.py
from django.shortcuts import redirect, reverse
from urllib.parse import urlencode
from .models import Product

def call_checkout_view(request):
    """
    Create a cart/order and redirect to PayFast checkout
    """
    # Get or create your product/cart
    cart = Product.objects.create(
        price=89.99,
        name="iPhone XS",
        description="Latest iPhone For sale"
    )
    
    # Build checkout parameters
    params = urlencode({
        'amount': cart.price,
        'item_name': cart.name,
        'item_description': cart.description,
        'custom_str1': f'cart_{cart.id}',  # Store cart reference
        'custom_int1': 1,                   # Quantity or other metadata
    })
    
    # Redirect to dj-payfast checkout view
    url = f"{reverse('payfast:checkout')}?{params}"
    return redirect(url)
```

Add URL pattern:

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('buy/<int:product_id>/', views.call_checkout_view, name='buy_product'),
]
```

### Method 2: Manual Payment Creation

For more control, create the payment record yourself:

```python
# views.py
from django.shortcuts import render, redirect, reverse
from payfast.models import PayFastPayment
import uuid

def checkout_view(request):
    """
    Create payment and show checkout page
    """
    # Create unique payment ID
    payment_id = str(uuid.uuid4())
    
    # Create payment record
    payment = PayFastPayment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        m_payment_id=payment_id,
        amount=99.99,
        item_name='Premium Subscription',
        item_description='1 month premium access',
        email_address=request.user.email if request.user.is_authenticated else 'guest@example.com',
        name_first=request.user.first_name if request.user.is_authenticated else '',
        name_last=request.user.last_name if request.user.is_authenticated else '',
        custom_str1='subscription_premium',
        custom_int1=1,  # Duration in months
    )
    
    # Redirect to payment with payment ID
    return redirect('payfast:checkout', payment_id=payment.m_payment_id)
```

### Method 3: Using the Form Directly

For embedding in your own templates:

```python
# views.py
from django.shortcuts import render
from django.urls import reverse
from payfast.forms import PayFastPaymentForm
from payfast.models import PayFastPayment
import uuid

def custom_checkout_view(request):
    """
    Display custom checkout page with PayFast form
    """
    # Create payment
    payment = PayFastPayment.objects.create(
        user=request.user,
        m_payment_id=str(uuid.uuid4()),
        amount=149.99,
        item_name='Pro Plan',
        email_address=request.user.email,
    )
    
    # Build callback URLs
    return_url = request.build_absolute_uri(reverse('payment_success'))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
    notify_url = request.build_absolute_uri(reverse('payfast:notify'))
    
    # Create form
    form = PayFastPaymentForm(initial={
        'amount': payment.amount,
        'item_name': payment.item_name,
        'm_payment_id': payment.m_payment_id,
        'email_address': payment.email_address,
        'return_url': return_url,
        'cancel_url': cancel_url,
        'notify_url': notify_url,
    })
    
    return render(request, 'myapp/checkout.html', {
        'form': form,
        'payment': payment,
    })
```

Template:

```html
<!-- myapp/checkout.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>Complete Your Payment</h1>
    
    <div class="payment-details">
        <h2>{{ payment.item_name }}</h2>
        <h3>Amount: R{{ payment.amount }}</h3>
    </div>

    <form action="{{ form.get_action_url }}" method="post">
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">
            Pay R{{ payment.amount }} with PayFast
        </button>
    </form>
</div>
{% endblock %}
```

---

## Usage Examples

### Example 1: E-commerce Checkout

```python
# views.py
from django.shortcuts import redirect, reverse
from urllib.parse import urlencode
from .models import Order

def process_order_checkout(request, order_id):
    """
    Process order and redirect to PayFast checkout
    """
    order = Order.objects.get(id=order_id, user=request.user)
    
    # Calculate total
    total = order.calculate_total()
    
    # Build item description
    items = ', '.join([f"{item.quantity}x {item.product.name}" 
                       for item in order.items.all()])
    
    params = urlencode({
        'amount': total,
        'item_name': f'Order #{order.id}',
        'item_description': items,
        'custom_str1': f'order_{order.id}',
        'custom_int1': order.items.count(),
        'email_address': request.user.email,
    })
    
    url = f"{reverse('payfast:checkout')}?{params}"
    return redirect(url)
```

### Example 2: Subscription Payment

```python
# views.py
from django.shortcuts import redirect, reverse
from urllib.parse import urlencode
from .models import Subscription

def subscribe_to_plan(request, plan_id):
    """
    Create subscription and process payment
    """
    plan = get_object_or_404(Plan, id=plan_id)
    
    # Create subscription
    subscription = Subscription.objects.create(
        user=request.user,
        plan=plan,
        status='pending',
    )
    
    params = urlencode({
        'amount': plan.price,
        'item_name': f'{plan.name} Subscription',
        'item_description': f'{plan.duration_months} months of {plan.name}',
        'custom_str1': f'subscription_{subscription.id}',
        'custom_str2': plan.slug,
        'custom_int1': plan.duration_months,
        'email_address': request.user.email,
    })
    
    url = f"{reverse('payfast:checkout')}?{params}"
    return redirect(url)
```

### Example 3: Donation Widget

```python
# views.py
from django.shortcuts import render, redirect, reverse
from urllib.parse import urlencode

def donate_view(request):
    """
    Process donation
    """
    if request.method == 'POST':
        amount = request.POST.get('amount')
        donor_name = request.POST.get('name')
        donor_email = request.POST.get('email')
        message = request.POST.get('message', '')
        
        params = urlencode({
            'amount': amount,
            'item_name': 'Donation',
            'item_description': f'Donation from {donor_name}',
            'custom_str1': 'donation',
            'custom_str2': message[:255],  # Store message
            'email_address': donor_email,
            'name_first': donor_name.split()[0] if donor_name else '',
        })
        
        url = f"{reverse('payfast:checkout')}?{params}"
        return redirect(url)
    
    return render(request, 'donate.html')
```

### Example 4: Event Ticket Purchase

```python
# views.py
from django.shortcuts import redirect, reverse
from urllib.parse import urlencode
from .models import Event, Ticket

def buy_tickets(request, event_id):
    """
    Purchase event tickets
    """
    event = get_object_or_404(Event, id=event_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Create ticket reservation
    ticket = Ticket.objects.create(
        event=event,
        user=request.user,
        quantity=quantity,
        total_price=event.ticket_price * quantity,
        status='reserved',
    )
    
    params = urlencode({
        'amount': ticket.total_price,
        'item_name': f'{event.name} - Tickets',
        'item_description': f'{quantity} ticket(s) for {event.name}',
        'custom_str1': f'ticket_{ticket.id}',
        'custom_str2': event.slug,
        'custom_int1': quantity,
        'email_address': request.user.email,
    })
    
    url = f"{reverse('payfast:checkout')}?{params}"
    return redirect(url)
```

---

## Handling Payment Completion

### Using Django Signals

The recommended way to handle payment completion is using Django signals:

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from payfast.models import PayFastPayment
from django.core.mail import send_mail
from .models import Order, Subscription

@receiver(post_save, sender=PayFastPayment)
def handle_payment_completion(sender, instance, created, **kwargs):
    """
    Handle payment status changes
    """
    if instance.status == 'complete' and instance.payment_status == 'COMPLETE':
        # Extract custom data
        custom_type = instance.custom_str1.split('_')[0] if instance.custom_str1 else None
        custom_id = instance.custom_str1.split('_')[1] if instance.custom_str1 else None
        
        # Handle based on payment type
        if custom_type == 'order':
            handle_order_payment(custom_id, instance)
        elif custom_type == 'subscription':
            handle_subscription_payment(custom_id, instance)
        elif custom_type == 'donation':
            handle_donation(instance)
        elif custom_type == 'ticket':
            handle_ticket_payment(custom_id, instance)

def handle_order_payment(order_id, payment):
    """Process completed order"""
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.payment_reference = payment.pf_payment_id
        order.save()
        
        # Send confirmation email
        send_mail(
            subject='Order Confirmation',
            message=f'Your order #{order.id} has been confirmed!',
            from_email='noreply@example.com',
            recipient_list=[payment.email_address],
        )
        
        # Generate invoice
        # order.generate_invoice()
        
    except Order.DoesNotExist:
        print(f"Order {order_id} not found")

def handle_subscription_payment(subscription_id, payment):
    """Activate subscription"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.status = 'active'
        subscription.activated_at = payment.completed_at
        subscription.save()
        
        # Grant access
        subscription.user.profile.is_premium = True
        subscription.user.profile.save()
        
    except Subscription.DoesNotExist:
        print(f"Subscription {subscription_id} not found")

def handle_donation(payment):
    """Process donation"""
    # Log donation
    # Send thank you email
    send_mail(
        subject='Thank You for Your Donation',
        message=f'Thank you for your generous donation of R{payment.amount}!',
        from_email='noreply@example.com',
        recipient_list=[payment.email_address],
    )
```

Register signals in `apps.py`:

```python
# apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        import myapp.signals  # Register signals
```

---

## Querying Payments

### Get User's Payments

```python
from payfast.models import PayFastPayment

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
```

### Calculate Revenue

```python
from django.db.models import Sum, Count, Avg

# Total revenue
total = PayFastPayment.objects.filter(
    status='complete'
).aggregate(Sum('amount'))['amount__sum']

# Monthly revenue
from django.utils import timezone

now = timezone.now()
month_start = now.replace(day=1, hour=0, minute=0, second=0)

monthly_revenue = PayFastPayment.objects.filter(
    status='complete',
    completed_at__gte=month_start
).aggregate(Sum('amount'))['amount__sum']

# Average transaction value
avg_payment = PayFastPayment.objects.filter(
    status='complete'
).aggregate(Avg('amount'))['amount__avg']
```

### Get Payment by Custom Field

```python
# Find payment by order ID
order_id = "order_123"
payment = PayFastPayment.objects.filter(
    custom_str1=f'order_{order_id}',
    status='complete'
).first()

# Find all donations
donations = PayFastPayment.objects.filter(
    custom_str1__startswith='donation',
    status='complete'
)
```

---

## REST API (Optional)

If you have `djangorestframework` installed, dj-payfast provides API endpoints:

### API Endpoints

```
GET    /payfast/payments/           - List all payments
POST   /payfast/payments/           - Create new payment
GET    /payfast/payments/{id}/      - Get payment details
PATCH  /payfast/payments/{id}/      - Update payment
DELETE /payfast/payments/{id}/      - Delete payment
```

### API Examples

**List Payments:**

```python
import requests

response = requests.get('http://localhost:8000/payfast/payments/')
payments = response.json()
```

**Create Payment:**

```python
import requests

data = {
    'm_payment_id': 'unique-payment-id',
    'amount': '199.99',
    'item_name': 'Premium Plan',
    'email_address': 'user@example.com',
}

response = requests.post('http://localhost:8000/payfast/payments/', json=data)
payment = response.json()
```

---

## Security

### Production Checklist

Before going live:

- [ ] Set `PAYFAST_TEST_MODE = False`
- [ ] Use production credentials
- [ ] Set secure `PAYFAST_PASSPHRASE`
- [ ] Enable HTTPS
- [ ] Configure proper logging
- [ ] Test webhook URL is accessible
- [ ] Set up error monitoring
- [ ] Review security settings

### HTTPS Configuration

```python
# settings.py (production)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## Testing

### Local Development with ngrok

PayFast needs to reach your webhook URL. Use ngrok for local testing:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start ngrok
ngrok http 8000

# Use the ngrok URL in your notify_url
# Example: https://abc123.ngrok.io/payfast/notify/
```

### Test Card Details (Sandbox)

When testing in sandbox mode, use these test card details:

- **Card Number**: 4242 4242 4242 4242
- **Expiry**: Any future date
- **CVV**: Any 3 digits

---

## Troubleshooting

### Common Issues

**1. Webhook not receiving notifications**

- Check that notify_url is publicly accessible
- Use ngrok for local development
- Check PayFast ITN logs in admin: `/admin/payfast/payfastnotification/`

**2. Signature validation failing**

- Verify passphrase matches exactly
- Check that `PAYFAST_TEST_MODE` is set correctly
- Verify merchant credentials

**3. Payment status not updating**

- Check webhook logs in Django admin
- Ensure webhook handler isn't blocked by firewall
- Verify IP validation isn't too strict

---

## FAQ

**Q: Can I use dj-payfast without authentication?**  
A: Yes! The `user` field is optional. You can process guest checkouts.

**Q: How do I store additional data with payments?**  
A: Use the custom fields: `custom_str1-5` and `custom_int1-5`

**Q: Can I customize the checkout page?**  
A: Yes! Either customize the included templates or create your own using `PayFastPaymentForm`

**Q: How do I handle refunds?**  
A: Refunds are processed through the PayFast dashboard, not programmatically

**Q: Is this production-ready?**  
A: Yes! dj-payfast includes all necessary security features and has been used in production

---

## Support

- **GitHub**: [github.com/carrington-dev/dj-payfast](https://github.com/carrington-dev/dj-payfast)
- **Issues**: [GitHub Issues](https://github.com/carrington-dev/dj-payfast/issues)
- **Documentation**: [Full Docs](https://carrington-dev.github.io/dj-payfast/)
- **PayFast Docs**: [developers.payfast.co.za](https://developers.payfast.co.za)

---

## License

MIT License - See LICENSE file for details

---