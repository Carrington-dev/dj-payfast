# ============================================================================
# payfast/apps.py
# ============================================================================

from django.apps import AppConfig


class PayFastConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payfast'
    verbose_name = 'PayFast Payments'

