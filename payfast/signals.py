# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from payfast.models import PayFastPayment

@receiver(post_save, sender=PayFastPayment)
def handle_payment_complete(sender, instance, **kwargs):
    """Handle completed payments"""
    if instance.status == 'complete' and instance.payment_status == 'COMPLETE':
        # Grant access to user
        if instance.user:
            grant_premium_access(instance.user)
        
        # Send confirmation email
        send_confirmation_email(instance)

def grant_premium_access(user):
    """Grant premium access to user"""
    # Your logic here
    pass

def send_confirmation_email(payment):
    """Send payment confirmation email"""
    # Your logic here
    pass