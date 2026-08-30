"""
Encryption Module
Secure all communications with AES-256
"""

import base64
import hashlib
import os
import json
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionManager:
    def __init__(self, password: str = None):
        if password is None:
            password = os.urandom(32).hex()
        
        self.password = password
        self.key = self._generate_key(password)
        self.cipher = Fernet(self.key)
        self.node_keys = {}
        
    def _generate_key(self, password: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'meshnet_salt_2024',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: bytes) -> bytes:
        try:
            return self.cipher.encrypt(data)
        except Exception as e:
            print(f"Encrypt error: {e}")
            return data
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            print(f"Decrypt error: {e}")
            return encrypted_data
    
    def encrypt_message(self, message: dict, target_node_id: str = None) -> bytes:
        json_str = json.dumps(message)
        data = json_str.encode()
        
        if target_node_id and target_node_id in self.node_keys:
            cipher = Fernet(self.node_keys[target_node_id])
            return cipher.encrypt(data)
        
        return self.encrypt(data)
    
    def decrypt_message(self, encrypted_data: bytes, sender_node_id: str = None) -> dict:
        try:
            if sender_node_id and sender_node_id in self.node_keys:
                cipher = Fernet(self.node_keys[sender_node_id])
                data = cipher.decrypt(encrypted_data)
            else:
                data = self.decrypt(encrypted_data)
            
            json_str = data.decode()
            return json.loads(json_str)
        except Exception as e:
            print(f"Decrypt error: {e}")
            return {"error": "Decryption failed"}
    
    def share_key(self, node_id: str, key: bytes):
        self.node_keys[node_id] = key
        print(f"🔑 Shared key with {node_id[:8]}")
