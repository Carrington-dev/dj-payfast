# ============================================================================
# payfast/views.py
# ============================================================================

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View
from django.utils.decorators import method_decorator
import requests
import json

from rest_framework.viewsets import ModelViewSet
from .models import PayFastPayment, PayFastNotification
from .serializers import PayFastPaymentCreateSerializer
from .utils import verify_signature, validate_ip
from . import conf



def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from payfast.models import PayFastPayment
from payfast.forms import PayFastPaymentForm
from payfast.serializers import PayFastPaymentDetailSerializer
from payfast.utils import generate_signature
from payfast.conf import PAYFAST_URL
from .utils import generateSignature
import uuid
import pprint
from django.conf import settings

@login_required
def checkout_view(request, ):
    """Handle checkout and create PayFast payment"""
    
    # Create unique payment ID
    amount = request.GET.get("amount", 9.99)
    item_name = request.GET.get("item_name", 'Premium Subscription')
    item_description = request.GET.get("item_description", '1 month premium access')
    email_address = request.GET.get("email_address", "mcrn96m@gmail.com")
    name_first = request.GET.get("name_first", "John")
    name_last = request.GET.get("name_last", "Doe")

    payment_id = str(uuid.uuid4())
    
    # Create payment record
    payment = PayFastPayment.objects.create(
        user=request.user,
        m_payment_id=payment_id,
        amount=amount,  # Your price in ZAR
        item_name=item_name,
        item_description=item_description,
        email_address=email_address,
        name_first=request.user.first_name or name_first,
        name_last=request.user.last_name or name_last,
    )
    
    # Build callback URLs
    return_url = request.build_absolute_uri(reverse('payfast:payment_success', kwargs={'pk': payment.pk}))
    cancel_url = request.build_absolute_uri(reverse('payfast:payment_cancel', kwargs={'pk': payment.pk}))
    notify_url = request.build_absolute_uri(reverse('payfast:notify', ))



    data =  (PayFastPaymentDetailSerializer(payment ).data)

   
    # Create PayFast form
   

    initialData = {
        # Merchant details
        "merchant_id": settings.PAYFAST_MERCHANT_ID,
        "merchant_key": settings.PAYFAST_MERCHANT_KEY,
        'return_url': return_url,
        'cancel_url': cancel_url,
        'notify_url': notify_url,
        # Buyer details
        'name_first': data['name_first'] or "John",
        'name_last': data['name_last'] or "Doe",
        'email_address': data.get('email_address', 'test@test.com'),
        # Transaction details
        'm_payment_id': data["m_payment_id"], #Unique payment ID to pass through to notify_url
        'amount': data["amount"],
        'item_name': f'Order#{payment_id[:22]}',
    }

    signature = generateSignature(initialData, settings.PAYFAST_PASSPHRASE)
    initialData['signature'] = signature
    

    # signature = generate_signature(initialData, settings.PAYFAST_PASSPHRASE)
    
 
    htmlForm = f'<form action="{ PAYFAST_URL }" method="post">'
    for key in initialData:
        htmlForm += f'<input name="{key}"  type="hidden" value="{initialData[key]}" />'

    htmlForm += f"<button type=\"submit\" class=\"btn btn-pay\" id=\"pay-btn\">\
                <i class=\"bi bi-lock-fill\"></i><span>Pay R{ payment.amount } with PayFast</span> \
                    </button></form>"


    
    return render(request, 'payfast/checkout.html', {
        # 'form': form,
        "htmlForm": htmlForm,
        'payment': payment,
    })

def payment_success_view(request, pk):
    """Handle successful payment return"""
    
    payment = get_object_or_404(PayFastPayment, pk=pk)
    payment.status = "complete"
    payment.save()
    
    return render(request, 'payfast/payment_success.html')

def payment_cancel_view(request, pk):
    """Handle cancelled payment"""
    
    payment = get_object_or_404(PayFastPayment, pk=pk)
    payment.status = "cancelled"
    payment.save()

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
        if not verify_signature(post_data):
            notification.is_valid = False
            notification.validation_errors = 'Invalid signature'
            notification.save()
            return HttpResponseBadRequest('Invalid signature')
        
        # Validate with PayFast server
        if not self.validate_with_payfast(post_data):
            notification.is_valid = False
            notification.validation_errors = 'Server validation failed'
            notification.save()
            return HttpResponseBadRequest('Validation failed')
        
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
    serializer_class = PayFastPaymentCreateSerializer
    queryset = PayFastPayment.objects.all()