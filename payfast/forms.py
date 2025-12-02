

# ============================================================================
# payfast/forms.py
# ============================================================================

from django import forms
from . import conf
from .utils import generate_signature


class PayFastPaymentForm(forms.Form):
    """Form to generate PayFast payment request"""
    
    # Merchant details
    merchant_id = forms.CharField(widget=forms.HiddenInput(), initial=conf.PAYFAST_MERCHANT_ID)
    merchant_key = forms.CharField(widget=forms.HiddenInput(), initial=conf.PAYFAST_MERCHANT_KEY)
    
    # Transaction details
    amount = forms.DecimalField(widget=forms.HiddenInput(), max_digits=10, decimal_places=2)
    item_name = forms.CharField(widget=forms.HiddenInput(), max_length=255)
    item_description = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    # Unique payment ID
    m_payment_id = forms.CharField(widget=forms.HiddenInput())
    
    # Customer details
    name_first = forms.CharField(widget=forms.HiddenInput(), required=False)
    name_last = forms.CharField(widget=forms.HiddenInput(), required=False)
    email_address = forms.EmailField(widget=forms.HiddenInput())
    cell_number = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    # URLs
    return_url = forms.URLField(widget=forms.HiddenInput(), required=False)
    cancel_url = forms.URLField(widget=forms.HiddenInput(), required=False)
    notify_url = forms.URLField(widget=forms.HiddenInput())
    
    # Custom fields
    custom_str1 = forms.CharField(widget=forms.HiddenInput(), required=False)
    custom_str2 = forms.CharField(widget=forms.HiddenInput(), required=False)
    custom_str3 = forms.CharField(widget=forms.HiddenInput(), required=False)
    custom_str4 = forms.CharField(widget=forms.HiddenInput(), required=False)
    custom_str5 = forms.CharField(widget=forms.HiddenInput(), required=False)
    custom_int1 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    custom_int2 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    custom_int3 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    custom_int4 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    custom_int5 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    # Signature
    signature = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate signature if initial data provided
        if self.initial:
            data = {k: str(v) for k, v in self.initial.items() if v is not None and v != ''}
            signature = generate_signature(data)
            self.fields['signature'].initial = signature
    
    def get_action_url(self):
        """Get PayFast form action URL"""
        return conf.PAYFAST_URL