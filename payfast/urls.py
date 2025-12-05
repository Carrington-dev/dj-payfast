from django.urls import path, include
from django.views.generic import TemplateView
from . import views

# Define app namespace
app_name = 'payfast'

# ============================================================================
# Main URL Patterns
# ============================================================================

urlpatterns = [
    # ========================================================================
    # Webhook Endpoint (ITN - Instant Transaction Notification)
    # ========================================================================
    # This is the primary endpoint that PayFast calls to send payment updates
    # IMPORTANT: This URL must be publicly accessible via HTTPS in production
    # Example: https://yourdomain.com/payfast/notify/
    path(
        'notify/',
        views.PayFastNotifyView.as_view(),
        name='notify'
    ),
    
    # ========================================================================
    # Alternative webhook URL (for backward compatibility)
    # ========================================================================
    path(
        'webhook/',
        views.PayFastNotifyView.as_view(),
        name='webhook'
    ),
    
    # ========================================================================
    # ITN Handler (alias)
    # ========================================================================
    path(
        'itn/',
        views.PayFastNotifyView.as_view(),
        name='itn'
    ),
]
