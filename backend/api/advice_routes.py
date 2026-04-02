"""API routes for LLM-based advice generation."""
from flask import Blueprint, request, jsonify
import asyncio
from agents.llm_agent import LLMAgent
from agents.orchestrator import DiabetesOrchestrator
from utils.logger import get_logger

logger = get_logger(__name__)

advice_bp = Blueprint('advice', __name__)
llm_agent = LLMAgent()
orchestrator = DiabetesOrchestrator()


@advice_bp.route('/generate', methods=['POST'])
def generate_advice():
    """
    Generate personalized advice based on risk assessment.

    Expected input (JSON):
    {
        "risk_score": 0.65,
        "risk_factors": [...],
        "lifestyle_data": {...},
        "retinal_findings": {...}
    }

    Returns:
    - JSON with personalized recommendations
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        logger.info(f"Generating advice for risk score: {data.get('risk_score')}")

        # Run LLM advice generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(llm_agent.execute(data))
        loop.close()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Advice generation endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@advice_bp.route('/complete-analysis', methods=['POST'])
def complete_analysis():
    """
    Complete end-to-end diabetes detection and advice generation.

    Expected input (multipart/form-data):
    - image: retinal image file
    - lifestyle_data: JSON string with lifestyle information

    Returns:
    - Complete analysis with risk assessment, advice, and simulations
    """
    try:
        # Get image
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        image_bytes = image_file.read()

        # Get lifestyle data
        lifestyle_json = request.form.get('lifestyle_data')
        if not lifestyle_json:
            return jsonify({'error': 'No lifestyle data provided'}), 400

        import json
        lifestyle_data = json.loads(lifestyle_json)

        logger.info("Running complete diabetes detection analysis")

        # Build task for orchestrator
        task = {
            'image': image_bytes,
            'lifestyle_data': lifestyle_data,
            'user_id': request.form.get('user_id', 'anonymous')
        }

        # Run orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.execute(task))
        loop.close()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Complete analysis endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500
