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

from .models import PayFastPayment, PayFastNotification
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
        
        return HttpResponse('OK', status=2