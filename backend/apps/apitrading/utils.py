from cryptography.fernet import Fernet
from django.conf import settings

# Initialiser Fernet avec la clé de chiffrement
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_key(key):
    """Chiffre une clé API."""
    return fernet.encrypt(key.encode()).decode()

def decrypt_key(encrypted_key):
    """Déchiffre une clé API."""
    return fernet.decrypt(encrypted_key.encode()).decode()
