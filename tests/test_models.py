from django.test import TestCase
from payfast.forms import PayFastPaymentForm
from payfast import conf
from decimal import Decimal


class PayFastPaymentFormTestCase(TestCase):
    """Test cases for PayFastPaymentForm"""
    
    def test_form_initialization(self):
        """Test form initializes with required fields"""
        form = PayFastPaymentForm()
        
        # Check that key fields exist
        self.assertIn('merchant_id', form.fields)
        self.assertIn('merchant_key', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('item_name', form.fields)
        self.assertIn('m_payment_id', form.fields)
        self.assertIn('email_address', form.fields)
        self.assertIn('signature', form.fields)
    
    def test_form_with_initial_data(self):
        """Test form with initial payment data"""
        initial_data = {
            'amount': Decimal('99.99'),
            'item_name': 'Test Product',
            'm_payment_id': 'PF123456789',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/payfast/notify/',
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        
        # Verify initial values are set
        self.assertEqual(form.fields['amount'].initial, Decimal('99.99'))
        self.assertEqual(form.fields['item_name'].initial, 'Test Product')
        self.assertEqual(form.fields['email_address'].initial, 'test@example.com')
    
    def test_signature_generated(self):
        """Test that signature is automatically generated"""
        initial_data = {
            'amount': Decimal('100.00'),
            'item_name': 'Test Item',
            'm_payment_id': 'PF123',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        
        # Signature should be generated
        signature = form.fields['signature'].initial
        self.assertIsNotNone(signature)
        self.assertEqual(len(signature), 32)  # MD5 hash length
    
    def test_merchant_details_auto_populated(self):
        """Test merchant ID and key are auto-populated from settings"""
        form = PayFastPaymentForm()
        
        self.assertEqual(
            form.fields['merchant_id'].initial,
            conf.PAYFAST_MERCHANT_ID
        )
        self.assertEqual(
            form.fields['merchant_key'].initial,
            conf.PAYFAST_MERCHANT_KEY
        )
    
    def test_get_action_url(self):
        """Test get_action_url returns correct PayFast URL"""
        form = PayFastPaymentForm()
        action_url = form.get_action_url()
        
        self.assertEqual(action_url, conf.PAYFAST_URL)
        
        # URL should match test mode setting
        if conf.PAYFAST_TEST_MODE:
            self.assertIn('sandbox', action_url)
        else:
            self.assertNotIn('sandbox', action_url)
    
    def test_all_fields_are_hidden(self):
        """Test that all form fields are hidden inputs"""
        form = PayFastPaymentForm()
        
        for field_name, field in form.fields.items():
            # All fields should be HiddenInput widgets
            self.assertEqual(
                field.widget.__class__.__name__,
                'HiddenInput',
                f"Field {field_name} should be HiddenInput"
            )
    
    def test_form_with_optional_fields(self):
        """Test form with optional fields like name and custom data"""
        initial_data = {
            'amount': Decimal('149.99'),
            'item_name': 'Premium Plan',
            'm_payment_id': 'PF456',
            'email_address': 'premium@example.com',
            'notify_url': 'https://example.com/notify/',
            'name_first': 'John',
            'name_last': 'Doe',
            'custom_str1': 'order_123',
            'custom_int1': 5,
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        
        self.assertEqual(form.fields['name_first'].initial, 'John')
        self.assertEqual(form.fields['name_last'].initial, 'Doe')
        self.assertEqual(form.fields['custom_str1'].initial, 'order_123')
        self.assertEqual(form.fields['custom_int1'].initial, 5)
    
    def test_form_signature_changes_with_data(self):
        """Test that different data produces different signatures"""
        initial_data1 = {
            'amount': Decimal('100.00'),
            'item_name': 'Product A',
            'm_payment_id': 'PF001',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
        }
        
        initial_data2 = {
            'amount': Decimal('200.00'),
            'item_name': 'Product B',
            'm_payment_id': 'PF002',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
        }
        
        form1 = PayFastPaymentForm(initial=initial_data1)
        form2 = PayFastPaymentForm(initial=initial_data2)
        
        signature1 = form1.fields['signature'].initial
        signature2 = form2.fields['signature'].initial
        
        self.assertNotEqual(signature1, signature2)
    
    def test_form_with_minimal_data(self):
        """Test form with only required fields"""
        minimal_data = {
            'amount': Decimal('50.00'),
            'item_name': 'Minimal Product',
            'm_payment_id': 'PF_MIN',
            'email_address': 'minimal@example.com',
            'notify_url': 'https://example.com/notify/',
        }
        
        form = PayFastPaymentForm(initial=minimal_data)
        
        # Should still generate signature
        self.assertIsNotNone(form.fields['signature'].initial)
    
    def test_form_return_and_cancel_urls(self):
        """Test form with return and cancel URLs"""
        initial_data = {
            'amount': Decimal('99.99'),
            'item_name': 'Test',
            'm_payment_id': 'PF789',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
            'return_url': 'https://example.com/success/',
            'cancel_url': 'https://example.com/cancel/',
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        
        self.assertEqual(
            form.fields['return_url'].initial,
            'https://example.com/success/'
        )
        self.assertEqual(
            form.fields['cancel_url'].initial,
            'https://example.com/cancel/'
        )
    
    def test_form_cell_number_field(self):
        """Test form with cell number"""
        initial_data = {
            'amount': Decimal('99.99'),
            'item_name': 'Test',
            'm_payment_id': 'PF_CELL',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
            'cell_number': '+27821234567',
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        
        self.assertEqual(
            form.fields['cell_number'].initial,
            '+27821234567'
        )


class PayFastFormEdgeCasesTestCase(TestCase):
    """Test edge cases in PayFast form"""
    
    def test_form_with_decimal_amount(self):
        """Test form handles decimal amounts correctly"""
        initial_data = {
            'amount': Decimal('99.99'),
            'item_name': 'Test',
            'm_payment_id': 'PF_DEC',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        # Should not raise any errors
        self.assertIsNotNone(form.fields['signature'].initial)
    
    def test_form_with_special_characters_in_item_name(self):
        """Test form handles special characters in item name"""
        initial_data = {
            'amount': Decimal('100.00'),
            'item_name': 'Test & Product "Special"',
            'm_payment_id': 'PF_SPEC',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        # Should generate signature without errors
        self.assertIsNotNone(form.fields['signature'].initial)
    
    def test_form_with_unicode_characters(self):
        """Test form handles unicode characters"""
        initial_data = {
            'amount': Decimal('100.00'),
            'item_name': 'Product 日本語',
            'm_payment_id': 'PF_UNI',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        # Should handle unicode without errors
        self.assertIsNotNone(form.fields['signature'].initial)
    
    def test_form_with_all_custom_fields(self):
        """Test form with all custom fields populated"""
        initial_data = {
            'amount': Decimal('199.99'),
            'item_name': 'Test',
            'm_payment_id': 'PF_ALL',
            'email_address': 'test@example.com',
            'notify_url': 'https://example.com/notify/',
            'custom_str1': 'string1',
            'custom_str2': 'string2',
            'custom_str3': 'string3',
            'custom_str4': 'string4',
            'custom_str5': 'string5',
            'custom_int1': 1,
            'custom_int2': 2,
            'custom_int3': 3,
            'custom_int4': 4,
            'custom_int5': 5,
        }
        
        form = PayFastPaymentForm(initial=initial_data)
        
        # All custom fields should be set
        for i in range(1, 6):
            self.assertEqual(
                form.fields[f'custom_str{i}'].initial,
                f'string{i}'
            )
            self.assertEqual(
                form.fields[f'custom_int{i}'].initial,
                i
            )