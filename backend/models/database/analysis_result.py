"""Analysis results model for storing user predictions."""
from datetime import datetime
from models.database import db


class AnalysisResult(db.Model):
    """Store diabetes risk analysis results."""

    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Analysis metadata
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    analysis_type = db.Column(db.String(50), nullable=False)  # 'retinal', 'lifestyle', 'complete'

    # Risk scores (0-100)
    retinal_risk = db.Column(db.Float)
    lifestyle_risk = db.Column(db.Float)
    combined_risk = db.Column(db.Float)
    confidence_score = db.Column(db.Float)

    # Risk category
    risk_category = db.Column(db.String(20))  # 'low', 'moderate', 'high', 'very_high'

    # Input data
    retinal_image_path = db.Column(db.String(500))
    lifestyle_data = db.Column(db.JSON)  # Store all lifestyle inputs

    # Results and recommendations
    detailed_results = db.Column(db.JSON)  # Store full analysis output
    recommendations = db.Column(db.JSON)  # AI-generated recommendations

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('analysis_results', passive_deletes=True))

    def __init__(self, user_id, analysis_type, **kwargs):
        """Initialize analysis result."""
        self.user_id = user_id
        self.analysis_type = analysis_type

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def calculate_risk_category(self):
        """Calculate risk category based on combined risk score."""
        if self.combined_risk is None:
            return 'unknown'

        if self.combined_risk < 25:
            return 'low'
        elif self.combined_risk < 50:
            return 'moderate'
        elif self.combined_risk < 75:
            return 'high'
        else:
            return 'very_high'

    def to_dict(self):
        """Convert analysis result to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'analysis_type': self.analysis_type,
            'retinal_risk': self.retinal_risk,
            'lifestyle_risk': self.lifestyle_risk,
            'combined_risk': self.combined_risk,
            'confidence_score': self.confidence_score,
            'risk_category': self.risk_category or self.calculate_risk_category(),
            'lifestyle_data': self.lifestyle_data,
            'detailed_results': self.detailed_results,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_summary_dict(self):
        """Convert to summary dictionary (less data)."""
        return {
            'id': self.id,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'analysis_type': self.analysis_type,
            'combined_risk': self.combined_risk,
            'risk_category': self.risk_category or self.calculate_risk_category(),
            'confidence_score': self.confidence_score
        }

    def __repr__(self):
        return f'<AnalysisResult {self.id} - User {self.user_id} - Risk: {self.combined_risk}%>'
