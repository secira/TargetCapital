#!/usr/bin/env python3
"""
Create test user account with Target Pro access for broker testing
"""

from app import app, db
from models import User, PricingPlan
from werkzeug.security import generate_password_hash

def create_test_user():
    with app.app_context():
        # Check if test user already exists
        test_user = User.query.filter_by(username='traderplususer').first()
        
        if not test_user:
            # Create Target Pro test user
            test_user = User(
                username='traderplususer',
                email='traderplus@test.com',
                password_hash=generate_password_hash('trader123'),
                pricing_plan=PricingPlan.TARGET_PRO,
                is_active=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Target Pro test user created:")
            print("   Username: traderplususer")
            print("   Password: trader123")
            print("   Plan: Target Pro (has access to broker features)")
        else:
            # Update existing user to Target Pro
            test_user.pricing_plan = PricingPlan.TARGET_PRO
            test_user.is_active = True
            db.session.commit()
            
            print("✅ Updated existing test user to Target Pro plan")
            print("   Username: traderplususer")
            print("   Password: trader123")
            print("   Plan: Target Pro (has access to broker features)")

if __name__ == '__main__':
    create_test_user()