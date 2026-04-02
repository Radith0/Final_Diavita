"""Authentication decorators for route protection."""
from functools import wraps
from flask import request, jsonify
from .jwt_utils import get_current_user
from models.database import db
from models.database.user_history import UserHistory


def jwt_required(f):
    """Decorator to require valid JWT token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not user:
            return jsonify({'error': 'Authentication required', 'message': 'Invalid or missing token'}), 401

        # Add user info to request context
        request.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not user:
            return jsonify({'error': 'Authentication required', 'message': 'Invalid or missing token'}), 401

        if user.get('role') != 'admin':
            return jsonify({'error': 'Forbidden', 'message': 'Admin access required'}), 403

        # Add user info to request context
        request.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def track_user_action(action_type):
    """Decorator to track user actions in history."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            result = f(*args, **kwargs)

            # Track the action if user is authenticated
            user = getattr(request, 'current_user', None)
            if user:
                try:
                    history_entry = UserHistory(
                        user_id=user.get('user_id'),
                        action_type=action_type,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent'),
                        action_details={
                            'endpoint': request.endpoint,
                            'method': request.method,
                            'path': request.path
                        }
                    )
                    db.session.add(history_entry)
                    db.session.commit()
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Error tracking user action: {e}")
                    db.session.rollback()

            return result

        return decorated_function
    return decorator