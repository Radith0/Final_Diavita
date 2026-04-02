"""User model for authentication and authorization."""
from datetime import datetime
from models.database import db
import bcrypt


class User(db.Model):
    """User model with role-based access control."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='normal')  # 'admin' or 'normal'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    # Relationships
    history_entries = db.relationship('UserHistory', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, username, email, password, role='normal'):
        """Initialize user with hashed password."""
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        """Hash and set user password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_sensitive:
            data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'