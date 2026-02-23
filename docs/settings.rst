Settings
========

You can provide ``dj-payfast`` settings like this:

.. code-block:: python

    # e.g. in your Django settings file:
    # PayFast Configuration
    PAYFAST_MERCHANT_ID = 'your_merchant_id'
    PAYFAST_MERCHANT_KEY = 'your_merchant_key'
    PAYFAST_PASSPHRASE = 'your_passphrase'  # Optional but recommended
    PAYFAST_TEST_MODE = True  # Set to False for production

.. note::

    All following setting names written in CAPS with PAYFAST prefix are payfast settings.

PAYFAST_MERCHANT_ID
-------------

Merchant ID provided by PayFast.
This is useful if you want to make multiple PayFast merchant accounts for different environments.

**Required**: ``True``

PAYFAST_MERCHANT_KEY
-----------

merchant key provided by PayFast.
This is useful if you want to make multiple PayFast merchant accounts for different environments.

.. versionchanged::     2.0.0
This setting is now required.

As the merchant key is required to generate the signature for PayFast requests, it is now a required setting. If you do not have a merchant key, you can obtain one from your PayFast account dashboard.
**Required**: ``True``

PAYFAST_PASSPHRASE
-----------------
Passphrase provided by PayFast.
This is optional but recommended for added security. If you choose to use a passphrase, make sure to set it in your PayFast account settings as well.
**Required**: ``False``

PAYFAST_TEST_MODE
-----------------
When set to ``True``, all transactions will be processed in PayFast's sandbox environment. This allows you to test your integration without processing real payments. Remember to set this to ``False`` when you are ready to go live.
**Required**: ``True`` (default: ``True``)