"""
Script to create an admin user for tCapital Trading Platform
Run this script to create the first admin user
"""

import os
import sys
from app import app, db
from models import Admin

def create_admin_user():
    """Create an admin user interactively"""
    with app.app_context():
        print("🔐 tCapital Admin User Creation")
        print("=" * 40)
        
        # Check if admin table exists and has users
        try:
            existing_admins = Admin.query.count()
            if existing_admins > 0:
                print(f"⚠️  Found {existing_admins} existing admin(s)")
                create_another = input("Create another admin user? (y/n): ").lower()
                if create_another != 'y':
                    print("Exiting...")
                    return
        except Exception as e:
            print(f"Note: Admin table might not exist yet: {e}")
            print("Creating admin table...")
            db.create_all()
        
        # Get admin details
        print("\nEnter admin details:")
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            return
        
        # Check if username already exists
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print(f"❌ Admin with username '{username}' already exists!")
            return
        
        email = input("Email: ").strip()
        if not email:
            print("❌ Email cannot be empty!")
            return
        
        # Check if email already exists
        existing_email = Admin.query.filter_by(email=email).first()
        if existing_email:
            print(f"❌ Admin with email '{email}' already exists!")
            return
        
        first_name = input("First Name (optional): ").strip()
        last_name = input("Last Name (optional): ").strip()
        
        import getpass
        password = getpass.getpass("Password: ")
        if len(password) < 6:
            print("❌ Password must be at least 6 characters long!")
            return
        
        confirm_password = getpass.getpass("Confirm Password: ")
        if password != confirm_password:
            print("❌ Passwords do not match!")
            return
        
        is_super_admin = input("Make super admin? (y/n): ").lower() == 'y'
        
        try:
            # Create admin user
            admin = Admin(
                username=username,
                email=email,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None,
                is_super_admin=is_super_admin
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"\n✅ Admin user '{username}' created successfully!")
            print(f"📧 Email: {email}")
            print(f"👑 Super Admin: {'Yes' if is_super_admin else 'No'}")
            print(f"\n🌐 Admin Login URL: /admin/login")
            print(f"🔗 Full URL: https://your-domain.com/admin/login")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()