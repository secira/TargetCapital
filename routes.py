from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db
from models import BlogPost, TeamMember, Testimonial, User, WatchlistItem, StockAnalysis
import logging
import random
from datetime import datetime, timedelta

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
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    featured_posts = BlogPost.query.filter_by(is_featured=True).limit(3).all()
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



@app.route('/contact', methods=['POST'])
def contact():
    """Contact form submission route"""
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if not all([name, email, message]):
        flash('Please fill in all required fields.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # In a real application, you would send an email or save to database
    logging.info(f"Contact form submission: {name} ({email}) - {message}")
    flash('Thank you for your message. We will get back to you soon!', 'success')
    
    return redirect(request.referrer or url_for('index'))

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
        
        user = User.query.filter_by(username=username).first()
        
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

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard route"""
    # Get user's watchlist
    watchlist = WatchlistItem.query.filter_by(user_id=current_user.id).all()
    
    # Get recent stock analyses
    recent_analyses = StockAnalysis.query.order_by(StockAnalysis.analysis_date.desc()).limit(10).all()
    
    # Generate mock market data for demo
    mock_market_data = generate_mock_market_data()
    
    return render_template('dashboard/dashboard.html', 
                         watchlist=watchlist, 
                         recent_analyses=recent_analyses,
                         market_data=mock_market_data)

@app.route('/dashboard/stock-analysis')
@login_required
def stock_analysis():
    """Stock analysis dashboard"""
    # Get all stock analyses
    analyses = StockAnalysis.query.order_by(StockAnalysis.analysis_date.desc()).all()
    return render_template('dashboard/stock_analysis.html', analyses=analyses)

@app.route('/dashboard/watchlist')
@login_required
def watchlist():
    """User watchlist management"""
    watchlist_items = WatchlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/watchlist.html', watchlist_items=watchlist_items)

@app.route('/dashboard/add-to-watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    """Add stock to watchlist"""
    symbol = request.form.get('symbol', '').upper()
    company_name = request.form.get('company_name', '')
    target_price = request.form.get('target_price')
    notes = request.form.get('notes', '')
    
    if not symbol:
        flash('Stock symbol is required.', 'error')
        return redirect(url_for('watchlist'))
    
    # Check if already in watchlist
    existing = WatchlistItem.query.filter_by(user_id=current_user.id, symbol=symbol).first()
    if existing:
        flash(f'{symbol} is already in your watchlist.', 'warning')
        return redirect(url_for('watchlist'))
    
    # Create new watchlist item
    watchlist_item = WatchlistItem(
        user_id=current_user.id,
        symbol=symbol,
        company_name=company_name,
        target_price=float(target_price) if target_price else None,
        notes=notes
    )
    
    db.session.add(watchlist_item)
    db.session.commit()
    
    flash(f'{symbol} added to your watchlist!', 'success')
    return redirect(url_for('watchlist'))

@app.route('/dashboard/remove-from-watchlist/<int:item_id>')
@login_required
def remove_from_watchlist(item_id):
    """Remove stock from watchlist"""
    item = WatchlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    symbol = item.symbol
    
    db.session.delete(item)
    db.session.commit()
    
    flash(f'{symbol} removed from your watchlist.', 'info')
    return redirect(url_for('watchlist'))

@app.route('/seed-demo-data')
def seed_demo_data():
    """Seed the database with demo data for testing"""
    try:
        # Create demo user if not exists
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            demo_user = User(
                username='demo',
                email='demo@aitradebot.com',
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

def generate_mock_market_data():
    """Generate mock market data for demonstration"""
    stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50, 'change': 2.15},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 2845.20, 'change': -12.50},
        {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 378.90, 'change': 5.80},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 245.30, 'change': -8.20},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'price': 495.75, 'change': 15.60},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'price': 142.85, 'change': 3.25}
    ]
    
    for stock in stocks:
        stock['change_percent'] = (stock['change'] / (stock['price'] - stock['change'])) * 100
        stock['trend'] = 'up' if stock['change'] > 0 else 'down'
    
    return stocks

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
