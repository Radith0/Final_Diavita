"""
Optimize fusion weights for combining retinal and lifestyle predictions.
Uses gradient descent to find optimal weights that minimize prediction error.
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.metrics import mean_squared_error, roc_auc_score
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


class FusionWeightOptimizer:
    """
    Learns optimal weights for fusing retinal and lifestyle model predictions.
    Constraint: w1 + w2 = 1 (weights must sum to 1)
    """

    def __init__(self,
                 initial_w1: float = None,  # Initial weight for retinal (None = load from JSON)
                 initial_w2: float = None,  # Initial weight for lifestyle (None = load from JSON)
                 learning_rate: float = 0.01,
                 regularization: float = 0.001):
        """
        Initialize weight optimizer.

        Args:
            initial_w1: Initial weight for retinal model (None = load from JSON)
            initial_w2: Initial weight for lifestyle model (None = load from JSON)
            learning_rate: Learning rate for gradient descent
            regularization: L2 regularization strength
        """
        # If initial values are None, try to load from JSON
        if initial_w1 is None or initial_w2 is None:
            weights_file = Path(__file__).parent / 'optimal_weights.json'
            if weights_file.exists():
                try:
                    with open(weights_file, 'r') as f:
                        weights_data = json.load(f)
                        initial_w1 = weights_data.get('retinal_weight', 0.5)
                        initial_w2 = weights_data.get('lifestyle_weight', 0.5)
                        logger.info(f"Loaded initial weights from JSON: w1={initial_w1:.3f}, w2={initial_w2:.3f}")
                except Exception as e:
                    logger.warning(f"Failed to load weights from JSON: {e}")
                    initial_w1 = 0.5
                    initial_w2 = 0.5
            else:
                # Default to equal weights if no JSON found
                initial_w1 = 0.5
                initial_w2 = 0.5

        # Ensure weights sum to 1
        total = initial_w1 + initial_w2
        self.w1 = initial_w1 / total
        self.w2 = initial_w2 / total

        self.learning_rate = learning_rate
        self.regularization = regularization
        self.training_history = []
        self.best_weights = (self.w1, self.w2)
        self.best_loss = float('inf')

        logger.info(f"Initialized weight optimizer: w1={self.w1:.3f}, w2={self.w2:.3f}")

    def compute_loss(self,
                     y_true: np.ndarray,
                     retinal_preds: np.ndarray,
                     lifestyle_preds: np.ndarray,
                     w1: float,
                     w2: float) -> float:
        """
        Compute loss function for given weights.

        Loss = MSE + regularization_term

        Args:
            y_true: Ground truth labels
            retinal_preds: Predictions from retinal model
            lifestyle_preds: Predictions from lifestyle model
            w1: Weight for retinal model
            w2: Weight for lifestyle model

        Returns:
            Loss value
        """
        # Ensure weights sum to 1
        w2 = 1 - w1  # Constraint: w1 + w2 = 1

        # Compute weighted predictions
        y_pred = w1 * retinal_preds + w2 * lifestyle_preds

        # Mean squared error
        mse_loss = mean_squared_error(y_true, y_pred)

        # L2 regularization to prevent extreme weights
        reg_loss = self.regularization * (w1**2 + w2**2)

        total_loss = mse_loss + reg_loss

        return total_loss

    def compute_gradient(self,
                         y_true: np.ndarray,
                         retinal_preds: np.ndarray,
                         lifestyle_preds: np.ndarray,
                         w1: float) -> float:
        """
        Compute gradient of loss with respect to w1.
        Since w2 = 1 - w1, we only need gradient for w1.

        Args:
            y_true: Ground truth labels
            retinal_preds: Predictions from retinal model
            lifestyle_preds: Predictions from lifestyle model
            w1: Current weight for retinal model

        Returns:
            Gradient of loss w.r.t. w1
        """
        w2 = 1 - w1

        # Current predictions
        y_pred = w1 * retinal_preds + w2 * lifestyle_preds

        # Gradient of MSE w.r.t. w1
        # d/dw1 MSE = 2/n * sum((y_pred - y_true) * (retinal - lifestyle))
        n = len(y_true)
        pred_error = y_pred - y_true
        pred_diff = retinal_preds - lifestyle_preds

        mse_gradient = (2.0 / n) * np.sum(pred_error * pred_diff)

        # Gradient of regularization term
        reg_gradient = 2 * self.regularization * (w1 - w2)  # Since w2 = 1-w1

        total_gradient = mse_gradient + reg_gradient

        return total_gradient

    def train_batch(self,
                   y_true: np.ndarray,
                   retinal_preds: np.ndarray,
                   lifestyle_preds: np.ndarray,
                   epochs: int = 100) -> Dict:
        """
        Train weights using gradient descent on a batch of data.

        Args:
            y_true: Ground truth labels
            retinal_preds: Predictions from retinal model
            lifestyle_preds: Predictions from lifestyle model
            epochs: Number of training epochs

        Returns:
            Training results dictionary
        """
        logger.info(f"Starting weight optimization for {epochs} epochs")

        for epoch in range(epochs):
            # Compute current loss
            current_loss = self.compute_loss(
                y_true, retinal_preds, lifestyle_preds, self.w1, self.w2
            )

            # Compute gradient
            gradient = self.compute_gradient(
                y_true, retinal_preds, lifestyle_preds, self.w1
            )

            # Update weight with gradient descent
            self.w1 -= self.learning_rate * gradient

            # Ensure w1 stays in valid range [0, 1]
            self.w1 = np.clip(self.w1, 0.01, 0.99)
            self.w2 = 1 - self.w1

            # Track best weights
            if current_loss < self.best_loss:
                self.best_loss = current_loss
                self.best_weights = (self.w1, self.w2)

            # Log progress
            if epoch % 10 == 0:
                logger.debug(f"Epoch {epoch}: Loss={current_loss:.4f}, "
                           f"w1={self.w1:.3f}, w2={self.w2:.3f}, "
                           f"gradient={gradient:.4f}")

            self.training_history.append({
                'epoch': epoch,
                'loss': current_loss,
                'w1': self.w1,
                'w2': self.w2,
                'gradient': gradient
            })

        # Apply best weights
        self.w1, self.w2 = self.best_weights

        logger.info(f"Training complete. Best weights: w1={self.w1:.3f}, w2={self.w2:.3f}, "
                   f"Loss={self.best_loss:.4f}")

        return {
            'best_weights': self.best_weights,
            'best_loss': self.best_loss,
            'final_weights': (self.w1, self.w2),
            'history': self.training_history[-10:]  # Last 10 epochs
        }

    def optimize_with_scipy(self,
                           y_true: np.ndarray,
                           retinal_preds: np.ndarray,
                           lifestyle_preds: np.ndarray,
                           multi_start: bool = True,
                           retinal_bias: float = 0.1) -> Dict:
        """
        Alternative optimization using scipy.optimize with multiple improvements.

        Args:
            y_true: Ground truth labels
            retinal_preds: Predictions from retinal model
            lifestyle_preds: Predictions from lifestyle model
            multi_start: Use multiple random initializations to avoid local minima
            retinal_bias: Bias term to favor retinal model (0-1, higher = more bias)

        Returns:
            Optimization results
        """
        def objective(w1):
            """Objective function with optional retinal bias."""
            base_loss = self.compute_loss(
                y_true, retinal_preds, lifestyle_preds, w1[0], 1-w1[0]
            )

            if retinal_bias > 0:
                # Add penalty for giving too little weight to retinal
                retinal_penalty = retinal_bias * np.exp(-5 * w1[0])  # Exponential penalty for low w1
                # Also add a soft constraint to prefer w1 > 0.6
                soft_constraint = 0.01 * max(0, 0.6 - w1[0])**2
                return base_loss + retinal_penalty + soft_constraint
            else:
                # Pure optimization without bias
                return base_loss

        # Use full range if no bias, otherwise constrain
        if retinal_bias > 0:
            bounds = [(0.5, 0.95)]  # Force retinal weight to be at least 50%
        else:
            bounds = [(0.01, 0.99)]  # Full range

        best_result = None
        best_loss = float('inf')

        if multi_start:
            # Try multiple starting points across the full range to avoid local minima
            initial_points = [0.1, 0.3, 0.5, 0.7, 0.9]  # Cover full range
        else:
            initial_points = [self.w1]

        for x0_val in initial_points:
            x0 = np.array([x0_val])

            # Skip if outside bounds
            if x0_val < bounds[0][0] or x0_val > bounds[0][1]:
                continue

            # Optimize
            result = minimize(
                objective,
                x0,
                method='L-BFGS-B',
                bounds=bounds,
                options={'maxiter': 200, 'ftol': 1e-8}
            )

            # Track best result (based on actual loss, not biased objective)
            actual_loss = self.compute_loss(
                y_true, retinal_preds, lifestyle_preds, result.x[0], 1-result.x[0]
            )

            if actual_loss < best_loss:
                best_loss = actual_loss
                best_result = result

        # Use best result
        if best_result is not None:
            self.w1 = best_result.x[0]
            self.w2 = 1 - self.w1

            logger.info(f"Scipy optimization complete (multi_start={multi_start}). "
                       f"Optimal weights: w1={self.w1:.3f}, w2={self.w2:.3f}, "
                       f"Loss={best_loss:.4f}")

            return {
                'optimal_w1': self.w1,
                'optimal_w2': self.w2,
                'optimal_loss': best_loss,
                'success': best_result.success,
                'message': best_result.message,
                'multi_start': multi_start,
                'n_starts': len(initial_points)
            }
        else:
            return {
                'optimal_w1': 0.85,
                'optimal_w2': 0.15,
                'optimal_loss': float('inf'),
                'success': False,
                'message': 'Optimization failed'
            }

    def cross_validate_weights(self,
                              data_splits: List[Dict],
                              method: str = 'gradient') -> Dict:
        """
        Cross-validate to find robust weights across multiple data splits.

        Args:
            data_splits: List of dicts with 'y_true', 'retinal_preds', 'lifestyle_preds'
            method: 'gradient' or 'scipy'

        Returns:
            Cross-validation results
        """
        cv_weights = []
        cv_losses = []

        for i, split in enumerate(data_splits):
            logger.info(f"Cross-validation fold {i+1}/{len(data_splits)}")

            # Reset to initial weights
            self.w1 = 0.7
            self.w2 = 0.3

            if method == 'gradient':
                result = self.train_batch(
                    split['y_true'],
                    split['retinal_preds'],
                    split['lifestyle_preds'],
                    epochs=50
                )
                cv_weights.append(result['best_weights'])
                cv_losses.append(result['best_loss'])
            else:
                result = self.optimize_with_scipy(
                    split['y_true'],
                    split['retinal_preds'],
                    split['lifestyle_preds']
                )
                cv_weights.append((result['optimal_w1'], result['optimal_w2']))
                cv_losses.append(result['optimal_loss'])

        # Compute average weights
        avg_w1 = np.mean([w[0] for w in cv_weights])
        avg_w2 = np.mean([w[1] for w in cv_weights])

        # Ensure they sum to 1
        total = avg_w1 + avg_w2
        avg_w1 /= total
        avg_w2 /= total

        logger.info(f"Cross-validation complete. Average weights: "
                   f"w1={avg_w1:.3f}, w2={avg_w2:.3f}")

        return {
            'average_weights': (avg_w1, avg_w2),
            'std_w1': np.std([w[0] for w in cv_weights]),
            'std_w2': np.std([w[1] for w in cv_weights]),
            'average_loss': np.mean(cv_losses),
            'all_weights': cv_weights
        }

    def save_weights(self, filepath: str = 'models/fusion/optimal_weights.json'):
        """
        Save optimized weights to file.

        Args:
            filepath: Path to save weights
        """
        weights_data = {
            'retinal_weight': float(self.w1),
            'lifestyle_weight': float(self.w2),
            'best_loss': float(self.best_loss),
            'training_history': self.training_history[-20:] if self.training_history else [],
            'method': 'gradient_descent',
            'constraint': 'w1 + w2 = 1'
        }

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(weights_data, f, indent=2)

        logger.info(f"Weights saved to {filepath}")

        return weights_data

    @classmethod
    def load_weights(cls, filepath: str = 'models/fusion/optimal_weights.json'):
        """
        Load previously optimized weights.

        Args:
            filepath: Path to weights file

        Returns:
            FusionWeightOptimizer instance with loaded weights
        """
        filepath = Path(filepath)

        if not filepath.exists():
            logger.warning(f"Weights file not found: {filepath}. Using defaults.")
            return cls()

        with open(filepath, 'r') as f:
            weights_data = json.load(f)

        optimizer = cls(
            initial_w1=weights_data['retinal_weight'],
            initial_w2=weights_data['lifestyle_weight']
        )

        if 'training_history' in weights_data:
            optimizer.training_history = weights_data['training_history']
        if 'best_loss' in weights_data:
            optimizer.best_loss = weights_data['best_loss']

        logger.info(f"Loaded weights: w1={optimizer.w1:.3f}, w2={optimizer.w2:.3f}")

        return optimizer


# Example usage for training optimal weights
if __name__ == "__main__":
    # Simulate some training data
    np.random.seed(42)
    n_samples = 100

    # Generate synthetic predictions and ground truth
    y_true = np.random.binomial(1, 0.3, n_samples)  # Binary labels
    retinal_preds = y_true + np.random.normal(0, 0.2, n_samples)
    lifestyle_preds = y_true + np.random.normal(0, 0.3, n_samples)

    # Clip to [0, 1] range
    retinal_preds = np.clip(retinal_preds, 0, 1)
    lifestyle_preds = np.clip(lifestyle_preds, 0, 1)

    # Initialize optimizer
    optimizer = FusionWeightOptimizer(initial_w1=0.5, initial_w2=0.5)

    # Method 1: Gradient descent
    print("\n=== Gradient Descent Optimization ===")
    result_gd = optimizer.train_batch(y_true, retinal_preds, lifestyle_preds, epochs=100)
    print(f"Optimal weights (GD): w1={result_gd['best_weights'][0]:.3f}, "
          f"w2={result_gd['best_weights'][1]:.3f}")

    # Method 2: Scipy optimization
    print("\n=== Scipy Optimization ===")
    optimizer2 = FusionWeightOptimizer(initial_w1=0.5, initial_w2=0.5)
    result_scipy = optimizer2.optimize_with_scipy(y_true, retinal_preds, lifestyle_preds)
    print(f"Optimal weights (Scipy): w1={result_scipy['optimal_w1']:.3f}, "
          f"w2={result_scipy['optimal_w2']:.3f}")

    # Save weights
    optimizer.save_weights()
    print("\nWeights saved successfully!")