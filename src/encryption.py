import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Fixed application-wide salt. Changing this will invalidate all stored entries.
_SALT = b'C\xb7\xfa\xb8\x1c\xd1v\xcb]\xa2QtX<P\xb7'


def derive_pass(password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('ascii')))


def encrypt_message(message, pwd):
    key = derive_pass(pwd)
    return Fernet(key).encrypt(message.encode())


def decrypt_message(encrypted_message, pwd):
    key = derive_pass(pwd)
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_message.encode('ascii')).decode()
    except InvalidToken:
        return 'Wrong password'
