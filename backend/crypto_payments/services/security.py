from django.utils import timezone
from django.db import transaction
from typing import Optional
from decimal import Decimal
import logging
from ..models import CryptoWallet, AccountFreeze, SecurityThreshold, WithdrawalAutomation
from ..exceptions import SecurityError

logger = logging.getLogger(__name__)

class SecurityService:
    """Service for handling security-related operations"""
    
    @staticmethod
    def get_threshold(threshold_type: str) -> Optional[Decimal]:
        """Get active threshold value"""
        threshold = SecurityThreshold.objects.filter(
            threshold_type=threshold_type,
            is_active=True
        ).first()
        return threshold.value if threshold else None
        
    @staticmethod
    def check_wallet_frozen(wallet: CryptoWallet) -> bool:
        """Check if wallet has any active freezes"""
        return AccountFreeze.objects.filter(
            wallet=wallet,
            status='active'
        ).exists()
    
    @classmethod
    def freeze_account(
        cls,
        wallet: CryptoWallet,
        freeze_type: str,
        reason: str,
        admin_user=None,
        expires_at=None
    ) -> AccountFreeze:
        """Create new account freeze"""
        with transaction.atomic():
            freeze = AccountFreeze.objects.create(
                wallet=wallet,
                freeze_type=freeze_type,
                reason=reason,
                expires_at=expires_at,
                created_by=admin_user
            )
            
            # Update wallet status
            wallet.status = 'suspended'
            wallet.save()
            
            logger.warning(f"Account frozen: {wallet.pk} - {reason}")
            return freeze
    
    @classmethod
    def lift_freeze(cls, freeze: AccountFreeze, admin_user) -> bool:
        """Lift an active account freeze"""
        with transaction.atomic():
            if not freeze.is_active():
                return False
                
            freeze.status = 'lifted'
            freeze.lifted_at = timezone.now()
            freeze.lifted_by = admin_user
            freeze.save()
            
            # Check if wallet has other active freezes
            if not AccountFreeze.objects.filter(
                wallet=freeze.wallet,
                status='active'
            ).exists():
                freeze.wallet.status = 'active'
                freeze.wallet.save()
                
            logger.info(f"Account freeze lifted: {freeze.wallet.pk}")
            return True
    
    @classmethod
    def check_withdrawal_automation(
        cls,
        wallet: CryptoWallet,
        amount: Decimal
    ) -> Optional[str]:
        """
        Check if withdrawal can be automated
        Returns automation type if allowed, None if manual review required
        """
        try:
            # Check for active freezes
            if cls.check_wallet_frozen(wallet):
                return None
                
            # Get automation rules
            automation = WithdrawalAutomation.objects.filter(
                currency_type=wallet.currency_type,
                is_active=True,
                min_amount__lte=amount,
                max_amount__gte=amount
            ).first()
            
            if not automation:
                return None
                
            # Additional checks for instant processing
            if automation.automation_type == 'instant':
                # Check if amount exceeds suspicious threshold
                suspicious_amount = cls.get_threshold('suspicious_amount')
                if suspicious_amount and amount > suspicious_amount:
                    return None
                    
                # Check recent withdrawal history
                recent_count = wallet.crypto_transactions.filter(
                    transaction_type='withdrawal',
                    created_at__gte=timezone.now() - timezone.timedelta(hours=1)
                ).count()
                
                if recent_count >= 3:  # Configurable threshold
                    return None
            
            return automation.automation_type
            
        except Exception as e:
            logger.error(f"Error checking withdrawal automation: {str(e)}")
            return None
