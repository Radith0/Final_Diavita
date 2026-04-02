"""Ensemble fusion methods for multimodal predictions."""
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class EnsembleFusion:
    """Ensemble methods for fusing retinal and lifestyle predictions."""

    def __init__(self, method: str = 'weighted_average', use_optimized_weights: bool = True):
        """
        Initialize ensemble fusion.

        Args:
            method: Fusion method ('weighted_average', 'max', 'min', 'learned')
            use_optimized_weights: Whether to load optimized weights from training
        """
        self.method = method
        self.use_optimized_weights = use_optimized_weights

        # Initialize with defaults, will be overridden if optimized weights exist
        self.retinal_weight = 0.5  # Default equal weights
        self.lifestyle_weight = 0.5  # Default equal weights

        # Always try to load optimized weights from JSON if using weighted methods
        if method in ['weighted_average', 'learned']:
            self._load_optimized_weights()
        elif use_optimized_weights:
            # Even for other methods, load weights if requested
            self._load_optimized_weights()

        logger.info(f"EnsembleFusion initialized with method: {method}, "
                   f"weights: retinal={self.retinal_weight:.3f}, lifestyle={self.lifestyle_weight:.3f}")

    def fuse(self, retinal_risk: float, lifestyle_risk: float,
             retinal_confidence: float = 1.0,
             lifestyle_confidence: float = 1.0) -> float:
        """
        Fuse multimodal risk predictions.

        Args:
            retinal_risk: Risk score from retinal analysis (0-1)
            lifestyle_risk: Risk score from lifestyle analysis (0-1)
            retinal_confidence: Confidence of retinal prediction
            lifestyle_confidence: Confidence of lifestyle prediction

        Returns:
            Fused risk score (0-1)
        """
        try:
            if self.method == 'weighted_average':
                fused = self._weighted_average(
                    retinal_risk, lifestyle_risk,
                    retinal_confidence, lifestyle_confidence
                )
            elif self.method == 'max':
                fused = max(retinal_risk, lifestyle_risk)
            elif self.method == 'min':
                fused = min(retinal_risk, lifestyle_risk)
            elif self.method == 'geometric_mean':
                fused = np.sqrt(retinal_risk * lifestyle_risk)
            else:
                fused = self._weighted_average(
                    retinal_risk, lifestyle_risk,
                    retinal_confidence, lifestyle_confidence
                )

            # Ensure output is in valid range
            fused = min(max(fused, 0.0), 1.0)

            logger.debug(f"Fused risk: retinal={retinal_risk:.3f}, lifestyle={lifestyle_risk:.3f} -> {fused:.3f}")

            return float(fused)

        except Exception as e:
            logger.error(f"Fusion failed: {str(e)}")
            # Fallback to simple average
            return float((retinal_risk + lifestyle_risk) / 2.0)

    def _load_optimized_weights(self):
        """Load optimized weights from training if available."""
        weights_file = Path(__file__).parent / 'optimal_weights.json'

        try:
            if weights_file.exists():
                with open(weights_file, 'r') as f:
                    weights_data = json.load(f)
                    self.retinal_weight = weights_data.get('retinal_weight', 0.7)
                    self.lifestyle_weight = weights_data.get('lifestyle_weight', 0.3)

                    # Ensure weights sum to 1
                    total = self.retinal_weight + self.lifestyle_weight
                    if abs(total - 1.0) > 0.001:  # Allow small floating point errors
                        self.retinal_weight /= total
                        self.lifestyle_weight /= total

                    logger.info(f"Loaded optimized weights from {weights_file}")
                    logger.info(f"Optimal weights: retinal={self.retinal_weight:.3f}, "
                               f"lifestyle={self.lifestyle_weight:.3f}, "
                               f"loss={weights_data.get('best_loss', 'N/A')}")
            else:
                logger.info("No optimized weights found, using defaults")
        except Exception as e:
            logger.warning(f"Failed to load optimized weights: {e}, using defaults")

    def _weighted_average(self, retinal_risk: float, lifestyle_risk: float,
                         retinal_confidence: float, lifestyle_confidence: float) -> float:
        """
        Compute confidence-weighted average using optimized or default weights.

        Args:
            retinal_risk: Retinal risk score
            lifestyle_risk: Lifestyle risk score
            retinal_confidence: Retinal confidence
            lifestyle_confidence: Lifestyle confidence

        Returns:
            Weighted average risk score
        """
        # Use optimized weights (loaded in __init__)
        retinal_weight = self.retinal_weight
        lifestyle_weight = self.lifestyle_weight

        # Optional: Adjust weights based on confidence
        # This creates a dynamic weighting based on model confidence
        if self.use_optimized_weights:
            # Use fixed optimized weights (no confidence adjustment)
            # These weights were learned to minimize prediction error
            pass
        else:
            # Adjust weights based on confidence for non-optimized mode
            total_confidence = retinal_confidence + lifestyle_confidence
            if total_confidence > 0:
                # Modulate base weights by confidence
                conf_factor_retinal = retinal_confidence / total_confidence
                conf_factor_lifestyle = lifestyle_confidence / total_confidence

                # Blend base weights with confidence factors
                retinal_weight = retinal_weight * 0.7 + conf_factor_retinal * 0.3
                lifestyle_weight = lifestyle_weight * 0.7 + conf_factor_lifestyle * 0.3

                # Renormalize to ensure sum = 1
                total = retinal_weight + lifestyle_weight
                retinal_weight /= total
                lifestyle_weight /= total

        # Weighted average with constraint w1 + w2 = 1
        fused = (retinal_weight * retinal_risk) + (lifestyle_weight * lifestyle_risk)

        logger.debug(f"Fusion weights used: retinal={retinal_weight:.3f}, lifestyle={lifestyle_weight:.3f}")

        return fused

    def fuse_with_uncertainty(self, predictions: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Fuse predictions with uncertainty quantification.

        Args:
            predictions: Dict of {modality: {risk, confidence}}

        Returns:
            Dict with fused risk and uncertainty estimate
        """
        risks = []
        confidences = []

        for modality, pred in predictions.items():
            risks.append(pred['risk'])
            confidences.append(pred['confidence'])

        risks = np.array(risks)
        confidences = np.array(confidences)

        # Weighted fusion
        weights = confidences / confidences.sum()
        fused_risk = np.sum(risks * weights)

        # Uncertainty as variance of predictions
        uncertainty = np.std(risks)

        # Overall confidence (lower if predictions disagree)
        agreement_penalty = 1.0 - (uncertainty * 2.0)  # Scale uncertainty to penalty
        fused_confidence = np.mean(confidences) * max(agreement_penalty, 0.5)

        return {
            'risk': float(fused_risk),
            'confidence': float(fused_confidence),
            'uncertainty': float(uncertainty)
        }
