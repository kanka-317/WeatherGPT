"""
Security and password hashing utilities for WeatherGPT (SIH PS 26068)
Uses PBKDF2-HMAC-SHA256 with 100,000 iterations and cryptographic per-user salt.
"""

import hmac
import hashlib
import os
import json
import base64
import time
from typing import Optional, Dict, Any
from app.core.config import settings

ITERATIONS = 100000


def hash_password(password: str) -> str:
    """Hashes a plaintext password using a cryptographically secure 16-byte random salt."""
    salt = os.urandom(16).hex()
    pwd_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    key = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, ITERATIONS)
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a candidate password against the stored salt and hash."""
    try:
        if not hashed_password or "$" not in hashed_password:
            return False
        salt, stored_hash = hashed_password.split("$", 1)
        pwd_bytes = plain_password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")
        new_hash = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, ITERATIONS)
        return hmac.compare_digest(new_hash.hex(), stored_hash)
    except Exception:
        return False


def create_token(payload: Dict[str, Any], expires_in_seconds: int = 86400 * 7) -> str:
    """Generates an HMAC-SHA256 signed session token for authenticated user sessions."""
    data = payload.copy()
    data["exp"] = int(time.time()) + expires_in_seconds
    data["iat"] = int(time.time())
    
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).decode().rstrip("=")
    
    signature = hmac.new(
        settings.JWT_SECRET.encode(),
        f"{header}.{body}".encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{header}.{body}.{sig_b64}"


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Validates signature and expiration of an authentication token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, body, sig = parts
        
        expected_sig = hmac.new(
            settings.JWT_SECRET.encode(),
            f"{header}.{body}".encode(),
            hashlib.sha256
        ).digest()
        expected_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(sig, expected_b64):
            return None
            
        # Add padding back for base64 decode
        rem = len(body) % 4
        padded_body = body + ("=" * (4 - rem) if rem else "")
        payload = json.loads(base64.urlsafe_b64decode(padded_body.encode()).decode())
        
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
