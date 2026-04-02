"""Tests for JWT utility functions."""
import os
import time
import pytest
import jwt as pyjwt

os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_ACCESS_TOKEN_EXPIRES'] = '3600'

from utils.auth.jwt_utils import create_access_token, verify_token


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_returns_token_and_expiry(self):
        """Test that token and expiry are returned."""
        token, expires_in = create_access_token(1, 'testuser', 'normal')
        assert isinstance(token, str)
        assert len(token) > 0
        assert expires_in == 3600

    def test_token_contains_user_info(self):
        """Test that token payload contains user info."""
        token, _ = create_access_token(42, 'john', 'admin')
        secret = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
        payload = pyjwt.decode(token, secret, algorithms=['HS256'])
        assert payload['user_id'] == 42
        assert payload['username'] == 'john'
        assert payload['role'] == 'admin'

    def test_token_has_expiration(self):
        """Test that token has exp claim."""
        token, _ = create_access_token(1, 'testuser', 'normal')
        secret = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
        payload = pyjwt.decode(token, secret, algorithms=['HS256'])
        assert 'exp' in payload
        assert 'iat' in payload


class TestVerifyToken:
    """Tests for verify_token function."""

    def test_valid_token(self):
        """Test verifying a valid token."""
        token, _ = create_access_token(1, 'testuser', 'normal')
        payload = verify_token(token)
        assert payload is not None
        assert payload['user_id'] == 1
        assert payload['username'] == 'testuser'

    def test_expired_token(self):
        """Test verifying an expired token."""
        secret = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
        import datetime
        payload = {
            'user_id': 1,
            'username': 'testuser',
            'role': 'normal',
            'exp': datetime.datetime.utcnow() - datetime.timedelta(seconds=10),
            'iat': datetime.datetime.utcnow() - datetime.timedelta(seconds=100)
        }
        token = pyjwt.encode(payload, secret, algorithm='HS256')
        result = verify_token(token)
        assert result is None

    def test_invalid_token_string(self):
        """Test verifying a random invalid string."""
        result = verify_token('not-a-valid-token')
        assert result is None

    def test_tampered_token(self):
        """Test verifying a token signed with wrong key."""
        import datetime
        payload = {
            'user_id': 1,
            'username': 'testuser',
            'role': 'normal',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
            'iat': datetime.datetime.utcnow()
        }
        token = pyjwt.encode(payload, 'wrong-secret-key', algorithm='HS256')
        result = verify_token(token)
        assert result is None

    def test_empty_token(self):
        """Test verifying an empty string."""
        result = verify_token('')
        assert result is None
