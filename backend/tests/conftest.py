"""Shared test fixtures for backend tests."""
import os
import sys
import pytest

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_ACCESS_TOKEN_EXPIRES'] = '3600'
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from models.database import db as _db


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    return app


@pytest.fixture(scope='function')
def db(app):
    """Create fresh database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Create test client."""
    return app.test_client()
