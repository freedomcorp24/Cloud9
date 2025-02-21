from django.utils import timezone
from django.db import transaction
from ..models import DepositAddress, CryptoTransaction
from ..node_integration import NodeFactory

class DepositService:
    """Service for managing deposit addresses and monitoring payments"""
    
    @staticmethod
    def check_pending_deposits():
        """Check status of pending deposits"""
        pending_deposits = DepositAddress.objects.filter(
            status__in=['active', 'pending']
        ).select_related('wallet')
        
        for deposit in pending_deposits:
            if deposit.status == 'active' and deposit.is_expired:
                # Mark expired addresses without payment as expired
                deposit.status = 'expired'
                deposit.save()
                continue
                
            # Check for payment on address
            node = NodeFactory.get_node(deposit.wallet.currency)
            payment = node.check_address(deposit.address)
            
            if payment:
                with transaction.atomic():
                    if deposit.status == 'active':
                        deposit.status = 'pending'
                        deposit.payment_detected_at = timezone.now()
                        
                    # Check confirmations
                    if payment['confirmations'] >= deposit.required_confirmations:
                        # Create completed transaction
                        CryptoTransaction.objects.create(
                            wallet=deposit.wallet,
                            tx_hash=payment['tx_hash'],
                            amount_crypto=payment['amount'],
                            transaction_type='deposit',
                            status='completed'
                        )
                        
                        # Update wallet balance
                        deposit.wallet.balance += payment['amount']
                        deposit.wallet.save()
                        
                        # Mark deposit as completed
                        deposit.status = 'completed'
                        
                    deposit.save()
