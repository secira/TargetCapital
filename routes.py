from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db
from models import (BlogPost, TeamMember, Testimonial, User, WatchlistItem, StockAnalysis, 
                   AIAnalysis, PortfolioOptimization, TradingSignal, AIStockPick, Portfolio,
                   PricingPlan, SubscriptionStatus, Payment, Referral, ContactMessage, UserBroker)
from services.nse_service import nse_service
from services.market_data_service import market_data_service
from services.ai_agent_service import AgenticAICoordinator
import logging
import random
import os
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Razorpay configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_dummy_key')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'dummy_secret')

# Initialize Razorpay client when keys are available
razorpay_client = None
if RAZORPAY_KEY_ID != 'rzp_test_dummy_key' and RAZORPAY_KEY_SECRET != 'dummy_secret':
    try:
        import razorpay
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except ImportError:
        logging.warning("Razorpay library not installed")

# Template Context Processor
@app.context_processor
def inject_pricing_plans():
    """Make PricingPlan and SubscriptionStatus available to all templates"""
    return {
        'PricingPlan': PricingPlan,
        'SubscriptionStatus': SubscriptionStatus
    }

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def plan_required(*allowed_plans):
    """Decorator to require specific pricing plan access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if current_user.pricing_plan not in allowed_plans:
                flash('This feature requires a higher subscription plan. Please upgrade your account.', 'warning')
                return redirect(url_for('account_billing'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    """Home page route"""
    # Get featured testimonials
    testimonials = Testimonial.query.limit(3).all()
    return render_template('index.html', testimonials=testimonials)

@app.route('/about')
def about():
    """About Us page route"""
    # Get team members
    team_members = TeamMember.query.all()
    testimonials = Testimonial.query.limit(2).all()
    return render_template('about.html', team_members=team_members, testimonials=testimonials)

@app.route('/services')
def services():
    """Services page route"""
    testimonials = Testimonial.query.limit(3).all()
    return render_template('services.html', testimonials=testimonials)

@app.route('/algo-trading')
def algo_trading():
    """ALGO Trading page route"""
    testimonials = Testimonial.query.limit(2).all()
    return render_template('algo_trading.html', testimonials=testimonials)

@app.route('/blog')
def blog():
    """Blog listing page route"""
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    featured_posts = BlogPost.query.filter_by(is_featured=True, status='published').limit(3).all()
    return render_template('blog.html', posts=posts, featured_posts=featured_posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    """Individual blog post page route"""
    post = BlogPost.query.get_or_404(post_id)
    # Get related posts (same author or recent posts)
    related_posts = BlogPost.query.filter(
        BlogPost.id != post_id
    ).order_by(BlogPost.created_at.desc()).limit(3).all()
    
    testimonials = Testimonial.query.limit(2).all()
    return render_template('blog_post.html', post=post, related_posts=related_posts, testimonials=testimonials)



@app.route('/pricing')
def pricing():
    """Pricing page route"""
    return render_template('pricing.html')



@app.route('/careers')
def careers():
    """Careers page route"""
    return render_template('careers.html')

@app.route('/news')
def news():
    """In the News page route"""
    return render_template('news.html')

@app.route('/partners')
def partners():
    """Partners page route"""
    return render_template('partners.html')

@app.route('/trading-signals')
def trading_signals():
    """Public Trading Signals page route"""
    return render_template('trading_signals.html')

@app.route('/stock-research')
def stock_research():
    """Stock Research service page route"""
    return render_template('stock_research.html')

@app.route('/portfolio-analysis')
def portfolio_analysis():
    """Portfolio Analysis service page route"""
    return render_template('portfolio_analysis.html')

@app.route('/algo-trading-service')
def algo_trading_service():
    """Algorithmic Trading service page route"""
    return render_template('algo_trading.html')

@app.route('/account-handling')
def account_handling():
    """Account Handling service page route"""
    return render_template('account_handling.html')

# Support and Legal Pages
@app.route('/help-center')
def help_center():
    """Help Center support page route"""
    return render_template('help_center.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page route"""
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    """Terms of Service page route"""
    return render_template('terms_of_service.html')

@app.route('/risk-disclosure')
def risk_disclosure():
    """Risk Disclosure page route"""
    return render_template('risk_disclosure.html')

@app.route('/compliance')
def compliance():
    """Compliance page route"""
    return render_template('compliance.html')

@app.route('/cancellation-refund-policy')
def cancellation_refund_policy():
    """Cancellation and Refund Policy page route"""
    return render_template('cancellation_refund_policy.html')

@app.route('/dashboard/broker-management')
@login_required
def broker_management():
    """Broker Management page"""
    brokers = UserBroker.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/broker_management.html', 
                         active_section='broker_management',
                         brokers=brokers)

@app.route('/add-broker', methods=['POST'])
@login_required
def add_broker():
    """Add new broker connection"""
    try:
        broker_name = request.form.get('broker_name')
        api_key = request.form.get('api_key')
        api_secret = request.form.get('api_secret')
        request_token = request.form.get('request_token')
        redirect_url = request.form.get('redirect_url')
        
        # Validate required fields
        if not all([broker_name, api_key, api_secret]):
            flash('Broker name, API key, and API secret are required.', 'error')
            return redirect(url_for('broker_management'))
        
        # Check if broker already exists for this user
        existing = UserBroker.query.filter_by(
            user_id=current_user.id, 
            broker_name=broker_name
        ).first()
        
        if existing:
            flash(f'You already have a {broker_name} connection configured.', 'error')
            return redirect(url_for('broker_management'))
        
        # Create new broker connection
        new_broker = UserBroker(
            user_id=current_user.id,
            broker_name=broker_name,
            api_key=api_key,
            api_secret=api_secret,
            request_token=request_token,
            redirect_url=redirect_url
        )
        
        db.session.add(new_broker)
        db.session.commit()
        
        flash(f'{broker_name} broker added successfully!', 'success')
        logging.info(f"User {current_user.id} added broker {broker_name}")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding broker for user {current_user.id}: {str(e)}")
        flash('Error adding broker. Please try again.', 'error')
    
    return redirect(url_for('broker_management'))

@app.route('/update-broker', methods=['POST'])
@login_required
def update_broker():
    """Update existing broker connection"""
    try:
        broker_id = request.form.get('broker_id')
        api_key = request.form.get('api_key')
        api_secret = request.form.get('api_secret')
        request_token = request.form.get('request_token')
        
        broker = UserBroker.query.filter_by(
            id=broker_id, 
            user_id=current_user.id
        ).first()
        
        if not broker:
            flash('Broker not found.', 'error')
            return redirect(url_for('broker_management'))
        
        # Update broker details
        if api_key:
            broker.api_key = api_key
        if api_secret:
            broker.api_secret = api_secret
        if request_token:
            broker.request_token = request_token
            
        broker.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'{broker.broker_name} updated successfully!', 'success')
        logging.info(f"User {current_user.id} updated broker {broker.broker_name}")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating broker: {str(e)}")
        flash('Error updating broker. Please try again.', 'error')
    
    return redirect(url_for('broker_management'))

