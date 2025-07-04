import logging

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import os

ENCRYPTION_KEY = b64decode(os.getenv("ENCRYPTION_KEY"))

BLOCK_SIZE = 16

def pad(data: bytes) -> bytes:
    padding_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([padding_len]) * padding_len

def unpad(data: bytes) -> bytes:
    padding_len = data[-1]
    return data[:-padding_len]

def encrypt_string(plain_text: str) -> str:
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plain_text.encode()))
    iv = b64encode(cipher.iv).decode()
    ct = b64encode(ct_bytes).decode()
    return f"{iv}:{ct}"

def decrypt_string(encrypted_data: str) -> str:
    iv, ct = encrypted_data.split(":")
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, b64decode(iv))
    pt = unpad(cipher.decrypt(b64decode(ct)))
    return pt.decode()
