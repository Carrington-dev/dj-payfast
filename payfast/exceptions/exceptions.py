# ============================================================================
# payfast/exceptions.py
# ============================================================================

"""
Custom exceptions for dj-payfast

This module defines all custom exceptions used throughout the dj-payfast library.
These exceptions provide more granular error handling for PayFast integration.
"""


class PayFastError(Exception):
    """
    Base exception for all PayFast-related errors.
    
    All custom exceptions in dj-payfast inherit from this base class,
    making it easy to catch all PayFast-specific errors with a single except clause.
    
    Example:
        try:
            process_payment()
        except PayFastError as e:
            logger.error(f"PayFast error occurred: {e}")
    """
    pass


class PayFastConfigurationError(PayFastError):
    """
    Raised when PayFast configuration is invalid or missing.
    
    This exception is raised when required settings (PAYFAST_MERCHANT_ID,
    PAYFAST_MERCHANT_KEY, etc.) are missing or invalid.
    
    Example:
        if not PAYFAST_MERCHANT_ID:
            raise PayFastConfigurationError("PAYFAST_MERCHANT_ID is not configured")
    """
    pass


class SignatureVerificationError(PayFastError):
    """
    Raised when PayFast signature verification fails.
    
    This exception indicates that the signature provided by PayFast
    does not match the calculated signature, suggesting the request
    may have been tampered with or is not authentic.
    
    Example:
        if not verify_signature(data):
            raise SignatureVerificationError("Invalid signature in webhook data")
    """
    pass


class PayFastValidationError(PayFastError):
    """
    Raised when PayFast server validation fails.
    
    This exception is raised when validation with PayFast servers
    fails, indicating the notification may not be authentic.
    
    Example:
        if not validate_with_payfast(data):
            raise PayFastValidationError("Server validation failed")
    """
    pass


class IPValidationError(PayFastError):
    """
    Raised when the request IP address is not from PayFast servers.
    
    This exception is raised when a webhook request comes from an
    IP address that is not recognized as belonging to PayFast.
    
    Example:
        if not validate_ip(ip_address):
            raise IPValidationError(f"Request from invalid IP: {ip_address}")
    """
    pass


class PaymentNotFoundError(PayFastError):
    """
    Raised when a payment record cannot be found.
    
    This exception is raised when attempting to retrieve a payment
    by its merchant payment ID or PayFast payment ID, but the
    record does not exist in the database.
    
    Example:
        try:
            payment = PayFastPayment.objects.get(m_payment_id=payment_id)
        except PayFastPayment.DoesNotExist:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")
    """
    pass


class DuplicatePaymentError(PayFastError):
    """
    Raised when attempting to create a duplicate payment.
    
    This exception is raised when trying to create a payment with
    a merchant payment ID that already exists in the database.
    
    Example:
        if PayFastPayment.objects.filter(m_payment_id=payment_id).exists():
            raise DuplicatePaymentError(f"Payment {payment_id} already exists")
    """
    pass


class InvalidPaymentStatusError(PayFastError):
    """
    Raised when a payment status is invalid or unexpected.
    
    This exception is raised when a payment has an invalid status
    or when attempting an operation that is not allowed for the
    current payment status.
    
    Example:
        if payment.status not in ['pending', 'complete']:
            raise InvalidPaymentStatusError(f"Invalid status: {payment.status}")
    """
    pass


class WebhookProcessingError(PayFastError):
    """
    Raised when webhook processing fails.
    
    This exception is raised when an error occurs during the
    processing of a PayFast webhook notification.
    
    Example:
        try:
            process_webhook(request)
        except Exception as e:
            raise WebhookProcessingError(f"Failed to process webhook: {e}")
    """
    pass


class InvalidAmountError(PayFastError):
    """
    Raised when a payment amount is invalid.
    
    This exception is raised when a payment amount is negative,
    zero, or otherwise invalid.
    
    Example:
        if amount <= 0:
            raise InvalidAmountError(f"Invalid amount: {amount}")
    """
    pass


class MissingFieldError(PayFastError):
    """
    Raised when a required field is missing.
    
    This exception is raised when required payment data is missing,
    such as email_address, item_name, or amount.
    
    Example:
        if not email_address:
            raise MissingFieldError("email_address is required")
    """
    pass


