"""Tests for User model."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.database.user import User
from models.database import db as _db


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, app, db):
        """Test creating a user."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            assert user.id is not None
            assert user.username == 'testuser'

    def test_password_is_hashed(self, app, db):
        """Test that password is stored hashed, not plain text."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            assert user.password_hash != 'pass123'

    def test_check_password_correct(self, app, db):
        """Test password check with correct password."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            assert user.check_password('pass123') is True

    def test_check_password_incorrect(self, app, db):
        """Test password check with wrong password."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            assert user.check_password('wrongpass') is False

    def test_set_password_changes_hash(self, app, db):
        """Test that set_password changes the hash."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            old_hash = user.password_hash
            user.set_password('newpass456')
            assert user.password_hash != old_hash

    def test_is_admin_true(self, app, db):
        """Test is_admin returns True for admin user."""
        with app.app_context():
            user = User(username='admin', email='admin@example.com', password='pass123', role='admin')
            db.session.add(user)
            db.session.commit()
            assert user.is_admin() is True

    def test_is_admin_false(self, app, db):
        """Test is_admin returns False for normal user."""
        with app.app_context():
            user = User(username='normal', email='normal@example.com', password='pass123', role='normal')
            db.session.add(user)
            db.session.commit()
            assert user.is_admin() is False

    def test_to_dict(self, app, db):
        """Test to_dict returns expected fields."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            d = user.to_dict()
            assert d['username'] == 'testuser'
            assert d['email'] == 'test@example.com'
            assert 'id' in d

    def test_to_dict_sensitive(self, app, db):
        """Test to_dict with sensitive data includes updated_at."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            d = user.to_dict(include_sensitive=True)
            assert 'updated_at' in d

    def test_to_dict_no_sensitive(self, app, db):
        """Test to_dict without sensitive flag excludes updated_at."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password='pass123')
            db.session.add(user)
            db.session.commit()
            d = user.to_dict(include_sensitive=False)
            assert 'updated_at' not in d

    def test_unique_username(self, app, db):
        """Test that duplicate username raises error."""
        with app.app_context():
            u1 = User(username='same', email='a@example.com', password='pass123')
            db.session.add(u1)
            db.session.commit()
            u2 = User(username='same', email='b@example.com', password='pass123')
            db.session.add(u2)
            with pytest.raises(Exception):
                db.session.commit()

    def test_unique_email(self, app, db):
        """Test that duplicate email raises error."""
        with app.app_context():
            u1 = User(username='user1', email='same@example.com', password='pass123')
            db.session.add(u1)
            db.session.commit()
            u2 = User(username='user2', email='same@example.com', password='pass123')
            db.session.add(u2)
            with pytest.raises(Exception):
                db.session.commit()
