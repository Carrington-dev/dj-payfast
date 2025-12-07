from django.urls import path, include
from django.views.generic import TemplateView
from . import views
from payfast.views import PayFastPaymentModelViewSet
from rest_framework.routers import DefaultRouter

# Define app namespace
app_name = 'payfast'

router = DefaultRouter()
router.register("payments", PayFastPaymentModelViewSet, basename="payment")

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

    path("checkout", views.checkout_view, name="checkout"),
    path("payment_success/<int:pk>", views.payment_success_view, name="payment_success"),
    path("payment_cancel/<int:pk>", views.payment_cancel_view, name="payment_cancel"),
    # path("payment_cancel/<int:pk>", payment_cancel_view, name="payment_cancel"),
]

urlpatterns += [
    path("", include(router.urls))
]
