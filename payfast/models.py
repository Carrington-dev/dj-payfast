
# ============================================================================
# payfast/models.py
# ============================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import reverse
from django.db import transaction


from payfast.utils import generate_pf_id

User = get_user_model()


class PayFastPayment(models.Model):
    """Model to store PayFast payment transactions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Primary fields
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payfast_payments')
    
    # Merchant transaction details
    merchant_id = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text='Merchant ID')

    # PayFast transaction details
    m_payment_id = models.CharField(max_length=100, default=generate_pf_id, help_text='Unique payment ID from merchant')
    pf_payment_id = models.CharField(max_length=100, blank=True, null=True, help_text='PayFast payment ID')
    signature = models.CharField(max_length=100, blank=True, null=True, help_text='PayFast payment sign')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_gross = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_net = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Item details
    item_name = models.CharField(max_length=255)
    item_description = models.TextField(blank=True)
    
    # Customer details
    name_first = models.CharField(max_length=100, blank=True)
    name_last = models.CharField(max_length=100, blank=True)
    email_address = models.EmailField()
    cell_number = models.CharField(max_length=20, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    payment_status = models.CharField(max_length=50, blank=True, help_text='PayFast payment status')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    custom_str1 = models.CharField(max_length=255, blank=True)
    custom_str2 = models.CharField(max_length=255, blank=True)
    custom_str3 = models.CharField(max_length=255, blank=True)
    custom_str4 = models.CharField(max_length=255, blank=True)
    custom_str5 = models.CharField(max_length=255, blank=True)
    custom_int1 = models.IntegerField(null=True, blank=True)
    custom_int2 = models.IntegerField(null=True, blank=True)
    custom_int3 = models.IntegerField(null=True, blank=True)
    custom_int4 = models.IntegerField(null=True, blank=True)
    custom_int5 = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PayFast Payment'
        verbose_name_plural = 'PayFast Payments'
    
    def __str__(self):
        return f'Payment {self.m_payment_id} - {self.status}'
    
    
    @transaction.atomic
    def mark_complete(self):
        """Mark payment as complete"""
        self.status = 'complete'
        self.completed_at = timezone.now()
        self.save()
    
    @transaction.atomic
    def mark_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()

    def get_payfast_url(self):
        return reverse("payfast:payfast_payment_view", kwargs={"pk": self.pk})

    def get_absolute_url(self):
        return reverse("payfast:payfast_payment_view", kwargs={"pk": self.pk})
    

    
    


class PayFastNotification(models.Model):
    """Model to log all PayFast ITN notifications"""
    
    payment = models.ForeignKey(PayFastPayment, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    
    # Raw notification data
    raw_data = models.JSONField(default=dict)
    
    # Validation
    is_valid = models.BooleanField(default=False)
    validation_errors = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PayFast Notification'
        verbose_name_plural = 'PayFast Notifications'
    
    def __str__(self):
        return f'Notification {self.id} - {"Valid" if self.is_valid else "Invalid"}'

