"""User history model for tracking user actions and predictions."""
from datetime import datetime
from models.database import db


class UserHistory(db.Model):
    """Track user actions and predictions."""

    __tablename__ = 'user_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action_type = db.Column(db.String(50), nullable=False)  # e.g., 'login', 'prediction', 'upload', 'logout'
    action_details = db.Column(db.JSON)  # Store additional action details as JSON
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Prediction specific fields
    prediction_type = db.Column(db.String(50))  # e.g., 'retinal', 'lifestyle', 'fusion'
    prediction_result = db.Column(db.JSON)  # Store prediction results
    confidence_score = db.Column(db.Float)

    # Relationships
    user = db.relationship('User', back_populates='history_entries')

    def __init__(self, user_id, action_type, action_details=None, ip_address=None,
                 user_agent=None, prediction_type=None, prediction_result=None, confidence_score=None):
        """Initialize history entry."""
        self.user_id = user_id
        self.action_type = action_type
        self.action_details = action_details or {}
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.prediction_type = prediction_type
        self.prediction_result = prediction_result
        self.confidence_score = confidence_score

    def to_dict(self):
        """Convert history entry to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'action_details': self.action_details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'prediction_type': self.prediction_type,
            'prediction_result': self.prediction_result,
            'confidence_score': self.confidence_score
        }

    def __repr__(self):
        return f'<UserHistory {self.id} - {self.action_type} by User {self.user_id}>'
