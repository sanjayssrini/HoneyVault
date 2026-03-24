import json
import hashlib


def encode_vault(vault):
    return hashlib.sha256(json.dumps(vault, sort_keys=True).encode()).hexdigest()

def encode_message(vault):
    """
    Generate a deterministic seed from vault content.
    Same vault content will always produce the same seed.
    """
    # Sort keys to ensure consistent ordering
    vault_str = json.dumps(vault, sort_keys=True)
    seed = hashlib.sha256(vault_str.encode()).hexdigest()
    return seed
