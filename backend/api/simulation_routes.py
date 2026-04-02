"""API routes for what-if simulations."""
from flask import Blueprint, request, jsonify
import asyncio
from agents.simulation_agent import SimulationAgent
from utils.logger import get_logger

logger = get_logger(__name__)

simulation_bp = Blueprint('simulation', __name__)
simulation_agent = SimulationAgent()


@simulation_bp.route('/create', methods=['POST'])
def create_simulations():
    """
    Create what-if simulations for lifestyle interventions.

    Expected input (JSON):
    {
        "risk_score": 0.65,
        "lifestyle_data": {...},
        "risk_factors": [...]
    }

    Returns:
    - JSON with simulation scenarios showing potential risk reduction
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if 'risk_score' not in data:
            return jsonify({'error': 'Risk score is required'}), 400

        logger.info(f"Creating simulations for risk score: {data.get('risk_score')}")

        # Run simulation agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(simulation_agent.execute(data))
        loop.close()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Simulation endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/compare', methods=['POST'])
def compare_interventions():
    """
    Compare multiple intervention scenarios side-by-side.

    Expected input (JSON):
    {
        "risk_score": 0.65,
        "interventions": ["weight_loss", "exercise", "diet"]
    }

    Returns:
    - JSON with comparison of interventions
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        risk_score = data.get('risk_score', 0.5)
        interventions = data.get('interventions', [])

        logger.info(f"Comparing {len(interventions)} interventions")

        # Create comparison
        comparison = {
            'current_risk': risk_score,
            'interventions': []
        }

        # Run simulations for each intervention
        # This is simplified - you can extend with actual simulation logic
        for intervention in interventions:
            # Placeholder comparison
            comparison['interventions'].append({
                'name': intervention,
                'projected_risk': risk_score * 0.8,  # Example reduction
                'effort_level': 'moderate'
            })

        return jsonify(comparison), 200

    except Exception as e:
        logger.error(f"Comparison endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500