class PayFastAPIError(PayFastError):
    """
    Raised when communication with PayFast API fails.
    
    This exception is raised when there is an error communicating
    with PayFast servers, such as network errors or API errors.
    
    Example:
        try:
            response = requests.post(PAYFAST_URL, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            raise PayFastAPIError(f"API request failed: {e}")
    """
    pass


class PaymentAlreadyProcessedError(PayFastError):
    """
    Raised when attempting to process a payment that has already been processed.
    
    This exception is raised when trying to mark a payment as complete
    or failed when it has already been processed.
    
    Example:
        if payment.status == 'complete':
            raise PaymentAlreadyProcessedError("Payment already marked as complete")
    """
    pass


class InvalidCallbackURLError(PayFastError):
    """
    Raised when a callback URL is invalid or malformed.
    
    This exception is raised when return_url, cancel_url, or notify_url
    is not a valid URL format.
    
    Example:
        from urllib.parse import urlparse
        if not urlparse(notify_url).scheme:
            raise InvalidCallbackURLError("notify_url must be a valid URL")
    """
    pass


class TestModeError(PayFastError):
    """
    Raised when test mode configuration is incorrect.
    
    This exception is raised when attempting production operations
    in test mode or vice versa.
    
    Example:
        if PAYFAST_TEST_MODE and not use_sandbox_credentials:
            raise TestModeError("Must use sandbox credentials in test mode")
    """
    pass


# ============================================================================
# Helper Functions
# ============================================================================

def raise_configuration_error_if_not_set(*settings):
    """
    Helper function to check if required settings are configured.
    
    Args:
        *settings: Variable number of setting names to check
        
    Raises:
        PayFastConfigurationError: If any setting is not configured
        
    Example:
        raise_configuration_error_if_not_set(
            'PAYFAST_MERCHANT_ID',
            'PAYFAST_MERCHANT_KEY'
        )
    """
    from . import conf
    
    for setting_name in settings:
        setting_value = getattr(conf, setting_name, None)
        if not setting_value:
            raise PayFastConfigurationError(
                f"{setting_name} is not configured. "
                f"Please set it in your Django settings."
            )


def raise_if_invalid_amount(amount):
    """
    Helper function to validate payment amount.
    
    Args:
        amount: The payment amount to validate
        
    Raises:
        InvalidAmountError: If amount is invalid
        
    Example:
        raise_if_invalid_amount(payment.amount)
    """
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise InvalidAmountError(
                f"Amount must be greater than zero, got: {amount}"
            )
    except (TypeError, ValueError) as e:
        raise InvalidAmountError(
            f"Invalid amount format: {amount} - {str(e)}"
        )


def raise_if_missing_field(data, field_name):
    """
    Helper function to check if required field is present.
    
    Args:
        data: Dictionary containing the data
        field_name: Name of the required field
        
    Raises:
        MissingFieldError: If field is missing or empty
        
    Example:
        raise_if_missing_field(payment_data, 'email_address')
    """
    if field_name not in data or not data[field_name]:
        raise MissingFieldError(
            f"Required field '{field_name}' is missing or empty"
        )


# ============================================================================
# Context Managers
# ============================================================================

class handle_payfast_errors:
    """
    Context manager for handling PayFast errors gracefully.
    
    This context manager catches PayFast exceptions and handles them
    appropriately, logging errors and optionally re-raising them.
    
    Example:
        with handle_payfast_errors(logger=logger):
            process_payment(data)
    """
    
    def __init__(self, logger=None, raise_on_error=False):
        """
        Initialize the context manager.
        
        Args:
            logger: Optional logger for error logging
            raise_on_error: Whether to re-raise exceptions after logging
        """
        self.logger = logger
        self.raise_on_error = raise_on_error
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True
        
        if issubclass(exc_type, PayFastError):
            if self.logger:
                self.logger.error(
                    f"PayFast error occurred: {exc_type.__name__}: {exc_val}"
                )
            
            if not self.raise_on_error:
                return True  # Suppress the exception
        
        return False  # Let other exceptions propagate


# ============================================================================
# Decorators
# ============================================================================

def require_payfast_configuration(func):
    """
    Decorator to ensure PayFast is properly configured before executing function.
    
    Example:
        @require_payfast_configuration
        def create_payment(data):
            # Payment creation logic
            pass
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        raise_configuration_error_if_not_set(
            'PAYFAST_MERCHANT_ID',
            'PAYFAST_MERCHANT_KEY'
        )
        return func(*args, **kwargs)
    
    return wrapper


# ============================================================================