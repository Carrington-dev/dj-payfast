# Security Best Practices

This document outlines security best practices for using dj-payfast in your Django application.

## Table of Contents

- [Overview](#overview)
- [Signature Security](#signature-security)
- [Passphrase Configuration](#passphrase-configuration)
- [IP Address Validation](#ip-address-validation)
- [HTTPS Requirements](#https-requirements)
- [Webhook Security](#webhook-security)
- [Configuration Security](#configuration-security)
- [Database Security](#database-security)
- [Testing Security](#testing-security)
- [Production Checklist](#production-checklist)
- [Common Security Issues](#common-security-issues)

## Overview

dj-payfast implements multiple layers of security to protect your payment transactions:

1. **Signature Verification** - Cryptographic verification of all payment data
2. **IP Validation** - Ensures requests come from PayFast servers
3. **Server-Side Validation** - Double-checks with PayFast servers
4. **HTTPS Enforcement** - Encrypted communication (production requirement)
5. **Secure Credential Storage** - Environment-based configuration

## Signature Security

### What is a Signature?

A signature is an MD5 hash generated from your payment data combined with your passphrase. It ensures that:

- Payment data hasn't been tampered with
- The request genuinely comes from PayFast
- The merchant credentials are valid

### How Signatures Work

```python
from payfast.utils import generate_signature

# Payment data
data = {
    'merchant_id': '10000100',
    'merchant_key': '46f0cd694581a',
    'amount': '199.99',
    'item_name': 'Premium Plan',
}

# Generate signature
signature = generate_signature(data, passphrase='your_passphrase')
```

The signature is calculated as:

```
MD5(sorted_param_string + '&passphrase=your_passphrase')
```

### Signature Verification Process

dj-payfast automatically verifies signatures in webhooks:

```python
from payfast.utils import verify_signature

# Incoming webhook data
webhook_data = request.POST.dict()

# Verify signature
if verify_signature(webhook_data):
    # Signature is valid - process payment
    process_payment(webhook_data)
else:
    # Invalid signature - reject request
    log_security_alert()
    return HttpResponseBadRequest('Invalid signature')
```

### Signature Best Practices

1. **Always Use a Passphrase**
   ```python
   # settings.py
   PAYFAST_PASSPHRASE = 'your_very_secure_random_passphrase'
   ```

2. **Never Disable Signature Verification**
   ```python
   # ❌ NEVER DO THIS
   if not PAYFAST_TEST_MODE:  # Don't skip verification in any mode
       verify_signature(data)
   
   # ✅ ALWAYS VERIFY
   if not verify_signature(data):
       raise SignatureVerificationError()
   ```

3. **Log Failed Verifications**
   ```python
   if not verify_signature(data):
       logger.critical(f"Signature verification failed from IP {ip_address}")
       # Send alert to security team
       send_security_alert(data)
   ```

## Passphrase Configuration

### What is a Passphrase?

A passphrase is a secret string that adds an extra layer of security to your PayFast integration. It's used in signature generation and should be:

- Long (at least 16 characters)
- Random and unpredictable
- Different for sandbox and production
- Kept absolutely secret

### Generating a Secure Passphrase

**Using Python:**

```python
import secrets

# Generate a secure random passphrase
passphrase = secrets.token_urlsafe(32)
print(passphrase)
# Example output: '8kJh3nM9pQw2xYzA5tLr7sVb1cDf4gHj6kNm8pQw2xYz'
```

**Using OpenSSL:**

```bash
openssl rand -base64 32
```

**Using Django:**

```python
from django.utils.crypto import get_random_string

passphrase = get_random_string(length=32)
```

### Configuring Your Passphrase

**In PayFast Dashboard:**

1. Log in to your PayFast account (sandbox or production)
2. Navigate to **Settings → Integration**
3. Find the **Security Passphrase** section
4. Enter your generated passphrase
5. Save the settings

**In Django Settings:**

```python
# settings.py
import os

# Never hardcode - use environment variables
PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
```

**In Environment Variables:**

```bash
# .env
PAYFAST_PASSPHRASE=your_secure_passphrase_here
```

### Passphrase Rotation

Periodically rotate your passphrase for enhanced security:

```python
# 1. Generate new passphrase
new_passphrase = secrets.token_urlsafe(32)

# 2. Update in PayFast dashboard first
# 3. Update environment variable
# 4. Deploy changes
# 5. Monitor for any issues

# Keep old passphrase for 24-48 hours in case of delayed webhooks
OLD_PAYFAST_PASSPHRASE = os.environ.get('OLD_PAYFAST_PASSPHRASE')

def verify_signature_with_fallback(data):
    """Verify with new passphrase, fallback to old"""
    if verify_signature(data, PAYFAST_PASSPHRASE):
        return True
    if OLD_PAYFAST_PASSPHRASE:
        return verify_signature(data, OLD_PAYFAST_PASSPHRASE)
    return False
```

## IP Address Validation

### Why Validate IP Addresses?

IP validation ensures that webhook requests actually come from PayFast servers, not from attackers trying to forge payment confirmations.

### Valid PayFast IP Addresses

PayFast webhooks come from these hosts:

- `www.payfast.co.za`
- `sandbox.payfast.co.za`
- `w1w.payfast.co.za`
- `w2w.payfast.co.za`

### Implementation

```python
from payfast.utils import validate_ip

def process_webhook(request):
    # Get client IP
    ip_address = get_client_ip(request)
    
    # Validate IP
    if not validate_ip(ip_address):
        logger.warning(f"Webhook from invalid IP: {ip_address}")
        return HttpResponseForbidden('Invalid IP address')
    
    # Continue processing
    process_payment_notification(request)
```

### Enhanced IP Validation

For production environments, implement DNS resolution:

```python
import socket

def validate_ip_strict(ip_address):
    """Validate IP by resolving PayFast hostnames"""
    valid_hosts = [
        'www.payfast.co.za',
        'sandbox.payfast.co.za',
        'w1w.payfast.co.za',
        'w2w.payfast.co.za',
    ]
    
    valid_ips = set()
    for host in valid_hosts:
        try:
            ip = socket.gethostbyname(host)
            valid_ips.add(ip)
        except socket.gaierror:
            logger.error(f"Could not resolve {host}")
    
    return ip_address in valid_ips
```

### Handling Proxy Servers

If using a reverse proxy (nginx, Apache), ensure you get the real client IP:

```python
def get_client_ip(request):
    """Get real client IP behind proxy"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

**Nginx Configuration:**

```nginx
location /payfast/ {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_pass http://your-app;
}
```

## HTTPS Requirements

### Why HTTPS is Required

PayFast **requires** HTTPS for production webhooks because:

- Protects payment data in transit
- Prevents man-in-the-middle attacks
- Ensures data integrity
- Required by PCI DSS compliance

### Enforcing HTTPS

**Django Settings:**

```python
# settings.py (production)

# Redirect all HTTP to HTTPS
SECURE_SSL_REDIRECT = True

# Set secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Proxy SSL header (if behind reverse proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### SSL Certificate Setup

**Using Let's Encrypt (Free):**

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Verify HTTPS:**

```bash
# Test your SSL configuration
curl -I https://yourdomain.com/payfast/notify/

# Should return 200 OK with HTTPS
```

## Webhook Security

### Three-Layer Verification

dj-payfast implements three layers of webhook security:

```python
@csrf_exempt  # PayFast can't send CSRF token
@require_POST  # Only POST requests
def webhook_handler(request):
    # Layer 1: IP Validation
    if not validate_ip(get_client_ip(request)):
        return HttpResponseForbidden()
    
    # Layer 2: Signature Verification
    if not verify_signature(request.POST.dict()):
        return HttpResponseBadRequest('Invalid signature')
    
    # Layer 3: Server-Side Validation
    if not validate_with_payfast(request.POST.dict()):
        return HttpResponseBadRequest('Validation failed')
    
    # All checks passed - process payment
    process_payment(request.POST)
    return HttpResponse('OK')
```

### Server-Side Validation

Always validate with PayFast servers:

```python
import requests
from payfast import conf

def validate_with_payfast(post_data):
    """
    Validate notification with PayFast servers
    This is the most important security check
    """
    try:
        # Send data to PayFast for validation
        response = requests.post(
            conf.PAYFAST_VALIDATE_URL,
            data=post_data,
            timeout=10
        )
        
        # Check response
        if response.text == 'VALID':
            return True
        else:
            logger.warning(f"PayFast validation failed: {response.text}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Error validating with PayFast: {e}")
        return False
```

### Webhook Logging

Log all webhook activity for audit trails:

```python
from payfast.models import PayFastNotification

def log_webhook(request, is_valid, error=None):
    """Log all webhook attempts"""
    PayFastNotification.objects.create(
        raw_data=request.POST.dict(),
        is_valid=is_valid,
        validation_errors=error or '',
        ip_address=get_client_ip(request),
    )
```

### Webhook Rate Limiting

Protect against DoS attacks:

```python
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests

def rate_limit_webhook(request):
    """Rate limit webhook requests"""
    ip = get_client_ip(request)
    cache_key = f'webhook_rate_limit_{ip}'
    
    # Allow max 10 requests per minute per IP
    request_count = cache.get(cache_key, 0)
    if request_count > 10:
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        return HttpResponseTooManyRequests()
    
    cache.set(cache_key, request_count + 1, 60)  # 60 seconds
    return None
```

## Configuration Security

### Never Commit Credentials

**❌ NEVER DO THIS:**

```python
# settings.py - WRONG!
PAYFAST_MERCHANT_ID = '10000100'
PAYFAST_MERCHANT_KEY = '46f0cd694581a'
PAYFAST_PASSPHRASE = 'my_secret_passphrase'
```

**✅ DO THIS:**

```python
# settings.py - CORRECT
import os

PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')

# Validate in production
if not DEBUG:
    assert PAYFAST_MERCHANT_ID, "PAYFAST_MERCHANT_ID not configured"
    assert PAYFAST_MERCHANT_KEY, "PAYFAST_MERCHANT_KEY not configured"
    assert PAYFAST_PASSPHRASE, "PAYFAST_PASSPHRASE not configured"
```

### Environment Variables

**Using .env file (local development):**

```bash
# .env (add to .gitignore!)
PAYFAST_MERCHANT_ID=10000100
PAYFAST_MERCHANT_KEY=46f0cd694581a
PAYFAST_PASSPHRASE=your_secure_passphrase
PAYFAST_TEST_MODE=True
```

**Load with python-decouple:**

```python
from decouple import config

PAYFAST_MERCHANT_ID = config('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = config('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = config('PAYFAST_PASSPHRASE')
PAYFAST_TEST_MODE = config('PAYFAST_TEST_MODE', default=True, cast=bool)
```

### Secrets Management

**AWS Secrets Manager:**

```python
import boto3
import json

def get_payfast_credentials():
    """Retrieve credentials from AWS Secrets Manager"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='payfast-credentials')
    credentials = json.loads(response['SecretString'])
    return credentials

credentials = get_payfast_credentials()
PAYFAST_MERCHANT_ID = credentials['merchant_id']
PAYFAST_MERCHANT_KEY = credentials['merchant_key']
PAYFAST_PASSPHRASE = credentials['passphrase']
```

**Azure Key Vault:**

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_secret(secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url="https://your-vault.vault.azure.net/",
        credential=credential
    )
    return client.get_secret(secret_name).value

PAYFAST_MERCHANT_ID = get_secret('payfast-merchant-id')
PAYFAST_MERCHANT_KEY = get_secret('payfast-merchant-key')
PAYFAST_PASSPHRASE = get_secret('payfast-passphrase')
```

## Database Security

### Sensitive Data Storage

```python
# models.py - Example of secure data storage
from django.db import models
from django.contrib.auth.models import User

class PayFastPayment(models.Model):
    # ✅ Store payment ID (not sensitive)
    m_payment_id = models.CharField(max_length=100, unique=True)
    
    # ✅ Store user reference (FK)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # ✅ Store email (needed for receipts)
    email_address = models.EmailField()
    
    # ❌ NEVER store these in database:
    # - Credit card numbers
    # - CVV codes
    # - Full card details
    # - Merchant keys
    # - Passphrases
```

### Database Encryption

**Encrypt sensitive fields:**

```python
from django_cryptography.fields import encrypt

class PayFastPayment(models.Model):
    # Encrypt custom fields if they contain sensitive data
    custom_str1 = encrypt(models.CharField(max_length=255, blank=True))
```

### Database Access Control

```python
# settings.py

# Use read-only database user for analytics
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'payfast_db',
        'USER': 'payfast_user',  # Limited permissions
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'OPTIONS': {
            'sslmode': 'require',  # Require SSL
        }
    }
}
```

## Testing Security

### Test Mode Separation

**Always separate test and production:**

```python
# settings/base.py
PAYFAST_TEST_MODE = True

# settings/production.py
PAYFAST_TEST_MODE = False

# Enforce different credentials
if PAYFAST_TEST_MODE:
    assert 'sandbox' in PAYFAST_MERCHANT_ID.lower(), "Use sandbox credentials in test mode"
else:
    assert 'sandbox' not in PAYFAST_MERCHANT_ID.lower(), "Don't use sandbox credentials in production"
```

### Security Testing

**Test signature verification:**

```python
# tests/test_security.py
from django.test import TestCase
from payfast.utils import verify_signature

class SecurityTestCase(TestCase):
    def test_invalid_signature_rejected(self):
        """Ensure invalid signatures are rejected"""
        data = {
            'amount': '100.00',
            'signature': 'invalid_signature_here'
        }
        self.assertFalse(verify_signature(data))
    
    def test_tampered_data_rejected(self):
        """Ensure tampered data is rejected"""
        # Create valid signature
        data = {'amount': '100.00'}
        signature = generate_signature(data)
        data['signature'] = signature
        
        # Tamper with data
        data['amount'] = '1.00'
        
        # Should fail verification
        self.assertFalse(verify_signature(data))
```

## Production Checklist

Before going live, verify:

### Configuration

- [ ] `PAYFAST_TEST_MODE = False`
- [ ] Production merchant credentials configured
- [ ] Secure passphrase generated and configured
- [ ] Environment variables properly set
- [ ] No credentials in version control
- [ ] `.env` file in `.gitignore`

### HTTPS

- [ ] Valid SSL certificate installed
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT = True`)
- [ ] Secure cookies enabled
- [ ] HSTS configured
- [ ] Mixed content warnings resolved

### Webhook

- [ ] Webhook URL publicly accessible
- [ ] Webhook URL uses HTTPS
- [ ] IP validation enabled
- [ ] Signature verification enabled
- [ ] Server-side validation enabled
- [ ] Webhook logging configured
- [ ] Error notifications set up

### Security

- [ ] Django `SECRET_KEY` is random and secure
- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] CSRF protection enabled
- [ ] SQL injection protection verified
- [ ] XSS protection enabled
- [ ] Database backups configured

### Monitoring

- [ ] Error logging configured
- [ ] Payment audit trail enabled
- [ ] Failed webhook alerts set up
- [ ] Security event monitoring
- [ ] Regular security audits scheduled

## Common Security Issues

### Issue 1: Signature Verification Disabled

**Problem:**
```python
# ❌ WRONG - Skipping verification
if PAYFAST_TEST_MODE:
    # Process without verification
    process_payment(data)
else:
    if verify_signature(data):
        process_payment(data)
```

**Solution:**
```python
# ✅ CORRECT - Always verify
if not verify_signature(data):
    raise SecurityError("Invalid signature")
process_payment(data)
```

### Issue 2: Credentials in Code

**Problem:**
```python
# ❌ WRONG - Hardcoded credentials
PAYFAST_MERCHANT_KEY = '46f0cd694581a'
```

**Solution:**
```python
# ✅ CORRECT - Environment variables
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
```

### Issue 3: HTTP Webhook URL

**Problem:**
```
http://example.com/payfast/notify/  # ❌ Not secure
```

**Solution:**
```
https://example.com/payfast/notify/  # ✅ Secure
```

### Issue 4: No Server-Side Validation

**Problem:**
```python
# ❌ WRONG - Only checking signature
if verify_signature(data):
    process_payment(data)
```

**Solution:**
```python
# ✅ CORRECT - Multiple validations
if not verify_signature(data):
    return HttpResponseBadRequest('Invalid signature')

if not validate_with_payfast(data):
    return HttpResponseBadRequest('Validation failed')

process_payment(data)
```

### Issue 5: Insufficient Logging

**Problem:**
```python
# ❌ WRONG - No logging
process_payment(data)
```

**Solution:**
```python
# ✅ CORRECT - Comprehensive logging
logger.info(f"Processing payment {payment_id}")
try:
    process_payment(data)
    logger.info(f"Payment {payment_id} completed successfully")
except Exception as e:
    logger.error(f"Payment {payment_id} failed: {e}")
    raise
```

## Security Resources

### Official Documentation

- [PayFast Security Guide](https://developers.payfast.co.za/docs#security)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### Tools

- **SSL Testing**: [SSL Labs](https://www.ssllabs.com/ssltest/)
- **Security Headers**: [Security Headers](https://securityheaders.com/)
- **Django Security**: `python manage.py check --deploy`

### Regular Security Tasks

1. **Weekly**: Review failed webhook attempts
2. **Monthly**: Rotate passphrases and secrets
3. **Quarterly**: Security audit and penetration testing
4. **Annually**: SSL certificate renewal

## Getting Help

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email security concerns to: security@example.com
3. Include detailed information about the vulnerability
4. Allow time for a fix before public disclosure

## Conclusion

Security is not optional when handling payments. Always:

- ✅ Use passphrases
- ✅ Verify signatures
- ✅ Validate IP addresses
- ✅ Use HTTPS in production
- ✅ Store credentials securely
- ✅ Log all payment activity
- ✅ Test security measures

Remember: **Security is a process, not a destination**. Regularly review and update your security practices.