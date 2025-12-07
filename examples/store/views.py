from django.shortcuts import redirect, reverse
from urllib.parse import urlencode
from .models import Product

def call_checkout_view(request):

    # Create an order with details listed below
    cart = Product(
        price = 89.99,
        name= "iPhone XS",
        description="Latest iPhone For sale"
    )

    cart.save()
    
    params = urlencode({
        'amount': cart.price,
        'item_name': f'{cart.name}',
        'item_description': cart.description,
        'custom_str1': f'cart_{cart.id}',
        'custom_int1': 1,
    })
    
    url = f"{reverse('payfast:checkout')}?{params}"
    return redirect(url)