import hmac
import hashlib
import base64
import json
from .utils.uuid_util import generate_uuid
from .utils.time_util import get_expiry_timestamp
from .config import SUPPORTED_ALGORITHMS
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom

def adjust_secret_key_length(secret):
    """
    Adjust the length of the secret key to be 16, 24, or 32 bytes for AES.
    """
    secret = secret.encode()
    key_length = len(secret)

    if key_length == 16 or key_length == 24 or key_length == 32:
        return secret
    elif key_length < 16:
        return secret.ljust(16, b'\0')
    elif key_length < 24:
        return secret.ljust(24, b'\0')
    elif key_length < 32:
        return secret.ljust(32, b'\0')
    else:
        return secret[:32]

def encrypt_payload(payload, secret):
    """
    Encrypt the payload using AES encryption (CBC mode).
    """
    secret = adjust_secret_key_length(secret)
    iv = urandom(16)

    payload_json = json.dumps(payload)
    padding = 16 - len(payload_json) % 16
    payload_json = payload_json + chr(padding) * padding

    cipher = Cipher(algorithms.AES(secret), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted_payload = encryptor.update(payload_json.encode()) + encryptor.finalize()

    encrypted_data = base64.urlsafe_b64encode(iv + encrypted_payload).decode().rstrip("=")
    
    return encrypted_data

def generate_token(header, payload, secret, expires_in=3600, encrypt=False):
    if not header or not payload or not secret:
        raise ValueError("Header, payload, and secret are required.")

    if header.get("alg") not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {header.get('alg')}")

    # Add unique identifier (UUID) and expiration time to the payload
    payload["jti"] = generate_uuid()
    payload["exp"] = get_expiry_timestamp(expires_in)

    # Convert header to Base64URL encoding
    base64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")

    # Encrypt the payload if needed
    try:
        if encrypt:
            base64_payload = encrypt_payload(payload, secret)
        else:
            base64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    except Exception as e:
        raise ValueError(f"Error encrypting payload: {e}")

    # Create signature using HMAC algorithm
    try:
        signature_input = f"{base64_header}.{base64_payload}"
        alg = header["alg"].replace("HS", "sha")
        digest_method = getattr(hashlib, alg.lower())
        signature = base64.urlsafe_b64encode(
            hmac.new(secret.encode(), signature_input.encode(), digest_method).digest()
        ).decode().rstrip("=")
    except Exception as e:
        raise ValueError(f"Error creating signature: {e}")

    return f"{signature_input}.{signature}"

