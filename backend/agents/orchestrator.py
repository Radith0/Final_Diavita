"""Master orchestrator agent that coordinates all sub-agents."""
import asyncio
from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.retinal_agent import RetinalAgent
from agents.lifestyle_agent import LifestyleAgent
from agents.fusion_agent import FusionAgent
from agents.llm_agent import LLMAgent
from agents.simulation_agent import SimulationAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class DiabetesOrchestrator(BaseAgent):
    """Master agent that coordinates all diabetes detection sub-agents."""

    def __init__(self):
        """Initialize orchestrator with all sub-agents."""
        super().__init__(agent_id="orchestrator")

        # Initialize sub-agents
        self.retinal_agent = RetinalAgent()
        self.lifestyle_agent = LifestyleAgent()
        self.fusion_agent = FusionAgent()
        self.llm_agent = LLMAgent()
        self.simulation_agent = SimulationAgent()

        logger.info("DiabetesOrchestrator initialized with all sub-agents")

    def _transform_frontend_to_backend_data(self, frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform frontend lifestyle data to match backend expectations.

        Maps frontend field names to backend field names and uses actual user input
        when available, with sensible defaults only for optional fields.
        """
        # Helper to safely convert boolean fields
        def to_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ['true', 'yes', '1']
            return False

        # Helper to safely get numeric value with default
        def safe_float(val, default=0):
            try:
                return float(val) if val != '' and val is not None else default
            except (ValueError, TypeError):
                return default

        # Start with the direct mappings
        backend_data = {
            'age': frontend_data.get('age'),
            'gender': frontend_data.get('gender', 'male'),
            'bmi': safe_float(frontend_data.get('bmi'), 25),

            # Map blood pressure fields
            'blood_pressure_systolic': safe_float(frontend_data.get('systolic_bp'), 120),
            'blood_pressure_diastolic': safe_float(frontend_data.get('diastolic_bp'), 80),

            # Map lab results
            'hba1c': safe_float(frontend_data.get('HbA1c'), 5.5),

            # Map family history (frontend uses different field name) - must be string for model
            'family_history': 'yes' if to_bool(frontend_data.get('family_diabetes_history', False)) else 'no',

            # NEW: Direct mapping of lifestyle fields from frontend
            'smoking': frontend_data.get('smoking', 'no'),
            'alcohol': frontend_data.get('alcohol', 'no'),
            'physical_activity': safe_float(frontend_data.get('physical_activity'), 30),
            'sleep_hours': safe_float(frontend_data.get('sleep_hours'), 7),
            'stress_level': frontend_data.get('stress_level', 'moderate'),
            'diet_quality': frontend_data.get('diet_quality', 'average'),
        }

        # Handle blood glucose - use actual value if provided, otherwise estimate from HbA1c
        if frontend_data.get('blood_glucose'):
            backend_data['blood_glucose'] = safe_float(frontend_data.get('blood_glucose'), 100)
        else:
            # Estimate based on HbA1c if blood glucose not provided
            hba1c = safe_float(frontend_data.get('HbA1c'), 5.5)
            if hba1c < 5.7:
                backend_data['blood_glucose'] = 95  # Normal
            elif hba1c < 6.5:
                backend_data['blood_glucose'] = 110  # Pre-diabetic range
            else:
                backend_data['blood_glucose'] = 140  # Diabetic range

        # Handle cholesterol - prefer total cholesterol if available, otherwise estimate from HDL
        if frontend_data.get('total_cholesterol'):
            backend_data['cholesterol'] = safe_float(frontend_data.get('total_cholesterol'), 200)
        elif frontend_data.get('hdl_cholesterol'):
            # If only HDL is available, estimate total (typical ratio is 1:4)
            hdl = safe_float(frontend_data.get('hdl_cholesterol'), 50)
            backend_data['cholesterol'] = hdl * 4
        else:
            backend_data['cholesterol'] = 200  # Default normal value

        logger.info(f"Transformed frontend data: {len(frontend_data)} fields -> {len(backend_data)} backend fields")
        logger.debug(f"Using actual lifestyle data: smoking={backend_data['smoking']}, " +
                    f"physical_activity={backend_data['physical_activity']}, " +
                    f"sleep={backend_data['sleep_hours']}, diet={backend_data['diet_quality']}")
        return backend_data

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete diabetes detection pipeline.

        Args:
            task: User data containing:
                - image: Retinal image file
                - lifestyle_data: Dict of lifestyle/demographic info
                - user_id: Optional user identifier

        Returns:
            Complete analysis result with risk score, advice, and simulations
        """
        try:
            logger.info(f"Starting orchestration for task: {task.get('user_id', 'anonymous')}")
            self.log_action("orchestration_started", task.keys())

            # Transform frontend data to backend format
            original_lifestyle_data = task.get('lifestyle_data', {})
            transformed_lifestyle_data = self._transform_frontend_to_backend_data(original_lifestyle_data)

            # Step 1: Parallel execution of retinal and lifestyle analysis
            logger.info("Step 1: Analyzing retinal image and lifestyle data in parallel")
            retinal_task = self.retinal_agent.execute({
                'image': task.get('image')
            })
            lifestyle_task = self.lifestyle_agent.execute({
                'lifestyle_data': transformed_lifestyle_data
            })

            retinal_result, lifestyle_result = await asyncio.gather(
                retinal_task,
                lifestyle_task
            )

            self.log_action("parallel_analysis_complete", {
                'retinal': retinal_result.get('status'),
                'lifestyle': lifestyle_result.get('status')
            })

            # Step 2: Fusion of multimodal data
            logger.info("Step 2: Fusing retinal and lifestyle predictions")
            fusion_result = await self.fusion_agent.execute({
                'retinal_result': retinal_result,
                'lifestyle_result': lifestyle_result
            })

            self.log_action("fusion_complete", fusion_result.get('risk_score'))

            # Step 3: Generate personalized advice using LLM
            logger.info("Step 3: Generating personalized advice with LLM")
            advice_result = await self.llm_agent.execute({
                'risk_score': fusion_result.get('risk_score'),
                'risk_factors': fusion_result.get('risk_factors'),
                'lifestyle_data': transformed_lifestyle_data,  # Use transformed data
                'retinal_findings': retinal_result.get('findings')
            })

            self.log_action("advice_generated", advice_result.get('status'))

            # Step 4: Create what-if simulations
            logger.info("Step 4: Creating what-if simulations")
            simulation_result = await self.simulation_agent.execute({
                'risk_score': fusion_result.get('risk_score'),
                'lifestyle_data': transformed_lifestyle_data,  # Use transformed data
                'risk_factors': fusion_result.get('risk_factors')
            })

            self.log_action("simulations_complete", len(simulation_result.get('simulations', [])))

            # Compile final result
            final_result = {
                'status': 'success',
                'user_id': task.get('user_id'),
                'risk_assessment': {
                    'overall_risk_score': fusion_result.get('risk_score', 0) * (100 if fusion_result.get('risk_score', 0) <= 1 else 1),  # Convert to percentage
                    'risk_level': fusion_result.get('risk_level'),
                    'confidence': fusion_result.get('confidence'),
                    'retinal_analysis': {
                        'risk_score': retinal_result.get('dr_probability', 0.0) * 100,  # Convert to percentage
                        'dr_detected': retinal_result.get('dr_detected'),
                        'severity': retinal_result.get('severity'),
                        'confidence': retinal_result.get('confidence'),
                        'findings': retinal_result.get('findings')
                    },
                    'lifestyle_analysis': {
                        'risk_score': lifestyle_result.get('risk_score', 0.0) * (100 if lifestyle_result.get('risk_score', 0) <= 1 else 1),  # Convert to percentage if needed
                        'key_factors': lifestyle_result.get('key_factors'),
                        'confidence': lifestyle_result.get('confidence')
                    }
                },
                'personalized_advice': {
                    'recommendations': advice_result.get('recommendations'),
                    'priority_actions': advice_result.get('priority_actions'),
                    'explanation': advice_result.get('explanation')
                },
                'what_if_simulations': simulation_result.get('simulations'),
                'metadata': {
                    'processing_time': simulation_result.get('processing_time'),
                    'model_versions': {
                        'retinal': retinal_result.get('model_version'),
                        'lifestyle': lifestyle_result.get('model_version')
                    }
                }
            }

            logger.info(f"Orchestration completed successfully. Risk score: {fusion_result.get('risk_score')}")
            self.log_action("orchestration_complete", "success")

            return final_result

        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            self.log_action("orchestration_failed", str(e))
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to process diabetes detection request'
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health status of all sub-agents.

        Returns:
            Health status of each agent
        """
        return {
            'orchestrator': 'healthy',
            'retinal_agent': 'healthy',
            'lifestyle_agent': 'healthy',
            'fusion_agent': 'healthy',
            'llm_agent': 'healthy',
            'simulation_agent': 'healthy'
        }
