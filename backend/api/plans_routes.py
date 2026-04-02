"""Health plans API routes."""
from flask import Blueprint, request, jsonify
from models.database import db
from models.database.health_plan import HealthPlan
from utils.auth import jwt_required
from utils.logger import get_logger

logger = get_logger(__name__)

plans_bp = Blueprint('plans', __name__)


@plans_bp.route('/create', methods=['POST'])
@jwt_required
def create_plan():
    """Create new health plan."""
    try:
        user = request.current_user
        data = request.get_json()

        plan = HealthPlan(
            user_id=user['user_id'],
            plan_name=data['plan_name'],
            plan_type=data['plan_type'],
            description=data.get('description'),
            scenario_parameters=data.get('scenario_parameters'),
            expected_outcomes=data.get('expected_outcomes'),
            target_date=data.get('target_date'),
            milestones=data.get('milestones')
        )

        # Add plan to session first
        db.session.add(plan)

        # If this is marked as primary or user has no plans, set as primary
        if data.get('is_primary') or not HealthPlan.query.filter_by(user_id=user['user_id']).first():
            # Deactivate all other primary plans for this user
            HealthPlan.query.filter_by(user_id=user['user_id'], is_primary=True).update({'is_primary': False})
            plan.is_primary = True

        db.session.commit()

        logger.info(f"Health plan created for user {user['user_id']}: {plan.plan_name}")

        return jsonify({
            'message': 'Plan created successfully',
            'plan': plan.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating plan: {str(e)}")
        return jsonify({'error': 'Failed to create plan', 'message': str(e)}), 500


@plans_bp.route('/my-plans', methods=['GET'])
@jwt_required
def get_my_plans():
    """Get all plans for current user."""
    try:
        user = request.current_user

        plans = HealthPlan.query.filter_by(user_id=user['user_id']).order_by(
            HealthPlan.is_primary.desc(),
            HealthPlan.created_at.desc()
        ).all()

        return jsonify({
            'plans': [plan.to_dict() for plan in plans],
            'total': len(plans)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving plans: {str(e)}")
        return jsonify({'error': 'Failed to get plans', 'message': str(e)}), 500


@plans_bp.route('/primary', methods=['GET'])
@jwt_required
def get_primary_plan():
    """Get active primary plan."""
    try:
        user = request.current_user

        plan = HealthPlan.query.filter_by(
            user_id=user['user_id'],
            is_primary=True
        ).first()

        if not plan:
            return jsonify({'message': 'No primary plan set'}), 404

        return jsonify({
            'plan': plan.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving primary plan: {str(e)}")
        return jsonify({'error': 'Failed to get primary plan', 'message': str(e)}), 500


@plans_bp.route('/<int:plan_id>/set-primary', methods=['PUT'])
@jwt_required
def set_primary_plan(plan_id):
    """Set plan as primary."""
    try:
        user = request.current_user

        plan = HealthPlan.query.filter_by(id=plan_id, user_id=user['user_id']).first()

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        plan.set_as_primary()

        logger.info(f"Plan {plan_id} set as primary for user {user['user_id']}")

        return jsonify({
            'message': 'Plan set as primary',
            'plan': plan.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error setting primary plan: {str(e)}")
        return jsonify({'error': 'Failed to set primary plan', 'message': str(e)}), 500


@plans_bp.route('/<int:plan_id>/progress', methods=['PUT'])
@jwt_required
def update_progress(plan_id):
    """Update plan progress."""
    try:
        user = request.current_user
        data = request.get_json()

        plan = HealthPlan.query.filter_by(id=plan_id, user_id=user['user_id']).first()

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        progress_value = data.get('progress', 0)
        plan.update_progress(progress_value)

        db.session.commit()

        logger.info(f"Plan {plan_id} progress updated to {progress_value}%")

        return jsonify({
            'message': 'Progress updated',
            'plan': plan.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating progress: {str(e)}")
        return jsonify({'error': 'Failed to update progress', 'message': str(e)}), 500


@plans_bp.route('/<int:plan_id>/checkpoint', methods=['POST'])
@jwt_required
def add_checkpoint(plan_id):
    """Add progress checkpoint."""
    try:
        user = request.current_user
        data = request.get_json()

        plan = HealthPlan.query.filter_by(id=plan_id, user_id=user['user_id']).first()

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        checkpoint_data = data.get('checkpoint_data', {})
        plan.add_checkpoint(checkpoint_data)

        db.session.commit()

        logger.info(f"Checkpoint added to plan {plan_id}")

        return jsonify({
            'message': 'Checkpoint added',
            'plan': plan.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding checkpoint: {str(e)}")
        return jsonify({'error': 'Failed to add checkpoint', 'message': str(e)}), 500


@plans_bp.route('/<int:plan_id>', methods=['GET'])
@jwt_required
def get_plan(plan_id):
    """Get specific plan."""
    try:
        user = request.current_user

        plan = HealthPlan.query.filter_by(id=plan_id, user_id=user['user_id']).first()

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        return jsonify({
            'plan': plan.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving plan: {str(e)}")
        return jsonify({'error': 'Failed to get plan', 'message': str(e)}), 500


@plans_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required
def update_plan(plan_id):
    """Update plan details."""
    try:
        user = request.current_user
        data = request.get_json()

        plan = HealthPlan.query.filter_by(id=plan_id, user_id=user['user_id']).first()

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        # Update fields
        if 'plan_name' in data:
            plan.plan_name = data['plan_name']
        if 'description' in data:
            plan.description = data['description']
        if 'status' in data:
            plan.status = data['status']
        if 'target_date' in data:
            plan.target_date = data['target_date']
        if 'milestones' in data:
            plan.milestones = data['milestones']

        db.session.commit()

        logger.info(f"Plan {plan_id} updated")

        return jsonify({
            'message': 'Plan updated',
            'plan': plan.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating plan: {str(e)}")
        return jsonify({'error': 'Failed to update plan', 'message': str(e)}), 500


@plans_bp.route('/<int:plan_id>', methods=['DELETE'])
@jwt_required
def delete_plan(plan_id):
    """Delete plan."""
    try:
        user = request.current_user

        plan = HealthPlan.query.filter_by(id=plan_id, user_id=user['user_id']).first()

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        db.session.delete(plan)
        db.session.commit()

        logger.info(f"Plan {plan_id} deleted")

        return jsonify({'message': 'Plan deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting plan: {str(e)}")
        return jsonify({'error': 'Failed to delete plan', 'message': str(e)}), 500