@app.route('/api/broker/<int:broker_id>')
@login_required
def get_broker_details(broker_id):
    """Get broker details for editing"""
    try:
        broker = UserBroker.query.filter_by(
            id=broker_id, 
            user_id=current_user.id
        ).first()
        
        if not broker:
            return jsonify({'success': False, 'message': 'Broker not found'})
        
        return jsonify({
            'success': True,
            'broker': {
                'id': broker.id,
                'broker_name': broker.broker_name,
                'api_key': broker.api_key,
                'request_token': broker.request_token,
                'status': broker.status
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting broker details: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/broker/<int:broker_id>', methods=['DELETE'])
@login_required
def delete_broker(broker_id):
    """Delete broker connection"""
    try:
        broker = UserBroker.query.filter_by(
            id=broker_id, 
            user_id=current_user.id
        ).first()
        
        if not broker:
            return jsonify({'success': False, 'message': 'Broker not found'})
        
        broker_name = broker.broker_name
        db.session.delete(broker)
        db.session.commit()
        
        logging.info(f"User {current_user.id} deleted broker {broker_name}")
        return jsonify({'success': True, 'message': f'{broker_name} connection deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting broker: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/broker/<int:broker_id>/refresh-token', methods=['POST'])
@login_required
def refresh_broker_token(broker_id):
    """Refresh broker access token"""
    try:
        data = request.get_json()
        request_token = data.get('request_token')
        
        broker = UserBroker.query.filter_by(
            id=broker_id, 
            user_id=current_user.id
        ).first()
        
        if not broker:
            return jsonify({'success': False, 'message': 'Broker not found'})
        
        if not request_token:
            return jsonify({'success': False, 'message': 'Request token is required'})
        
        # Update request token and simulate token refresh
        # In real implementation, you would call the broker's API here
        broker.request_token = request_token
        broker.access_token = f"access_token_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        broker.last_token_refresh = datetime.utcnow()
        
        db.session.commit()
        
        logging.info(f"User {current_user.id} refreshed token for broker {broker.broker_name}")
        return jsonify({'success': True, 'message': 'Token refreshed successfully'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error refreshing token: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with email notifications"""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            company = request.form.get('company', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            
            # Validate required fields
            if not all([first_name, last_name, email, message]):
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('contact'))
            
            # Create full name
            full_name = f"{first_name} {last_name}"
            
            # Map subject to inquiry type
            inquiry_type_map = {
                'general': 'General',
                'support': 'Support',
                'sales': 'Sales', 
                'partnership': 'Partnership',
                'feedback': 'Feedback'
            }
            inquiry_type = inquiry_type_map.get(subject, 'General')
            
            # Create contact message record
            contact_message = ContactMessage(
                name=full_name,
                email=email,
                subject=subject,
                message=message,
                phone=phone if phone else None,
                company=company if company else None,
                inquiry_type=inquiry_type,
                ip_address=request.environ.get('REMOTE_ADDR'),
                user_agent=request.environ.get('HTTP_USER_AGENT')
            )
            
            # Save to database
            db.session.add(contact_message)
            db.session.commit()
            
            # Send email notifications
            from services.email_service import email_service
            
            # Send confirmation email to user
            email_sent_to_user = email_service.send_contact_confirmation(contact_message)
            
            # Send notification email to admin
            email_sent_to_admin = email_service.send_contact_notification(contact_message)
            
            # Show success message
            if email_sent_to_user:
                flash('Thank you for your message! We\'ve sent you a confirmation email and will get back to you within 24 hours.', 'success')
            else:
                flash('Thank you for your message! We will get back to you within 24 hours.', 'success')
            
            # Log the contact submission
            logging.info(f"New contact message from {full_name} ({email}) - Type: {inquiry_type}")
            
            return redirect(url_for('contact'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Contact form submission error: {str(e)}")
            flash('Sorry, there was an error sending your message. Please try again or contact us directly.', 'error')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Admin route to view contact messages
@app.route('/admin/contact-messages')
@login_required
@admin_required
def admin_contact_messages():
    """Admin page to view and manage contact messages"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = ContactMessage.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    messages = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get statistics
    stats = {
        'total': ContactMessage.query.count(),
        'new': ContactMessage.query.filter_by(status='new').count(),
        'read': ContactMessage.query.filter_by(status='read').count(),
        'replied': ContactMessage.query.filter_by(status='replied').count(),
        'closed': ContactMessage.query.filter_by(status='closed').count(),
    }
    
    return render_template('admin/contact_messages.html', 
                         messages=messages, 
                         stats=stats,
                         status_filter=status_filter)

@app.route('/admin/contact-message/<int:message_id>')
@login_required 
@admin_required
def admin_view_contact_message(message_id):
    """View individual contact message"""
    message = ContactMessage.query.get_or_404(message_id)
    
    # Mark as read if it's new
    if message.status == 'new':
        message.status = 'read'
        db.session.commit()
    
    return render_template('admin/view_contact_message.html', message=message)

@app.route('/admin/contact-message/<int:message_id>/update-status', methods=['POST'])
@login_required
@admin_required  
def admin_update_contact_status(message_id):
    """Update contact message status"""
    message = ContactMessage.query.get_or_404(message_id)
    new_status = request.form.get('status')
    
    if new_status in ['new', 'read', 'replied', 'closed']:
        message.status = new_status
        if new_status == 'replied':
            message.replied_at = datetime.utcnow()
        db.session.commit()
        flash(f'Message status updated to {new_status}.', 'success')
    
    return redirect(url_for('admin_view_contact_message', message_id=message_id))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required.', 'error')
            return redirect(url_for('account_settings'))
        
        # Check if current password is correct
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('account_settings'))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('account_settings'))
        
        # Check password length
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('account_settings'))
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password updated successfully!', 'success')
        logging.info(f"User {current_user.id} changed password")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Password change failed for user {current_user.id}: {str(e)}")
        flash('Error updating password. Please try again.', 'error')
    
    return redirect(url_for('account_settings'))

@app.route('/update-preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update user preferences"""
    try:
        # Get form data
        email_trading_alerts = request.form.get('email_trading_alerts') == 'on'
        email_market_updates = request.form.get('email_market_updates') == 'on'
        email_billing_updates = request.form.get('email_billing_updates') == 'on'
        email_promotional = request.form.get('email_promotional') == 'on'
        default_dashboard_view = request.form.get('default_dashboard_view', 'overview')
        theme_preference = request.form.get('theme_preference', 'light')
        timezone = request.form.get('timezone', 'Asia/Kolkata')
        
        # For now, we'll store preferences in session since we don't have a UserPreferences model
        # In a full implementation, you'd want to create a UserPreferences model
        session['user_preferences'] = {
            'email_trading_alerts': email_trading_alerts,
            'email_market_updates': email_market_updates,
            'email_billing_updates': email_billing_updates,
            'email_promotional': email_promotional,
            'default_dashboard_view': default_dashboard_view,
            'theme_preference': theme_preference,
            'timezone': timezone
        }
        
        flash('Preferences updated successfully!', 'success')
        logging.info(f"User {current_user.id} updated preferences")
        
    except Exception as e:
        logging.error(f"Preferences update failed for user {current_user.id}: {str(e)}")
        flash('Error updating preferences. Please try again.', 'error')
    
    return redirect(url_for('account_settings'))



# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')
        
        # Support login with username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if not all([username, email, password]):
            flash('Please fill in all required fields.', 'error')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        # Update profile information
        current_user.first_name = request.form.get('first_name', '').strip()
        current_user.last_name = request.form.get('last_name', '').strip()
        current_user.username = request.form.get('username', '').strip()
        current_user.email = request.form.get('email', '').strip()
        
        # Handle password change
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if new_password:
            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('auth/profile.html')
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('auth/profile.html')
            
            current_user.set_password(new_password)
        
        # Validate required fields
        if not current_user.username or not current_user.email:
            flash('Username and email are required.', 'error')
            return render_template('auth/profile.html')
        
        # Check for duplicate username/email (excluding current user)
        existing_username = User.query.filter(
            User.username == current_user.username, 
            User.id != current_user.id
        ).first()
        if existing_username:
            flash('Username already exists.', 'error')
            return render_template('auth/profile.html')
        
        existing_email = User.query.filter(
            User.email == current_user.email, 
            User.id != current_user.id
        ).first()
        if existing_email:
            flash('Email already registered.', 'error')
            return render_template('auth/profile.html')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Get user statistics
    trading_signals_count = TradingSignal.query.filter_by(user_id=current_user.id).count()
    analyses_count = StockAnalysis.query.count()  # Could be user-specific in future
    
    return render_template('auth/profile.html', 
                         trading_signals_count=trading_signals_count,
                         analyses_count=analyses_count)

# OAuth success redirect routes
@app.route('/auth/google/callback')
def google_oauth_success():
    """Handle successful Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        flash('Google authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/auth/facebook/callback')
def facebook_oauth_success():
    """Handle successful Facebook OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        flash('Facebook authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard route"""
    # Get recent stock analyses
    recent_analyses = StockAnalysis.query.order_by(StockAnalysis.analysis_date.desc()).limit(10).all()
    
    # Calculate user statistics
    days_active = (datetime.utcnow() - current_user.created_at).days
    trading_signals_count = TradingSignal.query.filter_by(user_id=current_user.id).count()
    
    # Calculate user level based on trading activity
    if trading_signals_count >= 20:
        user_level = "Expert Trader"
        level_progress = 100
    elif trading_signals_count >= 10:
        user_level = "Advanced Trader"
        level_progress = 75
    elif trading_signals_count >= 5:
        user_level = "Intermediate"
        level_progress = 50
    elif trading_signals_count >= 1:
        user_level = "Beginner"
        level_progress = 25
    else:
        user_level = "New User"
        level_progress = 10
    
    # Use mock data for now to ensure dashboard loads properly
    market_data = generate_mock_market_data()
    
    return render_template('dashboard/dashboard.html', 
                         trading_signals_count=trading_signals_count,
                         recent_analyses=recent_analyses,
                         market_data=market_data,
                         days_active=days_active,
                         user_level=user_level,
                         level_progress=level_progress)

@app.route('/dashboard/stock-analysis')
@login_required
def stock_analysis():
    """Stock analysis dashboard"""
    # Get all stock analyses
    analyses = StockAnalysis.query.order_by(StockAnalysis.analysis_date.desc()).all()
    return render_template('dashboard/stock_analysis.html', analyses=analyses)





@app.route('/seed-demo-data')
def seed_demo_data():
    """Seed the database with demo data for testing"""
    try:
        # Create demo user if not exists
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            demo_user = User(
                username='demo',
                email='demo@tcapital.com',
                first_name='Demo',
                last_name='User'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
        
        # Create sample stock analyses
        sample_analyses = [
            {
                'symbol': 'AAPL',
                'company_name': 'Apple Inc.',
                'current_price': 175.50,
                'previous_close': 173.35,
                'change_amount': 2.15,
                'change_percent': 1.24,
                'volume': 45000000,
                'market_cap': 2750000000000,
                'pe_ratio': 28.5,
                'day_high': 176.80,
                'day_low': 174.20,
                'week_52_high': 198.23,
                'week_52_low': 124.17,
                'ai_recommendation': 'BUY',
                'ai_confidence': 85.5,
                'ai_notes': 'Strong earnings momentum and product innovation pipeline'
            },
            {
                'symbol': 'GOOGL',
                'company_name': 'Alphabet Inc.',
                'current_price': 2845.20,
                'previous_close': 2857.70,
                'change_amount': -12.50,
                'change_percent': -0.44,
                'volume': 25000000,
                'market_cap': 1800000000000,
                'pe_ratio': 25.2,
                'day_high': 2860.00,
                'day_low': 2840.15,
                'week_52_high': 3030.93,
                'week_52_low': 2193.62,
                'ai_recommendation': 'HOLD',
                'ai_confidence': 72.3,
                'ai_notes': 'Solid fundamentals but facing regulatory headwinds'
            },
            {
                'symbol': 'TSLA',
                'company_name': 'Tesla Inc.',
                'current_price': 245.30,
                'previous_close': 253.50,
                'change_amount': -8.20,
                'change_percent': -3.23,
                'volume': 78000000,
                'market_cap': 780000000000,
                'pe_ratio': 45.8,
                'day_high': 248.90,
                'day_low': 243.10,
                'week_52_high': 299.29,
                'week_52_low': 138.80,
                'ai_recommendation': 'SELL',
                'ai_confidence': 68.1,
                'ai_notes': 'High volatility and production concerns'
            }
        ]
        
        for analysis_data in sample_analyses:
            existing = StockAnalysis.query.filter_by(symbol=analysis_data['symbol']).first()
            if not existing:
                analysis = StockAnalysis(**analysis_data)
                db.session.add(analysis)
        
        # Create sample watchlist items for demo user
        sample_watchlist = [
            {'symbol': 'AAPL', 'company_name': 'Apple Inc.', 'target_price': 180.00, 'notes': 'Strong buy on next dip'},
            {'symbol': 'MSFT', 'company_name': 'Microsoft Corp.', 'target_price': 400.00, 'notes': 'Cloud growth story'},
            {'symbol': 'NVDA', 'company_name': 'NVIDIA Corp.', 'target_price': 500.00, 'notes': 'AI revolution leader'}
        ]
        
        for item_data in sample_watchlist:
            existing = WatchlistItem.query.filter_by(user_id=demo_user.id, symbol=item_data['symbol']).first()
            if not existing:
                item = WatchlistItem(
                    user_id=demo_user.id,
                    **item_data
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Demo data seeded successfully! You can login with username: demo, password: demo123', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error seeding demo data: {str(e)}', 'error')
        logging.error(f"Error seeding demo data: {str(e)}")
    
    return redirect(url_for('index'))

# NSE India API routes
@app.route('/api/nse/quote/<symbol>')
@login_required
def get_nse_quote(symbol):
    """Get real-time NSE stock quote"""
    try:
        quote = nse_service.get_stock_quote(symbol.upper())
        if quote:
            return jsonify({'success': True, 'data': quote})
        else:
            return jsonify({'success': False, 'error': 'Stock not found'})
    except Exception as e:
        logging.error(f"Error fetching NSE quote for {symbol}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch stock data'})

@app.route('/api/nse/search/<query>')
@login_required
def search_nse_stocks(query):
    """Search NSE stocks by symbol or name"""
    try:
        results = nse_service.search_stocks(query)
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        logging.error(f"Error searching NSE stocks: {str(e)}")
        return jsonify({'success': False, 'error': 'Search failed'})

@app.route('/api/nse/market-overview')
@login_required
def get_market_overview():
    """Get NSE market overview with indices and top movers"""
    try:
        overview = {
            'indices': nse_service.get_market_indices(),
            'top_gainers': nse_service.get_top_gainers(5),
            'top_losers': nse_service.get_top_losers(5),
            'most_active': nse_service.get_most_active(5),
            'market_status': nse_service.get_market_status()
        }
        return jsonify({'success': True, 'data': overview})
    except Exception as e:
        logging.error(f"Error fetching market overview: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch market data'})



@app.route('/dashboard/trading-signals')
@login_required
def dashboard_trading_signals():
    """Dashboard Trading Signals page with real data from database"""
    from datetime import date
    
    # Get filter parameters
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    symbol_type = request.args.get('symbol_type', 'all')
    signal_status = request.args.get('status', 'all')
    
    # Build query for trading signals
    query = TradingSignal.query
    
    # Filter by date
    if selected_date:
        query = query.filter(TradingSignal.open_date == selected_date)
    
    # Filter by symbol type
    if symbol_type != 'all':
        query = query.filter(TradingSignal.symbol_type == symbol_type)
    
    # Filter by status
    if signal_status != 'all':
        query = query.filter(TradingSignal.signal_status == signal_status)
    
    # Get signals ordered by creation date
    trading_signals = query.order_by(TradingSignal.creation_date.desc()).all()
    
    # Calculate summary statistics
    total_signals = len(trading_signals)
    active_signals = len([s for s in trading_signals if s.signal_status == 'Active'])
    closed_signals = len([s for s in trading_signals if s.signal_status == 'Closed'])
    
    # Calculate success rate for closed signals
    profitable_signals = len([s for s in trading_signals if s.signal_status == 'Closed' and s.calculate_pnl()[0] > 0])
    success_rate = (profitable_signals / closed_signals * 100) if closed_signals > 0 else 0
    
    # Get unique symbol types for filter dropdown
    symbol_types = db.session.query(TradingSignal.symbol_type).distinct().all()
    symbol_types = [st[0] for st in symbol_types]
    
    return render_template('dashboard/trading_signals.html',
                         trading_signals=trading_signals,
                         total_signals=total_signals,
                         active_signals=active_signals,
                         success_rate=success_rate,
                         selected_date=selected_date,
                         symbol_type=symbol_type,
                         signal_status=signal_status,
                         symbol_types=symbol_types,
                         today=date.today())

@app.route('/admin/trading-signals/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_trading_signal():
    """Admin route to create new trading signals"""
    from datetime import date
    
    if request.method == 'POST':
        try:
            # Create new trading signal from form data
            signal = TradingSignal(
                user_id=current_user.id,
                open_date=datetime.strptime(request.form['open_date'], '%Y-%m-%d').date(),
                symbol_type=request.form['symbol_type'],
                ticker_symbol=request.form['ticker_symbol'].upper(),
                option_type=request.form.get('option_type'),
                trade_strategy=request.form.get('trade_strategy'),
                strike_price=float(request.form['strike_price']) if request.form.get('strike_price') else None,
                expiration_date=datetime.strptime(request.form['expiration_date'], '%Y-%m-%d').date() if request.form.get('expiration_date') else None,
                number_of_units=int(request.form['number_of_units']),
                trade_direction=request.form['trade_direction'],
                entry_price=float(request.form['entry_price']),
                current_price=float(request.form['current_price']) if request.form.get('current_price') else None,
                trade_fees=float(request.form['trade_fees']) if request.form.get('trade_fees') else None,
                capital_risk=float(request.form['capital_risk']),
                trading_account=request.form.get('trading_account'),
                signal_status='Active'
            )
            
            db.session.add(signal)
            db.session.commit()
            
            flash(f'Trading signal for {signal.ticker_symbol} created successfully!', 'success')
            return redirect(url_for('dashboard_trading_signals'))
            
        except Exception as e:
            logging.error(f"Error creating trading signal: {str(e)}")
            flash('Error creating trading signal. Please check your input.', 'error')
    
    return render_template('admin/create_trading_signal.html', today=date.today())

@app.route('/admin/trading-signals/update/<int:signal_id>', methods=['POST'])
@login_required
@admin_required
def update_trading_signal(signal_id):
    """Admin route to update trading signal prices and status"""
    try:
        signal = TradingSignal.query.get_or_404(signal_id)
        
        # Update fields that can be modified
        if request.form.get('current_price'):
            signal.current_price = float(request.form['current_price'])
        
        if request.form.get('exit_price'):
            signal.exit_price = float(request.form['exit_price'])
            signal.exit_date = datetime.now().date()
            signal.signal_status = 'Closed'
            
            # Calculate P&L
            pnl_amount, pnl_percentage = signal.calculate_pnl()
            signal.pnl_amount = pnl_amount
            signal.pnl_percentage = pnl_percentage
            
            if pnl_amount > 0:
                signal.trade_result = 'Profit'
            elif pnl_amount < 0:
                signal.trade_result = 'Loss'
            else:
                signal.trade_result = 'Breakeven'
        
        if request.form.get('signal_status'):
            signal.signal_status = request.form['signal_status']
        
        if request.form.get('reason_for_exit'):
            signal.reason_for_exit = request.form['reason_for_exit']
        
        db.session.commit()
        flash(f'Trading signal for {signal.ticker_symbol} updated successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Error updating trading signal: {str(e)}")
        flash('Error updating trading signal.', 'error')
    
    return redirect(url_for('dashboard_trading_signals'))

@app.route('/dashboard/stock-picker')
@login_required
def dashboard_stock_picker():
    """AI-powered stock picker for research and analysis"""
    from datetime import date
    
    # Get selected date for AI picks
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    # Fetch AI stock picks for the selected date
    ai_picks = AIStockPick.query.filter_by(pick_date=selected_date).all()
    
    return render_template('dashboard/stock_picker.html', 
                         current_user=current_user,
                         ai_picks=ai_picks,
                         selected_date=selected_date,
                         today=date.today())

@app.route('/dashboard/detailed-analysis/<string:symbol>')
@login_required
def detailed_stock_analysis(symbol):
    """Detailed stock analysis page based on Infosys format"""
    from datetime import date
    
    # Sample data structure - in production this would come from AI analysis
    stock_data = {
        'INFY': {
            'company_name': 'Infosys Limited',
            'current_price': 1447.70,
            'pe_ratio': 22.0,
            'market_cap': '₹6.15 lakh crore',
            'market_cap_category': 'Large Cap',
            'annual_revenue': '193,000',
            'revenue_growth': '10',
            'profit_margin': '18-20',
            'quarterly_results': 'Q1 FY25 revenue and profit both up YoY, though margin growth slowed due to higher wage costs',
            'global_presence': '98%+ of revenue from outside India, diversified client base (North America, Europe, APAC)',
            'debt_position': 'Virtually debt-free, with robust cash reserves for buybacks/dividends',
            'focus_areas': 'Enterprise AI (Infosys Topaz), cloud migration, digital transformation, and consulting',
            'recent_contracts': 'Multiple multi-million dollar wins with large US/European firms and public sector AI initiatives',
            'innovation': 'Strong push in generative AI, cloud, and cybersecurity services',
            'dividend_yield': 2.6,
            'buyback_info': 'Periodically announced, supporting shareholder value',
            'sector_position': 'Second largest listed IT services firm in India (after TCS)',
            'competitors': 'TCS, Accenture, IBM, Cognizant, Wipro, HCL Tech',
            'operating_risks': ['Cost inflation and margin pressure', 'Talent war and salary hikes', 'Client IT budget constraints'],
            'market_risks': ['Currency fluctuations impact', 'US/EU tech spending softness', 'Global recession concerns'],
            'consensus_rating': 'HOLD/BUY',
            'consensus_details': 'Majority "Hold" rating, some "Buy" on dips',
            'target_price': 1650.00,
            'upside_potential': 14.0,
            'long_term_outlook': 'Expected to benefit from AI/cloud/digital transformation trends',
            'short_term_view': 'Range-bound movement as cost pressures and global moderation persist',
            'debt_status': 'Debt-free',
            'fair_value_status': 'Slight premium/near value',
            'ai_verdict': 'Infosys continues to be a high-quality core IT holding in India. Long-term investors may hold/accumulate on dips, given its digital competency, strong balance sheet, and global client diversification.',
            'ai_recommendation': 'HOLD with selective buying opportunities on market dips',
            'disclaimer': 'Always check your risk profile and investment horizon. For updated targets, review latest quarterly results and analyst notes.'
        },
        'RELIANCE': {
            'company_name': 'Reliance Industries Limited',
            'current_price': 2845.60,
            'pe_ratio': 25.5,
            'market_cap': '₹19.2 lakh crore',
            'market_cap_category': 'Large Cap',
            'annual_revenue': '792,000',
            'revenue_growth': '12',
            'profit_margin': '8-10',
            'quarterly_results': 'Strong performance across retail and telecom segments with steady oil & gas business',
            'global_presence': 'Diversified operations in petrochemicals, oil refining, telecommunications, and retail',
            'debt_position': 'Debt reduced significantly, strong cash generation from operations',
            'focus_areas': 'Digital services expansion, retail growth, green energy transition',
            'recent_contracts': 'Major partnerships in renewable energy and digital infrastructure',
            'innovation': 'Investment in new energy solutions and digital technologies',
            'dividend_yield': 0.5,
            'buyback_info': 'Focus on growth investments rather than buybacks',
            'sector_position': 'Largest private sector company in India with diversified business model',
            'competitors': 'ONGC, IOC, Bharti Airtel, other energy and telecom companies',
            'operating_risks': ['Oil price volatility', 'Regulatory changes in telecom', 'Competition in retail'],
            'market_risks': ['Global energy transitions', 'Economic slowdown impact', 'Interest rate changes'],
            'consensus_rating': 'BUY',
            'consensus_details': 'Strong buy recommendations based on diversified growth prospects',
            'target_price': 3100.00,
            'upside_potential': 8.9,
            'long_term_outlook': 'Well-positioned for energy transition and digital economy growth',
            'short_term_view': 'Steady performance expected with potential volatility from oil prices',
            'debt_status': 'Net debt reduced',
            'fair_value_status': 'Fair to attractive valuation',
            'ai_verdict': 'Reliance remains a core holding for diversified growth exposure in the Indian market with strong fundamentals across multiple business segments.',
            'ai_recommendation': 'BUY for long-term wealth creation',
            'disclaimer': 'Monitor oil prices and regulatory changes in telecom sector for short-term volatility.'
        }
    }
    
    # Add default data for other stocks
    if symbol.upper() not in stock_data:
        stock_data[symbol.upper()] = {
            'company_name': f'{symbol.upper()} Limited',
            'current_price': 1500.00,
            'pe_ratio': 20.0,
            'market_cap': '₹5.0 lakh crore',
            'market_cap_category': 'Large Cap',
            'annual_revenue': '150,000',
            'revenue_growth': '8',
            'profit_margin': '15-18',
            'quarterly_results': f'Recent quarterly results show consistent performance with stable margins for {symbol}',
            'global_presence': 'Strong domestic presence with growing international operations',
            'debt_position': 'Manageable debt levels with adequate liquidity',
            'focus_areas': 'Core business expansion and digital transformation initiatives',
            'recent_contracts': 'Secured new business partnerships and expansion opportunities',
            'innovation': 'Investment in technology upgrades and operational efficiency',
            'dividend_yield': 2.0,
            'buyback_info': 'Regular dividend payouts with occasional share buybacks',
            'sector_position': f'Leading player in {symbol} sector with strong market position',
            'competitors': 'Various industry players with competitive positioning',
            'operating_risks': ['Market competition', 'Cost inflation', 'Regulatory changes'],
            'market_risks': ['Economic volatility', 'Interest rate fluctuations', 'Global market conditions'],
            'consensus_rating': 'HOLD',
            'consensus_details': 'Mixed analyst views with cautious optimism',
            'target_price': 1650.00,
            'upside_potential': 10.0,
            'long_term_outlook': 'Positive long-term growth prospects with strategic initiatives',
            'short_term_view': 'Near-term performance subject to market conditions',
            'debt_status': 'Manageable debt',
            'fair_value_status': 'Fair valuation',
            'ai_verdict': f'{symbol} shows stable fundamentals with growth potential. Suitable for long-term investors seeking steady returns with moderate risk.',
            'ai_recommendation': 'HOLD with monitoring for entry opportunities',
            'disclaimer': 'Investment decisions should be based on individual risk tolerance and financial goals.'
        }
    
    # Get stock data
    data = stock_data.get(symbol.upper())
    
    return render_template('dashboard/detailed_stock_analysis.html',
                         stock_symbol=symbol.upper(),
                         analysis_date=date.today().strftime('%B %d, %Y'),
                         **data)

@app.route('/dashboard/my-portfolio')
@login_required
def dashboard_my_portfolio():
    """Portfolio management with unified broker view and real data"""
    from datetime import date, datetime
    from sqlalchemy import func
    
    # Get user's portfolio holdings
    portfolio_holdings = Portfolio.query.filter_by(user_id=current_user.id).all()
    
    # If no data exists, create sample portfolio for demonstration
    if not portfolio_holdings:
        sample_data = [
            {
                'broker_id': 'zerodha',
                'ticker_symbol': 'RELIANCE',
                'stock_name': 'Reliance Industries Limited',
                'asset_type': 'Stocks',
                'quantity': 50,
                'date_purchased': date(2024, 6, 15),
                'purchase_price': 2650.00,
                'purchased_value': 132500.00,
                'current_price': 2845.60,
                'current_value': 142280.00,
                'sector': 'Oil & Gas',
                'exchange': 'NSE'
            },
            {
                'broker_id': 'angel',
                'ticker_symbol': 'INFY',
                'stock_name': 'Infosys Limited',
                'asset_type': 'Stocks',
                'quantity': 75,
                'date_purchased': date(2024, 7, 20),
                'purchase_price': 1420.00,
                'purchased_value': 106500.00,
                'current_price': 1447.70,
                'current_value': 108577.50,
                'sector': 'Information Technology',
                'exchange': 'NSE'
            },
            {
                'broker_id': 'zerodha',
                'ticker_symbol': 'HDFCBANK',
                'stock_name': 'HDFC Bank Limited',
                'asset_type': 'Stocks',
                'quantity': 30,
                'date_purchased': date(2024, 5, 10),
                'purchase_price': 1580.00,
                'purchased_value': 47400.00,
                'current_price': 1625.30,
                'current_value': 48759.00,
                'sector': 'Banking',
                'exchange': 'NSE'
            },
            {
                'broker_id': 'dhan',
                'ticker_symbol': 'TCS',
                'stock_name': 'Tata Consultancy Services',
                'asset_type': 'Stocks',
                'quantity': 25,
                'date_purchased': date(2024, 8, 1),
                'purchase_price': 3950.00,
                'purchased_value': 98750.00,
                'current_price': 4125.80,
                'current_value': 103145.00,
                'sector': 'Information Technology',
                'exchange': 'NSE'
            },
            {
                'broker_id': 'zerodha',
                'ticker_symbol': 'BAJFINANCE',
                'stock_name': 'Bajaj Finance Limited',
                'asset_type': 'Stocks',
                'quantity': 15,
                'date_purchased': date(2024, 4, 25),
                'purchase_price': 6800.00,
                'purchased_value': 102000.00,
                'current_price': 6750.45,
                'current_value': 101256.75,
                'sector': 'Financial Services',
                'exchange': 'NSE'
            }
        ]
        
        for data in sample_data:
            portfolio_holding = Portfolio(
                user_id=current_user.id,
                **data
            )
            db.session.add(portfolio_holding)
        
        db.session.commit()
        portfolio_holdings = Portfolio.query.filter_by(user_id=current_user.id).all()
    
    # Calculate portfolio summary
    total_investment = sum(holding.purchased_value for holding in portfolio_holdings)
    total_current_value = sum(holding.current_value or holding.purchased_value for holding in portfolio_holdings)
    total_pnl = total_current_value - total_investment
    total_pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    # Group holdings by sector for sectorial analysis
    sector_analysis = {}
    for holding in portfolio_holdings:
        sector = holding.sector or 'Others'
        if sector not in sector_analysis:
            sector_analysis[sector] = {
                'investment': 0,
                'current_value': 0,
                'holdings_count': 0
            }
        sector_analysis[sector]['investment'] += holding.purchased_value
        sector_analysis[sector]['current_value'] += holding.current_value or holding.purchased_value
        sector_analysis[sector]['holdings_count'] += 1
    
    # Group holdings by broker
    broker_analysis = {}
    broker_names = {
        'zerodha': 'Zerodha',
        'angel': 'Angel Broking',
        'dhan': 'Dhan',
        'upstox': 'Upstox',
        'icici': 'ICICI Direct'
    }
    
    for holding in portfolio_holdings:
        broker = holding.broker_id
        if broker not in broker_analysis:
            broker_analysis[broker] = {
                'name': broker_names.get(broker, broker.title()),
                'investment': 0,
                'current_value': 0,
                'holdings_count': 0,
                'holdings': []
            }
        broker_analysis[broker]['investment'] += holding.purchased_value
        broker_analysis[broker]['current_value'] += holding.current_value or holding.purchased_value
        broker_analysis[broker]['holdings_count'] += 1
        broker_analysis[broker]['holdings'].append(holding)
    
    return render_template('dashboard/my_portfolio.html',
                         current_user=current_user,
                         portfolio_holdings=portfolio_holdings,
                         total_investment=total_investment,
                         total_current_value=total_current_value,
                         total_pnl=total_pnl,
                         total_pnl_percentage=total_pnl_percentage,
                         sector_analysis=sector_analysis,
                         broker_analysis=broker_analysis)

@app.route('/dashboard/trade-now')
@login_required
def trade_now():
    """Trade execution page with algorithmic trading signals"""
    from datetime import datetime, date
    
    # Get selected date from query parameter or use today
    selected_date_str = request.args.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get trading signals for selected date
    trading_signals = TradingSignal.query.filter(
        db.func.date(TradingSignal.creation_date) == selected_date
    ).all()
    
    # If no signals for today, create sample data for demo
    if not trading_signals and selected_date == date.today():
        sample_signals = [
            TradingSignal(
                user_id=current_user.id,
                open_date=selected_date,
                symbol_type='stocks',
                ticker_symbol='RELIANCE',
                trade_direction='Long',
                entry_price=2450.50,
                number_of_units=50,
                capital_risk=122525.00,
                signal_status='Active',
                trading_account='Zerodha'
            ),
            TradingSignal(
                user_id=current_user.id,
                open_date=selected_date,
                symbol_type='stocks',
                ticker_symbol='TCS',
                trade_direction='Long',
                entry_price=3420.75,
                number_of_units=30,
                capital_risk=102622.50,
                signal_status='Active',
                trading_account='Angel One'
            ),
            TradingSignal(
                user_id=current_user.id,
                open_date=selected_date,
                symbol_type='stocks',
                ticker_symbol='HDFCBANK',
                trade_direction='Short',
                entry_price=1680.25,
                number_of_units=40,
                capital_risk=67210.00,
                signal_status='Active',
                trading_account='Dhan'
            ),
            TradingSignal(
                user_id=current_user.id,
                open_date=selected_date,
                symbol_type='futures',
                ticker_symbol='NIFTY24DEC',
                trade_direction='Long',
                entry_price=24850.00,
                number_of_units=1,
                capital_risk=24850.00,
                signal_status='Active',
                trading_account='Zerodha'
            ),
            TradingSignal(
                user_id=current_user.id,
                open_date=selected_date,
                symbol_type='options',
                ticker_symbol='RELIANCE',
                option_type='call',
                strike_price=2500.00,
                trade_direction='Long',
                entry_price=45.50,
                number_of_units=100,
                capital_risk=4550.00,
                signal_status='Active',
                trading_account='Angel One'
            )
        ]
        
        for signal in sample_signals:
            db.session.add(signal)
        
        try:
            db.session.commit()
            trading_signals = sample_signals
        except Exception as e:
            db.session.rollback()
            print(f"Error creating sample signals: {e}")
            trading_signals = []
    
    # Organize signals by type
    signals_by_type = {
        'Stocks': [s for s in trading_signals if s.symbol_type == 'stocks'],
        'Options': [s for s in trading_signals if s.symbol_type == 'options'],
        'Futures': [s for s in trading_signals if s.symbol_type == 'futures']
    }
    
    # Calculate statistics
    total_signals = len(trading_signals)
    buy_signals = len([s for s in trading_signals if s.trade_direction == 'Long'])
    sell_signals = len([s for s in trading_signals if s.trade_direction == 'Short'])
    avg_confidence = 78.5  # Mock average confidence score
    
    # Mock broker data - replace with actual broker integration
    brokers = [
        {'broker_id': 'zerodha', 'name': 'Zerodha'},
        {'broker_id': 'angel', 'name': 'Angel Broking'},
        {'broker_id': 'dhan', 'name': 'Dhan'}
    ]
    
    return render_template('dashboard/trade_now_simple.html',
                         current_user=current_user,
                         selected_date=selected_date,
                         trading_signals=trading_signals,
                         signals_by_type=signals_by_type,
                         total_signals=total_signals,
                         buy_signals=buy_signals,
                         sell_signals=sell_signals,
                         avg_confidence=avg_confidence,
                         brokers=brokers)

@app.route('/dashboard/account-handling')
@login_required
def dashboard_account_handling():
    """Dashboard Account Handling page"""
    from datetime import date
    return render_template('dashboard/account_handling.html', today=date.today())







@app.route('/dashboard/nse-stocks')
@login_required
def dashboard_nse_stocks():
    """NSE India stocks dashboard with real-time data"""
    try:
        # Get Indian market data using enhanced market data service
        trending_indian_stocks = market_data_service.get_trending_stocks('INDIA', 15)
        market_indices = market_data_service.get_market_indices()
        
        # Filter Indian indices
        indian_indices = [idx for idx in market_indices if idx.get('exchange') == 'NSE']
        
        # Get market status and additional data from NSE service
        market_status = nse_service.get_market_status()
        top_gainers = nse_service.get_top_gainers(10)
        top_losers = nse_service.get_top_losers(10)
        
        # If no data from enhanced service, fallback to original NSE service
        if not trending_indian_stocks:
            popular_symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN']
            trending_indian_stocks = nse_service.get_multiple_quotes(popular_symbols)
        
        if not indian_indices:
            indian_indices = nse_service.get_market_indices()
        
        return render_template('dashboard/nse_stocks.html',
                             popular_stocks=trending_indian_stocks,
                             market_status=market_status,
                             indices=indian_indices,
                             top_gainers=top_gainers,
                             top_losers=top_losers,
                             last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logging.error(f"Error loading NSE stocks dashboard: {str(e)}")
        flash('Unable to load NSE market data. Please try again later.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/dashboard/live-market')
@login_required
def live_market():
    """Live market data dashboard"""
    return render_template('dashboard/live_market.html',
                          last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/dashboard/add-nse-stock', methods=['POST'])
@login_required
def add_nse_stock_to_watchlist():
    """Add NSE stock to watchlist with real-time data"""
    try:
        symbol = request.form.get('symbol', '').upper()
        target_price = request.form.get('target_price')
        notes = request.form.get('notes', '')
        
        if not symbol:
            flash('Stock symbol is required.', 'error')
            return redirect(url_for('dashboard_watchlist'))
        
        # Get real-time data from NSE
        stock_data = nse_service.get_stock_quote(symbol)
        if not stock_data:
            flash(f'Unable to find stock {symbol} on NSE. Please check the symbol.', 'error')
            return redirect(url_for('dashboard_watchlist'))
        
        # Check if already in watchlist
        existing = WatchlistItem.query.filter_by(user_id=current_user.id, symbol=symbol).first()
        if existing:
            flash(f'{symbol} is already in your watchlist.', 'warning')
            return redirect(url_for('dashboard_watchlist'))
        
        # Create new watchlist item with NSE data
        watchlist_item = WatchlistItem(
            user_id=current_user.id,
            symbol=symbol,
            company_name=stock_data['company_name'],
            target_price=float(target_price) if target_price else None,
            notes=notes
        )
        
        db.session.add(watchlist_item)
        db.session.commit()
        
        flash(f'{symbol} ({stock_data["company_name"]}) added to your watchlist!', 'success')
        return redirect(url_for('dashboard_watchlist'))
        
    except Exception as e:
        logging.error(f"Error adding NSE stock to watchlist: {str(e)}")
        flash('Error adding stock to watchlist. Please try again.', 'error')
        return redirect(url_for('dashboard_watchlist'))

@app.route('/dashboard/analyze-nse-stock', methods=['POST'])
@login_required
def analyze_nse_stock():
    """Analyze NSE stock and save to database"""
    try:
        symbol = request.form.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Stock symbol is required'})
        
        # Get real-time data from NSE
        stock_data = nse_service.get_stock_quote(symbol)
        if not stock_data:
            return jsonify({'success': False, 'error': f'Stock {symbol} not found on NSE'})
        
        # Create or update stock analysis
        analysis = StockAnalysis.query.filter_by(symbol=symbol).first()
        if not analysis:
            analysis = StockAnalysis()
        
        # Update analysis with NSE data
        analysis.symbol = symbol
        analysis.company_name = stock_data['company_name']
        analysis.current_price = stock_data['current_price']
        analysis.previous_close = stock_data['previous_close']
        analysis.change_amount = stock_data['change_amount']
        analysis.change_percent = stock_data['change_percent']
        analysis.volume = stock_data['volume']
        analysis.day_high = stock_data['day_high']
        analysis.day_low = stock_data['day_low']
        analysis.week_52_high = stock_data['week_52_high']
        analysis.week_52_low = stock_data['week_52_low']
        analysis.pe_ratio = stock_data['pe_ratio']
        analysis.analysis_date = datetime.utcnow()
        
        # Generate AI recommendation based on price movement
        if stock_data['change_percent'] > 2:
            analysis.ai_recommendation = 'BUY'
            analysis.ai_confidence = min(85.0, 70 + abs(stock_data['change_percent']))
            analysis.ai_notes = f"Strong upward momentum with {stock_data['change_percent']:.2f}% gain"
        elif stock_data['change_percent'] < -2:
            analysis.ai_recommendation = 'SELL'
            analysis.ai_confidence = min(85.0, 70 + abs(stock_data['change_percent']))
            analysis.ai_notes = f"Significant decline of {stock_data['change_percent']:.2f}% - consider risk"
        else:
            analysis.ai_recommendation = 'HOLD'
            analysis.ai_confidence = 65.0
            analysis.ai_notes = "Stable price movement - monitor for trends"
        
        if analysis.id is None:
            db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'data': {
                'symbol': symbol,
                'company_name': analysis.company_name,
                'current_price': analysis.current_price,
                'change_percent': analysis.change_percent,
                'recommendation': analysis.ai_recommendation,
                'confidence': analysis.ai_confidence,
                'notes': analysis.ai_notes
            }
        })
        
    except Exception as e:
        logging.error(f"Error analyzing NSE stock: {str(e)}")
        return jsonify({'success': False, 'error': 'Analysis failed. Please try again.'})

def generate_mock_market_data():
    """Generate mock market data for fallback"""
    from types import SimpleNamespace
    
    # Create mock objects with proper attributes matching market_data_service format
    def create_stock(symbol, company_name, current_price, change_percent):
        stock = SimpleNamespace()
        stock.symbol = symbol
        stock.company_name = company_name
        stock.current_price = current_price
        stock.change = change_percent * current_price / 100  # Calculate absolute change
        stock.change_percent = f"{change_percent:.2f}"  # Format as string
        return stock
    
    return {
        'indices': [
            create_stock('SPY', 'S&P 500 ETF', 445.23, 1.2),
            create_stock('QQQ', 'NASDAQ-100 ETF', 378.45, -0.8),
            create_stock('^DJI', 'Dow Jones', 34567.89, 0.5)
        ],
        'trending_us': [
            create_stock('AAPL', 'Apple Inc.', 175.43, 2.1),
            create_stock('GOOGL', 'Alphabet Inc.', 142.56, -0.8),
            create_stock('MSFT', 'Microsoft Corp.', 378.85, 1.4),
            create_stock('NVDA', 'NVIDIA Corp.', 875.28, 3.7),
            create_stock('TSLA', 'Tesla Inc.', 248.50, 5.2)
        ],
        'trending_india': [],
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Admin Blog Management Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_posts = BlogPost.query.count()
    published_posts = BlogPost.query.filter_by(status='published').count()
    draft_posts = BlogPost.query.filter_by(status='draft').count()
    recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_posts=total_posts,
                         published_posts=published_posts,
                         draft_posts=draft_posts,
                         recent_posts=recent_posts)

@app.route('/admin/blog')
@admin_required
def admin_blog_list():
    """Admin blog post list"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = BlogPost.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    posts = query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/blog_list.html', posts=posts, status_filter=status_filter)

@app.route('/admin/blog/new', methods=['GET', 'POST'])
@admin_required
def admin_blog_new():
    """Create new blog post"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category')
        tags = request.form.get('tags')
        featured_image = request.form.get('featured_image')
        meta_description = request.form.get('meta_description')
        status = request.form.get('status', 'draft')
        is_featured = request.form.get('is_featured') == 'on'
        
        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('admin/blog_form.html')
        
        # Create new blog post
        post = BlogPost(
            title=title,
            content=content,
            excerpt=excerpt,
            author_id=current_user.id,
            author_name=current_user.get_full_name(),
            category=category,
            tags=tags,
            featured_image=featured_image,
            meta_description=meta_description,
            status=status,
            is_featured=is_featured
        )
        
        # Generate slug
        post.slug = post.generate_slug()
        
        # Set published date if publishing
        if status == 'published':
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.commit()
        
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin_blog_list'))
    
    return render_template('admin/blog_form.html', post=None)

@app.route('/admin/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(post_id):
    """Edit blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.excerpt = request.form.get('excerpt')
        post.category = request.form.get('category')
        post.tags = request.form.get('tags')
        post.featured_image = request.form.get('featured_image')
        post.meta_description = request.form.get('meta_description')
        
        old_status = post.status
        post.status = request.form.get('status', 'draft')
        post.is_featured = request.form.get('is_featured') == 'on'
        
        # Update slug if title changed
        new_slug = post.generate_slug()
        if new_slug != post.slug:
            post.slug = new_slug
        
        # Set published date if publishing for the first time
        if old_status != 'published' and post.status == 'published':
            post.published_at = datetime.utcnow()
        
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin_blog_list'))
    
    return render_template('admin/blog_form.html', post=post)

@app.route('/admin/blog/<int:post_id>/delete', methods=['POST'])
@admin_required
def admin_blog_delete(post_id):
    """Delete blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin_blog_list'))

@app.route('/admin/blog/<int:post_id>/toggle-featured', methods=['POST'])
@admin_required
def admin_blog_toggle_featured(post_id):
    """Toggle featured status of blog post"""
    post = BlogPost.query.get_or_404(post_id)
    post.is_featured = not post.is_featured
    db.session.commit()
    
    status = 'featured' if post.is_featured else 'unfeatured'
    flash(f'Post "{post.title}" has been {status}.', 'success')
    return redirect(url_for('admin_blog_list'))

# Update blog routes to handle slug-based URLs
@app.route('/blog/<slug>')
def blog_post_by_slug(slug):
    """Individual blog post page route by slug"""
    post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Increment view count
    post.view_count += 1
    db.session.commit()
    
    # Get related posts (same category or recent posts)
    related_posts = BlogPost.query.filter(
        BlogPost.id != post.id,
        BlogPost.status == 'published'
    ).order_by(BlogPost.created_at.desc()).limit(3).all()
    
    testimonials = Testimonial.query.limit(2).all()
    return render_template('blog_post.html', post=post, related_posts=related_posts, testimonials=testimonials)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Real-time Market Data API Endpoints

@app.route('/api/stock/<symbol>')
def api_get_stock(symbol):
    """Get real-time stock data"""
    exchange = request.args.get('exchange', 'US')
    try:
        stock_data = market_data_service.get_stock_quote(symbol, exchange)
        if stock_data:
            return jsonify({
                'success': True,
                'data': stock_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Stock not found'
            }), 404
    except Exception as e:
        logging.error(f"API error for stock {symbol}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/market/indices')
def api_market_indices():
    """Get market indices"""
    try:
        indices = market_data_service.get_market_indices()
        return jsonify({
            'success': True,
            'data': indices,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"API error for market indices: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch market indices'
        }), 500

@app.route('/api/market/trending')
def api_trending_stocks():
    """Get trending stocks"""
    market = request.args.get('market', 'US')
    limit = int(request.args.get('limit', 10))
    try:
        trending = market_data_service.get_trending_stocks(market, limit)
        return jsonify({
            'success': True,
            'data': trending,
            'market': market,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"API error for trending stocks: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch trending stocks'
        }), 500

@app.route('/api/search/stocks')
def api_search_stocks():
    """Search stocks by symbol or company name"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Query parameter required'
        }), 400
    
    try:
        results = market_data_service.search_stocks(query, limit)
        return jsonify({
            'success': True,
            'data': results,
            'query': query
        })
    except Exception as e:
        logging.error(f"API error for stock search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Search failed'
        }), 500

# Agentic AI Routes
@app.route('/dashboard/ai-advisor')
@login_required
def ai_advisor():
    """AI Advisor Dashboard - Main agentic AI interface"""
    from datetime import date
    # Get recent AI analyses for the user
    recent_analyses = AIAnalysis.query.filter_by(user_id=current_user.id).order_by(
        AIAnalysis.created_at.desc()
    ).limit(10).all()
    
    # Get portfolio optimization history
    portfolio_optimizations = PortfolioOptimization.query.filter_by(
        user_id=current_user.id
    ).order_by(PortfolioOptimization.created_at.desc()).limit(5).all()
    
    return render_template('dashboard/ai_advisor.html', 
                         recent_analyses=recent_analyses,
                         portfolio_optimizations=portfolio_optimizations,
                         current_user=current_user,
                         today=date.today())

@app.route('/api/ai/analyze-stock', methods=['POST'])
@login_required
def api_ai_analyze_stock():
    """Comprehensive AI stock analysis using all agents"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol is required'}), 400
        
        # Initialize AI coordinator
        ai_coordinator = AgenticAICoordinator()
        
        # Get user's portfolio for context
        watchlist_items = WatchlistItem.query.filter_by(user_id=current_user.id).all()
        portfolio = {
            'total_value': 100000,  # Default portfolio value
            'positions': [{'symbol': item.symbol, 'value': 10000} for item in watchlist_items]
        }
        
        # Perform Agentic AI analysis (learn, reason, act, adapt)
        analysis_result = ai_coordinator.analyze_with_agentic_ai(symbol, "comprehensive")
        
        if 'error' in analysis_result:
            return jsonify({'success': False, 'error': analysis_result['error']}), 500
        
        # Store Agentic AI analysis in database
        ai_analysis = AIAnalysis(
            user_id=current_user.id,
            symbol=symbol,
            analysis_type='AGENTIC_AI',
            trading_recommendation=analysis_result.get('final_recommendation', 'HOLD'),
            trading_confidence=analysis_result.get('confidence', 0.5),
            trading_reasoning=analysis_result.get('reasoning_summary', 'Agentic AI analysis completed'),
            sentiment_score=0.5,  # Will be enhanced with research sentiment
            sentiment_label='NEUTRAL',
            news_sentiment='NEUTRAL',
            risk_level='MEDIUM',
            suggested_position_size=0.1,
            final_recommendation=analysis_result.get('final_recommendation', 'HOLD'),
            overall_confidence=analysis_result.get('confidence', 0.5),
            technical_indicators=str(analysis_result.get('research_insights', []))
        )
        
        db.session.add(ai_analysis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': analysis_result,
            'analysis_id': ai_analysis.id
        })
        
    except Exception as e:
        logging.error(f"AI stock analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze stock'
        }), 500

@app.route('/api/ai/optimize-portfolio', methods=['POST'])
@login_required
def api_ai_optimize_portfolio():
    """AI-powered portfolio optimization"""
    try:
        # Get user's current portfolio
        watchlist_items = WatchlistItem.query.filter_by(user_id=current_user.id).all()
        
        portfolio = {
            'total_value': 100000,  # This could be calculated from actual holdings
            'positions': [
                {
                    'symbol': item.symbol,
                    'value': 10000,  # This should be actual position value
                    'target_price': item.target_price
                } for item in watchlist_items
            ]
        }
        
        # Initialize AI coordinator
        ai_coordinator = AgenticAICoordinator()
        
        # Perform portfolio optimization
        optimization_result = ai_coordinator.optimize_portfolio_comprehensive(portfolio)
        
        if 'error' in optimization_result:
            return jsonify({'success': False, 'error': optimization_result['error']}), 500
        
        # Store optimization results
        portfolio_opt = PortfolioOptimization(
            user_id=current_user.id,
            total_value=portfolio['total_value'],
            num_positions=len(portfolio['positions']),
            rebalance_needed=optimization_result['optimization'].get('rebalance_needed', False),
            efficiency_score=optimization_result['optimization'].get('efficiency_score'),
            diversification_score=optimization_result['optimization'].get('diversification_score'),
            suggested_actions=str(optimization_result['optimization'].get('suggested_actions', [])),
            allocation_recommendations=str(optimization_result['optimization'].get('risk_adjusted_allocation', {}))
        )
        
        db.session.add(portfolio_opt)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': optimization_result,
            'optimization_id': portfolio_opt.id
        })
        
    except Exception as e:
        logging.error(f"Portfolio optimization error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to optimize portfolio'
        }), 500

@app.route('/api/n8n/trigger-workflow', methods=['POST'])
@login_required
def api_trigger_n8n_workflow():
    """Trigger n8n workflow for Agentic AI automation"""
    try:
        data = request.get_json()
        workflow_type = data.get('workflow_type')
        workflow_data = data.get('data', {})
        
        if not workflow_type:
            return jsonify({'success': False, 'error': 'Workflow type is required'}), 400
        
        # Initialize AI coordinator for n8n integration
        ai_coordinator = AgenticAICoordinator()
        
        # Trigger the specified workflow
        result = ai_coordinator._trigger_n8n_workflow(workflow_type, workflow_data)
        
        return jsonify({
            'success': result,
            'message': f'Workflow {workflow_type} triggered successfully' if result else f'Failed to trigger workflow {workflow_type}',
            'workflow_type': workflow_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"n8n workflow trigger error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/sentiment-analysis/<symbol>')
@login_required
def api_ai_sentiment_analysis(symbol):
    """Get AI sentiment analysis for a specific stock"""
    try:
        ai_coordinator = AgenticAICoordinator()
        sentiment_result = ai_coordinator.sentiment_agent.analyze_sentiment(symbol.upper())
        
        if 'error' in sentiment_result:
            return jsonify({'success': False, 'error': sentiment_result['error']}), 500
        
        return jsonify({
            'success': True,
            'data': sentiment_result
        })
        
    except Exception as e:
        logging.error(f"Sentiment analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze sentiment'
        }), 500

@app.route('/api/ai/trading-signals/<symbol>')
@login_required
def api_ai_trading_signals(symbol):
    """Get AI trading signals for a specific stock"""
    try:
        ai_coordinator = AgenticAICoordinator()
        trading_result = ai_coordinator.trading_agent.analyze_stock(symbol.upper())
        
        if 'error' in trading_result:
            return jsonify({'success': False, 'error': trading_result['error']}), 500
        
        return jsonify({
            'success': True,
            'data': trading_result
        })
        
    except Exception as e:
        logging.error(f"Trading signals error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get trading signals'
        }), 500

# Account Management Routes
@app.route('/account/profile')
@login_required
def account_profile():
    """User profile management"""
    # Get user statistics for display
    trading_signals_count = TradingSignal.query.count()
    return render_template('account/profile.html', 
                         active_section='profile',
                         trading_signals_count=trading_signals_count,
                         PricingPlan=PricingPlan)

@app.route('/account/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.username = request.form.get('username')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating profile: ' + str(e), 'error')
        
    return redirect(url_for('account_profile'))

@app.route('/account')
@login_required
def account_settings():
    """Account settings page"""
    # Get user preferences from session or use defaults
    user_preferences = session.get('user_preferences', {
        'email_trading_alerts': True,
        'email_market_updates': True,
        'email_billing_updates': True,
        'email_promotional': False,
        'default_dashboard_view': 'overview',
        'theme_preference': 'light',
        'timezone': 'Asia/Kolkata'
    })
    
    return render_template('account/settings.html', 
                         active_section='account',
                         user_preferences=user_preferences)

@app.route('/account/billing')
@login_required
def account_billing():
    """Billing and subscription management"""
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).limit(10).all()
    
    return render_template('account/billing.html', 
                         active_section='billing',
                         payments=payments,
                         PricingPlan=PricingPlan,
                         razorpay_key_id=RAZORPAY_KEY_ID)

@app.route('/account/referrals')
@login_required
def account_referrals():
    """Referrals management"""
    if not current_user.referral_code:
        current_user.generate_referral_code()
        db.session.commit()
    
    referrals = Referral.query.filter_by(referrer_id=current_user.id).order_by(Referral.created_at.desc()).all()
    
    referral_stats = {
        'total_referrals': len(referrals),
        'successful_referrals': sum(1 for r in referrals if r.status == 'paid'),
        'pending_referrals': sum(1 for r in referrals if r.status == 'pending'),
        'total_earned': sum(r.reward_amount for r in referrals if r.status == 'paid'),
        'pending_amount': sum(r.reward_amount for r in referrals if r.status == 'pending'),
        'paid_amount': sum(r.reward_amount for r in referrals if r.status == 'paid')
    }
    
    return render_template('account/referrals.html', 
                         active_section='referrals',
                         referrals=referrals,
                         referral_stats=referral_stats)

# API Routes for Account Management
@app.route('/api/create-order', methods=['POST'])
@login_required
def create_razorpay_order():
    """Create Razorpay order for subscription payment"""
    try:
        data = request.get_json()
        plan_type = data.get('plan_type')
        amount = data.get('amount')
        
        if razorpay_client:
            # Create actual Razorpay order
            order_data = {
                'amount': amount * 100,  # Amount in paise
                'currency': 'INR',
                'receipt': f'tcapital_{current_user.id}_{int(datetime.now().timestamp())}',
                'notes': {
                    'user_id': str(current_user.id),
                    'plan_type': plan_type,
                    'email': current_user.email
                }
            }
            order = razorpay_client.order.create(data=order_data)
            
            return jsonify({
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key': RAZORPAY_KEY_ID
            })
        else:
            # Fallback for demo/testing without real keys
            order_data = {
                'success': True,
                'order_id': f'order_{int(datetime.now().timestamp())}',
                'amount': amount * 100,
                'currency': 'INR',
                'key': RAZORPAY_KEY_ID
            }
            return jsonify(order_data)
        
    except Exception as e:
        logging.error(f"Razorpay order creation failed: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to create payment order'})

@app.route('/api/payment-success', methods=['POST'])
@login_required
def handle_payment_success():
    """Handle successful payment and upgrade user plan"""
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')
        order_id = data.get('order_id')
        signature = data.get('signature')
        plan_type = data.get('plan_type')
        
        # Verify payment signature if using real Razorpay
        if razorpay_client and signature:
            try:
                razorpay_client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                })
            except:
                return jsonify({'success': False, 'message': 'Payment verification failed'})
        
        # Determine plan and amount
        if plan_type == 'trader':
            current_user.pricing_plan = PricingPlan.TRADER
            amount = 1999
        elif plan_type == 'trader_plus':
            current_user.pricing_plan = PricingPlan.TRADER_PLUS
            amount = 3999
        else:
            return jsonify({'success': False, 'message': 'Invalid plan type'})
        
        # Update user subscription
        current_user.subscription_status = SubscriptionStatus.ACTIVE
        current_user.subscription_start_date = datetime.utcnow()
        current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
        current_user.total_payments += amount
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            razorpay_payment_id=payment_id,
            razorpay_order_id=order_id,
            amount=amount,
            status='captured',
            plan_type=current_user.pricing_plan,
            billing_period='monthly'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        logging.info(f"User {current_user.id} upgraded to {plan_type} plan")
        return jsonify({'success': True, 'message': 'Plan upgraded successfully!'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Payment processing failed: {str(e)}")
        return jsonify({'success': False, 'message': 'Payment processing failed'})

@app.route('/api/generate-referral-code', methods=['POST'])
@login_required
def generate_referral_code():
    """Generate referral code for user"""
    try:
        referral_code = current_user.generate_referral_code()
        db.session.commit()
        
        return jsonify({'success': True, 'referral_code': referral_code})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

