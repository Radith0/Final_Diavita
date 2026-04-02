"""Initialize database and create default users."""
import os
from app import create_app
from models.database import db
from models.database.user import User

def init_database():
    """Initialize database and create default users."""
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()

        if not admin_user:
            print("\nCreating default admin user...")
            admin = User(
                username='admin',
                email='admin@diabetesapp.com',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print("  Username: admin")
            print("  Password: admin123")
            print("  IMPORTANT: Change this password in production!")
        else:
            print("\nAdmin user already exists.")

        # Create a sample normal user
        normal_user = User.query.filter_by(username='user').first()

        if not normal_user:
            print("\nCreating sample normal user...")
            user = User(
                username='user',
                email='user@diabetesapp.com',
                password='user123',
                role='normal'
            )
            db.session.add(user)
            db.session.commit()
            print("Normal user created successfully!")
            print("  Username: user")
            print("  Password: user123")
        else:
            print("\nSample normal user already exists.")

        print("\n✓ Database initialization completed!")


if __name__ == '__main__':
    init_database()