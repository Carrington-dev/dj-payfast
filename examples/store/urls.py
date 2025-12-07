from django.urls import path, include
from .views import checkout_view, payment_cancel_view, payment_success_view

urlpatterns = [
    path("checkout_view/", checkout_view, name="checkout"),
    path("payment_success_view/", payment_success_view, name="payment_success"),
    path("payment_cancel_view/", payment_cancel_view, name="payment_cancel"),
]
