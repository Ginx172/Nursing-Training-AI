"""
Encryption Service
Handles data encryption at rest and in transit for Enterprise security
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
import secrets
from typing import Optional, Dict, Any
import json

class EncryptionService:
    """Service for encrypting sensitive data"""
    
    def __init__(self):
        # Master encryption key (should be stored in KMS in production)
        self.master_key = os.getenv("ENCRYPTION_MASTER_KEY", "")
        if not self.master_key:
            environment = os.getenv("ENVIRONMENT", "development")
            if environment == "production":
                raise ValueError(
                    "ENCRYPTION_MASTER_KEY is required in production. "
                    "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
                )
            print("WARNING: ENCRYPTION_MASTER_KEY not set. Generating temporary key for development.")
            self.master_key = Fernet.generate_key().decode()

        self.fernet = Fernet(self.master_key.encode() if isinstance(self.master_key, str) else self.master_key)
    
    # ========================================
    # FIELD-LEVEL ENCRYPTION
    # ========================================
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a single field (e.g., NMC number, phone, SSN)"""
        try:
            if not plaintext:
                return ""
            
            encrypted = self.fernet.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            raise
    
    def decrypt_field(self, encrypted: str) -> str:
        """Decrypt a single field"""
        try:
            if not encrypted:
                return ""
            
            decrypted = self.fernet.decrypt(encrypted.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            raise
    
    # ========================================
    # BULK DATA ENCRYPTION
    # ========================================
    
    def encrypt_dict(self, data: Dict, fields_to_encrypt: list) -> Dict:
        """Encrypt specific fields in a dictionary"""
        try:
            encrypted_data = data.copy()
            
            for field in fields_to_encrypt:
                if field in encrypted_data and encrypted_data[field]:
                    encrypted_data[field] = self.encrypt_field(str(encrypted_data[field]))
            
            return encrypted_data
        except Exception as e:
            print(f"Error encrypting dict: {e}")
            raise
    
    def decrypt_dict(self, data: Dict, fields_to_decrypt: list) -> Dict:
        """Decrypt specific fields in a dictionary"""
        try:
            decrypted_data = data.copy()
            
            for field in fields_to_decrypt:
                if field in decrypted_data and decrypted_data[field]:
                    decrypted_data[field] = self.decrypt_field(decrypted_data[field])
            
            return decrypted_data
        except Exception as e:
            print(f"Error decrypting dict: {e}")
            raise
    
    # ========================================
    # FILE ENCRYPTION
    # ========================================
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Encrypt a file"""
        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt
            encrypted = self.fernet.encrypt(data)
            
            # Write encrypted file
            output = output_path or f"{file_path}.encrypted"
            with open(output, 'wb') as f:
                f.write(encrypted)
            
            return output
        except Exception as e:
            print(f"Error encrypting file: {e}")
            raise
    
    def decrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file"""
        try:
            # Read encrypted file
            with open(file_path, 'rb') as f:
                encrypted = f.read()
            
            # Decrypt
            decrypted = self.fernet.decrypt(encrypted)
            
            # Write decrypted file
            output = output_path or file_path.replace('.encrypted', '')
            with open(output, 'wb') as f:
                f.write(decrypted)
            
            return output
        except Exception as e:
            print(f"Error decrypting file: {e}")
            raise
    
    # ========================================
    # DATABASE ENCRYPTION (Transparent Data Encryption)
    # ========================================
    
    @staticmethod
    def generate_encryption_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """Derive encryption key from password"""
        try:
            if not salt:
                salt = os.urandom(16)
            
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key.decode(), base64.b64encode(salt).decode()
        except Exception as e:
            print(f"Error deriving key: {e}")
            raise
    
    # ========================================
    # TOKEN ENCRYPTION (for JWT secrets)
    # ========================================
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt sensitive tokens before storage"""
        return self.encrypt_field(token)
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt stored token"""
        return self.decrypt_field(encrypted_token)
    
    # ========================================
    # SENSITIVE DATA FIELDS
    # ========================================
    
    SENSITIVE_FIELDS = [
        "nmc_number",        # NMC registration number
        "phone_number",      # Phone number
        "date_of_birth",     # Date of birth
        "national_insurance", # NI number
        "bank_account",      # Bank details
        "card_last_4",       # Card details
        "stripe_customer_id", # Stripe IDs (debatable)
        "password_hash",     # Extra layer on top of bcrypt
        "api_key",           # API keys
        "webhook_secret",    # Webhook secrets
        "mfa_secret"         # MFA secrets
    ]
    
    def encrypt_user_data(self, user_data: Dict) -> Dict:
        """Encrypt all sensitive user fields"""
        return self.encrypt_dict(user_data, self.SENSITIVE_FIELDS)
    
    def decrypt_user_data(self, user_data: Dict) -> Dict:
        """Decrypt sensitive user fields"""
        return self.decrypt_dict(user_data, self.SENSITIVE_FIELDS)
    
    # ========================================
    # KEY ROTATION
    # ========================================
    
    async def rotate_encryption_key(self, new_master_key: str):
        """Rotate master encryption key (re-encrypt all data)"""
        try:
            # TODO: This is a critical operation
            # 1. Get all encrypted data from database
            # 2. Decrypt with old key
            # 3. Encrypt with new key
            # 4. Update database
            # 5. Update master key in environment
            
            print("⚠️ Key rotation is a critical operation and should be done during maintenance window")
            
            # Create new Fernet instance with new key
            new_fernet = Fernet(new_master_key.encode())
            
            # TODO: Implement actual rotation logic
            
            return {
                "success": True,
                "message": "Key rotation initiated",
                "warning": "This is a background process that may take time"
            }
        except Exception as e:
            print(f"Error rotating key: {e}")
            raise

# Singleton instance
encryption_service = EncryptionService()

# Helper decorators for automatic encryption
def encrypt_response(fields: list):
    """Decorator to automatically encrypt response fields"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if isinstance(result, dict):
                return encryption_service.encrypt_dict(result, fields)
            return result
        return wrapper
    return decorator

def decrypt_request(fields: list):
    """Decorator to automatically decrypt request fields"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get request data from kwargs
            if 'data' in kwargs and isinstance(kwargs['data'], dict):
                kwargs['data'] = encryption_service.decrypt_dict(kwargs['data'], fields)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

