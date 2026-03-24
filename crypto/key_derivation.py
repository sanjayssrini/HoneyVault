import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def derive_key(password: str, salt: bytes, iterations=200_000):
    """
    Derives a 256-bit key from password using PBKDF2.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,          # 256-bit key
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode())

def generate_salt():
    return os.urandom(16)

def encode_salt(salt: bytes):
    return base64.b64encode(salt).decode()

def decode_salt(salt_str: str):
    return base64.b64decode(salt_str)
