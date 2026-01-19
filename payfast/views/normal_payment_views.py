from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.conf import settings


from rest_framework.viewsets import ModelViewSet


# Create your views here.
from payfast.conf import PAYFAST_URL
from payfast.pagination import PayfastPagination
from payfast.models import PayFastPayment, PayFastNotification
from payfast.serializers import PayFastPaymentCreateSerializer, PayFastPaymentListSerializer, PayFastPaymentUpdateSerializer, PayFastPaymentDetailSerializer
from payfast.utils import generate_signature, validate_ip, generate_pf_id


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def checkout_view(request):
    """
    Handle checkout and create PayFast payment.
    
    This view now:
    1. Checks if a pending payment already exists in the session
    2. Only creates a new payment if necessary
    3. Prevents duplicate payments on page refresh
    """
    
    # Get payment parameters from query string
    amount = request.GET.get("amount", 9.99)
    item_name = request.GET.get("item_name", 'Premium Subscription')
    item_description = request.GET.get("item_description", '1 month premium access')
    email_address = request.GET.get("email_address", request.user.email)
    name_first = request.GET.get("name_first", request.user.first_name or "John")
    name_last = request.GET.get("name_last", request.user.last_name or "Doe")
    
    # Custom fields (optional)
    custom_str1 = request.GET.get("custom_str1", "")
    custom_int1 = request.GET.get("custom_int1", None)
    
    # Check if there's already a pending payment in the session
    session_payment_id = request.session.get('pending_payment_id')
    payment = None
    
    if session_payment_id:
        try:
            # Try to get the existing payment
            payment = PayFastPayment.objects.get(
                m_payment_id=session_payment_id,
                user=request.user,
                status='pending'
            )
            print(f"✓ Using existing payment: {payment.m_payment_id}")
        except PayFastPayment.DoesNotExist:
            # Payment doesn't exist or is no longer pending
            payment = None
            del request.session['pending_payment_id']
    
    # Create new payment only if we don't have a pending one
    if payment is None:
        payment_id = generate_pf_id()
        
        payment = PayFastPayment.objects.create(
            user=request.user,
            m_payment_id=payment_id,
            amount=float(amount),
            item_name=item_name,
            item_description=item_description,
            email_address=email_address,
            name_first=name_first,
            name_last=name_last,
            custom_str1=custom_str1,
            custom_int1=int(custom_int1) if custom_int1 else None,
        )
        
        # Store payment ID in session
        request.session['pending_payment_id'] = payment.m_payment_id
        print(f"✓ Created new payment: {payment.m_payment_id}")
    
    # Build callback URLs
    return_url = request.build_absolute_uri(
        reverse('payfast:payment_success', kwargs={'pk': payment.pk})
    )
    cancel_url = request.build_absolute_uri(
        reverse('payfast:payment_cancel', kwargs={'pk': payment.pk})
    )
    notify_url = request.build_absolute_uri(reverse('payfast:notify'))
    
    # Build PayFast form data
    initial_data = {
        # Merchant details
        "merchant_id": settings.PAYFAST_MERCHANT_ID,
        "merchant_key": settings.PAYFAST_MERCHANT_KEY,
        
        # Callback URLs
        'return_url': return_url,
        'cancel_url': cancel_url,
        'notify_url': notify_url,
        
        # Buyer details
        'name_first': payment.name_first or "John",
        'name_last': payment.name_last or "Doe",
        'email_address': payment.email_address,
        
        # Transaction details
        'payment_id': payment.id,
        'm_payment_id': payment.m_payment_id,
        'amount': str(payment.amount),
        'item_name': payment.item_name,
        'item_description': payment.item_description,
    }
    
    # Add custom fields if present
    if payment.custom_str1:
        initial_data['custom_str1'] = payment.custom_str1
    if payment.custom_int1:
        initial_data['custom_int1'] = str(payment.custom_int1)
    
    # Generate signature
    signature = generate_signature(initial_data, settings.PAYFAST_PASSPHRASE)
    initial_data['signature'] = signature
    
    # Generate HTML form
    html_form = f'<form action="{PAYFAST_URL}" method="post">'
    for key, value in initial_data.items():
        html_form += f'<input name="{key}" type="hidden" value="{value}" />'
    
    html_form += f'''
        <button type="submit" class="btn btn-pay" id="pay-btn">
            <i class="bi bi-lock-fill"></i>
            <span>Pay R{payment.amount} with PayFast</span>
        </button>
    </form>'''
    
    return render(request, 'payfast/checkout.html', {
        'htmlForm': html_form,
        'payment': payment,
    })


