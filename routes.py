from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db
from models import BlogPost, TeamMember, Testimonial, User, WatchlistItem, StockAnalysis
from services.nse_service import nse_service
import logging
import random
from datetime import datetime, timedelta
from functools import wraps

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/dashboard/nse-stocks')
@login_required
def nse_stocks():
    """NSE India stocks dashboard"""
    try:
        # Get popular Indian stocks for display
        popular_symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN']
        popular_stocks = nse_service.get_multiple_quotes(popular_symbols)
        
        # Get market overview
        market_status = nse_service.get_market_status()
        indices = nse_service.get_market_indices()
        top_gainers = nse_service.get_top_gainers(10)
        top_losers = nse_service.get_top_losers(10)
        
        return render_template('dashboard/nse_stocks.html',
                             popular_stocks=popular_stocks,
                             market_status=market_status,
                             indices=indices,
                             top_gainers=top_gainers,
                             top_losers=top_losers)
    except Exception as e:
        logging.error(f"Error loading NSE stocks dashboard: {str(e)}")
        flash('Unable to load NSE market data. Please try again later.', 'error')
        return redirect(url_for('dashboard'))

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
            return redirect(url_for('watchlist'))
        
        # Get real-time data from NSE
        stock_data = nse_service.get_stock_quote(symbol)
        if not stock_data:
            flash(f'Unable to find stock {symbol} on NSE. Please check the symbol.', 'error')
            return redirect(url_for('watchlist'))
        
        # Check if already in watchlist
        existing = WatchlistItem.query.filter_by(user_id=current_user.id, symbol=symbol).first()
        if existing:
            flash(f'{symbol} is already in your watchlist.', 'warning')
            return redirect(url_for('watchlist'))
        
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
        return redirect(url_for('watchlist'))
        
    except Exception as e:
        logging.error(f"Error adding NSE stock to watchlist: {str(e)}")
        flash('Error adding stock to watchlist. Please try again.', 'error')
        return redirect(url_for('watchlist'))

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
    """Generate mock market data for demonstration - now using NSE data when available"""
    try:
        # Try to get real NSE data for popular stocks
        popular_symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN']
        real_data = nse_service.get_multiple_quotes(popular_symbols)
        
        if real_data:
            # Convert NSE data to match expected format
            market_data = []
            for stock in real_data:
                market_data.append({
                    'symbol': stock['symbol'],
                    'name': stock['company_name'],
                    'price': stock['current_price'],
                    'change': stock['change_amount'],
                    'change_percent': stock['change_percent'],
                    'trend': 'up' if stock['change_amount'] > 0 else 'down'
                })
            return market_data
    except Exception as e:
        logging.warning(f"Failed to fetch real NSE data, using fallback: {str(e)}")
    
    # Fallback to demo data if NSE service fails
    stocks = [
        {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd.', 'price': 2450.75, 'change': 15.20},
        {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'price': 3890.40, 'change': -22.50},
        {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Limited', 'price': 1678.90, 'change': 8.80},
        {'symbol': 'INFY', 'name': 'Infosys Limited', 'price': 1456.30, 'change': -12.20},
        {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Limited', 'price': 1089.75, 'change': 18.60},
        {'symbol': 'SBIN', 'name': 'State Bank of India', 'price': 542.85, 'change': 5.25}
    ]
    
    for stock in stocks:
        stock['change_percent'] = (stock['change'] / (stock['price'] - stock['change'])) * 100
        stock['trend'] = 'up' if stock['change'] > 0 else 'down'
    
    return stocks

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
