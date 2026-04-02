"""Analysis results API routes."""
from flask import Blueprint, request, jsonify
from models.database import db
from models.database.analysis_result import AnalysisResult
from utils.auth import jwt_required, admin_required
from utils.logger import get_logger

logger = get_logger(__name__)

results_bp = Blueprint('results', __name__)


@results_bp.route('/save', methods=['POST'])
@jwt_required
def save_analysis_result():
    """Save analysis result for user."""
    try:
        user = request.current_user
        data = request.get_json()

        # Create new analysis result
        result = AnalysisResult(
            user_id=user['user_id'],
            analysis_type=data.get('analysis_type', 'complete'),
            retinal_risk=data.get('retinal_risk'),
            lifestyle_risk=data.get('lifestyle_risk'),
            combined_risk=data.get('combined_risk'),
            confidence_score=data.get('confidence_score'),
            lifestyle_data=data.get('lifestyle_data'),
            detailed_results=data.get('detailed_results'),
            recommendations=data.get('recommendations'),
            retinal_image_path=data.get('retinal_image_path')
        )

        # Calculate risk category
        result.risk_category = result.calculate_risk_category()

        db.session.add(result)
        db.session.commit()

        logger.info(f"Analysis result saved for user {user['user_id']}")

        return jsonify({
            'message': 'Analysis result saved successfully',
            'result': result.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving analysis result: {str(e)}")
        return jsonify({'error': 'Failed to save result', 'message': str(e)}), 500


@results_bp.route('/my-results', methods=['GET'])
@jwt_required
def get_my_results():
    """Get all analysis results for current user."""
    try:
        user = request.current_user
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = AnalysisResult.query.filter_by(user_id=user['user_id']).order_by(
            AnalysisResult.analysis_date.desc()
        )

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'results': [result.to_dict() for result in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}")
        return jsonify({'error': 'Failed to get results', 'message': str(e)}), 500


@results_bp.route('/latest', methods=['GET'])
@jwt_required
def get_latest_result():
    """Get latest analysis result for current user."""
    try:
        user = request.current_user

        result = AnalysisResult.query.filter_by(user_id=user['user_id']).order_by(
            AnalysisResult.analysis_date.desc()
        ).first()

        if not result:
            return jsonify({'message': 'No analysis results found'}), 404

        return jsonify({
            'result': result.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving latest result: {str(e)}")
        return jsonify({'error': 'Failed to get latest result', 'message': str(e)}), 500


@results_bp.route('/<int:result_id>', methods=['GET'])
@jwt_required
def get_result_by_id(result_id):
    """Get specific analysis result."""
    try:
        user = request.current_user

        result = AnalysisResult.query.filter_by(id=result_id, user_id=user['user_id']).first()

        if not result:
            return jsonify({'error': 'Result not found'}), 404

        return jsonify({
            'result': result.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving result: {str(e)}")
        return jsonify({'error': 'Failed to get result', 'message': str(e)}), 500


@results_bp.route('/summary', methods=['GET'])
@jwt_required
def get_results_summary():
    """Get summary of all results for current user."""
    try:
        user = request.current_user

        results = AnalysisResult.query.filter_by(user_id=user['user_id']).order_by(
            AnalysisResult.analysis_date.desc()
        ).all()

        if not results:
            return jsonify({
                'total_analyses': 0,
                'latest_risk': None,
                'risk_trend': None,
                'analyses': []
            }), 200

        # Calculate statistics
        latest_result = results[0]
        risk_values = [r.combined_risk for r in results if r.combined_risk is not None]

        trend = None
        if len(risk_values) >= 2:
            if risk_values[0] < risk_values[1]:
                trend = 'improving'
            elif risk_values[0] > risk_values[1]:
                trend = 'worsening'
            else:
                trend = 'stable'

        return jsonify({
            'total_analyses': len(results),
            'latest_risk': latest_result.combined_risk,
            'latest_category': latest_result.risk_category or latest_result.calculate_risk_category(),
            'risk_trend': trend,
            'analyses': [r.to_summary_dict() for r in results]
        }), 200

    except Exception as e:
        logger.error(f"Error getting results summary: {str(e)}")
        return jsonify({'error': 'Failed to get summary', 'message': str(e)}), 500


@results_bp.route('/<int:result_id>', methods=['DELETE'])
@jwt_required
def delete_result(result_id):
    """Delete an analysis result."""
    try:
        user = request.current_user

        result = AnalysisResult.query.filter_by(id=result_id, user_id=user['user_id']).first()

        if not result:
            return jsonify({'error': 'Result not found'}), 404

        db.session.delete(result)
        db.session.commit()

        logger.info(f"Result {result_id} deleted by user {user['user_id']}")

        return jsonify({'message': 'Result deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting result: {str(e)}")
        return jsonify({'error': 'Failed to delete result', 'message': str(e)}), 500


# Admin routes
@results_bp.route('/all', methods=['GET'])
@admin_required
def get_all_results():
    """Get all analysis results (admin only)."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = AnalysisResult.query.order_by(AnalysisResult.analysis_date.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'results': [result.to_dict() for result in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving all results: {str(e)}")
        return jsonify({'error': 'Failed to get results', 'message': str(e)}), 500
