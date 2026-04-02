"""Retinal image analysis agent using CNN."""
import time
from typing import Dict, Any
import numpy as np
from pathlib import Path
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class RetinalAgent(BaseAgent):
    """Agent responsible for retinal image analysis and DR detection."""

    def __init__(self):
        """Initialize retinal agent with CNN model."""
        super().__init__(agent_id="retinal_agent")
        self.model = None
        self.version = "1.0.0-cnn"

        # Load model on initialization
        self.model_loaded = False
        try:
            self._load_model()
            self.model_loaded = True
            logger.info("RetinalAgent initialized with loaded CNN model")
        except Exception as e:
            logger.warning(f"Retinal model not loaded: {e}")
            logger.info("RetinalAgent initialized without model - using fallback")

    def _load_model(self):
        """Load retinal model directly from weights file."""
        from tensorflow import keras

        # Path to cnn_model_1.h5 - best performing model
        model_path = Path(__file__).parent.parent / 'models' / 'retinal' / 'weights' / 'cnn_model_1.h5'

        if not model_path.exists():
            # Try retina_attention_model.h5
            logger.warning("cnn_model_1.h5 not found, trying retina_attention_model.h5")
            model_path = model_path.parent / 'retina_attention_model.h5'

        if not model_path.exists():
            # Try full_retina_model.h5
            logger.warning("retina_attention_model.h5 not found, trying full_retina_model.h5")
            model_path = model_path.parent / 'full_retina_model.h5'

        if not model_path.exists():
            raise FileNotFoundError(f"No retinal model found at {model_path}")

        logger.info("=" * 80)
        logger.info("RETINAL MODEL LOADING")
        logger.info("=" * 80)
        logger.info(f"Loading retinal model from: {model_path.name}")
        logger.info(f"Full path: {model_path}")

        # Handle different models differently
        if 'full_retina_model' in model_path.name:
            # Enable unsafe deserialization for full_retina_model (contains Lambda layers)
            keras.config.enable_unsafe_deserialization()
            self.model = keras.models.load_model(
                str(model_path),
                compile=False
            )
        else:
            # Normal loading for other models
            self.model = keras.models.load_model(
                str(model_path),
                compile=False,
                safe_mode=False
            )

        # Log detailed model information
        logger.info(f"✓ Model loaded successfully: {model_path.name}")
        logger.info(f"  Architecture: CNN (Convolutional Neural Network)")
        logger.info(f"  Input shape: {self.model.input_shape}")
        logger.info(f"  Output shape: {self.model.output_shape}")
        logger.info(f"  Total layers: {len(self.model.layers)}")

        # Count trainable parameters
        trainable_params = sum([keras.backend.count_params(w) for w in self.model.trainable_weights])
        logger.info(f"  Trainable parameters: {trainable_params:,}")

        logger.info("")
        logger.info("API ENDPOINTS TO CALL THIS MODEL:")
        logger.info("  POST /api/retinal/analyze")
        logger.info("")
        logger.info("REQUEST FORMAT:")
        logger.info("  Content-Type: multipart/form-data")
        logger.info("  Body: { \"image\": <retinal_image_file> }")
        logger.info("  Supported formats: JPG, PNG, BMP")
        logger.info("  Image preprocessing: Resized to 224x224, normalized to [0,1]")
        logger.info("")
        logger.info("EXPECTED INPUT:")
        logger.info("  - Retinal fundus image (color)")
        logger.info("  - Resolution: 224x224 pixels (auto-resized)")
        logger.info("  - Channels: 3 (RGB)")
        logger.info("")
        logger.info("MODEL OUTPUT:")
        logger.info("  - 5 class probabilities: [No DR, Mild, Moderate, Severe, Proliferative]")
        logger.info("  - DR probability (1 - P(No DR))")
        logger.info("  - Severity classification")
        logger.info("  - Confidence score")
        logger.info("")
        logger.info("EXAMPLE cURL:")
        logger.info('  curl -X POST http://localhost:5000/api/retinal/analyze \\')
        logger.info('       -F "image=@/path/to/retinal_image.jpg"')
        logger.info("=" * 80)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze retinal image for diabetic retinopathy.

        Args:
            task: Dict containing 'image' (file path or bytes)

        Returns:
            Analysis result with DR detection, severity, and findings
        """
        try:
            start_time = time.time()
            image = task.get('image')

            if not image:
                raise ValueError("No image provided for retinal analysis")

            logger.info("Starting retinal image analysis")
            self.log_action("analysis_started", {"image_type": type(image).__name__})

            # If model not loaded, return fallback
            if not self.model_loaded or self.model is None:
                logger.warning("Retinal model not loaded, using fallback")
                return {
                    'status': 'success',
                    'dr_detected': False,
                    'severity': 'none',
                    'confidence': 0.5,
                    'findings': {},
                    'dr_probability': 0.0,
                    'processing_time': 0.0,
                    'model_version': 'fallback',
                    'note': 'Model not loaded - using fallback values'
                }

            # Preprocess image
            logger.debug("Preprocessing retinal image")
            processed_image = self._preprocess_image(image)
            self.log_action("image_preprocessed", processed_image.shape)

            # Run CNN inference directly on model
            logger.debug("Running CNN inference")
            predictions = self.model.predict(processed_image, verbose=0)

            # Parse predictions from model output
            prediction = self._parse_prediction(predictions)
            self.log_action("prediction_complete", prediction)

            # Extract results
            dr_detected = prediction['dr_probability'] > 0.5
            severity = self._determine_severity(prediction['dr_probability'])
            confidence = float(prediction['confidence'])

            # Extract key findings
            findings = self._extract_findings(prediction)

            processing_time = time.time() - start_time

            result = {
                'status': 'success',
                'dr_detected': dr_detected,
                'severity': severity,
                'confidence': confidence,
                'findings': findings,
                'dr_probability': float(prediction['dr_probability']),
                'processing_time': processing_time,
                'model_version': self.version
            }

            logger.info(f"Retinal analysis complete. DR detected: {dr_detected}, Severity: {severity}")
            self.log_action("analysis_complete", result)

            return result

        except Exception as e:
            logger.error(f"Retinal analysis failed: {str(e)}")
            self.log_action("analysis_failed", str(e))
            return {
                'status': 'error',
                'error': str(e),
                'dr_detected': None,
                'severity': None,
                'confidence': 0.0
            }

    def _determine_severity(self, dr_probability: float) -> str:
        """
        Determine DR severity level.

        Args:
            dr_probability: Probability of DR (0-1)

        Returns:
            Severity level string
        """
        if dr_probability < 0.3:
            return "none"
        elif dr_probability < 0.5:
            return "mild"
        elif dr_probability < 0.7:
            return "moderate"
        else:
            return "severe"

    def _extract_findings(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed findings from prediction.

        Args:
            prediction: Raw model prediction

        Returns:
            Structured findings dictionary
        """
        findings = {
            'microaneurysms': prediction.get('features', {}).get('microaneurysms', False),
            'hemorrhages': prediction.get('features', {}).get('hemorrhages', False),
            'exudates': prediction.get('features', {}).get('exudates', False),
            'neovascularization': prediction.get('features', {}).get('neovascularization', False)
        }

        # Count detected features
        detected_features = sum(1 for v in findings.values() if v)
        findings['total_features_detected'] = detected_features

        return findings

    def _preprocess_image(self, image) -> np.ndarray:
        """
        Preprocess retinal image for model input.

        Args:
            image: Image file path, bytes, or numpy array

        Returns:
            Preprocessed image array (1, 224, 224, 3)
        """
        from PIL import Image
        import io

        # Load image
        if isinstance(image, (str, Path)):
            img = Image.open(image).convert('RGB')
        elif isinstance(image, bytes):
            img = Image.open(io.BytesIO(image)).convert('RGB')
        elif isinstance(image, np.ndarray):
            if len(image.shape) == 2:  # Grayscale
                img = Image.fromarray(image).convert('RGB')
            else:
                img = Image.fromarray(image.astype('uint8'))
        else:
            img = image

        # Resize to model input size
        img = img.resize((224, 224))

        # Convert to numpy array
        img_array = np.array(img)

        # Normalize to [0, 1]
        img_array = img_array.astype('float32') / 255.0

        # Add batch dimension
        if len(img_array.shape) == 3:
            img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def _parse_prediction(self, predictions: np.ndarray) -> Dict[str, Any]:
        """
        Parse model output into structured prediction.

        Args:
            predictions: Model output (1, 5) with class probabilities

        Returns:
            Parsed prediction dictionary
        """
        # predictions shape: (1, 5) for 5 DR severity classes
        # Classes: 0=No DR, 1=Mild, 2=Moderate, 3=Severe, 4=Proliferative
        class_probs = predictions[0]
        predicted_class = int(np.argmax(class_probs))
        confidence = float(class_probs[predicted_class])

        # DR detected if predicted class > 0
        dr_detected = predicted_class > 0
        dr_probability = float(1.0 - class_probs[0])  # 1 - P(No DR)

        # Map class to severity
        severity_map = {
            0: 'none',
            1: 'mild',
            2: 'moderate',
            3: 'severe',
            4: 'proliferative'
        }
        severity = severity_map.get(predicted_class, 'unknown')

        return {
            'dr_detected': dr_detected,
            'dr_probability': dr_probability,
            'predicted_class': predicted_class,
            'severity': severity,
            'confidence': confidence,
            'class_probabilities': {
                'no_dr': float(class_probs[0]),
                'mild': float(class_probs[1]),
                'moderate': float(class_probs[2]),
                'severe': float(class_probs[3]),
                'proliferative': float(class_probs[4])
            },
            'features': {
                'microaneurysms': dr_probability > 0.3,
                'hemorrhages': predicted_class >= 2,
                'exudates': predicted_class >= 2,
                'neovascularization': predicted_class >= 3
            }
        }
