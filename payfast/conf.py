# ============================================================================
# payfast/conf.py
# ============================================================================

from django.conf import settings

PAYFAST_MERCHANT_ID = getattr(settings, 'PAYFAST_MERCHANT_ID', '')
PAYFAST_MERCHANT_KEY = getattr(settings, 'PAYFAST_MERCHANT_KEY', '')
PAYFAST_PASSPHRASE = getattr(settings, 'PAYFAST_PASSPHRASE', '')
PAYFAST_TEST_MODE = getattr(settings, 'PAYFAST_TEST_MODE', True)

# PayFast URLs
PAYFAST_URL = 'https://sandbox.payfast.co.za/eng/process' if PAYFAST_TEST_MODE else 'https://www.payfast.co.za/eng/process'
PAYFAST_VALIDATE_URL = 'https://sandbox.payfast.co.za/eng/query/validate' if PAYFAST_TEST_MODE else 'https://www.payfast.co.za/eng/query/validate'
