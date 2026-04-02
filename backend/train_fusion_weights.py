#!/usr/bin/env python
"""
Train optimal fusion weights using historical data or synthetic examples.
This finds the best w1 (retinal) and w2 (lifestyle) weights where w1 + w2 = 1.
"""

import numpy as np
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from models.fusion.weight_optimizer import FusionWeightOptimizer


def generate_training_data(n_samples=500):
    """
    Generate synthetic training data for weight optimization.
    In practice, you'd use real labeled data.
    """
    np.random.seed(42)

    # Simulate that retinal is generally more accurate (lower noise)
    # but lifestyle captures different aspects

    y_true = np.random.binomial(1, 0.35, n_samples).astype(float)  # 35% positive rate

    # Retinal predictions: More accurate, less noise
    retinal_noise = np.random.normal(0, 0.15, n_samples)
    retinal_preds = y_true + retinal_noise
    # Add some systematic bias for cases retinal might miss
    mask_retinal_miss = np.random.random(n_samples) < 0.1  # 10% cases retinal misses
    retinal_preds[mask_retinal_miss] = 1 - y_true[mask_retinal_miss]

    # Lifestyle predictions: Slightly less accurate, more noise
    lifestyle_noise = np.random.normal(0, 0.25, n_samples)
    lifestyle_preds = y_true + lifestyle_noise
    # Lifestyle is good at catching behavioral risk factors
    mask_lifestyle_good = np.random.random(n_samples) < 0.15  # 15% cases lifestyle excels
    lifestyle_preds[mask_lifestyle_good] = y_true[mask_lifestyle_good] + np.random.normal(0, 0.1, np.sum(mask_lifestyle_good))

    # Clip to [0, 1] range
    retinal_preds = np.clip(retinal_preds, 0, 1)
    lifestyle_preds = np.clip(lifestyle_preds, 0, 1)

    return y_true, retinal_preds, lifestyle_preds


def calibrate_lifestyle_predictions(lifestyle_preds):
    """
    Calibrate lifestyle predictions to have better range.
    Maps [0.4, 1.0] range to [0.0, 1.0] for better fusion.
    """
    # Apply isotonic regression or sigmoid calibration
    # For now, using simple linear scaling
    min_val = 0.4  # Observed minimum from lifestyle model
    calibrated = (lifestyle_preds - min_val) / (1.0 - min_val)
    return np.clip(calibrated, 0, 1)


def compute_adaptive_weights(retinal_confidence, lifestyle_confidence):
    """
    Compute adaptive weights based on model confidence.
    Higher confidence gets higher weight.
    """
    # Base weights favor retinal model
    base_retinal = 0.7
    base_lifestyle = 0.3

    # Adjust based on confidence
    total_conf = retinal_confidence + lifestyle_confidence
    if total_conf > 0:
        w1 = base_retinal + 0.2 * (retinal_confidence / total_conf - 0.5)
        w2 = 1 - w1
    else:
        w1, w2 = base_retinal, base_lifestyle

    return np.clip(w1, 0.5, 0.9), np.clip(w2, 0.1, 0.5)


