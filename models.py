from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    author_name = db.Column(db.String(100), nullable=False)  # For backward compatibility
    featured_image = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.String(200), nullable=True)  # Comma-separated tags
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    meta_description = db.Column(db.String(160), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    
    # Relationship to author
    author = db.relationship('User', backref='blog_posts', foreign_keys=[author_id])
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def set_tags_from_list(self, tags_list):
        """Set tags from a list"""
        if tags_list:
            self.tags = ', '.join(tags_list)
        else:
            self.tags = None
    
    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        import re
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))  # Average 200 words per minute

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    image_url = db.Column(db.String(500), nullable=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship to watchlist
    watchlist = db.relationship('WatchlistItem', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

class WatchlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    target_price = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Unique constraint to prevent duplicate symbols per user
    __table_args__ = (db.UniqueConstraint('user_id', 'symbol', name='unique_user_symbol'),)

class StockAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_close = db.Column(db.Float, nullable=False)
    change_amount = db.Column(db.Float, nullable=False)
    change_percent = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger, nullable=True)
    market_cap = db.Column(db.BigInteger, nullable=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    day_high = db.Column(db.Float, nullable=True)
    day_low = db.Column(db.Float, nullable=True)
    week_52_high = db.Column(db.Float, nullable=True)
    week_52_low = db.Column(db.Float, nullable=True)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    ai_recommendation = db.Column(db.String(20), nullable=True)  # BUY, SELL, HOLD
    ai_confidence = db.Column(db.Float, nullable=True)  # Confidence score 0-1
    risk_level = db.Column(db.String(10), nullable=True)  # LOW, MEDIUM, HIGH

class AIAnalysis(db.Model):
    """Store comprehensive AI agent analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    symbol = db.Column(db.String(10), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # STOCK, PORTFOLIO, SENTIMENT
    
    # Trading Agent Results
    trading_recommendation = db.Column(db.String(20), nullable=True)
    trading_confidence = db.Column(db.Float, nullable=True)
    trading_reasoning = db.Column(db.Text, nullable=True)
    
    # Sentiment Agent Results
    sentiment_score = db.Column(db.Float, nullable=True)
    sentiment_label = db.Column(db.String(20), nullable=True)
    news_sentiment = db.Column(db.String(20), nullable=True)
    
    # Risk Agent Results
    risk_level = db.Column(db.String(10), nullable=True)
    suggested_position_size = db.Column(db.Float, nullable=True)
    risk_warnings = db.Column(db.Text, nullable=True)
    
    # Final Recommendation
    final_recommendation = db.Column(db.String(20), nullable=False)
    overall_confidence = db.Column(db.Float, nullable=False)
    
    # Technical Indicators (JSON stored as text)
    technical_indicators = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PortfolioOptimization(db.Model):
    """Store portfolio optimization recommendations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Current portfolio state
    total_value = db.Column(db.Float, nullable=False)
    num_positions = db.Column(db.Integer, nullable=False)
    
    # Optimization results
    rebalance_needed = db.Column(db.Boolean, default=False)
    efficiency_score = db.Column(db.Float, nullable=True)
    diversification_score = db.Column(db.Float, nullable=True)
    
    # Recommendations (JSON stored as text)
    suggested_actions = db.Column(db.Text, nullable=True)
    allocation_recommendations = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref='portfolio_optimizations')

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship("User")


