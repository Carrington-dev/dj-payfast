# test_signature.py
import hashlib
from urllib.parse import urlencode
from collections import OrderedDict
from decouple import config

def test_signature():
    # Your PayFast credentials
    merchant_id = config('merchant_id',)  # Your merchant ID
    merchant_key = config('merchant_key')  # Your merchant key
    passphrase = config('passphrase')  # Your passphrase
    
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
    
    return signature

if __name__ == '__main__':
    test_signature()