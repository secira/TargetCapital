"""
OAuth authentication setup for Google and Facebook login
"""
import os
from flask import Blueprint, redirect, url_for, flash, session
from flask_login import login_user, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from app import db
from models import User, OAuth
from datetime import datetime
import logging

# Create OAuth blueprints
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=["openid", "email", "profile"]
)

facebook_bp = make_facebook_blueprint(
    client_id=os.environ.get("FACEBOOK_APP_ID"),
    client_secret=os.environ.get("FACEBOOK_APP_SECRET"),
    scope="email"
)

def create_or_update_user_from_oauth(provider_name, oauth_info):
    """Create or update user from OAuth provider information"""
    try:
        if provider_name == "google":
            user_id = oauth_info.get("sub")
            email = oauth_info.get("email")
            first_name = oauth_info.get("given_name", "")
            last_name = oauth_info.get("family_name", "")
            username = email.split("@")[0] if email else f"google_user_{user_id}"
        
        elif provider_name == "facebook":
            user_id = oauth_info.get("id")
            email = oauth_info.get("email")
            name_parts = oauth_info.get("name", "").split(" ", 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            username = email.split("@")[0] if email else f"fb_user_{user_id}"
        
        else:
            return None
        
        if not email:
            logging.warning(f"No email provided by {provider_name} OAuth")
            return None
        
        # Check if user already exists by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update existing user info if needed
            if not user.first_name and first_name:
                user.first_name = first_name
            if not user.last_name and last_name:
                user.last_name = last_name
            db.session.commit()
            return user
        
        # Check if username exists, make unique if needed
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Create new user
        user = User()
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        # Set a random password hash for OAuth users
        user.set_password(f"oauth_{provider_name}_{user_id}")
        
        db.session.add(user)
        db.session.commit()
        
        logging.info(f"Created new user from {provider_name} OAuth: {email}")
        return user
        
    except Exception as e:
        logging.error(f"Error creating user from {provider_name} OAuth: {str(e)}")
        db.session.rollback()
        return None

# OAuth callback handlers using flask-dance signals
from flask_dance.consumer import oauth_authorized
from sqlalchemy.exc import NoResultFound

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        flash('Failed to log in with Google.', 'error')
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash('Failed to fetch user info from Google.', 'error')
        return False

    google_info = resp.json()
    user = create_or_update_user_from_oauth("google", google_info)
    
    if user:
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        flash('Successfully logged in with Google!', 'success')
        return False  # Don't redirect automatically
    else:
        flash('Failed to create user account. Please try again.', 'error')
        return False

@oauth_authorized.connect_via(facebook_bp)
def facebook_logged_in(blueprint, token):
    if not token:
        flash('Failed to log in with Facebook.', 'error')
        return False

    resp = blueprint.session.get("/me?fields=id,email,name")
    if not resp.ok:
        flash('Failed to fetch user info from Facebook.', 'error')
        return False

    facebook_info = resp.json()
    user = create_or_update_user_from_oauth("facebook", facebook_info)
    
    if user:
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        flash('Successfully logged in with Facebook!', 'success')
        return False  # Don't redirect automatically
    else:
        flash('Failed to create user account. Please try again.', 'error')
        return False

# OAuth storage will use the model from models.py