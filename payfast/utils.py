
# ============================================================================
# payfast/utils.py
# ============================================================================

import hashlib
import random
import string
import urllib.parse
from urllib.parse import urlencode
from collections import OrderedDict


def generate_pf_id(prefix="PF", length=11):
    """
    Generate an ID like PF18K07G4P9
    
    prefix: fixed prefix (default 'PF')
    length: total length of the ID (default 11)
    """
    # Remaining characters after prefix
    remaining = length - len(prefix)

    # Pool of uppercase letters + digits
    chars = string.ascii_uppercase + string.digits

    random_part = ''.join(random.choice(chars) for _ in range(remaining))
    return prefix + random_part


def generateSignature(dataArray, passPhrase = ''):
    payload = ""
    for key in dataArray:
        # Get all the data from Payfast and prepare parameter string
        payload += key + "=" + urllib.parse.quote_plus(str(dataArray[key]).replace("+", " ")) + "&"
    # After looping through, cut the last & or append your passphrase
    payload = payload[:-1]
    if passPhrase != '':
        payload += f"&passphrase={passPhrase}"
    return hashlib.md5(payload.encode()).hexdigest()


def generate_signature(data_dict, passphrase=None):
    """
    Generate PayFast security signature
    
    Args:
        data_dict: Dictionary of payment data
        passphrase: PayFast passphrase (optional but recommended)
    
    Returns:
        MD5 signature string
    """
    from . import conf
    
    # Remove signature if present
    data = {k: v for k, v in data_dict.items() if k != 'signature'}
    
    # Sort by keys
    ordered_data = OrderedDict(sorted(data.items()))
    
    # Create parameter string
    param_string = urlencode(ordered_data)
    
    # Add passphrase if provided
    if passphrase or conf.PAYFAST_PASSPHRASE:
        param_string += f'&passphrase={passphrase or conf.PAYFAST_PASSPHRASE}'
    
    # Generate MD5 signature
    signature = hashlib.md5(param_string.encode()).hexdigest()
    
    return signature


def verify_signature(data_dict, passphrase=None):
    """
    Verify PayFast signature
    
    Args:
        data_dict: Dictionary containing payment data and signature
        passphrase: PayFast passphrase
    
    Returns:
        Boolean indicating if signature is valid
    """
    received_signature = data_dict.get('signature', '')
    calculated_signature = generateSignature(data_dict, passphrase)
    
    return received_signature == calculated_signature


def validate_ip(ip_address):
    """
    Validate that the request comes from PayFast servers
    
    Args:
        ip_address: IP address to validate
    
    Returns:
        Boolean indicating if IP is valid
    """
    # PayFast valid IP addresses
    valid_hosts = [
        'www.payfast.co.za',
        'sandbox.payfast.co.za',
        'w1w.payfast.co.za',
        'w2w.payfast.co.za',
    ]
    
    # In production, you should resolve these hosts to IPs and check
    # For now, we'll return True (implement proper validation in production)
    return True

