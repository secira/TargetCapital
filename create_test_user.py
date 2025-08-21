#!/usr/bin/env python3
"""
Create test user account with TraderPlus access for broker testing
"""

from app import app, db
from models import User, PricingPlan
from werkzeug.security import generate_password_hash

def create_test_user():
    with app.app_context():
        # Check if test user already exists
        test_user = User.query.filter_by(username='traderplususer').first()
        
        if not test_user:
            # Create TraderPlus test user
            test_user = User(
                username='traderplususer',
                email='traderplus@test.com',
                password_hash=generate_password_hash('trader123'),
                pricing_plan=PricingPlan.TRADER_PLUS,
                is_active=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ TraderPlus test user created:")
            print("   Username: traderplususer")
            print("   Password: trader123")
            print("   Plan: TraderPlus (has access to broker features)")
        else:
            # Update existing user to TraderPlus
            test_user.pricing_plan = PricingPlan.TRADER_PLUS
            test_user.is_active = True
            db.session.commit()
            
            print("✅ Updated existing test user to TraderPlus plan")
            print("   Username: traderplususer")
            print("   Password: trader123")
            print("   Plan: TraderPlus (has access to broker features)")

if __name__ == '__main__':
    create_test_user()