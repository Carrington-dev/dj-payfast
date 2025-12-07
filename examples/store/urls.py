from django.urls import path, include
from .views import checkout_view, payment_cancel_view, payment_success_view

app_name="store"

urlpatterns = [
    path("checkout", checkout_view, name="checkout"),
    path("payment_success/<int:pk>", payment_success_view, name="payment_success"),
    path("payment_cancel/<int:pk>", payment_cancel_view, name="payment_cancel"),
    # path("payment_cancel/<int:pk>", payment_cancel_view, name="payment_cancel"),
]
