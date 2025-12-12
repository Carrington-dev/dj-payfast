# ============================================================================
# payfast/admin.py
# ============================================================================

from django.contrib import admin
from .models import PayFastPayment, PayFastNotification

admin.site.site_header = "PayFast"
admin.site.site_title = "PayFast Portal"
admin.site.index_title = "Welcome to PayFast Payment Portal"


@admin.register(PayFastPayment)
class PayFastPaymentAdmin(admin.ModelAdmin):
    """Admin configuration for PayFastPayment model"""
    
    list_display = [
        'm_payment_id',
        'user',
        'amount',
        'status',
        'email_address',
        'created_at',
        'completed_at',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'completed_at',
    ]
    
    search_fields = [
        'm_payment_id',
        'pf_payment_id',
        'email_address',
        'item_name',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'completed_at',
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'm_payment_id',
                'pf_payment_id',
                'user',
                'status',
                'payment_status',
            )
        }),
        ('Amount Details', {
            'fields': (
                'amount',
                'amount_gross',
                'amount_fee',
                'amount_net',
            )
        }),
        ('Item Details', {
            'fields': (
                'item_name',
                'item_description',
            )
        }),
        ('Customer Details', {
            'fields': (
                'name_first',
                'name_last',
                'email_address',
                'cell_number',
            )
        }),
        ('Custom Fields', {
            'classes': ('collapse',),
            'fields': (
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
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
            )
        }),
    )


@admin.register(PayFastNotification)
class PayFastNotificationAdmin(admin.ModelAdmin):
    """Admin configuration for PayFastNotification model"""
    
    list_display = [
        'id',
        'payment',
        'is_valid',
        'ip_address',
        'created_at',
    ]
    
    list_filter = [
        'is_valid',
        'created_at',
    ]
    
    search_fields = [
        'payment__m_payment_id',
        'ip_address',
    ]
    
    readonly_fields = [
        'payment',
        'raw_data',
        'is_valid',
        'validation_errors',
        'ip_address',
        'created_at',
    ]
    
    fieldsets = (
        ('Notification Details', {
            'fields': (
                'payment',
                'is_valid',
                'validation_errors',
                'ip_address',
                'created_at',
            )
        }),
        ('Raw Data', {
            'fields': (
                'raw_data',
            )
        }),
    )