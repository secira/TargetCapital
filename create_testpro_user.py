#!/usr/bin/env python3
"""
Create Target Pro test user
"""

from app import app, db
from models import User, PricingPlan, SubscriptionStatus
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_testpro_user():
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email='testpro@targetcapital.ai').first()
        
        if existing_user:
            print(f"⚠️  User with email testpro@targetcapital.ai already exists (ID: {existing_user.id})")
            response = input("Update existing user to Target Pro? (yes/no): ")
            if response.lower() == 'yes':
                existing_user.pricing_plan = PricingPlan.TARGET_PRO
                existing_user.subscription_status = SubscriptionStatus.ACTIVE
                existing_user.subscription_start_date = datetime.utcnow()
                existing_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
                db.session.commit()
                
                print("✅ Updated existing user to Target Pro plan")
                print(f"   Email: {existing_user.email}")
                print(f"   Plan: {existing_user.pricing_plan.value}")
                print(f"   Status: {existing_user.subscription_status.value}")
                print(f"   Valid until: {existing_user.subscription_end_date.strftime('%B %d, %Y')}")
                return
            else:
                print("Cancelled.")
                return
        
        # Create new Target Pro test user
        test_user = User(
            username='testpro',
            email='testpro@targetcapital.ai',
            password_hash=generate_password_hash('Neo2025@@##'),
            pricing_plan=PricingPlan.TARGET_PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            subscription_start_date=datetime.utcnow(),
            subscription_end_date=datetime.utcnow() + timedelta(days=30),
            first_name='Test',
            last_name='Pro',
            total_payments=2999.00
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Target Pro test user created successfully!")
        print("="*60)
        print(f"   Username: {test_user.username}")
        print(f"   Email: {test_user.email}")
        print(f"   Password: Neo2025@@##")
        print(f"   Plan: {test_user.pricing_plan.value} (Target Pro)")
        print(f"   Price: ₹{test_user.get_plan_price()}/month")
        print(f"   Status: {test_user.subscription_status.value}")
        print(f"   Valid until: {test_user.subscription_end_date.strftime('%B %d, %Y')}")
        print("="*60)
        print("\n🎯 Features Available:")
        print("   ✅ AI stock analysis")
        print("   ✅ Daily Trading Signals")
        print("   ✅ Portfolio optimization")
        print("   ✅ Connect to a broker")
        print("   ✅ Trade execution (1 primary broker)")
        print("   ✅ Priority email support")

if __name__ == '__main__':
    create_testpro_user()
