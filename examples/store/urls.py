from store import views
from django.urls import path

urlpatterns = [
    path("checkout", views.call_checkout_view, name="call_checkout_view")
]
