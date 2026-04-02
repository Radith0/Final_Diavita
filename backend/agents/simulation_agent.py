"""What-if simulation agent for behavior change modeling."""
import time
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class SimulationAgent(BaseAgent):
    """Agent responsible for creating what-if simulations."""

    def __init__(self):
        """Initialize simulation agent."""
        super().__init__(agent_id="simulation_agent")
        logger.info("SimulationAgent initialized")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create what-if simulations showing impact of lifestyle changes.

        Args:
            task: Dict containing:
                - risk_score: Current risk score
                - lifestyle_data: User's current lifestyle
                - risk_factors: Identified modifiable risk factors

        Returns:
            List of simulations showing potential risk reduction
        """
        try:
            start_time = time.time()

            risk_score = task.get('risk_score', 0.5)
            lifestyle_data = task.get('lifestyle_data', {})
            risk_factors = task.get('risk_factors', [])

            logger.info(f"Creating simulations for risk score: {risk_score}")
            self.log_action("simulation_started", {"current_risk": risk_score})

            # Helper to safely convert to float
            def safe_float(value, default=0):
                if value == '' or value is None:
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default

            # Generate simulations for modifiable factors
            simulations = []

            # Get numeric values safely
            bmi = safe_float(lifestyle_data.get('bmi'), 0)
            physical_activity = safe_float(lifestyle_data.get('physical_activity'), 0)
            sleep_hours = safe_float(lifestyle_data.get('sleep_hours'), 8)

            # Simulation 1: Weight loss (if BMI is high)
            if bmi > 25:
                simulations.append(self._simulate_weight_loss(risk_score, bmi))

            # Simulation 2: Increased physical activity
            if physical_activity < 150:
                simulations.append(self._simulate_increased_activity(risk_score, physical_activity))

            # Simulation 3: Improved sleep
            if sleep_hours < 7:
                simulations.append(self._simulate_better_sleep(risk_score, sleep_hours))

            # Simulation 4: Dietary improvements
            simulations.append(self._simulate_healthy_diet(risk_score))

            # Simulation 5: Smoking cessation (if applicable)
            if lifestyle_data.get('smoking', False):
                simulations.append(self._simulate_quit_smoking(risk_score))

            # Simulation 6: Combined interventions
            simulations.append(self._simulate_combined_changes(risk_score, lifestyle_data))

            processing_time = time.time() - start_time

            result = {
                'status': 'success',
                'simulations': simulations,
                'current_risk': risk_score,
                'best_scenario': min(simulations, key=lambda x: x['projected_risk']),
                'processing_time': processing_time
            }

            logger.info(f"Generated {len(simulations)} simulations in {processing_time:.2f}s")
            self.log_action("simulation_complete", len(simulations))

            return result

        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            self.log_action("simulation_failed", str(e))
            return {
                'status': 'error',
                'error': str(e),
                'simulations': []
            }

    def _simulate_weight_loss(self, current_risk: float, current_bmi: float) -> Dict[str, Any]:
        """Simulate impact of 5-7% weight loss."""
        target_bmi = current_bmi * 0.93  # 7% reduction
        risk_reduction = 0.15  # Research shows ~15% risk reduction
        projected_risk = max(current_risk - risk_reduction, 0.0)

        return {
            'intervention': 'Weight Loss',
            'description': f'Reduce BMI from {current_bmi:.1f} to {target_bmi:.1f} (7% reduction)',
            'action_items': [
                'Create a caloric deficit of 500 calories/day',
                'Combine dietary changes with increased physical activity',
                'Set realistic goal of 1-2 lbs weight loss per week',
                'Track progress weekly'
            ],
            'current_risk': current_risk,
            'projected_risk': projected_risk,
            'risk_reduction_percent': ((current_risk - projected_risk) / current_risk * 100),
            'timeframe': '3-6 months',
            'difficulty': 'moderate',
            'impact': 'high'
        }

    def _simulate_increased_activity(self, current_risk: float, current_activity: float) -> Dict[str, Any]:
        """Simulate impact of meeting activity guidelines (150 min/week)."""
        target_activity = 150  # WHO recommendation
        risk_reduction = 0.10  # ~10% risk reduction
        projected_risk = max(current_risk - risk_reduction, 0.0)

        return {
            'intervention': 'Increased Physical Activity',
            'description': f'Increase weekly exercise from {current_activity} to {target_activity} minutes',
            'action_items': [
                'Start with 30 minutes of brisk walking 5 days/week',
                'Gradually increase intensity (cycling, swimming, jogging)',
                'Include strength training 2 days/week',
                'Use fitness tracker to monitor progress'
            ],
            'current_risk': current_risk,
            'projected_risk': projected_risk,
            'risk_reduction_percent': ((current_risk - projected_risk) / current_risk * 100),
            'timeframe': '2-3 months',
            'difficulty': 'moderate',
            'impact': 'moderate-high'
        }

    def _simulate_better_sleep(self, current_risk: float, current_sleep: float) -> Dict[str, Any]:
        """Simulate impact of improving sleep to 7-9 hours."""
        target_sleep = 7.5
        risk_reduction = 0.08
        projected_risk = max(current_risk - risk_reduction, 0.0)

        return {
            'intervention': 'Improved Sleep Quality',
            'description': f'Increase sleep from {current_sleep} to {target_sleep} hours per night',
            'action_items': [
                'Establish consistent sleep schedule (same bedtime/wake time)',
                'Create relaxing bedtime routine',
                'Limit screen time 1 hour before bed',
                'Optimize sleep environment (dark, cool, quiet)'
            ],
            'current_risk': current_risk,
            'projected_risk': projected_risk,
            'risk_reduction_percent': ((current_risk - projected_risk) / current_risk * 100),
            'timeframe': '1-2 months',
            'difficulty': 'easy-moderate',
            'impact': 'moderate'
        }

    def _simulate_healthy_diet(self, current_risk: float) -> Dict[str, Any]:
        """Simulate impact of adopting Mediterranean-style diet."""
        risk_reduction = 0.12
        projected_risk = max(current_risk - risk_reduction, 0.0)

        return {
            'intervention': 'Healthy Diet Adoption',
            'description': 'Adopt Mediterranean-style eating pattern',
            'action_items': [
                'Increase vegetables and fruits to 5+ servings/day',
                'Choose whole grains over refined carbohydrates',
                'Include healthy fats (olive oil, nuts, avocados)',
                'Limit processed foods and added sugars',
                'Reduce red meat consumption'
            ],
            'current_risk': current_risk,
            'projected_risk': projected_risk,
            'risk_reduction_percent': ((current_risk - projected_risk) / current_risk * 100),
            'timeframe': '3-4 months',
            'difficulty': 'moderate',
            'impact': 'high'
        }

    def _simulate_quit_smoking(self, current_risk: float) -> Dict[str, Any]:
        """Simulate impact of smoking cessation."""
        risk_reduction = 0.18  # Significant impact
        projected_risk = max(current_risk - risk_reduction, 0.0)

        return {
            'intervention': 'Smoking Cessation',
            'description': 'Quit smoking completely',
            'action_items': [
                'Consult healthcare provider for cessation support',
                'Consider nicotine replacement therapy',
                'Join smoking cessation program',
                'Identify and avoid triggers',
                'Build support system'
            ],
            'current_risk': current_risk,
            'projected_risk': projected_risk,
            'risk_reduction_percent': ((current_risk - projected_risk) / current_risk * 100),
            'timeframe': '6-12 months',
            'difficulty': 'hard',
            'impact': 'very high'
        }

    def _simulate_combined_changes(self, current_risk: float, lifestyle_data: Dict) -> Dict[str, Any]:
        """Simulate impact of multiple lifestyle changes combined."""
        # Combined effect is typically 1.5-2x individual changes (not linear addition)
        risk_reduction = 0.35  # Up to 35% risk reduction with comprehensive changes
        projected_risk = max(current_risk - risk_reduction, 0.0)

        return {
            'intervention': 'Comprehensive Lifestyle Change',
            'description': 'Implement multiple healthy lifestyle changes simultaneously',
            'action_items': [
                'Achieve and maintain healthy weight',
                'Meet physical activity guidelines (150+ min/week)',
                'Adopt Mediterranean diet pattern',
                'Ensure 7-9 hours quality sleep',
                'Quit smoking (if applicable)',
                'Manage stress through mindfulness/relaxation',
                'Regular health check-ups and monitoring'
            ],
            'current_risk': current_risk,
            'projected_risk': projected_risk,
            'risk_reduction_percent': ((current_risk - projected_risk) / current_risk * 100),
            'timeframe': '6-12 months',
            'difficulty': 'hard',
            'impact': 'very high',
            'note': 'Best outcomes achieved with gradual, sustainable changes'
        }