@login_required
def payfast_payment_view(request, pk):
    """
    Handle checkout for an existing payment record.
    
    This view is used when redirecting back to complete an existing payment.
    """
    payment = get_object_or_404(PayFastPayment, pk=pk)
    
    # If payment is already complete, redirect to success page
    if payment.status == "complete":
        return redirect('payfast:payment_success', pk=payment.pk)
    
    # If payment is failed or cancelled, show that status
    if payment.status in ["failed", "cancelled"]:
        return redirect('payfast:payment_cancel', pk=payment.pk)
    
    # Build callback URLs
    return_url = request.build_absolute_uri(
        reverse('payfast:payment_success', kwargs={'pk': payment.pk})
    )
    cancel_url = request.build_absolute_uri(
        reverse('payfast:payment_cancel', kwargs={'pk': payment.pk})
    )
    notify_url = request.build_absolute_uri(reverse('payfast:notify'))
    
    # Build PayFast form data
    initial_data = {
        # Merchant details
        "merchant_id": settings.PAYFAST_MERCHANT_ID,
        "merchant_key": settings.PAYFAST_MERCHANT_KEY,
        
        # Callback URLs
        'return_url': return_url,
        'cancel_url': cancel_url,
        'notify_url': notify_url,
        
        # Buyer details
        'name_first': payment.name_first or "John",
        'name_last': payment.name_last or "Doe",
        'email_address': payment.email_address,
        
        # Transaction details
        'm_payment_id': payment.m_payment_id,
        'amount': str(payment.amount),
        'item_name': payment.item_name,
        'item_description': payment.item_description,
    }
    
    # Add custom fields if present
    if payment.custom_str1:
        initial_data['custom_str1'] = payment.custom_str1
    if payment.custom_int1:
        initial_data['custom_int1'] = str(payment.custom_int1)
    
    # Generate signature
    signature = generate_signature(initial_data, settings.PAYFAST_PASSPHRASE)
    initial_data['signature'] = signature
    
    # Generate HTML form
    html_form = f'<form action="{PAYFAST_URL}" method="post">'
    for key, value in initial_data.items():
        html_form += f'<input name="{key}" type="hidden" value="{value}" />'
    
    html_form += f'''
        <button type="submit" class="btn btn-pay" id="pay-btn">
            <i class="bi bi-lock-fill"></i>
            <span>Pay R{payment.amount} with PayFast</span>
        </button>
    </form>'''
    
    return render(request, 'payfast/checkout.html', {
        'htmlForm': html_form,
        'payment': payment,
    })


def payment_success_view(request, pk):
    """Handle successful payment return"""
    payment = get_object_or_404(PayFastPayment, pk=pk)
    
    # Mark payment as complete
    if payment.status == 'pending':
        payment.mark_complete()
        payment.save()
    
    # Clear the session payment ID
    if 'pending_payment_id' in request.session:
        del request.session['pending_payment_id']
    
    return render(request, 'payfast/payment_success.html', {
        'payment': payment
    })


def payment_cancel_view(request, pk):
    """Handle cancelled payment"""
    payment = get_object_or_404(PayFastPayment, pk=pk)
    
    # Mark payment as cancelled
    if payment.status == 'pending':
        payment.status = 'cancelled'
        payment.save()
    
    # Clear the session payment ID
    if 'pending_payment_id' in request.session:
        del request.session['pending_payment_id']
    
    return render(request, 'payfast/payment_cancel.html', {
        "payment": payment
    })

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class PayFastNotifyView(View):
    """
    Handle PayFast ITN (Instant Transaction Notification) callbacks
    
    This view processes payment notifications from PayFast
    """
    
    def post(self, request, *args, **kwargs):
        # Get POST data
        post_data = request.POST.dict()
        print(post_data)
        # Get IP address
        ip_address = get_client_ip(request)
        
        # Initialize notification record
        notification = PayFastNotification(
            raw_data=post_data,
            ip_address=ip_address
        )
        
        # Validate IP address
        if not validate_ip(ip_address):
            notification.is_valid = False
            notification.validation_errors = 'Invalid IP address'
            notification.save()
            return HttpResponseBadRequest('Invalid IP')
        
        # Verify signature
        # if not verify_signature(post_data, conf.PAYFAST_PASSPHRASE):
        #     notification.is_valid = False
        #     notification.validation_errors = 'Invalid signature'
        #     notification.save()
        #     return HttpResponseBadRequest('Invalid signature')
        
        # Validate with PayFast server
        # if not self.validate_with_payfast(post_data):
        #     notification.is_valid = False
        #     notification.validation_errors = 'Server validation failed'
        #     notification.save()
        #     return HttpResponseBadRequest('Validation failed')
        
        # Get payment record
        m_payment_id = post_data.get('m_payment_id')
        try:
            payment = PayFastPayment.objects.get(m_payment_id=m_payment_id)
            notification.payment = payment
        except PayFastPayment.DoesNotExist:
            notification.is_valid = False
            notification.validation_errors = 'Payment not found'
            notification.save()
            return HttpResponseBadRequest('Payment not found')
        
        # Mark notification as valid
        notification.is_valid = True
        notification.save()
        
        # Update payment record
        payment.pf_payment_id = post_data.get('pf_payment_id')
        payment.payment_status = post_data.get('payment_status')
        payment.amount_gross = post_data.get('amount_gross')
        payment.amount_fee = post_data.get('amount_fee')
        payment.amount_net = post_data.get('amount_net')
        
        # Update status based on payment_status
        if post_data.get('payment_status') == 'COMPLETE':
            payment.mark_complete()
        else:
            payment.mark_failed()
        
        return HttpResponse('OK', status=200)


class PayFastPaymentModelViewSet(ModelViewSet):
    model = PayFastPayment
    queryset = PayFastPayment.objects.all()
    serializer_class = PayFastPaymentCreateSerializer
    pagination_class  = PayfastPagination

    serializer_classes = {
        "create": PayFastPaymentCreateSerializer,
        "list": PayFastPaymentListSerializer,
        "retrieve": PayFastPaymentDetailSerializer,
        "update": PayFastPaymentUpdateSerializer,
        "partial_update": PayFastPaymentUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, PayFastPaymentCreateSerializer)