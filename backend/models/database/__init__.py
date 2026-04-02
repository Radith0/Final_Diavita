from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """Initialize database with app context."""
    db.init_app(app)

    # Import models to ensure they're registered
    from models.database.user import User
    from models.database.user_history import UserHistory
    from models.database.analysis_result import AnalysisResult
    from models.database.health_plan import HealthPlan

    with app.app_context():
        db.create_all()
