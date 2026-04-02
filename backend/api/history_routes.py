"""User history API routes."""
from flask import Blueprint, request, jsonify
from models.database import db
from models.database.user_history import UserHistory
from utils.auth import jwt_required, admin_required
from utils.logger import get_logger

logger = get_logger(__name__)

history_bp = Blueprint('history', __name__)


@history_bp.route('/my-history', methods=['GET'])
@jwt_required
def get_my_history():
    """Get current user's history."""
    try:
        user = request.current_user
        user_id = user['user_id']

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_type = request.args.get('action_type', None)

        # Build query
        query = UserHistory.query.filter_by(user_id=user_id)

        if action_type:
            query = query.filter_by(action_type=action_type)

        # Order by most recent
        query = query.order_by(UserHistory.timestamp.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'history': [entry.to_dict() for entry in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        logger.error(f'Get user history error: {str(e)}')
        return jsonify({'error': 'Failed to get history', 'message': str(e)}), 500


@history_bp.route('/users/<int:user_id>/history', methods=['GET'])
@admin_required
def get_user_history(user_id):
    """Get specific user's history (admin only)."""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_type = request.args.get('action_type', None)

        # Build query
        query = UserHistory.query.filter_by(user_id=user_id)

        if action_type:
            query = query.filter_by(action_type=action_type)

        # Order by most recent
        query = query.order_by(UserHistory.timestamp.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'user_id': user_id,
            'history': [entry.to_dict() for entry in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        logger.error(f'Get user history error: {str(e)}')
        return jsonify({'error': 'Failed to get history', 'message': str(e)}), 500


@history_bp.route('/all-history', methods=['GET'])
@admin_required
def get_all_history():
    """Get all users' history (admin only)."""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_type = request.args.get('action_type', None)

        # Build query
        query = UserHistory.query

        if action_type:
            query = query.filter_by(action_type=action_type)

        # Order by most recent
        query = query.order_by(UserHistory.timestamp.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'history': [entry.to_dict() for entry in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        logger.error(f'Get all history error: {str(e)}')
        return jsonify({'error': 'Failed to get history', 'message': str(e)}), 500


@history_bp.route('/stats', methods=['GET'])
@jwt_required
def get_my_stats():
    """Get current user's activity statistics."""
    try:
        user = request.current_user
        user_id = user['user_id']

        # Get action type counts
        from sqlalchemy import func
        action_counts = db.session.query(
            UserHistory.action_type,
            func.count(UserHistory.id).label('count')
        ).filter_by(user_id=user_id).group_by(UserHistory.action_type).all()

        stats = {
            'action_counts': {action: count for action, count in action_counts},
            'total_actions': sum(count for _, count in action_counts)
        }

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f'Get user stats error: {str(e)}')
        return jsonify({'error': 'Failed to get stats', 'message': str(e)}), 500


@history_bp.route('/users/<int:user_id>/stats', methods=['GET'])
@admin_required
def get_user_stats(user_id):
    """Get specific user's activity statistics (admin only)."""
    try:
        # Get action type counts
        from sqlalchemy import func
        action_counts = db.session.query(
            UserHistory.action_type,
            func.count(UserHistory.id).label('count')
        ).filter_by(user_id=user_id).group_by(UserHistory.action_type).all()

        stats = {
            'user_id': user_id,
            'action_counts': {action: count for action, count in action_counts},
            'total_actions': sum(count for _, count in action_counts)
        }

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f'Get user stats error: {str(e)}')
        return jsonify({'error': 'Failed to get stats', 'message': str(e)}), 500
