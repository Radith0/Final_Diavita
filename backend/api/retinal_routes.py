"""API routes for retinal image analysis."""
from flask import Blueprint, request, jsonify
import asyncio
from agents.retinal_agent import RetinalAgent
from models.retinal.preprocessing import validate_image_quality
from utils.logger import get_logger

logger = get_logger(__name__)

retinal_bp = Blueprint('retinal', __name__)
retinal_agent = RetinalAgent()


@retinal_bp.route('/analyze', methods=['POST'])
def analyze_retinal_image():
    """
    Analyze uploaded retinal image for diabetic retinopathy.

    Expected input:
    - multipart/form-data with 'image' file

    Returns:
    - JSON with DR detection results
    """
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        # Read image bytes
        image_bytes = image_file.read()

        # Validate image quality
        validation = validate_image_quality(image_bytes)
        if not validation['is_valid']:
            return jsonify({
                'error': 'Invalid image',
                'details': validation
            }), 400

        # Run retinal analysis
        logger.info(f"Processing retinal image: {image_file.filename}")
        task = {'image': image_bytes}

        # Run async agent in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(retinal_agent.execute(task))
        loop.close()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Retinal analysis endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@retinal_bp.route('/validate', methods=['POST'])
def validate_image():
    """
    Validate retinal image without full analysis.

    Returns:
    - JSON with image quality validation results
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        image_bytes = image_file.read()

        validation = validate_image_quality(image_bytes)

        return jsonify(validation), 200

    except Exception as e:
        logger.error(f"Image validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500
