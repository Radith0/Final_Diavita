"""Configuration settings for the backend application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""

    # Application
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    PORT = int(os.getenv('PORT', 5000))

    # Groq AI
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///diabetes_app.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3002').split(',')

    # Paths
    BASE_DIR = Path(__file__).parent
    DATASET_PATH = BASE_DIR / os.getenv('DATASET_PATH', 'data/datasets')
    UPLOAD_FOLDER = BASE_DIR / os.getenv('UPLOAD_FOLDER', 'uploads')
    MODEL_DIR = BASE_DIR / 'models'

    # File Upload
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png').split(','))
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / os.getenv('LOG_FILE', 'logs/app.log')

    # Rate Limiting
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 60))

    # Model Configuration
    RETINAL_IMAGE_SIZE = 512
    BATCH_SIZE = 32
    SENSITIVITY_THRESHOLD = 0.90
    AUC_THRESHOLD = 0.85
    PROCESSING_TIME_THRESHOLD = 2.0

    # LLM Configuration
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 500

    @classmethod
    def init_app(cls):
        """Initialize application directories."""
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        cls.DATASET_PATH.mkdir(parents=True, exist_ok=True)
