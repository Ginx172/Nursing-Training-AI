"""
Multi-Factor Authentication (MFA) Service
Supports TOTP (Time-based One-Time Password), SMS, and Email verification
"""

import pyotp
import qrcode
import io
import base64
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import secrets
import hashlib

class MFAService:
    """Service for Multi-Factor Authentication"""
    
    def __init__(self):
        self.issuer_name = "Nursing Training AI"
        self.backup_codes_count = 10
    
    # ========================================
    # TOTP (Google Authenticator, Authy, etc.)
    # ========================================
    
    def generate_totp_secret(self, user_email: str) -> Tuple[str, str]:
        """Generate TOTP secret and provisioning URI"""
        try:
            # Generate random secret
            secret = pyotp.random_base32()
            
            # Create provisioning URI for QR code
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=user_email,
                issuer_name=self.issuer_name
            )
            
            return secret, provisioning_uri
        except Exception as e:
            print(f"Error generating TOTP secret: {e}")
            raise
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code image as base64 string"""
        try:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            print(f"Error generating QR code: {e}")
            raise
    
    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            print(f"Error verifying TOTP: {e}")
            return False
    
    # ========================================
    # BACKUP CODES
    # ========================================
    
    def generate_backup_codes(self) -> list:
        """Generate backup codes for account recovery"""
        try:
            codes = []
            for _ in range(self.backup_codes_count):
                # Generate 8-character code
                code = secrets.token_hex(4).upper()
                codes.append(code)
            
            return codes
        except Exception as e:
            print(f"Error generating backup codes: {e}")
            raise
    
    def hash_backup_code(self, code: str) -> str:
        """Hash backup code for secure storage"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_backup_code(self, code: str, hashed_code: str) -> bool:
        """Verify backup code against hash"""
        return self.hash_backup_code(code) == hashed_code
    
    # ========================================
    # SMS-BASED MFA
    # ========================================
    
    async def send_sms_code(self, phone_number: str) -> Dict:
        """Send verification code via SMS"""
        try:
            # Generate 6-digit code
            code = f"{secrets.randbelow(1000000):06d}"
            
            # TODO: Integrate with SMS provider (Twilio, AWS SNS, etc.)
            # For now, just return the code (in production, send via SMS)
            
            # Hash and store code
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            expires_at = datetime.now() + timedelta(minutes=5)
            
            return {
                "success": True,
                "code_hash": code_hash,
                "expires_at": expires_at.isoformat(),
                "phone_last_4": phone_number[-4:],
                # Remove this in production:
                "code": code  # Only for development/testing
            }
        except Exception as e:
            print(f"Error sending SMS code: {e}")
            raise
    
    def verify_sms_code(
        self,
        provided_code: str,
        stored_hash: str,
        expires_at: str
    ) -> bool:
        """Verify SMS code"""
        try:
            # Check expiration
            expiry = datetime.fromisoformat(expires_at)
            if datetime.now() > expiry:
                return False
            
            # Verify code
            code_hash = hashlib.sha256(provided_code.encode()).hexdigest()
            return code_hash == stored_hash
        except Exception as e:
            print(f"Error verifying SMS code: {e}")
            return False
    
    # ========================================
    # EMAIL-BASED MFA
    # ========================================
    
    async def send_email_code(self, email: str) -> Dict:
        """Send verification code via email"""
        try:
            # Generate 6-digit code
            code = f"{secrets.randbelow(1000000):06d}"
            
            # TODO: Send email using email_service
            # email_service.send_mfa_code_email(email, code)
            
            # Hash and store
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            expires_at = datetime.now() + timedelta(minutes=10)
            
            return {
                "success": True,
                "code_hash": code_hash,
                "expires_at": expires_at.isoformat(),
                "email_masked": self._mask_email(email),
                # Remove this in production:
                "code": code  # Only for development/testing
            }
        except Exception as e:
            print(f"Error sending email code: {e}")
            raise
    
    def verify_email_code(
        self,
        provided_code: str,
        stored_hash: str,
        expires_at: str
    ) -> bool:
        """Verify email code"""
        try:
            # Check expiration
            expiry = datetime.fromisoformat(expires_at)
            if datetime.now() > expiry:
                return False
            
            # Verify code
            code_hash = hashlib.sha256(provided_code.encode()).hexdigest()
            return code_hash == stored_hash
        except Exception as e:
            print(f"Error verifying email code: {e}")
            return False
    
    # ========================================
    # USER MFA MANAGEMENT
    # ========================================
    
    async def enable_mfa_for_user(
        self,
        user_id: str,
        method: str,  # totp, sms, email
        contact_info: Optional[str] = None
    ) -> Dict:
        """Enable MFA for a user"""
        try:
            mfa_config = {
                "user_id": user_id,
                "method": method,
                "enabled": True,
                "enabled_at": datetime.now().isoformat()
            }
            
            if method == "totp":
                secret, uri = self.generate_totp_secret(contact_info or user_id)
                qr_code = self.generate_qr_code(uri)
                backup_codes = self.generate_backup_codes()
                
                mfa_config.update({
                    "secret": secret,  # Store encrypted in production
                    "qr_code": qr_code,
                    "backup_codes": [self.hash_backup_code(c) for c in backup_codes],
                    "backup_codes_plain": backup_codes  # Show once, then discard
                })
            
            elif method in ["sms", "email"]:
                mfa_config["contact"] = contact_info
            
            # TODO: Save to database (encrypt secret!)
            
            return mfa_config
        except Exception as e:
            print(f"Error enabling MFA: {e}")
            raise
    
    async def disable_mfa_for_user(self, user_id: str) -> bool:
        """Disable MFA for a user"""
        try:
            # TODO: Update database
            return True
        except Exception as e:
            print(f"Error disabling MFA: {e}")
            raise
    
    async def verify_mfa(
        self,
        user_id: str,
        code: str,
        method: str,
        stored_data: Dict
    ) -> bool:
        """Verify MFA code"""
        try:
            if method == "totp":
                return self.verify_totp_code(stored_data["secret"], code)
            
            elif method == "sms":
                return self.verify_sms_code(
                    code,
                    stored_data["code_hash"],
                    stored_data["expires_at"]
                )
            
            elif method == "email":
                return self.verify_email_code(
                    code,
                    stored_data["code_hash"],
                    stored_data["expires_at"]
                )
            
            elif method == "backup":
                # Verify backup code
                for hashed_code in stored_data.get("backup_codes", []):
                    if self.verify_backup_code(code, hashed_code):
                        # TODO: Mark backup code as used
                        return True
                return False
            
            return False
        except Exception as e:
            print(f"Error verifying MFA: {e}")
            return False
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _mask_email(self, email: str) -> str:
        """Mask email for security (j***@nhs.net)"""
        parts = email.split("@")
        if len(parts) != 2:
            return email
        
        username = parts[0]
        domain = parts[1]
        
        if len(username) <= 2:
            masked_username = username[0] + "*"
        else:
            masked_username = username[0] + "*" * (len(username) - 2) + username[-1]
        
        return f"{masked_username}@{domain}"

# Singleton instance
mfa_service = MFAService()

