"""API routes for lifestyle risk prediction."""
from flask import Blueprint, request, jsonify
import asyncio
from agents.lifestyle_agent import LifestyleAgent
from utils.logger import get_logger

logger = get_logger(__name__)

lifestyle_bp = Blueprint('lifestyle', __name__)
lifestyle_agent = LifestyleAgent()


@lifestyle_bp.route('/predict', methods=['POST'])
def predict_lifestyle_risk():
    """
    Predict diabetes risk from lifestyle and demographic data.

    Expected input (JSON):
    {
        "age": 45,
        "bmi": 28.5,
        "physical_activity": 120,  # minutes per week
        "sleep_hours": 6.5,
        "family_history": true,
        "smoking": false,
        "diet_quality": 6,
        "gender": "male"
    }

    Returns:
    - JSON with risk prediction and key factors
    """
    try:
        # Get JSON data
        lifestyle_data = request.get_json()

        if not lifestyle_data:
            return jsonify({'error': 'No lifestyle data provided'}), 400

        # Validate required fields
        if 'age' not in lifestyle_data:
            return jsonify({'error': 'Age is required'}), 400

        logger.info(f"Processing lifestyle prediction for age: {lifestyle_data.get('age')}")

        # Run lifestyle analysis
        task = {'lifestyle_data': lifestyle_data}

        # Run async agent in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(lifestyle_agent.execute(task))
        loop.close()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Lifestyle prediction endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500
