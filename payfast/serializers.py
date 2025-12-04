# ============================================================================
# payfast/serializers.py
# ============================================================================

"""
Serializers for dj-payfast

This module provides Django REST Framework serializers for PayFast models,
enabling easy API integration and data validation.

Note: Requires djangorestframework to be installed:
    pip install djangorestframework
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PayFastPayment, PayFastNotification
from .utils import generate_signature
import uuid

User = get_user_model()


# ============================================================================
# Payment Serializers
# ============================================================================

class PayFastPaymentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing PayFast payments (simplified view)
    
    Used for list views where full details are not needed.
    """
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PayFastPayment
        fields = [
            'id',
            'm_payment_id',
            'pf_payment_id',
            'user',
            'user_email',
            'user_name',
            'amount',
            'item_name',
            'status',
            'status_display',
            'created_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'pf_payment_id',
            'created_at',
            'completed_at',
        ]
    
    def get_user_name(self, obj):
        """Get full name of the user"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return f"{obj.name_first} {obj.name_last}".strip()


class PayFastPaymentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed PayFast payment information
    
    Includes all payment fields and related data.
    """
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notifications_count = serializers.IntegerField(
        source='notifications.count',
        read_only=True
    )
    
    class Meta:
        model = PayFastPayment
        fields = '__all__'
        read_only_fields = [
            'id',
            'pf_payment_id',
            'amount_gross',
            'amount_fee',
            'amount_net',
            'payment_status',
            'created_at',
            'updated_at',
            'completed_at',
        ]


class PayFastPaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new PayFast payments
    
    Validates required fields and generates unique payment IDs.
    """
    
    # Optional: auto-generate m_payment_id if not provided
    m_payment_id = serializers.CharField(required=False)
    
    class Meta:
        model = PayFastPayment
        fields = [
            'm_payment_id',
            'user',
            'amount',
            'item_name',
            'item_description',
            'name_first',
            'name_last',
            'email_address',
            'cell_number',
            'custom_str1',
            'custom_str2',
            'custom_str3',
            'custom_str4',
            'custom_str5',
            'custom_int1',
            'custom_int2',
            'custom_int3',
            'custom_int4',
            'custom_int5',
        ]
    
    def validate_amount(self, value):
        """Validate payment amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value
    
    def validate_email_address(self, value):
        """Validate email address format"""
        if not value:
            raise serializers.ValidationError("Email address is required")
        return value.lower()
    
    def create(self, validated_data):
        """Create payment with auto-generated ID if not provided"""
        if 'm_payment_id' not in validated_data or not validated_data['m_payment_id']:
            validated_data['m_payment_id'] = str(uuid.uuid4())
        
        return super().create(validated_data)


class PayFastPaymentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating PayFast payment status
    
    Limited to status updates and custom fields only.
    """
    
    class Meta:
        model = PayFastPayment
        fields = [
            'status',
            'custom_str1',
            'custom_str2',
            'custom_str3',
            'custom_str4',
            'custom_str5',
            'custom_int1',
            'custom_int2',
            'custom_int3',
            'custom_int4',
            'custom_int5',
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        instance = self.instance
        if instance:
            # Don't allow changing from complete to other statuses
            if instance.status == 'complete' and value != 'complete':
                raise serializers.ValidationError(
                    "Cannot change status from complete"
                )
        return value


# ============================================================================
# Notification Serializers
# ============================================================================

class PayFastNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for PayFast ITN notifications
    
    Includes validation status and error details.
    """
    
    payment_id = serializers.CharField(source='payment.m_payment_id', read_only=True)
    
    class Meta:
        model = PayFastNotification
        fields = [
            'id',
            'payment',
            'payment_id',
            'raw_data',
            'is_valid',
            'validation_errors',
            'ip_address',
            'created_at',
        ]
        read_only_fields = '__all__'


class PayFastNotificationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for notification lists
    
    Excludes raw_data for performance.
    """
    
    payment_id = serializers.CharField(source='payment.m_payment_id', read_only=True)
    
    class Meta:
        model = PayFastNotification
        fields = [
            'id',
            'payment',
            'payment_id',
            'is_valid',
            'validation_errors',
            'ip_address',
            'created_at',
        ]
        read_only_fields = '__all__'


# ============================================================================
# Payment Form Data Serializers
# ============================================================================

class PayFastFormDataSerializer(serializers.Serializer):
    """
    Serializer for generating PayFast form data
    
    Generates all required fields including signature for PayFast submission.
    """
    
    # Required fields
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    item_name = serializers.CharField(max_length=255)
    m_payment_id = serializers.CharField(max_length=100)
    email_address = serializers.EmailField()
    notify_url = serializers.URLField()
    
    # Optional fields
    item_description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    name_first = serializers.CharField(max_length=100, required=False, allow_blank=True)
    name_last = serializers.CharField(max_length=100, required=False, allow_blank=True)
    cell_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    return_url = serializers.URLField(required=False, allow_blank=True)
    cancel_url = serializers.URLField(required=False, allow_blank=True)
    
    # Custom fields
    custom_str1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    custom_str2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    custom_str3 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    custom_str4 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    custom_str5 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    custom_int1 = serializers.IntegerField(required=False, allow_null=True)
    custom_int2 = serializers.IntegerField(required=False, allow_null=True)
    custom_int3 = serializers.IntegerField(required=False, allow_null=True)
    custom_int4 = serializers.IntegerField(required=False, allow_null=True)
    custom_int5 = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value
    
    def to_representation(self, instance):
        """Add merchant details and signature to output"""
        from . import conf
        
        data = super().to_representation(instance)
        
        # Add merchant details
        data['merchant_id'] = conf.PAYFAST_MERCHANT_ID
        data['merchant_key'] = conf.PAYFAST_MERCHANT_KEY
        
        # Remove empty values
        data = {k: str(v) for k, v in data.items() if v not in [None, '', 'None']}
        
        # Generate signature
        signature = generate_signature(data)
        data['signature'] = signature
        
        # Add action URL
        data['action_url'] = conf.PAYFAST_URL
        
        return data


# ============================================================================
# Statistics Serializers
# ============================================================================

class PaymentStatisticsSerializer(serializers.Serializer):
    """
    Serializer for payment statistics
    
    Provides summary data for payments.
    """
    
    total_payments = serializers.IntegerField()
    completed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    cancelled_payments = serializers.IntegerField()
    
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_completed_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    total_fees = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


class PaymentTimeSeriesSerializer(serializers.Serializer):
    """
    Serializer for time-series payment data
    
    Used for charts and analytics.
    """
    
    date = serializers.DateField()
    payment_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    completed_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()


# ============================================================================
# Webhook Data Serializers
# ============================================================================

class PayFastWebhookDataSerializer(serializers.Serializer):
    """
    Serializer for validating incoming webhook data from PayFast
    
    Validates all expected fields from PayFast ITN.
    """
    
    # PayFast ITN fields
    m_payment_id = serializers.CharField(required=True)
    pf_payment_id = serializers.CharField(required=True)
    payment_status = serializers.CharField(required=True)
    item_name = serializers.CharField(required=True)
    item_description = serializers.CharField(required=False, allow_blank=True)
    amount_gross = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    amount_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    amount_net = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    
    # Customer details
    name_first = serializers.CharField(required=False, allow_blank=True)
    name_last = serializers.CharField(required=False, allow_blank=True)
    email_address = serializers.EmailField(required=False, allow_blank=True)
    
    # Custom fields
    custom_str1 = serializers.CharField(required=False, allow_blank=True)
    custom_str2 = serializers.CharField(required=False, allow_blank=True)
    custom_str3 = serializers.CharField(required=False, allow_blank=True)
    custom_str4 = serializers.CharField(required=False, allow_blank=True)
    custom_str5 = serializers.CharField(required=False, allow_blank=True)
    custom_int1 = serializers.IntegerField(required=False, allow_null=True)
    custom_int2 = serializers.IntegerField(required=False, allow_null=True)
    custom_int3 = serializers.IntegerField(required=False, allow_null=True)
    custom_int4 = serializers.IntegerField(required=False, allow_null=True)
    custom_int5 = serializers.IntegerField(required=False, allow_null=True)
    
    # Signature
    signature = serializers.CharField(required=True)
    
    def validate_payment_status(self, value):
        """Validate payment status is recognized"""
        valid_statuses = ['COMPLETE', 'FAILED', 'PENDING', 'CANCELLED']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid payment status: {value}"
            )
        return value


# ============================================================================
# Nested Serializers
# ============================================================================

class PayFastPaymentWithNotificationsSerializer(serializers.ModelSerializer):
    """
    Payment serializer with nested notifications
    
    Includes all notification history for a payment.
    """
    
    notifications = PayFastNotificationListSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PayFastPayment
        fields = '__all__'


# ============================================================================
# User-Specific Serializers
# ============================================================================

class UserPaymentHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for user's payment history
    
    Simplified view for customer-facing APIs.
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PayFastPayment
        fields = [
            'id',
            'm_payment_id',
            'amount',
            'item_name',
            'item_description',
            'status',
            'status_display',
            'created_at',
            'completed_at',
        ]
        read_only_fields = '__all__'


# ============================================================================
# Bulk Operations Serializers
# ============================================================================

class BulkPaymentStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk payment status updates
    
    Allows updating multiple payments at once.
    """
    
    payment_ids = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        min_length=1
    )
    status = serializers.ChoiceField(
        choices=PayFastPayment.STATUS_CHOICES,
        required=True
    )
    
    def validate_status(self, value):
        """Only allow certain statuses for bulk updates"""
        allowed_statuses = ['cancelled', 'failed']
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Bulk updates only allowed for: {', '.join(allowed_statuses)}"
            )
        return value


# ============================================================================
# Export Serializers
# ============================================================================

class PayFastPaymentExportSerializer(serializers.ModelSerializer):
    """
    Serializer for exporting payment data
    
    Flattened structure suitable for CSV/Excel export.
    """
    
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PayFastPayment
        fields = [
            'id',
            'm_payment_id',
            'pf_payment_id',
            'user_id',
            'user_email',
            'amount',
            'amount_gross',
            'amount_fee',
            'amount_net',
            'item_name',
            'item_description',
            'name_first',
            'name_last',
            'email_address',
            'cell_number',
            'status',
            'status_display',
            'payment_status',
            'created_at',
            'completed_at',
            'custom_str1',
            'custom_str2',
            'custom_str3',
            'custom_int1',
            'custom_int2',
            'custom_int3',
        ]


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_payment_exists(m_payment_id):
    """
    Helper function to validate payment exists
    
    Args:
        m_payment_id: Merchant payment ID
        
    Returns:
        PayFastPayment instance
        
    Raises:
        serializers.ValidationError if not found
    """
    try:
        return PayFastPayment.objects.get(m_payment_id=m_payment_id)
    except PayFastPayment.DoesNotExist:
        raise serializers.ValidationError(
            f"Payment with ID {m_payment_id} not found"
        )


# ============================================================================