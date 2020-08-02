from cryptography.fernet import Fernet

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
password = b"password"

def derive_pass(password, salt=b'C\xb7\xfa\xb8\x1c\xd1v\xcb]\xa2QtX<P\xb7'):
    password=password.encode('ascii')
    #salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_message(message, pwd):
    """
    Encrypts a message
    """
    key=derive_pass(pwd)
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message

def decrypt_message(encrypted_message, pwd):
    """
    Decrypts an encrypted message
    """
    key=derive_pass(pwd)
    f = Fernet(key)
    try:
        encrypted_message=encrypted_message.encode('ascii')

        decrypted_message = f.decrypt(encrypted_message)

        res=decrypted_message.decode()
    except:
        res='Wrong password'
    return res

def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()