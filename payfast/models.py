
# ============================================================================
# payfast/models.py
# ============================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

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
    
    # PayFast transaction details
    m_payment_id = models.CharField(max_length=100, unique=True, db_index=True, help_text='Unique payment ID from merchant')
    pf_payment_id = models.CharField(max_length=100, blank=True, null=True, help_text='PayFast payment ID')
    
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
    
    def mark_complete(self):
        """Mark payment as complete"""
        self.status = 'complete'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()


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