def main():
    print("\n" + "="*60)
    print("TRAINING OPTIMAL FUSION WEIGHTS - ENHANCED VERSION")
    print("="*60)

    # Generate or load training data
    print("\n1. Generating training data...")
    y_true, retinal_preds, lifestyle_preds = generate_training_data(n_samples=1000)

    # Calibrate lifestyle predictions
    lifestyle_preds_calibrated = calibrate_lifestyle_predictions(lifestyle_preds)

    print(f"   • Samples: {len(y_true)}")
    print(f"   • Positive rate: {np.mean(y_true):.2%}")
    print(f"   • Retinal accuracy: {1 - np.mean(np.abs(retinal_preds - y_true)):.2%}")
    print(f"   • Lifestyle accuracy (raw): {1 - np.mean(np.abs(lifestyle_preds - y_true)):.2%}")
    print(f"   • Lifestyle accuracy (calibrated): {1 - np.mean(np.abs(lifestyle_preds_calibrated - y_true)):.2%}")

    # Initialize optimizer with different starting points
    print("\n2. Training with gradient descent...")
    optimizer = FusionWeightOptimizer(
        initial_w1=0.5,  # Start with equal weights
        initial_w2=0.5,
        learning_rate=0.01
    )

    # Train
    result = optimizer.train_batch(
        y_true[:800],  # Use 80% for training
        retinal_preds[:800],
        lifestyle_preds[:800],
        epochs=200
    )

    print(f"\n   ✓ Training complete!")
    print(f"   • Optimal weights: retinal={result['best_weights'][0]:.3f}, "
          f"lifestyle={result['best_weights'][1]:.3f}")
    print(f"   • Training loss: {result['best_loss']:.4f}")

    # Validate on test set
    print("\n3. Validating on test set...")
    test_loss = optimizer.compute_loss(
        y_true[800:],  # Use 20% for testing
        retinal_preds[800:],
        lifestyle_preds[800:],
        result['best_weights'][0],
        result['best_weights'][1]
    )
    print(f"   • Test loss: {test_loss:.4f}")

    # Try scipy optimization for comparison
    print("\n4. Comparing with scipy optimization (improved version)...")
    optimizer2 = FusionWeightOptimizer()
    scipy_result = optimizer2.optimize_with_scipy(
        y_true[:800],
        retinal_preds[:800],
        lifestyle_preds_calibrated[:800],  # Use calibrated predictions
        multi_start=True,  # Use multiple starting points
        retinal_bias=0.0  # No bias - let optimizer find true optimum
    )

    print(f"   • Scipy optimal weights: retinal={scipy_result['optimal_w1']:.3f}, "
          f"lifestyle={scipy_result['optimal_w2']:.3f}")
    print(f"   • Scipy loss: {scipy_result['optimal_loss']:.4f}")
    print(f"   • Used {scipy_result.get('n_starts', 1)} starting points")

    # Method 2: Fixed high retinal weight (domain expertise approach)
    print("\n5. Testing fixed high retinal weight (domain expertise)...")
    fixed_w1, fixed_w2 = 0.85, 0.15  # Give retinal 85% weight
    fixed_loss = optimizer.compute_loss(
        y_true[800:],
        retinal_preds[800:],
        lifestyle_preds_calibrated[800:],
        fixed_w1,
        fixed_w2
    )
    print(f"   • Fixed weights: retinal={fixed_w1:.3f}, lifestyle={fixed_w2:.3f}")
    print(f"   • Fixed weights loss: {fixed_loss:.4f}")

    # Method 3: Bayesian approach with prior favoring retinal
    print("\n6. Bayesian optimization with retinal prior...")
    # Start with strong prior for retinal
    bayesian_w1 = 0.8
    bayesian_w2 = 0.2
    prior_strength = 0.3  # How much to trust the prior

    # Update based on data
    data_w1 = scipy_result['optimal_w1']
    bayesian_w1 = prior_strength * 0.85 + (1 - prior_strength) * data_w1
    bayesian_w2 = 1 - bayesian_w1

    bayesian_loss = optimizer.compute_loss(
        y_true[800:],
        retinal_preds[800:],
        lifestyle_preds_calibrated[800:],
        bayesian_w1,
        bayesian_w2
    )
    print(f"   • Bayesian weights: retinal={bayesian_w1:.3f}, lifestyle={bayesian_w2:.3f}")
    print(f"   • Bayesian loss: {bayesian_loss:.4f}")

    # Method 4: Ensemble voting approach
    print("\n7. Ensemble voting approach...")
    methods_weights = [
        (result['best_weights'][0], result['best_weights'][1], "Gradient Descent"),
        (scipy_result['optimal_w1'], scipy_result['optimal_w2'], "Scipy"),
        (fixed_w1, fixed_w2, "Domain Expert"),
        (bayesian_w1, bayesian_w2, "Bayesian")
    ]

    # Average with preference for methods giving higher retinal weight
    ensemble_w1 = np.mean([w[0] for w in methods_weights if w[0] > 0.7])
    ensemble_w2 = 1 - ensemble_w1

    ensemble_loss = optimizer.compute_loss(
        y_true[800:],
        retinal_preds[800:],
        lifestyle_preds_calibrated[800:],
        ensemble_w1,
        ensemble_w2
    )
    print(f"   • Ensemble weights: retinal={ensemble_w1:.3f}, lifestyle={ensemble_w2:.3f}")
    print(f"   • Ensemble loss: {ensemble_loss:.4f}")

    # Compare all methods
    print("\n8. Comparing all methods...")
    all_methods = [
        ("Gradient Descent", result['best_weights'][0], result['best_weights'][1], test_loss),
        ("Scipy Optimization", scipy_result['optimal_w1'], scipy_result['optimal_w2'], scipy_result['optimal_loss']),
        ("Domain Expert (85/15)", fixed_w1, fixed_w2, fixed_loss),
        ("Bayesian Prior", bayesian_w1, bayesian_w2, bayesian_loss),
        ("Ensemble Voting", ensemble_w1, ensemble_w2, ensemble_loss)
    ]

    print("\n   Method Comparison:")
    print("   " + "-"*55)
    for method, w1, w2, loss in all_methods:
        print(f"   {method:<20} | w1={w1:.3f} w2={w2:.3f} | loss={loss:.4f}")

    # Choose the best based purely on lowest loss (no domain constraint)
    best_method = min(all_methods, key=lambda x: x[3])

    print(f"\n   ✓ Best method: {best_method[0]} with loss={best_method[3]:.4f}")

    print("\n9. Saving optimal weights...")

    # Use the selected method
    final_w1, final_w2 = best_method[1], best_method[2]

    # Save weights
    weights_data = {
        'retinal_weight': float(final_w1),
        'lifestyle_weight': float(final_w2),
        'best_loss': float(best_method[3]),
        'method': f'{best_method[0]}_optimized',
        'calibration': 'lifestyle_calibrated',
        'constraint': 'w1 + w2 = 1',
        'validation': {
            'method_used': best_method[0],
            'training_samples': 1000
        },
        'performance': {
            'retinal_standalone_accuracy': float(1 - np.mean(np.abs(retinal_preds - y_true))),
            'lifestyle_standalone_accuracy': float(1 - np.mean(np.abs(lifestyle_preds - y_true))),
            'lifestyle_calibrated_accuracy': float(1 - np.mean(np.abs(lifestyle_preds_calibrated - y_true))),
            'fused_accuracy_estimate': float(1 - best_method[3])
        }
    }

    output_path = Path(__file__).parent / 'models' / 'fusion' / 'optimal_weights.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(weights_data, f, indent=2)

    print(f"   ✓ Weights saved to {output_path}")

    # Summary
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"\n🎯 OPTIMAL FUSION WEIGHTS:")
    print(f"   • Retinal (w1): {final_w1:.3f} ({final_w1*100:.1f}%)")
    print(f"   • Lifestyle (w2): {final_w2:.3f} ({final_w2*100:.1f}%)")
    print(f"   • Constraint satisfied: w1 + w2 = {final_w1 + final_w2:.3f} ≈ 1.0")
    print(f"\n📊 EXPECTED PERFORMANCE:")
    print(f"   • Retinal only: {weights_data['performance']['retinal_standalone_accuracy']:.2%}")
    print(f"   • Lifestyle only: {weights_data['performance']['lifestyle_standalone_accuracy']:.2%}")
    print(f"   • Fused (optimal): {weights_data['performance']['fused_accuracy_estimate']:.2%}")
    print("\n✨ The fusion system will now use these optimized weights!")
    print("="*60)


if __name__ == "__main__":
    main()