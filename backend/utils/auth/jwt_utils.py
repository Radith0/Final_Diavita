"""JWT token utilities."""
from datetime import datetime, timedelta
from functools import wraps
import jwt
import os
from flask import request, jsonify


def create_access_token(user_id, username, role):
    """Create JWT access token for user."""
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    expires_in = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token, expires_in


def verify_token(token):
    """Verify and decode JWT token."""
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """Extract user information from request token."""
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None

    try:
        # Expected format: "Bearer <token>"
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        payload = verify_token(token)
        return payload
    except (IndexError, AttributeError):
        return None