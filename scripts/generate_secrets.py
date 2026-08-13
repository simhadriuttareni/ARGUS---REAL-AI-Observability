#!/usr/bin/env python
"""
Generate encryption secrets for ARGUS
"""

import secrets
import base64
from cryptography.fernet import Fernet

def generate_secrets():
    """Generate encryption keys and JWT secrets"""
    
    # Generate Fernet key (for encryption)
    fernet_key = Fernet.generate_key().decode()
    
    # Generate JWT secret
    jwt_secret = secrets.token_urlsafe(32)
    
    # Generate API key prefix
    api_key_prefix = secrets.token_hex(8)
    
    print("\n🔐 Generated Secrets for ARGUS")
    print("=" * 40)
    print(f"ENCRYPTION_KEY={fernet_key}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"API_KEY_PREFIX={api_key_prefix}")
    print("=" * 40)
    print("\n⚠️  Add these to your .env file")
    print("⚠️  Never commit these to version control")


if __name__ == "__main__":
    generate_secrets()