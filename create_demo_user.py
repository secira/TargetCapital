#!/usr/bin/env python3
"""
Script to create demo user account for tCapital application
"""

from app import app, db
from models import User

def create_demo_user():
    """Create demo user account"""
    with app.app_context():
        # Check if demo user already exists
        demo_user = User.query.filter_by(username='demo').first()
        if demo_user:
            print("Demo user already exists!")
            return
        
        # Create demo user
        demo_user = User(
            username='demo',
            email='demo@tcapital.com',
            first_name='Demo',
            last_name='User'
        )
        demo_user.set_password('demo123')
        
        db.session.add(demo_user)
        db.session.commit()
        
        print("Demo user created successfully!")
        print("Username: demo")
        print("Password: demo123")
        print("Email: demo@tcapital.com")

if __name__ == '__main__':
    create_demo_user()