"""Risk scoring and assessment logic."""
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class RiskScorer:
    """Comprehensive risk assessment and scoring."""

    def __init__(self):
        """Initialize risk scorer."""
        logger.info("RiskScorer initialized")

    def assess(self, fused_score: float, retinal_findings: Dict[str, Any],
               lifestyle_factors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess overall diabetes risk.

        Args:
            fused_score: Fused risk score from ensemble
            retinal_findings: Findings from retinal analysis
            lifestyle_factors: List of lifestyle risk factors

        Returns:
            Comprehensive risk assessment
        """
        # Determine risk level
        risk_level = self._get_risk_level(fused_score)

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(
            fused_score, retinal_findings, lifestyle_factors
        )

        # Generate risk interpretation
        interpretation = self._interpret_risk(
            fused_score, risk_level, retinal_findings, lifestyle_factors
        )

        assessment = {
            'risk_level': risk_level,
            'confidence': confidence,
            'interpretation': interpretation,
            'priority': self._get_priority(risk_level),
            'recommended_action': self._get_recommended_action(risk_level)
        }

        return assessment

    def _get_risk_level(self, score: float) -> str:
        """
        Categorize risk score into level.

        Args:
            score: Risk score (0-1)

        Returns:
            Risk level string
        """
        if score < 0.3:
            return 'low'
        elif score < 0.5:
            return 'moderate'
        elif score < 0.7:
            return 'high'
        else:
            return 'very_high'

    def _calculate_confidence(self, score: float, retinal_findings: Dict,
                             lifestyle_factors: List) -> float:
        """
        Calculate confidence in the assessment.

        Args:
            score: Risk score
            retinal_findings: Retinal analysis results
            lifestyle_factors: Lifestyle risk factors

        Returns:
            Confidence score (0-1)
        """
        # Base confidence
        confidence = 0.75

        # Increase if we have retinal data
        if retinal_findings:
            confidence += 0.10

        # Increase if we have multiple lifestyle factors
        if len(lifestyle_factors) >= 3:
            confidence += 0.10

        # Decrease if score is borderline (near category thresholds)
        if any(abs(score - threshold) < 0.05 for threshold in [0.3, 0.5, 0.7]):
            confidence -= 0.10

        return min(max(confidence, 0.5), 0.95)

    def _interpret_risk(self, score: float, risk_level: str,
                       retinal_findings: Dict, lifestyle_factors: List) -> str:
        """
        Generate human-readable risk interpretation.

        Args:
            score: Risk score
            risk_level: Categorized risk level
            retinal_findings: Retinal findings
            lifestyle_factors: Lifestyle factors

        Returns:
            Risk interpretation string
        """
        interpretations = {
            'low': "Your current risk of developing diabetes is low. Continue maintaining healthy lifestyle habits.",
            'moderate': "You have a moderate risk of developing diabetes. Making lifestyle changes now can significantly reduce your risk.",
            'high': "You have a high risk of developing diabetes. We strongly recommend implementing preventive measures and consulting with a healthcare provider.",
            'very_high': "You have a very high risk of developing diabetes. Please consult with a healthcare provider as soon as possible for comprehensive evaluation and intervention."
        }

        base_interpretation = interpretations.get(risk_level, "Unable to determine risk level")

        # Add context based on findings
        if retinal_findings.get('total_features_detected', 0) > 0:
            base_interpretation += " Retinal signs consistent with diabetes have been detected."

        if lifestyle_factors:
            modifiable_count = sum(1 for f in lifestyle_factors if f.get('modifiable', False))
            if modifiable_count > 0:
                base_interpretation += f" You have {modifiable_count} modifiable risk factor(s) that you can address."

        return base_interpretation

    def _get_priority(self, risk_level: str) -> str:
        """
        Get priority level for intervention.

        Args:
            risk_level: Risk level

        Returns:
            Priority string
        """
        priority_map = {
            'low': 'routine',
            'moderate': 'elevated',
            'high': 'urgent',
            'very_high': 'critical'
        }
        return priority_map.get(risk_level, 'routine')

    def _get_recommended_action(self, risk_level: str) -> str:
        """
        Get recommended next action.

        Args:
            risk_level: Risk level

        Returns:
            Recommended action string
        """
        actions = {
            'low': "Continue healthy lifestyle habits. Schedule routine check-up in 12 months.",
            'moderate': "Implement lifestyle modifications. Schedule check-up in 6 months.",
            'high': "Begin preventive interventions immediately. Consult healthcare provider within 1 month.",
            'very_high': "Seek immediate medical evaluation. Schedule appointment within 1-2 weeks."
        }
        return actions.get(risk_level, "Consult with healthcare provider")

    def calculate_prevention_potential(self, lifestyle_factors: List[Dict]) -> float:
        """
        Calculate how much risk could potentially be reduced through lifestyle changes.

        Args:
            lifestyle_factors: List of lifestyle risk factors

        Returns:
            Prevention potential score (0-1)
        """
        if not lifestyle_factors:
            return 0.0

        modifiable_factors = [f for f in lifestyle_factors if f.get('modifiable', False)]
        if not modifiable_factors:
            return 0.1

        # Weight by importance
        potential = sum(f.get('importance', 0.0) for f in modifiable_factors)
        potential = min(potential, 0.8)  # Cap at 80% potential reduction

        return potential
