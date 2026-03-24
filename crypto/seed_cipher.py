from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, base64

def encrypt_seed(seed, key):
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, seed.encode(), None)
    return {
        "nonce": base64.b64encode(nonce).decode(),
        "cipher": base64.b64encode(ct).decode()
    }

def decrypt_seed(blob, key):
    aes = AESGCM(key)
    nonce = base64.b64decode(blob["nonce"])
    ct = base64.b64decode(blob["cipher"])
    return aes.decrypt(nonce, ct, None).decode()
