"""Tests for authentication routes."""
import json
import pytest


class TestRegister:
    """Tests for POST /api/auth/register."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'testuser'

    def test_register_missing_fields(self, client):
        """Test registration with missing fields."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'password123'
        })
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password123'
        })
        assert response.status_code == 409

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        client.post('/api/auth/register', json={
            'username': 'user1',
            'email': 'same@example.com',
            'password': 'password123'
        })
        response = client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'same@example.com',
            'password': 'password123'
        })
        assert response.status_code == 409

    def test_register_invalid_role(self, client):
        """Test registration with invalid role."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'superadmin'
        })
        assert response.status_code == 400

    def test_register_admin_role(self, client):
        """Test registration with admin role."""
        response = client.post('/api/auth/register', json={
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password': 'password123',
            'role': 'admin'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['user']['role'] == 'admin'


class TestLogin:
    """Tests for POST /api/auth/login."""

    def _create_user(self, client):
        client.post('/api/auth/register', json={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'password123'
        })

    def test_login_success(self, client):
        """Test successful login."""
        self._create_user(client)
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['user']['username'] == 'loginuser'

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        self._create_user(client)
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/api/auth/login', json={
            'username': 'nouser',
            'password': 'password123'
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400


class TestHealthCheck:
    """Tests for GET /health."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestProtectedRoutes:
    """Tests for protected route access."""

    def _get_token(self, client):
        client.post('/api/auth/register', json={
            'username': 'authuser',
            'email': 'auth@example.com',
            'password': 'password123'
        })
        response = client.post('/api/auth/login', json={
            'username': 'authuser',
            'password': 'password123'
        })
        return response.get_json()['token']

    def test_access_with_valid_token(self, client):
        """Test accessing protected route with valid token."""
        token = self._get_token(client)
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200

    def test_access_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401

    def test_access_with_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        response = client.get('/api/auth/me', headers={
            'Authorization': 'Bearer invalidtoken123'
        })
        assert response.status_code == 401
