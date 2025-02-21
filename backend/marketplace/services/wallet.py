from django.db import transaction
from django.utils.translation import gettext_lazy as _
from ..models.wallet import UserWallet, WithdrawalAddress

class WalletService:
    """Service for handling wallet operations"""
    
    @staticmethod
    def create_wallet(user_profile):
        """Create a new wallet for a user"""
        return UserWallet.objects.create(user=user_profile)
        
    @staticmethod
    def add_withdrawal_address(wallet, currency, address):
        """Add a withdrawal address and check for suspicious activity"""
        # Check if address is used by other accounts
        used_by_others = WithdrawalAddress.objects.filter(
            address=address
        ).exclude(
            wallet=wallet
        ).exists()
        
        withdrawal_address = WithdrawalAddress.objects.create(
            wallet=wallet,
            currency=currency,
            address=address,
            used_by_other_accounts=used_by_others
        )
        
        if used_by_others:
            withdrawal_address.is_flagged = True
            withdrawal_address.flag_reason = _('Address used by multiple accounts')
            withdrawal_address.save()
            
        return withdrawal_address
        
    @staticmethod
    @transaction.atomic
    def update_balance(wallet, currency, amount):
        """Update wallet balance for specified currency"""
        if currency not in dict(WithdrawalAddress.CURRENCY_CHOICES):
            raise ValueError(f"Invalid currency: {currency}")
            
        balance_field = f"{currency}_balance"
        current_balance = getattr(wallet, balance_field)
        new_balance = current_balance + amount
        
        if new_balance < 0:
            raise ValueError(_("Insufficient balance"))
            
        setattr(wallet, balance_field, new_balance)
        wallet.save()
        
        return new_balance
