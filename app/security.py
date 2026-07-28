from cryptography.fernet import Fernet

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KEY_FILE = os.path.join(BASE_DIR, "..", "data", "secret.key")


def load_key():

    key_dir = os.path.dirname(KEY_FILE)

    if key_dir and not os.path.exists(key_dir):
        os.makedirs(key_dir, exist_ok=True)

    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as file:
            file.write(key)

    with open(KEY_FILE, "rb") as file:
        return file.read()


key = load_key()

cipher = Fernet(key)


def encrypt(password):
    return cipher.encrypt(password.encode()).decode()


def decrypt(password):
    return cipher.decrypt(password.encode()).decode()