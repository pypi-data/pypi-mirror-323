import os
import secrets

def generate_secret_key(length=64):
    """
    Generate a secure random secret key.
    
    :param length: Length of the secret key (default is 64).
    :return: A securely generated random string.
    """
    if length < 32:
        raise ValueError("Key length should be at least 32 characters for security.")
    return secrets.token_hex(length // 2)
