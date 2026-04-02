"""Multimodal data fusion agent."""
import time
from typing import Dict, Any
from agents.base_agent import BaseAgent
from models.fusion.ensemble import EnsembleFusion
from models.fusion.risk_scorer import RiskScorer
from utils.logger import get_logger

logger = get_logger(__name__)


class FusionAgent(BaseAgent):
    """Agent responsible for fusing retinal and lifestyle predictions."""

    def __init__(self):
        """Initialize fusion agent with ensemble methods."""
        super().__init__(agent_id="fusion_agent")
        self.ensemble = EnsembleFusion()
        self.risk_scorer = RiskScorer()
        logger.info("FusionAgent initialized")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fuse multimodal predictions into unified risk assessment.

        Args:
            task: Dict containing:
                - retinal_result: Output from RetinalAgent
                - lifestyle_result: Output from LifestyleAgent

        Returns:
            Fused risk assessment with combined score
        """
        try:
            start_time = time.time()

            retinal_result = task.get('retinal_result', {})
            lifestyle_result = task.get('lifestyle_result', {})

            logger.info("Starting multimodal fusion")
            self.log_action("fusion_started", {
                'retinal_status': retinal_result.get('status'),
                'lifestyle_status': lifestyle_result.get('status')
            })

            # Extract predictions
            retinal_risk = self._extract_retinal_risk(retinal_result)
            lifestyle_risk = lifestyle_result.get('risk_score', 0.5)

            # Fuse predictions using ensemble method
            logger.debug(f"Fusing risks: retinal={retinal_risk}, lifestyle={lifestyle_risk}")
            fused_score = self.ensemble.fuse(
                retinal_risk=retinal_risk,
                lifestyle_risk=lifestyle_risk,
                retinal_confidence=retinal_result.get('confidence', 0.5),
                lifestyle_confidence=lifestyle_result.get('confidence', 0.5)
            )

            # Calculate comprehensive risk assessment
            risk_assessment = self.risk_scorer.assess(
                fused_score=fused_score,
                retinal_findings=retinal_result.get('findings', {}),
                lifestyle_factors=lifestyle_result.get('key_factors', [])
            )

            processing_time = time.time() - start_time

            result = {
                'status': 'success',
                'risk_score': fused_score,
                'risk_level': risk_assessment['risk_level'],
                'confidence': risk_assessment['confidence'],
                'risk_factors': self._compile_risk_factors(retinal_result, lifestyle_result),
                'component_scores': {
                    'retinal': retinal_risk,
                    'lifestyle': lifestyle_risk
                },
                'processing_time': processing_time
            }

            logger.info(f"Fusion complete. Fused risk score: {fused_score:.2f}, Level: {risk_assessment['risk_level']}")
            self.log_action("fusion_complete", result)

            return result

        except Exception as e:
            logger.error(f"Fusion failed: {str(e)}")
            self.log_action("fusion_failed", str(e))
            return {
                'status': 'error',
                'error': str(e),
                'risk_score': 0.5,
                'risk_level': 'unknown'
            }

    def _extract_retinal_risk(self, retinal_result: Dict[str, Any]) -> float:
        """
        Extract risk score from retinal analysis.

        Args:
            retinal_result: Retinal agent output

        Returns:
            Normalized risk score (0-1)
        """
        if retinal_result.get('status') != 'success':
            return 0.5  # Default to medium risk if analysis failed

        dr_probability = retinal_result.get('dr_probability', 0.0)
        severity = retinal_result.get('severity', 'none')

        # Weight severity
        severity_weights = {
            'none': 0.0,
            'mild': 0.2,
            'moderate': 0.5,
            'severe': 0.7
        }

        severity_score = severity_weights.get(severity, 0.0)

        # Combine probability and severity
        risk_score = (dr_probability * 0.8) + (severity_score * 0.2)

        return min(max(risk_score * 2 , 0.0), 1.0)

    def _compile_risk_factors(self, retinal_result: Dict[str, Any],
                              lifestyle_result: Dict[str, Any]) -> list:
        """
        Compile all identified risk factors from both modalities.

        Args:
            retinal_result: Retinal agent output
            lifestyle_result: Lifestyle agent output

        Returns:
            Combined list of risk factors
        """
        risk_factors = []

        # Add retinal findings
        if retinal_result.get('dr_detected'):
            findings = retinal_result.get('findings', {})
            risk_factors.append({
                'source': 'retinal',
                'factor': 'Diabetic Retinopathy detected',
                'severity': retinal_result.get('severity'),
                'details': findings
            })

        # Add lifestyle factors
        lifestyle_factors = lifestyle_result.get('key_factors', [])
        for factor in lifestyle_factors:
            risk_factors.append({
                'source': 'lifestyle',
                'factor': factor.get('factor'),
                'value': factor.get('value'),
                'importance': factor.get('importance'),
                'modifiable': factor.get('modifiable')
            })

        return risk_factors
