from django.test import TestCase
from payfast.models import PayFastPayment, PayFastNotification

class PayFastModelsTestCase(TestCase):
    def setUp(self):
        # Create a sample PayFastPayment instance
        self.payment = PayFastPayment.objects.create(
            m_payment_id='TEST12345',
            amount=100.00,
            item_name='Test Item',
            item_description='This is a test item.'
        )
    
    def test_payment_creation(self):
        """Test that a PayFastPayment instance is created correctly"""
        self.assertEqual(self.payment.m_payment_id, 'TEST12345')
        self.assertEqual(self.payment.amount, 100.00)
        self.assertEqual(self.payment.item_name, 'Test Item')
        self.assertEqual(self.payment.item_description, 'This is a test item.')
        self.assertEqual(self.payment.status, 'pending')