import gnupg
import secrets
import string
from django.conf import settings
from django.utils import timezone
from ..models.user_profile import UserProfile

class PGPService:
    """Service for handling PGP operations"""
    def __init__(self):
        self.gpg = gnupg.GPG(gnupghome=settings.GPG_HOME)
        
    def generate_verification_code(self, length=32):
        """Generate random verification code"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
        
    def encrypt_message(self, message: str, pgp_key: str) -> str:
        """Encrypt a message using user's PGP key"""
        imported_key = self.gpg.import_keys(pgp_key)
        if not imported_key.fingerprints:
            raise ValueError("Invalid PGP key")
            
        encrypted = self.gpg.encrypt(
            message,
            imported_key.fingerprints[0],
            always_trust=True
        )
        if not encrypted.ok:
            raise ValueError(f"Encryption failed: {encrypted.status}")
            
        return str(encrypted)
        
    def verify_pgp_key(self, user_profile: UserProfile, verification_code: str) -> bool:
        """Verify PGP key ownership"""
        if not user_profile.pgp_verification_code:
            return False
            
        if verification_code != user_profile.pgp_verification_code:
            return False
            
        user_profile.pgp_key_verified = True
        user_profile.pgp_verification_code = None
        user_profile.save()
        
        return True
        
    def generate_2fa_message(self, user_profile: UserProfile) -> tuple:
        """Generate encrypted 2FA message with code"""
        code = self.generate_verification_code(6)
        welcome_phrase = f"Welcome back {user_profile.public_username}!"
        message = f"{welcome_phrase}\nYour 2FA code is: {code}"
        
        encrypted_message = self.encrypt_message(message, user_profile.pgp_public_key)
        return encrypted_message, code
