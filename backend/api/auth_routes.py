"""Authentication API routes."""
from flask import Blueprint, request, jsonify
from models.database import db
from models.database.user import User
from models.database.user_history import UserHistory
from utils.auth import jwt_required, admin_required, create_access_token
from utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields', 'required': required_fields}), 400

        username = data['username']
        email = data['email']
        password = data['password']
        role = data.get('role', 'normal')

        # Validate role
        if role not in ['admin', 'normal']:
            return jsonify({'error': 'Invalid role', 'message': 'Role must be either "admin" or "normal"'}), 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'User already exists', 'message': 'Username already taken'}), 409

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists', 'message': 'Email already registered'}), 409

        # Create new user
        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        # Create registration history entry
        history_entry = UserHistory(
            user_id=new_user.id,
            action_type='registration',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            action_details={'role': role}
        )
        db.session.add(history_entry)
        db.session.commit()

        logger.info(f'New user registered: {username} ({role})')

        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f'Registration error: {str(e)}')
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing credentials', 'message': 'Username and password required'}), 400

        username = data['username']
        password = data['password']

        # Find user
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials', 'message': 'Invalid username or password'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account disabled', 'message': 'Your account has been disabled'}), 403

        # Generate JWT token
        token, expires_in = create_access_token(user.id, user.username, user.role)

        # Update last login
        user.update_last_login()

        # Create login history entry
        history_entry = UserHistory(
            user_id=user.id,
            action_type='login',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(history_entry)
        db.session.commit()

        logger.info(f'User logged in: {username}')

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'expires_in': expires_in,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Login error: {str(e)}')
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """Logout user (client should remove token)."""
    try:
        user = request.current_user

        # Create logout history entry
        history_entry = UserHistory(
            user_id=user['user_id'],
            action_type='logout',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(history_entry)
        db.session.commit()

        logger.info(f"User logged out: {user['username']}")

        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Logout error: {str(e)}')
        return jsonify({'error': 'Logout failed', 'message': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user_info():
    """Get current user information."""
    try:
        user_data = request.current_user
        user = User.query.get(user_data['user_id'])

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        logger.error(f'Get user info error: {str(e)}')
        return jsonify({'error': 'Failed to get user info', 'message': str(e)}), 500


@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)."""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        }), 200

    except Exception as e:
        logger.error(f'Get users error: {str(e)}')
        return jsonify({'error': 'Failed to get users', 'message': str(e)}), 500


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get specific user by ID (admin only)."""
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict(include_sensitive=True)}), 200

    except Exception as e:
        logger.error(f'Get user error: {str(e)}')
        return jsonify({'error': 'Failed to get user', 'message': str(e)}), 500


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user (admin only)."""
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'email' in data:
            user.email = data['email']
        if 'role' in data and data['role'] in ['admin', 'normal']:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']

        db.session.commit()

        logger.info(f"User updated: {user.username} by admin")

        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict(include_sensitive=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Update user error: {str(e)}')
        return jsonify({'error': 'Failed to update user', 'message': str(e)}), 500


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)."""
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        username = user.username
        db.session.delete(user)
        db.session.commit()

        logger.info(f"User deleted: {username} by admin")

        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Delete user error: {str(e)}')
        return jsonify({'error': 'Failed to delete user', 'message': str(e)}), 500
