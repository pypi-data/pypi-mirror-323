import hmac
import hashlib
import base64
import json
from .utils.uuid_util import generate_uuid
from .utils.time_util import get_expiry_timestamp
from .config import SUPPORTED_ALGORITHMS
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
import time

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

def decrypt_payload(encrypted_data, secret):
    """
    Decrypt the encrypted payload using AES decryption (CBC mode).
    """
    secret = adjust_secret_key_length(secret)

    encrypted_data_bytes = base64.urlsafe_b64decode(encrypted_data + "==")
    
    iv = encrypted_data_bytes[:16]
    encrypted_payload = encrypted_data_bytes[16:]

    cipher = Cipher(algorithms.AES(secret), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_payload = decryptor.update(encrypted_payload) + decryptor.finalize()

    padding = decrypted_payload[-1]
    decrypted_payload = decrypted_payload[:-padding]
    return json.loads(decrypted_payload.decode())

def verify_token(token, secret, encrypt=False):
    if not token or not secret:
        raise ValueError("Token and secret are required for verification.")

    try:
        encoded_header, encoded_payload, provided_signature = token.split(".")
    except ValueError:
        raise ValueError("Invalid token format - Token must consist of header, payload, and signature.")

    signature_input = f"{encoded_header}.{encoded_payload}"

    # Decode and parse header
    try:
        decoded_header = json.loads(base64.urlsafe_b64decode(encoded_header + "==").decode())
    except (json.JSONDecodeError, UnicodeDecodeError, base64.binascii.Error) as e:
        raise ValueError(f"Invalid token header: {e}")

    if "alg" not in decoded_header:
        raise ValueError("Algorithm (alg) field is missing in token header.")

    try:
        alg = decoded_header["alg"].replace("HS", "sha")
        digest_method = getattr(hashlib, alg.lower())
    except AttributeError:
        raise ValueError("Unsupported or invalid algorithm specified in token header.")

    # Verify signature
    try:
        expected_signature = base64.urlsafe_b64encode(
            hmac.new(secret.encode(), signature_input.encode(), digest_method).digest()
        ).decode().rstrip("=")
    except Exception as e:
        raise ValueError(f"Error verifying signature: {e}")

    if provided_signature != expected_signature:
        raise ValueError("Invalid token signature.")

    # Decrypt payload if needed
    try:
        if encrypt:
            payload = decrypt_payload(encoded_payload, secret)
        else:
            payload = json.loads(base64.urlsafe_b64decode(encoded_payload + "==").decode())
    except Exception as e:
        raise ValueError(f"Error decrypting or decoding payload: {e}")

    if "exp" not in payload:
        raise ValueError("Token does not contain an expiration field.")

    if not isinstance(payload["exp"], int):
        raise ValueError("Token expiration time (exp) must be an integer.")

    if int(time.time()) >= payload["exp"]:
        raise ValueError("Token has expired.")

    return payload

