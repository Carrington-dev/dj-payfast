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
def checkout_view(request):
    """Handle checkout and create PayFast payment"""
    
    # Create unique payment ID
    payment_id = str(uuid.uuid4())
    
    # Create payment record
    payment = PayFastPayment.objects.create(
        user=request.user,
        m_payment_id=payment_id,
        amount=99.99,  # Your price in ZAR
        item_name='Premium Subscription',
        item_description='1 month premium access',
        email_address="mcrn96m@gmail.com",
        name_first=request.user.first_name,
        name_last=request.user.last_name,
    )
    
    # Build callback URLs
    return_url = request.build_absolute_uri(reverse('payment_success', kwargs={'pk': payment.pk}))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel', kwargs={'pk': payment.pk}))
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
    
    # form = PayFastPaymentForm(initial = initialData )

    # initialData = {
    #     "merchant_id": settings.PAYFAST_MERCHANT_ID,
    #     "merchant_key": settings.PAYFAST_MERCHANT_KEY,
    #     'amount': str(payment.amount),
    #     'item_name': payment.item_name,
    #     'item_description': payment.item_description,
    #     'm_payment_id': str(payment.m_payment_id) or "1234" ,
    #     'email_address': payment.email_address ,
    #     'name_first': payment.name_first or "First Name",
    #     'name_last': payment.name_last or "Last Name",
    #     'return_url': return_url,
    #     'cancel_url': cancel_url,
    #     'notify_url': notify_url,
        
    # }

    pprint.pprint(initialData)



    # signature = generate_signature(initialData, settings.PAYFAST_PASSPHRASE)
    
 
    htmlForm = f'<form action="{ PAYFAST_URL }" method="post">'
    for key in initialData:
        htmlForm += f'<input name="{key}"  type="hidden" value="{initialData[key]}" />'

    htmlForm += f"<button type=\"submit\" class=\"btn btn-pay\" id=\"pay-btn\">\
                <i class=\"bi bi-lock-fill\"></i><span>Pay R{ payment.amount } with PayFast</span> \
                    </button></form>"


    
    return render(request, 'checkout.html', {
        # 'form': form,
        "htmlForm": htmlForm,
        'payment': payment,
    })

def payment_success_view(request, pk):
    """Handle successful payment return"""
    
    payment = get_object_or_404(PayFastPayment, pk=pk)
    payment.status = "complete"
    payment.save()
    
    return render(request, 'payment_success.html')

def payment_cancel_view(request, pk):
    """Handle cancelled payment"""
    
    payment = get_object_or_404(PayFastPayment, pk=pk)
    payment.status = "cancelled"
    payment.save()

    return render(request, 'payment_cancel.html', {
        "payment": payment
    })