from django.test import TestCase
from payfast.models import PayFastPayment, PayFastNotification

class PayFastModelsTestCase(TestCase):
    def setUp(self):
        # Create a sample PayFastPayment instance
        self.payment = PayFastPayment.objects.create(
            m_payment_id='PF123456789',
            amount=100.00,
            item_name='Test Item',
            item_description='This is a test item.'
        )

        self.notification = PayFastNotification.objects.create(
            payment=self.payment,
        )
        
    
    def test_payment_creation(self):
        """Test that a PayFastPayment instance is created correctly"""
        self.assertEqual(self.payment.m_payment_id, 'PF123456789')
        self.assertEqual(self.payment.amount, 100.00)
        self.assertEqual(self.payment.item_name, 'Test Item')
        self.assertEqual(self.payment.item_description, 'This is a test item.')
        self.assertEqual(self.payment.status, 'pending')
    
    # def test_payment_deletion(self)
    
    # def test_notification_creation(self):
    #     """Test that a PayFastNotification instance is created correctly"""
        
    #     self.assertEqual(self.notification.payment, self.payment)
    #     self.assertEqual(self.notification.payment.m_payment_id, 'PF123456789')
    #     self.assertEqual(self.notification.payment.amount, 100.00)
    #     self.assertEqual(self.notification.payment.status, 'pending')

    # def test_mark_complete(self):
    #     """Test marking a payment as complete"""
    #     self.payment.mark_complete()
    #     self.assertEqual(self.payment.status, 'complete')
    #     self.assertIsNotNone(self.payment.completed_at)