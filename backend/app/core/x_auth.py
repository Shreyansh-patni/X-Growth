import hashlib
import base64
import os
import secrets

def generate_pkce_pair():
    """Generates a PKCE code_verifier and code_challenge."""
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode().rstrip("=")
    return code_verifier, code_challenge

def create_state():
    return secrets.token_urlsafe(32)
