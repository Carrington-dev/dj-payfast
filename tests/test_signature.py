# test_signature.py
import hashlib
from urllib.parse import urlencode
from collections import OrderedDict
from decouple import config

def test_signature():
    """Test PayFast signature generation"""
    # Your PayFast credentials
    merchant_id = config('PAYFAST_MERCHANT_ID', default="pass")  # Your merchant ID
    merchant_key = config('PAYFAST_MERCHANT_KEY', default="pass")  # Your merchant key
    passphrase = config('PAYFAST_PASSPHRASE', default="pass")  # Your passphrase
    
    # Test payment data
    data = {
        'merchant_id': merchant_id,
        'merchant_key': merchant_key,
        'amount': '100.00',
        'item_name': 'Test Product',
        'm_payment_id': 'test123',
        'email_address': 'test@example.com',
        'notify_url': 'https://example.com/payfast/notify/',
    }
    
    # Remove empty values
    clean_data = {k: str(v).strip() for k, v in data.items() if v}
    
    # Sort by keys
    ordered_data = OrderedDict(sorted(clean_data.items()))
    
    # Create parameter string
    param_string = urlencode(ordered_data)
    print("Parameter string:")
    print(param_string)
    print()
    
    # Add passphrase
    param_string += f'&passphrase={passphrase}'
    print("Parameter string with passphrase:")
    print(param_string)
    print()
    
    # Generate signature
    signature = hashlib.md5(param_string.encode()).hexdigest()
    print("Generated signature:")
    print(signature)
    
    # Assert that signature is not empty and is 32 characters (MD5 hash length)
    assert signature is not None, "Signature should not be None"
    assert len(signature) == 32, f"MD5 signature should be 32 characters, got {len(signature)}"
    assert isinstance(signature, str), f"Signature should be a string, got {type(signature)}"
    
    # Don't return anything - test functions should return None

if __name__ == '__main__':
    test_signature()