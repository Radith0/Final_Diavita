"""Health plan model for user goals and what-if scenarios."""
from datetime import datetime
from models.database import db


class HealthPlan(db.Model):
    """Store user health plans and goals."""

    __tablename__ = 'health_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Plan details
    plan_name = db.Column(db.String(200), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # 'weight_loss', 'exercise', 'diet', 'lifestyle_change', 'custom'
    description = db.Column(db.Text)

    # What-if scenario data
    scenario_parameters = db.Column(db.JSON)  # Target values (weight, BMI, exercise, diet, etc.)
    expected_outcomes = db.Column(db.JSON)  # Predicted results from simulation

    # Progress tracking
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    target_date = db.Column(db.DateTime)
    current_progress = db.Column(db.Float, default=0.0)  # Percentage 0-100

    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'paused', 'abandoned'
    is_primary = db.Column(db.Boolean, default=False)  # Only one primary plan per user

    # Milestones and checkpoints
    milestones = db.Column(db.JSON)  # Array of milestone objects
    checkpoints = db.Column(db.JSON)  # Array of checkpoint records

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref=db.backref('health_plans', passive_deletes=True))

    def __init__(self, user_id, plan_name, plan_type, **kwargs):
        """Initialize health plan."""
        self.user_id = user_id
        self.plan_name = plan_name
        self.plan_type = plan_type

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def update_progress(self, progress_value):
        """Update plan progress."""
        self.current_progress = max(0, min(100, progress_value))
        if self.current_progress >= 100 and self.status == 'active':
            self.status = 'completed'
            self.completed_at = datetime.utcnow()

    def set_as_primary(self):
        """Set this plan as primary (deactivate others)."""
        # Deactivate all other primary plans for this user
        HealthPlan.query.filter_by(user_id=self.user_id, is_primary=True).update({'is_primary': False})
        self.is_primary = True
        db.session.commit()

    def add_checkpoint(self, checkpoint_data):
        """Add a progress checkpoint."""
        if self.checkpoints is None:
            self.checkpoints = []

        checkpoint = {
            'date': datetime.utcnow().isoformat(),
            'data': checkpoint_data,
            'progress': self.current_progress
        }
        self.checkpoints.append(checkpoint)

    def to_dict(self):
        """Convert health plan to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_name': self.plan_name,
            'plan_type': self.plan_type,
            'description': self.description,
            'scenario_parameters': self.scenario_parameters,
            'expected_outcomes': self.expected_outcomes,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'current_progress': self.current_progress,
            'status': self.status,
            'is_primary': self.is_primary,
            'milestones': self.milestones,
            'checkpoints': self.checkpoints,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def to_summary_dict(self):
        """Convert to summary dictionary."""
        return {
            'id': self.id,
            'plan_name': self.plan_name,
            'plan_type': self.plan_type,
            'current_progress': self.current_progress,
            'status': self.status,
            'is_primary': self.is_primary,
            'start_date': self.start_date.isoformat() if self.start_date else None
        }

    def __repr__(self):
        return f'<HealthPlan {self.id} - {self.plan_name} ({self.status})>'
