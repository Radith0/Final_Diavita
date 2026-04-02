"""Lifestyle data analysis agent using Gradient Boosting."""
import time
from typing import Dict, Any
import numpy as np
from pathlib import Path
import joblib
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class LifestyleAgent(BaseAgent):
    """Agent responsible for lifestyle and demographic risk prediction."""

    def __init__(self):
        """Initialize lifestyle agent with Gradient Boosting model."""
        super().__init__(agent_id="lifestyle_agent")
        self.model = None
        self.scaler = None
        self.imputer = None
        self.version = "1.0.0"

        # Load model on initialization
        try:
            self._load_model()
            logger.info("LifestyleAgent initialized with loaded Gradient Boosting model")
        except Exception as e:
            logger.warning(f"Model not loaded on init: {e}. Predictions will fail until model is loaded.")
            logger.info("LifestyleAgent initialized without model")

    def _load_model(self):
        """Load lifestyle model and preprocessors directly from weight files."""
        weights_dir = Path(__file__).parent.parent / 'models' / 'lifestyle' / 'weights'

        logger.info("=" * 80)
        logger.info("LIFESTYLE MODEL LOADING")
        logger.info("=" * 80)

        # Load main model (from notebook export)
        model_path = weights_dir / 'gradient_boosting_model.pkl'
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        self.model = joblib.load(model_path)
        logger.info(f"✓ Loaded Gradient Boosting model from {model_path.name}")
        logger.info(f"  Full path: {model_path}")

        # Get model details
        model_type = type(self.model).__name__
        n_estimators = getattr(self.model, 'n_estimators', 'N/A')
        n_features = getattr(self.model, 'n_features_in_', 'N/A')

        logger.info(f"  Model type: {model_type}")
        logger.info(f"  Number of estimators: {n_estimators}")
        logger.info(f"  Number of features: {n_features}")

        # Load scaler (from notebook export)
        scaler_path = weights_dir / 'scaler.pkl'
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            logger.info(f"✓ Loaded scaler from {scaler_path.name}")
        else:
            logger.warning("⚠ Scaler not found, predictions may be inaccurate")

        # Load imputer (from notebook export)
        imputer_path = weights_dir / 'imputer.pkl'
        if imputer_path.exists():
            self.imputer = joblib.load(imputer_path)
            logger.info(f"✓ Loaded imputer from {imputer_path.name}")
        else:
            logger.warning("⚠ Imputer not found")

        logger.info("")
        logger.info("API ENDPOINTS TO CALL THIS MODEL:")
        logger.info("  POST /api/lifestyle/predict")
        logger.info("")
        logger.info("REQUEST FORMAT:")
        logger.info("  Content-Type: application/json")
        logger.info("  Body: { ...features... } (JSON object with features directly)")
        logger.info("")
        logger.info("REQUIRED INPUT FEATURES (16 total):")
        logger.info("  Numeric:")
        logger.info("    - age: Patient age (years)")
        logger.info("    - bmi: Body Mass Index")
        logger.info("    - hba1c: HbA1c level (%)")
        logger.info("    - blood_glucose: Blood glucose level (mg/dL)")
        logger.info("    - blood_pressure_systolic: Systolic BP (mmHg)")
        logger.info("    - blood_pressure_diastolic: Diastolic BP (mmHg)")
        logger.info("    - cholesterol: Total cholesterol (mg/dL)")
        logger.info("    - physical_activity: Minutes per week")
        logger.info("    - sleep_hours: Hours per night")
        logger.info("  Categorical:")
        logger.info("    - gender: 'male' or 'female'")
        logger.info("    - smoking: 'yes' or 'no'")
        logger.info("    - alcohol: 'no', 'moderate', or 'heavy'")
        logger.info("    - family_history: 'yes' or 'no'")
        logger.info("    - stress_level: 'low', 'moderate', or 'high'")
        logger.info("    - diet_quality: 'poor', 'average', or 'good'")
        logger.info("  Computed:")
        logger.info("    - bmi_age_interaction: (bmi * age) / 100")
        logger.info("")
        logger.info("MODEL OUTPUT:")
        logger.info("  - risk_score: Calibrated diabetes risk [0-1]")
        logger.info("  - risk_probability: Same as risk_score")
        logger.info("  - raw_probability: Uncalibrated model output")
        logger.info("  - confidence: Prediction confidence")
        logger.info("  - key_factors: Top 5 contributing risk factors")
        logger.info("")
        logger.info("PREPROCESSING PIPELINE:")
        logger.info("  1. Feature engineering (compute bmi_age_interaction)")
        logger.info("  2. Missing value imputation (numeric features)")
        logger.info("  3. Standard scaling (normalize features)")
        logger.info("  4. Gradient Boosting prediction")
        logger.info("  5. Probability calibration (maps [0.4,1.0] → [0.0,1.0])")
        logger.info("")
        logger.info("EXAMPLE cURL:")
        logger.info('  curl -X POST http://localhost:5000/api/lifestyle/predict \\')
        logger.info('       -H "Content-Type: application/json" \\')
        logger.info('       -d \'{"age": 45, "gender": "male", "bmi": 28.5,')
        logger.info('            "hba1c": 6.2, "blood_glucose": 110,')
        logger.info('            "blood_pressure_systolic": 130,')
        logger.info('            "blood_pressure_diastolic": 85,')
        logger.info('            "cholesterol": 220, "smoking": "no",')
        logger.info('            "alcohol": "moderate", "physical_activity": 150,')
        logger.info('            "family_history": "yes", "sleep_hours": 7,')
        logger.info('            "stress_level": "moderate", "diet_quality": "average"}\'')
        logger.info("=" * 80)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lifestyle data for diabetes risk.

        Args:
            task: Dict containing 'lifestyle_data' with demographic/behavioral info

        Returns:
            Risk prediction with key contributing factors
        """
        try:
            start_time = time.time()
            lifestyle_data = task.get('lifestyle_data', {})

            if not lifestyle_data:
                raise ValueError("No lifestyle data provided")

            logger.info(f"Starting lifestyle analysis for {len(lifestyle_data)} features")
            self.log_action("analysis_started", {"features_count": len(lifestyle_data)})

            # Feature engineering
            logger.debug("Engineering features from lifestyle data")
            features = self._engineer_features(lifestyle_data)
            self.log_action("features_engineered", features.shape)

            # Run Gradient Boosting prediction
            logger.debug("Running Gradient Boosting prediction")
            prediction = self._predict(features)
            self.log_action("prediction_complete", prediction)

            # Extract key risk factors
            key_factors = self._identify_key_factors(lifestyle_data, prediction)

            processing_time = time.time() - start_time

            result = {
                'status': 'success',
                'risk_score': float(prediction['risk_score']),
                'risk_probability': float(prediction['probability']),
                'confidence': float(prediction['confidence']),
                'key_factors': key_factors,
                'feature_importance': prediction.get('feature_importance', {}),
                'processing_time': processing_time,
                'model_version': self.version
            }

            logger.info(f"Lifestyle analysis complete. Risk score: {result['risk_score']:.2f}")
            self.log_action("analysis_complete", result)

            return result

        except Exception as e:
            logger.error(f"Lifestyle analysis failed: {str(e)}")
            self.log_action("analysis_failed", str(e))
            return {
                'status': 'error',
                'error': str(e),
                'risk_score': 0.0,
                'confidence': 0.0
            }

    def _identify_key_factors(self, lifestyle_data: Dict[str, Any],
                             prediction: Dict[str, Any]) -> list:
        """
        Identify key contributing risk factors.

        Args:
            lifestyle_data: Original lifestyle input
            prediction: Model prediction with feature importance

        Returns:
            List of key risk factors with their impact
        """
        key_factors = []
        feature_importance = prediction.get('feature_importance', {})

        # Helper to safely convert to number
        def safe_number(val):
            if val == '' or val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        # Common risk factors to check
        risk_checks = [
            ('bmi', 'High BMI', lambda x: safe_number(x) is not None and safe_number(x) > 30),
            ('age', 'Age over 45', lambda x: safe_number(x) is not None and safe_number(x) > 45),
            ('physical_activity', 'Low physical activity', lambda x: safe_number(x) is not None and safe_number(x) < 30),
            ('sleep_hours', 'Insufficient sleep', lambda x: safe_number(x) is not None and safe_number(x) < 6),
            ('family_history', 'Family history of diabetes', lambda x: x == True or x == 'true'),
            ('smoking', 'Smoking', lambda x: x == True or x == 'true'),
        ]

        for feature, description, condition in risk_checks:
            value = lifestyle_data.get(feature)
            if value is not None and value != '' and condition(value):
                importance = feature_importance.get(feature, 0.0)
                key_factors.append({
                    'factor': description,
                    'value': value,
                    'importance': float(importance),
                    'modifiable': feature not in ['age', 'family_history']
                })

        # Sort by importance
        key_factors.sort(key=lambda x: x['importance'], reverse=True)

        return key_factors[:5]  # Return top 5 factors

    def _engineer_features(self, lifestyle_data: Dict[str, Any]) -> np.ndarray:
        """Engineer features from raw lifestyle data."""
        # Extract and convert features to numpy array (16 features expected)
        features = []

        # Numeric features
        features.append(float(lifestyle_data.get('age', 40)))
        features.append(1 if lifestyle_data.get('gender', 'male').lower() == 'male' else 0)
        features.append(float(lifestyle_data.get('bmi', 25)))
        features.append(float(lifestyle_data.get('hba1c', 5.5)))
        features.append(float(lifestyle_data.get('blood_glucose', 100)))
        features.append(float(lifestyle_data.get('blood_pressure_systolic', 120)))
        features.append(float(lifestyle_data.get('blood_pressure_diastolic', 80)))
        features.append(float(lifestyle_data.get('cholesterol', 200)))

        # Binary features
        features.append(1 if lifestyle_data.get('smoking', 'no').lower() in ['yes', 'true', '1'] else 0)

        # Alcohol: no=0, moderate=1, heavy=2
        alcohol = lifestyle_data.get('alcohol', 'no').lower()
        features.append(0 if alcohol == 'no' else (1 if alcohol == 'moderate' else 2))

        features.append(float(lifestyle_data.get('physical_activity', 30)))
        features.append(1 if lifestyle_data.get('family_history', 'no').lower() in ['yes', 'true', '1'] else 0)
        features.append(float(lifestyle_data.get('sleep_hours', 7)))

        # Stress: low=0, moderate=1, high=2
        stress = lifestyle_data.get('stress_level', 'moderate').lower()
        features.append(0 if stress == 'low' else (1 if stress == 'moderate' else 2))

        # Diet quality: poor=0, average=1, good=2
        diet = lifestyle_data.get('diet_quality', 'average').lower()
        features.append(0 if diet == 'poor' else (1 if diet == 'average' else 2))

        # Add interaction feature
        bmi_age_interaction = features[2] * features[0] / 100
        features.append(bmi_age_interaction)

        return np.array([features])

    def _calibrate_probability(self, prob: float) -> float:
        """
        Calibrate the probability to handle high baseline.
        Maps [0.4, 1.0] range to [0.0, 1.0] for better fusion.
        """
        # Observed that minimum probability is around 0.4
        min_prob = 0.4
        max_prob = 1.0

        # Linear calibration
        if prob <= min_prob:
            return 0.0
        elif prob >= max_prob:
            return 1.0
        else:
            # Map [0.4, 1.0] to [0.0, 1.0]
            calibrated = (prob - min_prob) / (max_prob - min_prob)
            return float(np.clip(calibrated, 0, 1))

    def _predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Run prediction with preprocessing and calibration."""
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # Apply imputer to numeric columns (indices 2-7) if available
        if self.imputer is not None:
            features_copy = features.copy()
            numeric_indices = [2, 3, 4, 5, 6, 7]
            numeric_features = features_copy[:, numeric_indices]
            numeric_imputed = self.imputer.transform(numeric_features)
            features_copy[:, numeric_indices] = numeric_imputed
            features = features_copy

        # Apply scaler if available
        if self.scaler is not None:
            features = self.scaler.transform(features)

        # Predict
        prediction_proba = self.model.predict_proba(features)[0]
        prediction_class = self.model.predict(features)[0]

        raw_risk_score = float(prediction_proba[1])  # Probability of class 1 (diabetic)

        # Apply calibration to handle high baseline
        calibrated_risk_score = self._calibrate_probability(raw_risk_score)

        confidence = float(max(prediction_proba))

        return {
            'risk_score': calibrated_risk_score,
            'probability': calibrated_risk_score,
            'raw_probability': raw_risk_score,  # Keep raw for debugging
            'predicted_class': int(prediction_class),
            'confidence': confidence,
            'feature_importance': {}  # Can be populated from model.feature_importances_ if needed
        }
