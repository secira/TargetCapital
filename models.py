from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

# Import broker models
from models_broker import BrokerAccount, BrokerHolding, BrokerPosition, BrokerOrder

# Portfolio Asset Classes
class AssetType(Enum):
    EQUITIES = "equities"           # Individual stocks
    MUTUAL_FUNDS = "mutual_funds"   # Mutual fund units
    FIXED_INCOME = "fixed_income"   # Bonds, FDs, etc.
    FUTURES_OPTIONS = "futures_options"  # F&O contracts
    NPS = "nps"                     # National Pension System
    REAL_ESTATE = "real_estate"     # Real estate investments
    GOLD = "gold"                   # Gold ETFs, digital gold
    ETF = "etf"                     # Exchange traded funds
    CRYPTO = "crypto"               # Cryptocurrency holdings
    ESOP = "esop"                   # Employee stock options
    PRIVATE_EQUITY = "private_equity"  # Private equity investments

class AssetCategory(Enum):
    EQUITY = "equity"               # Growth-oriented investments
    DEBT = "debt"                   # Fixed income investments
    COMMODITIES = "commodities"     # Physical commodities
    ALTERNATIVE = "alternative"     # Alternative investments
    HYBRID = "hybrid"               # Balanced/hybrid funds

# Pricing Plan Enums
class PricingPlan(Enum):
    FREE = "free"
    TARGET_PLUS = "target_plus"
    TARGET_PRO = "target_pro"
    HNI = "hni"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

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

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    inquiry_type = db.Column(db.String(50), nullable=True)  # General, Support, Sales, Partnership
    status = db.Column(db.String(20), default='new')  # new, read, replied, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<ContactMessage {self.name} - {self.subject}>'

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
    username = db.Column(db.String(80), unique=True, nullable=True)  # Made nullable for mobile-only signup
    email = db.Column(db.String(120), unique=True, nullable=True)  # Made nullable for mobile-only signup
    password_hash = db.Column(db.String(256), nullable=True)  # Made nullable for OTP-only accounts
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Mobile number and OTP fields
    mobile_number = db.Column(db.String(20), unique=True, nullable=True)
    mobile_verified = db.Column(db.Boolean, default=False)
    current_otp = db.Column(db.String(10), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, default=0)
    last_otp_request = db.Column(db.DateTime, nullable=True)
    
    # Profile image (for OAuth login)
    profile_image_url = db.Column(db.String(500), nullable=True)
    
    # Subscription and Billing Information
    pricing_plan = db.Column(db.Enum(PricingPlan), default=PricingPlan.FREE, nullable=False)
    subscription_status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE, nullable=False)
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)  # Alias for payment system compatibility
    razorpay_customer_id = db.Column(db.String(100), nullable=True)
    razorpay_subscription_id = db.Column(db.String(100), nullable=True)
    billing_cycle = db.Column(db.String(20), default="monthly", nullable=True)  # monthly, yearly
    total_payments = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(20), unique=True, nullable=True)
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
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
    
    def can_access_menu(self, menu_item):
        """Check if user can access specific menu item based on pricing plan"""
        # Free users can access Dashboard, AI Advisor, and Trading Signals (view-only)
        if self.pricing_plan == PricingPlan.FREE:
            return menu_item in ['dashboard', 'ai_advisor', 'dashboard_trading_signals']
        
        # Target Plus users can access Trade Now but have limited broker features
        elif self.pricing_plan == PricingPlan.TARGET_PLUS:
            return menu_item not in []  # Target Plus can access all menus now
        
        # Target Pro and HNI users can access everything
        elif self.pricing_plan in [PricingPlan.TARGET_PRO, PricingPlan.HNI]:
            return True
            
        return False
    
    def get_plan_display_name(self):
        """Get human-readable plan name"""
        plan_names = {
            PricingPlan.FREE: "Free User",
            PricingPlan.TARGET_PLUS: "Target Plus",
            PricingPlan.TARGET_PRO: "Target Pro",
            PricingPlan.HNI: "HNI Account"
        }
        return plan_names.get(self.pricing_plan, "Unknown")
    
    def get_plan_price(self):
        """Get monthly price for the current plan"""
        prices = {
            PricingPlan.FREE: 0,
            PricingPlan.TARGET_PLUS: 1499,
            PricingPlan.TARGET_PRO: 2999,
            PricingPlan.HNI: 9999
        }
        return prices.get(self.pricing_plan, 0)
    
    def is_subscription_active(self):
        """Check if user has active subscription"""
        if self.pricing_plan == PricingPlan.FREE:
            return True  # Free plan is always active
        return (self.subscription_status == SubscriptionStatus.ACTIVE and 
                self.subscription_end_date and 
                self.subscription_end_date > datetime.utcnow())
    
    def generate_referral_code(self):
        """Generate unique referral code for user"""
        import string
        import random
        if not self.referral_code:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # Ensure uniqueness
            while User.query.filter_by(referral_code=code).first():
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.referral_code = code
            return code
        return self.referral_code


class Payment(db.Model):
    """Track all payment transactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    razorpay_payment_id = db.Column(db.String(100), unique=True, nullable=False)
    razorpay_order_id = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.String(20), nullable=False)  # captured, failed, refunded
    payment_method = db.Column(db.String(50), nullable=True)  # card, netbanking, upi
    plan_type = db.Column(db.Enum(PricingPlan), nullable=False)
    billing_period = db.Column(db.String(20), nullable=True)  # monthly, yearly
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='payments')

class Referral(db.Model):
    """Track referral rewards and commissions"""
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reward_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referrals_made')
    referred = db.relationship('User', foreign_keys=[referred_id], backref='referral_record')

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
    ai_notes = db.Column(db.Text, nullable=True)  # AI analysis notes
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

class PortfolioTrade(db.Model):
    """User's personal portfolio trades and trade journal"""
    __tablename__ = 'portfolio_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who made the trade
    open_date = db.Column(db.Date, nullable=False)
    symbol_type = db.Column(db.String(20), nullable=False)  # Index, futures, currency, crypto, options, stocks, gold
    ticker_symbol = db.Column(db.String(20), nullable=False)
    option_type = db.Column(db.String(20), nullable=True)  # call, put, stock
    trade_strategy = db.Column(db.String(100), nullable=True)  # Covered calls, Naked put, Buy and hold
    strike_price = db.Column(db.Float, nullable=True)  # Strike price for options
    expiration_date = db.Column(db.Date, nullable=True)  # Option expiry date
    number_of_units = db.Column(db.Integer, nullable=False)  # Number of contracts or shares
    trade_direction = db.Column(db.String(10), nullable=False)  # Long or Short
    entry_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    trade_fees = db.Column(db.Float, nullable=True)  # Brokerage charges
    capital_risk = db.Column(db.Float, nullable=False)  # Total purchase capital
    exit_date = db.Column(db.Date, nullable=True)
    exit_price = db.Column(db.Float, nullable=True)
    trade_result = db.Column(db.String(20), nullable=True)  # Profit, Loss, Breakeven
    trade_duration = db.Column(db.Integer, nullable=True)  # Days held
    assignment_details = db.Column(db.Text, nullable=True)
    reason_for_exit = db.Column(db.String(100), nullable=True)  # Stop loss, target, etc.
    trading_account = db.Column(db.String(50), nullable=True)  # Brokerage account
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status and performance tracking
    signal_status = db.Column(db.String(20), default='Active')  # Active, Closed, Stopped
    pnl_amount = db.Column(db.Float, nullable=True)
    pnl_percentage = db.Column(db.Float, nullable=True)
    
    # Relationship to user
    user = db.relationship('User', backref='portfolio_trades')
    
    def calculate_pnl(self):
        """Calculate P&L based on current or exit price"""
        if self.exit_price:
            price_diff = self.exit_price - self.entry_price
        elif self.current_price:
            price_diff = self.current_price - self.entry_price
        else:
            return 0, 0
            
        if self.trade_direction.lower() == 'short':
            price_diff = -price_diff
            
        pnl_amount = price_diff * self.number_of_units
        pnl_percentage = (price_diff / self.entry_price) * 100 if self.entry_price > 0 else 0
        
        return pnl_amount, pnl_percentage
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class based on status"""
        if self.signal_status == 'Active':
            return 'bg-primary'
        elif self.signal_status == 'Closed':
            return 'bg-success'
        elif self.signal_status == 'Stopped':
            return 'bg-danger'
        return 'bg-secondary'
    
    def get_pnl_class(self):
        """Return CSS class for P&L display"""
        pnl_amount, _ = self.calculate_pnl()
        if pnl_amount > 0:
            return 'text-success'
        elif pnl_amount < 0:
            return 'text-danger'
        return 'text-muted'

class AIStockPick(db.Model):
    """AI-generated daily stock picks for dashboard display"""
    __tablename__ = 'ai_stock_picks'
    
    id = db.Column(db.Integer, primary_key=True)
    pick_date = db.Column(db.Date, nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    target_price = db.Column(db.Float, nullable=True)
    recommendation = db.Column(db.String(20), nullable=False)  # BUY, SELL, HOLD
    confidence_score = db.Column(db.Integer, default=85)
    ai_reasoning = db.Column(db.Text, nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    market_cap = db.Column(db.String(50), nullable=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    dividend_yield = db.Column(db.Float, nullable=True)
    key_highlights = db.Column(db.Text, nullable=True)
    risk_factors = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_upside_percentage(self):
        """Calculate upside percentage"""
        if self.target_price and self.current_price:
            return ((self.target_price - self.current_price) / self.current_price) * 100
        return 0

class ManualEquityHolding(db.Model):
    """Manual equity holdings entered by users"""
    __tablename__ = 'manual_equity_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Which broker holds this
    
    # Stock Details
    symbol = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    isin = db.Column(db.String(20), nullable=True)
    
    # Transaction Details
    transaction_type = db.Column(db.String(10), nullable=False, default='BUY')  # BUY/SELL
    purchase_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    
    # Costs & Charges
    brokerage = db.Column(db.Float, default=0.0)
    stt = db.Column(db.Float, default=0.0)
    transaction_charges = db.Column(db.Float, default=0.0)
    gst = db.Column(db.Float, default=0.0)
    stamp_duty = db.Column(db.Float, default=0.0)
    total_charges = db.Column(db.Float, default=0.0)
    
    # Investment Calculation
    total_investment = db.Column(db.Float, nullable=False)  # (quantity * price) + charges
    
    # Current Market Data (updated periodically)
    current_price = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, nullable=True)
    unrealized_pnl = db.Column(db.Float, nullable=True)
    unrealized_pnl_percentage = db.Column(db.Float, nullable=True)
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Equity')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_equity_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_equity_holdings', foreign_keys=[broker_account_id])
    
    def calculate_totals(self):
        """Calculate total investment and current values"""
        self.total_charges = (self.brokerage or 0) + (self.stt or 0) + (self.transaction_charges or 0) + (self.gst or 0) + (self.stamp_duty or 0)
        self.total_investment = (self.quantity * self.purchase_price) + self.total_charges
        
        if self.current_price:
            self.current_value = self.quantity * self.current_price
            self.unrealized_pnl = self.current_value - self.total_investment
            if self.total_investment > 0:
                self.unrealized_pnl_percentage = (self.unrealized_pnl / self.total_investment) * 100

class ManualMutualFundHolding(db.Model):
    """Manual mutual fund holdings entered by users"""
    __tablename__ = 'manual_mutual_fund_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Which broker holds this
    
    # Fund Details
    scheme_name = db.Column(db.String(200), nullable=False)
    fund_house = db.Column(db.String(100), nullable=True)  # AMC Name
    isin = db.Column(db.String(20), nullable=True)
    folio_number = db.Column(db.String(50), nullable=True)
    fund_category = db.Column(db.String(50), nullable=True)  # Equity, Debt, Hybrid, etc.
    
    # Transaction Details
    transaction_type = db.Column(db.String(20), nullable=False, default='PURCHASE')  # PURCHASE/REDEMPTION/SWITCH_IN/SWITCH_OUT/DIVIDEND
    transaction_date = db.Column(db.Date, nullable=False)
    units = db.Column(db.Float, nullable=False)
    nav = db.Column(db.Float, nullable=False)  # Net Asset Value at transaction
    
    # Investment Amount
    amount = db.Column(db.Float, nullable=False)  # Total transaction amount
    
    # Costs & Charges
    entry_load = db.Column(db.Float, default=0.0)
    exit_load = db.Column(db.Float, default=0.0)
    stamp_duty = db.Column(db.Float, default=0.0)
    stt = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    total_charges = db.Column(db.Float, default=0.0)
    
    # Investment Calculation
    total_investment = db.Column(db.Float, nullable=False)  # amount + charges
    
    # Current Market Data (updated periodically)
    current_nav = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, nullable=True)
    unrealized_pnl = db.Column(db.Float, nullable=True)
    unrealized_pnl_percentage = db.Column(db.Float, nullable=True)
    
    # Returns & Performance
    xirr = db.Column(db.Float, nullable=True)  # Extended Internal Rate of Return
    absolute_return = db.Column(db.Float, nullable=True)
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Mutual Fund')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_mutual_fund_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_mutual_fund_holdings', foreign_keys=[broker_account_id])
    
    def calculate_totals(self):
        """Calculate total investment and current values"""
        self.total_charges = (self.entry_load or 0) + (self.exit_load or 0) + (self.stamp_duty or 0) + (self.stt or 0) + (self.other_charges or 0)
        self.total_investment = self.amount + self.total_charges
        
        if self.current_nav:
            self.current_value = self.units * self.current_nav
            self.unrealized_pnl = self.current_value - self.total_investment
            if self.total_investment > 0:
                self.unrealized_pnl_percentage = (self.unrealized_pnl / self.total_investment) * 100
                self.absolute_return = self.unrealized_pnl_percentage

class ManualFixedDepositHolding(db.Model):
    """Manual fixed deposit holdings entered by users"""
    __tablename__ = 'manual_fixed_deposit_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Which broker/bank holds this
    
    # Institution Details
    bank_name = db.Column(db.String(100), nullable=False)
    fd_number = db.Column(db.String(50), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    branch_name = db.Column(db.String(100), nullable=True)
    
    # FD Details
    deposit_type = db.Column(db.String(50), nullable=True)  # Regular, Tax Saver, Senior Citizen
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)  # Annual interest rate in percentage
    tenure_months = db.Column(db.Integer, nullable=True)  # Tenure in months
    tenure_days = db.Column(db.Integer, nullable=True)  # Tenure in days
    
    # Dates
    deposit_date = db.Column(db.Date, nullable=False)
    maturity_date = db.Column(db.Date, nullable=False)
    
    # Interest Details
    interest_frequency = db.Column(db.String(20), nullable=True)  # Monthly, Quarterly, Half-Yearly, Annual, Cumulative
    interest_payout = db.Column(db.String(20), nullable=True)  # Payout, Reinvest, Cumulative
    tds_applicable = db.Column(db.Boolean, default=False)
    tds_deducted = db.Column(db.Float, default=0.0)
    
    # Maturity & Current Values
    maturity_amount = db.Column(db.Float, nullable=True)
    interest_earned = db.Column(db.Float, default=0.0)
    current_value = db.Column(db.Float, nullable=True)
    
    # Nomination
    nominee_name = db.Column(db.String(100), nullable=True)
    nominee_relation = db.Column(db.String(50), nullable=True)
    
    # Status & Classification
    status = db.Column(db.String(20), default='Active')  # Active, Matured, Closed
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Fixed Deposit')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_fixed_deposit_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_fixed_deposit_holdings', foreign_keys=[broker_account_id])
    
    def calculate_maturity(self):
        """Calculate maturity amount and interest earned"""
        from datetime import date
        
        # Simple interest calculation
        if self.interest_frequency == 'Cumulative':
            # Compound interest for cumulative deposits
            if self.tenure_months:
                years = self.tenure_months / 12
            elif self.tenure_days:
                years = self.tenure_days / 365
            else:
                years = 0
            
            # A = P(1 + r/n)^(nt) - for quarterly compounding
            n = 4  # Quarterly compounding
            rate = self.interest_rate / 100
            self.maturity_amount = self.principal_amount * ((1 + rate/n) ** (n * years))
        else:
            # Simple interest for regular payouts
            if self.tenure_months:
                time_years = self.tenure_months / 12
            elif self.tenure_days:
                time_years = self.tenure_days / 365
            else:
                time_years = 0
            
            interest = self.principal_amount * (self.interest_rate / 100) * time_years
            self.maturity_amount = self.principal_amount + interest
        
        self.interest_earned = self.maturity_amount - self.principal_amount
        
        # Calculate current value based on days elapsed
        today = date.today()
        if today >= self.maturity_date:
            self.current_value = self.maturity_amount
            self.status = 'Matured'
        else:
            days_elapsed = (today - self.deposit_date).days
            total_days = (self.maturity_date - self.deposit_date).days
            
            if total_days > 0:
                if self.interest_frequency == 'Cumulative':
                    # Pro-rata compound interest
                    years_elapsed = days_elapsed / 365
                    n = 4
                    rate = self.interest_rate / 100
                    self.current_value = self.principal_amount * ((1 + rate/n) ** (n * years_elapsed))
                else:
                    # Pro-rata simple interest
                    time_years = days_elapsed / 365
                    interest_accrued = self.principal_amount * (self.interest_rate / 100) * time_years
                    self.current_value = self.principal_amount + interest_accrued
            else:
                self.current_value = self.principal_amount

class ManualRealEstateHolding(db.Model):
    """Manual real estate holdings entered by users"""
    __tablename__ = 'manual_real_estate_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Property management broker
    
    # Property Details
    property_name = db.Column(db.String(200), nullable=False)
    property_type = db.Column(db.String(50), nullable=True)  # Residential, Commercial, Land, Agricultural
    property_subtype = db.Column(db.String(50), nullable=True)  # Apartment, Villa, Plot, Office, etc.
    
    # Location
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    
    # Property Specifications
    area_sqft = db.Column(db.Float, nullable=True)
    area_unit = db.Column(db.String(20), default='sqft')  # sqft, sqm, acres, etc.
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    
    # Purchase Details
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    stamp_duty = db.Column(db.Float, default=0.0)
    registration_charges = db.Column(db.Float, default=0.0)
    brokerage = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    total_investment = db.Column(db.Float, nullable=False)
    
    # Loan Details
    loan_amount = db.Column(db.Float, default=0.0)
    loan_bank = db.Column(db.String(100), nullable=True)
    loan_account_number = db.Column(db.String(50), nullable=True)
    emi_amount = db.Column(db.Float, default=0.0)
    loan_tenure_months = db.Column(db.Integer, nullable=True)
    
    # Current Valuation
    current_market_value = db.Column(db.Float, nullable=True)
    valuation_date = db.Column(db.Date, nullable=True)
    unrealized_gain = db.Column(db.Float, nullable=True)
    unrealized_gain_percentage = db.Column(db.Float, nullable=True)
    
    # Rental Income
    is_rented = db.Column(db.Boolean, default=False)
    monthly_rent = db.Column(db.Float, default=0.0)
    tenant_name = db.Column(db.String(100), nullable=True)
    lease_start_date = db.Column(db.Date, nullable=True)
    lease_end_date = db.Column(db.Date, nullable=True)
    
    # Recurring Costs
    property_tax_annual = db.Column(db.Float, default=0.0)
    maintenance_monthly = db.Column(db.Float, default=0.0)
    insurance_annual = db.Column(db.Float, default=0.0)
    
    # Legal & Documents
    ownership_type = db.Column(db.String(50), nullable=True)  # Freehold, Leasehold
    deed_number = db.Column(db.String(100), nullable=True)
    survey_number = db.Column(db.String(100), nullable=True)
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Real Estate')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_real_estate_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_real_estate_holdings', foreign_keys=[broker_account_id])
    
    def calculate_values(self):
        """Calculate total investment and unrealized gains"""
        self.total_investment = (
            self.purchase_price + 
            (self.stamp_duty or 0) + 
            (self.registration_charges or 0) + 
            (self.brokerage or 0) + 
            (self.other_charges or 0)
        )
        
        if self.current_market_value:
            self.unrealized_gain = self.current_market_value - self.total_investment
            if self.total_investment > 0:
                self.unrealized_gain_percentage = (self.unrealized_gain / self.total_investment) * 100

class ManualCommodityHolding(db.Model):
    """Manual commodity holdings (Gold, Silver, etc.) entered by users"""
    __tablename__ = 'manual_commodity_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Which broker holds this
    
    # Commodity Details
    commodity_type = db.Column(db.String(50), nullable=False)  # Gold, Silver, Platinum, Palladium, etc.
    commodity_form = db.Column(db.String(50), nullable=True)  # Physical, Digital Gold, ETF, Sovereign Gold Bond
    sub_form = db.Column(db.String(50), nullable=True)  # Coins, Bars, Jewelry, Biscuit
    
    # Item Details
    item_name = db.Column(db.String(200), nullable=True)
    purity = db.Column(db.String(20), nullable=True)  # 24K, 22K, 18K for gold; 999, 925 for silver
    weight_grams = db.Column(db.Float, nullable=True)
    weight_unit = db.Column(db.String(10), default='grams')
    
    # Purchase Details
    purchase_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Float, nullable=True)  # Number of units/pieces
    purchase_rate_per_gram = db.Column(db.Float, nullable=True)
    purchase_amount = db.Column(db.Float, nullable=False)
    making_charges = db.Column(db.Float, default=0.0)  # For jewelry
    gst = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    total_investment = db.Column(db.Float, nullable=False)
    
    # Vendor/Store Details
    vendor_name = db.Column(db.String(100), nullable=True)
    bill_number = db.Column(db.String(50), nullable=True)
    hallmark_number = db.Column(db.String(50), nullable=True)  # For hallmarked jewelry
    
    # Current Valuation
    current_rate_per_gram = db.Column(db.Float, nullable=True)
    current_market_value = db.Column(db.Float, nullable=True)
    valuation_date = db.Column(db.Date, nullable=True)
    unrealized_gain = db.Column(db.Float, nullable=True)
    unrealized_gain_percentage = db.Column(db.Float, nullable=True)
    
    # Storage Details (for physical commodities)
    storage_location = db.Column(db.String(100), nullable=True)  # Bank Locker, Home Safe, etc.
    locker_number = db.Column(db.String(50), nullable=True)
    locker_rent_annual = db.Column(db.Float, default=0.0)
    insurance_annual = db.Column(db.Float, default=0.0)
    
    # Digital Gold Specific
    digital_platform = db.Column(db.String(100), nullable=True)  # Paytm, PhonePe, Google Pay, etc.
    digital_account_id = db.Column(db.String(100), nullable=True)
    
    # Sovereign Gold Bond Specific
    bond_issue_number = db.Column(db.String(50), nullable=True)
    bond_maturity_date = db.Column(db.Date, nullable=True)
    bond_interest_rate = db.Column(db.Float, nullable=True)
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Commodity')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_commodity_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_commodity_holdings', foreign_keys=[broker_account_id])
    
    def calculate_values(self):
        """Calculate total investment and unrealized gains"""
        self.total_investment = (
            self.purchase_amount + 
            (self.making_charges or 0) + 
            (self.gst or 0) + 
            (self.other_charges or 0)
        )
        
        if self.current_market_value:
            self.unrealized_gain = self.current_market_value - self.total_investment
            if self.total_investment > 0:
                self.unrealized_gain_percentage = (self.unrealized_gain / self.total_investment) * 100
        elif self.current_rate_per_gram and self.weight_grams:
            # Calculate current value based on weight and current rate
            self.current_market_value = self.weight_grams * self.current_rate_per_gram
            self.unrealized_gain = self.current_market_value - self.total_investment
            if self.total_investment > 0:
                self.unrealized_gain_percentage = (self.unrealized_gain / self.total_investment) * 100

class ManualCryptocurrencyHolding(db.Model):
    """Manual cryptocurrency holdings entered by users"""
    __tablename__ = 'manual_cryptocurrency_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Which broker/exchange holds this
    
    # Cryptocurrency Details
    crypto_symbol = db.Column(db.String(10), nullable=False)  # BTC, ETH, BNB, etc.
    crypto_name = db.Column(db.String(50), nullable=False)  # Bitcoin, Ethereum, etc.
    
    # Platform/Exchange Details
    platform = db.Column(db.String(100), nullable=True)  # WazirX, CoinDCX, Binance, etc.
    wallet_type = db.Column(db.String(50), nullable=True)  # Exchange, Hardware Wallet, Software Wallet, Cold Storage
    wallet_address = db.Column(db.String(200), nullable=True)
    
    # Purchase Details
    purchase_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # Number of coins/tokens
    purchase_rate_inr = db.Column(db.Float, nullable=False)  # Purchase rate per coin in INR
    purchase_amount = db.Column(db.Float, nullable=False)  # Total purchase amount
    transaction_fee = db.Column(db.Float, default=0.0)
    gas_fee = db.Column(db.Float, default=0.0)  # For ETH and similar
    other_charges = db.Column(db.Float, default=0.0)
    total_investment = db.Column(db.Float, nullable=False)
    
    # Transaction Details
    transaction_id = db.Column(db.String(200), nullable=True)
    transaction_hash = db.Column(db.String(200), nullable=True)
    
    # Current Valuation
    current_rate_inr = db.Column(db.Float, nullable=True)
    current_market_value = db.Column(db.Float, nullable=True)
    valuation_date = db.Column(db.Date, nullable=True)
    unrealized_gain = db.Column(db.Float, nullable=True)
    unrealized_gain_percentage = db.Column(db.Float, nullable=True)
    
    # Staking Details (if applicable)
    is_staked = db.Column(db.Boolean, default=False)
    staking_platform = db.Column(db.String(100), nullable=True)
    staking_apy = db.Column(db.Float, nullable=True)
    staking_rewards_earned = db.Column(db.Float, default=0.0)
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Cryptocurrency')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_cryptocurrency_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_cryptocurrency_holdings', foreign_keys=[broker_account_id])
    
    def calculate_values(self):
        """Calculate total investment and unrealized gains"""
        self.total_investment = (
            self.purchase_amount + 
            (self.transaction_fee or 0) + 
            (self.gas_fee or 0) + 
            (self.other_charges or 0)
        )
        
        if self.current_market_value:
            self.unrealized_gain = self.current_market_value - self.total_investment
            if self.total_investment > 0:
                self.unrealized_gain_percentage = (self.unrealized_gain / self.total_investment) * 100
        elif self.current_rate_inr and self.quantity:
            # Calculate current value based on quantity and current rate
            self.current_market_value = self.quantity * self.current_rate_inr
            self.unrealized_gain = self.current_market_value - self.total_investment
            if self.total_investment > 0:
                self.unrealized_gain_percentage = (self.unrealized_gain / self.total_investment) * 100

class ManualInsuranceHolding(db.Model):
    """Manual insurance policies entered by users"""
    __tablename__ = 'manual_insurance_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Insurance broker/agent
    
    # Policy Details
    insurance_type = db.Column(db.String(50), nullable=False)  # Life, Health, Motor, Term, etc.
    policy_name = db.Column(db.String(200), nullable=False)
    policy_number = db.Column(db.String(100), nullable=False)
    insurance_company = db.Column(db.String(100), nullable=False)
    
    # Policy Holder Details
    policy_holder_name = db.Column(db.String(100), nullable=True)
    insured_person_name = db.Column(db.String(100), nullable=True)
    
    # Coverage Details
    sum_assured = db.Column(db.Float, nullable=False)  # Coverage amount
    policy_term_years = db.Column(db.Integer, nullable=True)
    
    # Premium Details
    premium_amount = db.Column(db.Float, nullable=False)
    premium_frequency = db.Column(db.String(20), nullable=True)  # Monthly, Quarterly, Half-Yearly, Annual
    premium_payment_term_years = db.Column(db.Integer, nullable=True)
    total_premiums_paid = db.Column(db.Float, default=0.0)
    
    # Dates
    policy_start_date = db.Column(db.Date, nullable=False)
    policy_end_date = db.Column(db.Date, nullable=True)
    maturity_date = db.Column(db.Date, nullable=True)
    next_premium_due_date = db.Column(db.Date, nullable=True)
    
    # Maturity & Returns
    maturity_amount = db.Column(db.Float, nullable=True)
    bonus_accumulated = db.Column(db.Float, default=0.0)
    surrender_value = db.Column(db.Float, nullable=True)
    
    # Nominee Details
    nominee_name = db.Column(db.String(100), nullable=True)
    nominee_relation = db.Column(db.String(50), nullable=True)
    
    # Agent Details
    agent_name = db.Column(db.String(100), nullable=True)
    agent_contact = db.Column(db.String(50), nullable=True)
    
    # Status
    policy_status = db.Column(db.String(20), default='Active')  # Active, Lapsed, Matured, Surrendered
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Insurance')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_insurance_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_insurance_holdings', foreign_keys=[broker_account_id])

class ManualBankAccount(db.Model):
    """Manual bank accounts and cash holdings entered by users"""
    __tablename__ = 'manual_bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Account Details
    account_type = db.Column(db.String(50), nullable=False)  # Savings, Current, Cash, Salary
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=True)
    branch_name = db.Column(db.String(100), nullable=True)
    ifsc_code = db.Column(db.String(20), nullable=True)
    
    # Account Holder Details
    account_holder_name = db.Column(db.String(100), nullable=True)
    
    # Balance Details
    current_balance = db.Column(db.Float, nullable=False)
    as_on_date = db.Column(db.Date, nullable=True)
    
    # Interest Details (for Savings accounts)
    interest_rate = db.Column(db.Float, nullable=True)  # Annual interest rate
    interest_earned_ytd = db.Column(db.Float, default=0.0)  # Year to date
    
    # Account Status
    account_status = db.Column(db.String(20), default='Active')  # Active, Closed, Dormant
    account_opening_date = db.Column(db.Date, nullable=True)
    
    # Linked Services
    has_debit_card = db.Column(db.Boolean, default=False)
    has_internet_banking = db.Column(db.Boolean, default=False)
    has_mobile_banking = db.Column(db.Boolean, default=False)
    has_cheque_book = db.Column(db.Boolean, default=False)
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='Cash & Bank')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_bank_accounts')

class ManualFuturesOptionsHolding(db.Model):
    """Manual futures and options holdings entered by users"""
    __tablename__ = 'manual_futures_options_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True, index=True)  # Optional: Which broker holds this position
    
    # Contract Details
    contract_type = db.Column(db.String(20), nullable=False)  # Future, Call Option, Put Option
    underlying_asset = db.Column(db.String(100), nullable=False)  # Stock/Index name
    symbol = db.Column(db.String(50), nullable=True)  # Trading symbol
    
    # Contract Specifications
    strike_price = db.Column(db.Float, nullable=True)  # For options only
    lot_size = db.Column(db.Integer, nullable=False)
    quantity_lots = db.Column(db.Integer, nullable=False)  # Number of lots
    total_quantity = db.Column(db.Integer, nullable=False)  # lot_size * quantity_lots
    
    # Dates
    expiry_date = db.Column(db.Date, nullable=False)
    trade_date = db.Column(db.Date, nullable=False)
    
    # Position Details
    position_type = db.Column(db.String(10), nullable=False)  # Buy/Long or Sell/Short
    entry_price = db.Column(db.Float, nullable=False)
    premium_paid = db.Column(db.Float, default=0.0)  # For options
    
    # Charges
    brokerage = db.Column(db.Float, default=0.0)
    stt = db.Column(db.Float, default=0.0)  # Securities Transaction Tax
    exchange_charges = db.Column(db.Float, default=0.0)
    gst = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    total_charges = db.Column(db.Float, default=0.0)
    
    # Investment & Current Value
    total_investment = db.Column(db.Float, nullable=False)
    current_market_price = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, nullable=True)
    
    # P&L
    unrealized_pnl = db.Column(db.Float, nullable=True)
    unrealized_pnl_percentage = db.Column(db.Float, nullable=True)
    
    # Status
    position_status = db.Column(db.String(20), default='Open')  # Open, Closed, Expired
    exit_price = db.Column(db.Float, nullable=True)
    exit_date = db.Column(db.Date, nullable=True)
    realized_pnl = db.Column(db.Float, nullable=True)
    
    # Portfolio Classification
    portfolio_name = db.Column(db.String(100), default='Default')
    asset_class = db.Column(db.String(50), default='F&O')
    
    # Additional Information
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='manual_futures_options_holdings')
    broker_account = db.relationship('BrokerAccount', backref='manual_futures_options_holdings', foreign_keys=[broker_account_id])
    
    def calculate_values(self):
        """Calculate total investment, charges, and P&L"""
        # Calculate total quantity
        self.total_quantity = self.lot_size * self.quantity_lots
        
        # Calculate total charges
        self.total_charges = (
            (self.brokerage or 0) + 
            (self.stt or 0) + 
            (self.exchange_charges or 0) + 
            (self.gst or 0) + 
            (self.other_charges or 0)
        )
        
        # Calculate total investment
        if self.contract_type == 'Future':
            self.total_investment = (self.entry_price * self.total_quantity) + self.total_charges
        else:  # Options
            self.total_investment = (self.premium_paid * self.total_quantity) + self.total_charges
        
        # Calculate current value and P&L if current price is available
        if self.current_market_price and self.position_status == 'Open':
            if self.contract_type == 'Future':
                self.current_value = self.current_market_price * self.total_quantity
            else:  # Options
                self.current_value = self.current_market_price * self.total_quantity
            
            # Calculate unrealized P&L based on position type
            if self.position_type in ['Buy', 'Long']:
                self.unrealized_pnl = self.current_value - self.total_investment
            else:  # Sell/Short
                self.unrealized_pnl = self.total_investment - self.current_value
            
            if self.total_investment > 0:
                self.unrealized_pnl_percentage = (self.unrealized_pnl / self.total_investment) * 100

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    broker_id = db.Column(db.String(50), nullable=True)  # Temporary - matches current database
    ticker_symbol = db.Column(db.String(20), nullable=False)  # Original length
    stock_name = db.Column(db.String(200), nullable=False)  # Original column name - will be renamed later
    asset_type = db.Column(db.String(50), nullable=True)  # Temporary string type
    asset_category = db.Column(db.String(50), nullable=True)  # Temporary string type
    
    # F&O (Futures & Options) specific fields
    contract_type = db.Column(db.String(20), nullable=True)  # CALL, PUT, FUTURE (for F&O)
    strike_price = db.Column(db.Float, nullable=True)  # Strike price for options
    expiry_date = db.Column(db.Date, nullable=True)  # Expiry date for F&O contracts
    lot_size = db.Column(db.Integer, nullable=True)  # Lot size for F&O
    option_type = db.Column(db.String(20), nullable=True)  # CE, PE for options
    
    # NPS (National Pension System) specific fields
    nps_scheme = db.Column(db.String(100), nullable=True)  # NPS scheme name
    pension_fund_manager = db.Column(db.String(100), nullable=True)  # PFM name
    tier = db.Column(db.String(10), nullable=True)  # NPS Tier - Tier 1 or Tier 2
    
    # Real Estate specific fields
    property_type = db.Column(db.String(50), nullable=True)  # Residential, Commercial, Land
    property_location = db.Column(db.String(200), nullable=True)  # City/Area
    area_sqft = db.Column(db.Float, nullable=True)  # Area of property in square feet
    
    # Fixed Income specific fields (Bonds, FDs, etc.)
    maturity_date = db.Column(db.Date, nullable=True)  # Maturity for bonds/FDs
    interest_rate = db.Column(db.Float, nullable=True)  # Interest rate for fixed income
    coupon_rate = db.Column(db.Float, nullable=True)  # Coupon rate for bonds
    face_value = db.Column(db.Float, nullable=True)  # Face value of bond/FD
    
    # Gold specific fields
    gold_form = db.Column(db.String(50), nullable=True)  # Physical, Digital, ETF, Coins
    gold_purity = db.Column(db.String(20), nullable=True)  # 22K, 24K, etc.
    grams = db.Column(db.Float, nullable=True)  # Weight in grams for physical gold
    quantity = db.Column(db.Float, nullable=False)
    date_purchased = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)  # Price per unit when purchased
    purchased_value = db.Column(db.Float, nullable=False)  # Total purchase value
    current_price = db.Column(db.Float, nullable=True)  # Current market price per unit
    current_value = db.Column(db.Float, nullable=True)  # Current total value
    sector = db.Column(db.String(100), nullable=True)  # IT, Banking, Pharma, etc.
    exchange = db.Column(db.String(10), nullable=True)  # NSE, BSE
    isin = db.Column(db.String(20), nullable=True)  # ISIN code for unique identification
    trade_type = db.Column(db.String(20), nullable=False, default='long_term')  # intraday, short_term, long_term
    data_source = db.Column(db.String(20), nullable=False, default='broker')  # broker, manual_upload, api_sync
    last_sync_date = db.Column(db.DateTime, nullable=True)  # Last time data was synced from broker
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='portfolio_holdings')
    # broker_account = db.relationship('BrokerAccount', backref='portfolio_holdings', foreign_keys=[broker_account_id])  # Temporarily disabled
    
    def get_asset_type_display(self):
        """Get display name for asset type"""
        asset_type_names = {
            "equities": "Equities",
            "mutual_funds": "Mutual Funds", 
            "fixed_income": "Fixed Income",
            "futures_options": "Futures & Options",
            "nps": "National Pension System",
            "real_estate": "Real Estate",
            "gold": "Gold",
            "etf": "ETFs",
            "crypto": "Cryptocurrency",
            "esop": "ESOP",
            "private_equity": "Private Equity"
        }
        return asset_type_names.get(self.asset_type, self.asset_type.title() if self.asset_type else "Unknown")
    
    def get_broker_name(self):
        """Get broker name or 'Manual' if no broker"""
        if self.broker_id:
            return self.broker_id
        return "Manual Entry"
    
    @property
    def pnl_amount(self):
        """Calculate P&L amount"""
        if self.current_value and self.purchased_value:
            return self.current_value - self.purchased_value
        return 0
    
    @property
    def pnl_percentage(self):
        """Calculate P&L percentage"""
        if self.purchased_value and self.purchased_value > 0:
            return ((self.current_value or 0) - self.purchased_value) / self.purchased_value * 100
        return 0
    
    @property
    def allocation_percentage(self):
        """Calculate allocation percentage within user's portfolio"""
        total_value = db.session.query(db.func.sum(Portfolio.current_value)).filter_by(user_id=self.user_id).scalar() or 0
        if total_value > 0 and self.current_value:
            return (self.current_value / total_value) * 100
        return 0
    
    def get_pnl_class(self):
        """Return CSS class for P&L display"""
        pnl = self.pnl_amount
        if pnl > 0:
            return 'text-success'
        elif pnl < 0:
            return 'text-danger'
        return 'text-muted'
    
    # Asset Type Helper Methods
    def is_equity(self):
        """Check if this is an equity asset"""
        return self.asset_type in ['equities', 'esop']
    
    def is_futures_options(self):
        """Check if this is a F&O asset"""
        return self.asset_type == 'futures_options'
    
    def is_fixed_income(self):
        """Check if this is a fixed income asset"""
        return self.asset_type == 'fixed_income'
    
    def is_real_estate(self):
        """Check if this is a real estate asset"""
        return self.asset_type == 'real_estate'
    
    def is_gold(self):
        """Check if this is a gold asset"""
        return self.asset_type == 'gold'
    
    def is_nps(self):
        """Check if this is a NPS asset"""
        return self.asset_type == 'nps'
    
    def get_asset_category_display(self):
        """Get display name for asset category"""
        category_names = {
            "equity": "Equity",
            "debt": "Debt", 
            "commodities": "Commodities",
            "alternative": "Alternative",
            "hybrid": "Hybrid"
        }
        return category_names.get(self.asset_category, self.asset_category.title() if self.asset_category else "Unknown")
    
    def get_asset_specific_info(self):
        """Get asset-specific information as a dictionary"""
        info = {}
        
        if self.is_futures_options():
            info.update({
                'Contract Type': self.contract_type,
                'Strike Price': self.strike_price,
                'Expiry Date': self.expiry_date.strftime('%d-%m-%Y') if self.expiry_date else None,
                'Lot Size': self.lot_size,
                'Option Type': self.option_type
            })
        
        elif self.is_nps():
            info.update({
                'NPS Scheme': self.nps_scheme,
                'Pension Fund Manager': self.pension_fund_manager,
                'Tier': self.tier
            })
        
        elif self.is_real_estate():
            info.update({
                'Property Type': self.property_type,
                'Location': self.property_location,
                'Area (sq ft)': self.area_sqft
            })
        
        elif self.is_fixed_income():
            info.update({
                'Maturity Date': self.maturity_date.strftime('%d-%m-%Y') if self.maturity_date else None,
                'Interest Rate': f"{self.interest_rate}%" if self.interest_rate else None,
                'Coupon Rate': f"{self.coupon_rate}%" if self.coupon_rate else None,
                'Face Value': self.face_value
            })
        
        elif self.is_gold():
            info.update({
                'Gold Form': self.gold_form,
                'Purity': self.gold_purity,
                'Weight (grams)': self.grams
            })
        
        # Remove None values
        return {k: v for k, v in info.items() if v is not None}
    
    def has_expiry(self):
        """Check if this asset has an expiry date"""
        return self.expiry_date is not None
    
    def days_to_expiry(self):
        """Calculate days to expiry for F&O contracts"""
        if self.expiry_date:
            from datetime import date
            return (self.expiry_date - date.today()).days
        return None
    
    def is_expiring_soon(self, days=7):
        """Check if F&O contract is expiring within specified days"""
        days_left = self.days_to_expiry()
        return days_left is not None and days_left <= days
    
    def get_risk_level(self):
        """Get risk level based on asset type"""
        risk_levels = {
            'equities': 'Medium',
            'futures_options': 'High',
            'fixed_income': 'Low',
            'real_estate': 'Medium',
            'gold': 'Low',
            'nps': 'Low',
            'mutual_funds': 'Medium',
            'etf': 'Medium',
            'crypto': 'Very High',
            'esop': 'High',
            'private_equity': 'Very High'
        }
        return risk_levels.get(self.asset_type, 'Unknown')
    
    def validate_required_fields(self):
        """Validate that all required fields for this asset type are present"""
        errors = []
        
        if self.is_futures_options():
            if not self.contract_type:
                errors.append("Contract type is required for F&O assets")
            if not self.expiry_date:
                errors.append("Expiry date is required for F&O assets")
        
        elif self.is_real_estate() and not self.property_type:
            errors.append("Property type is required for real estate assets")
        
        elif self.is_nps() and not self.nps_scheme:
            errors.append("NPS scheme is required for NPS assets")
        
        elif self.is_fixed_income() and not self.maturity_date:
            errors.append("Maturity date is required for fixed income assets")
        
        elif self.is_gold() and not self.gold_form:
            errors.append("Gold form is required for gold assets")
        
        return errors
    
    def __repr__(self):
        return f'<Portfolio {self.ticker_symbol} - {self.quantity} units>'

class RiskProfile(db.Model):
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age_group = db.Column(db.String(20), nullable=False)  # 18-25, 26-35, 36-45, 46-55, 55+
    investment_goal = db.Column(db.String(50), nullable=False)  # wealth_creation, retirement, children_education, etc.
    investment_horizon = db.Column(db.String(20), nullable=False)  # short_term, medium_term, long_term
    risk_tolerance = db.Column(db.String(20), nullable=False)  # conservative, moderate, aggressive
    loss_tolerance = db.Column(db.Integer, nullable=False)  # Percentage willing to lose (5, 10, 15, 20, 25+)
    monthly_income = db.Column(db.String(20), nullable=True)  # <50k, 50k-1L, 1L-2L, 2L-5L, 5L+
    monthly_savings = db.Column(db.String(20), nullable=True)  # <10k, 10k-25k, 25k-50k, 50k+
    investment_experience = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    preferred_sectors = db.Column(db.Text, nullable=True)  # JSON array of preferred sectors
    risk_score = db.Column(db.Integer, nullable=True)  # Calculated risk score 1-100
    risk_category = db.Column(db.String(20), nullable=True)  # Conservative, Balanced, Aggressive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='risk_profile', uselist=False)

class PortfolioAnalysis(db.Model):
    __tablename__ = 'portfolio_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analysis_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    # Portfolio Metrics
    total_portfolio_value = db.Column(db.Float, nullable=False)
    total_invested_amount = db.Column(db.Float, nullable=False)
    total_pnl = db.Column(db.Float, nullable=False)
    total_pnl_percentage = db.Column(db.Float, nullable=False)
    number_of_holdings = db.Column(db.Integer, nullable=False)
    number_of_brokers = db.Column(db.Integer, nullable=False)
    
    # Risk Metrics
    portfolio_volatility = db.Column(db.Float, nullable=True)
    sharpe_ratio = db.Column(db.Float, nullable=True)
    portfolio_beta = db.Column(db.Float, nullable=True)
    max_drawdown = db.Column(db.Float, nullable=True)
    
    # Diversification Analysis
    sector_concentration = db.Column(db.Text, nullable=True)  # JSON: {sector: percentage}
    asset_allocation = db.Column(db.Text, nullable=True)  # JSON: {asset_type: percentage}
    top_holdings = db.Column(db.Text, nullable=True)  # JSON: [{symbol, percentage}]
    
    # Risk Flags
    concentration_risk = db.Column(db.Boolean, default=False)
    under_diversified = db.Column(db.Boolean, default=False)
    high_volatility_warning = db.Column(db.Boolean, default=False)
    sector_over_concentration = db.Column(db.Boolean, default=False)
    
    # AI Recommendations
    ai_health_score = db.Column(db.Integer, nullable=True)  # 1-100
    ai_risk_assessment = db.Column(db.String(20), nullable=True)  # Low, Medium, High
    ai_suggestions = db.Column(db.Text, nullable=True)  # JSON array of suggestions
    rebalance_recommendations = db.Column(db.Text, nullable=True)  # JSON array
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='portfolio_analyses')

class PortfolioRecommendation(db.Model):
    __tablename__ = 'portfolio_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('portfolio_analyses.id'), nullable=False)
    
    recommendation_type = db.Column(db.String(20), nullable=False)  # BUY, SELL, HOLD, REBALANCE
    ticker_symbol = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(200), nullable=False)
    action_priority = db.Column(db.String(10), nullable=False)  # HIGH, MEDIUM, LOW
    recommended_quantity = db.Column(db.Float, nullable=True)
    target_allocation = db.Column(db.Float, nullable=True)  # Percentage
    reasoning = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Integer, nullable=False, default=75)  # 1-100
    
    # Risk-based recommendations
    user_risk_alignment = db.Column(db.Boolean, default=True)
    sector_rebalance = db.Column(db.Boolean, default=False)
    
    is_implemented = db.Column(db.Boolean, default=False)
    implementation_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='portfolio_recommendations')
    analysis = db.relationship('PortfolioAnalysis', backref='recommendations')

class TradingAsset(db.Model):
    __tablename__ = 'trading_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), nullable=False, unique=True)
    company_name = db.Column(db.String(200), nullable=False)
    asset_class = db.Column(db.String(20), nullable=False)  # stocks, options, futures, mutual_funds, crypto
    exchange = db.Column(db.String(10), nullable=False)  # NSE, BSE, MCX
    sector = db.Column(db.String(100), nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    lot_size = db.Column(db.Integer, default=1)  # For futures/options
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TradingStrategy(db.Model):
    __tablename__ = 'trading_strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    strategy_type = db.Column(db.String(50), nullable=False)  # directional, non_directional, arbitrage
    asset_classes = db.Column(db.Text, nullable=False)  # JSON array of supported asset classes
    market_conditions = db.Column(db.Text, nullable=False)  # JSON: bullish, bearish, sideways
    risk_level = db.Column(db.String(10), nullable=False)  # LOW, MEDIUM, HIGH
    min_capital = db.Column(db.Float, nullable=True)
    max_loss_percentage = db.Column(db.Float, nullable=True)
    max_profit_percentage = db.Column(db.Float, nullable=True)
    success_rate = db.Column(db.Float, nullable=True)  # Backtest success rate
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradeRecommendation(db.Model):
    __tablename__ = 'trade_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('trading_assets.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('trading_strategies.id'), nullable=False)
    
    # Trade Parameters
    symbol = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_type = db.Column(db.String(10), nullable=False)  # MARKET, LIMIT
    product_type = db.Column(db.String(10), nullable=False)  # MIS, CNC, NRML
    
    # Options specific
    expiry_date = db.Column(db.Date, nullable=True)
    strike_price = db.Column(db.Float, nullable=True)
    option_type = db.Column(db.String(4), nullable=True)  # CALL, PUT
    
    # Risk Management
    entry_price = db.Column(db.Float, nullable=True)
    target_price = db.Column(db.Float, nullable=True)
    stop_loss = db.Column(db.Float, nullable=True)
    max_loss = db.Column(db.Float, nullable=True)
    max_profit = db.Column(db.Float, nullable=True)
    
    # Market Analysis
    market_direction = db.Column(db.String(10), nullable=False)  # BULLISH, BEARISH, SIDEWAYS
    confidence_score = db.Column(db.Integer, nullable=False, default=75)  # 1-100
    analysis_context = db.Column(db.Text, nullable=True)  # Trading view signals/analysis
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, DEPLOYED, EXECUTED, REJECTED
    recommendation_date = db.Column(db.DateTime, default=datetime.utcnow)
    deployed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='trade_recommendations')
    asset = db.relationship('TradingAsset', backref='recommendations')
    strategy = db.relationship('TradingStrategy', backref='recommendations')

class TradeExecution(db.Model):
    __tablename__ = 'trade_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('trade_recommendations.id'), nullable=False)
    broker_account_id = db.Column(db.Integer, nullable=True)  # Reference to broker account
    
    # Execution Details
    broker_order_id = db.Column(db.String(100), nullable=True)  # Broker's order ID
    execution_status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, FILLED, PARTIAL, REJECTED, CANCELLED
    
    # Order Details
    symbol = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    executed_quantity = db.Column(db.Integer, default=0)
    order_type = db.Column(db.String(10), nullable=False)
    product_type = db.Column(db.String(10), nullable=False)
    
    # Pricing
    order_price = db.Column(db.Float, nullable=True)
    executed_price = db.Column(db.Float, nullable=True)
    brokerage = db.Column(db.Float, nullable=True)
    taxes = db.Column(db.Float, nullable=True)
    total_charges = db.Column(db.Float, nullable=True)
    
    # Timestamps
    order_placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime, nullable=True)
    
    # Error handling
    error_message = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref='trade_executions')
    recommendation = db.relationship('TradeRecommendation', backref='executions')
    # broker_account relationship disabled to avoid dependency issues

class ActiveTrade(db.Model):
    __tablename__ = 'active_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    execution_id = db.Column(db.Integer, db.ForeignKey('trade_executions.id'), nullable=False)
    strategy_name = db.Column(db.String(100), nullable=False)
    
    # Position Details
    symbol = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    
    # P&L Tracking
    unrealized_pnl = db.Column(db.Float, default=0)
    realized_pnl = db.Column(db.Float, default=0)
    
    # Risk Management
    stop_loss = db.Column(db.Float, nullable=True)
    target_price = db.Column(db.Float, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    position_type = db.Column(db.String(5), nullable=False)  # LONG, SHORT
    
    # Timestamps
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='active_trades')
    execution = db.relationship('TradeExecution', backref='active_trade', uselist=False)

class TradeHistory(db.Model):
    __tablename__ = 'trade_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    active_trade_id = db.Column(db.Integer, db.ForeignKey('active_trades.id'), nullable=False)
    
    # Trade Summary
    symbol = db.Column(db.String(50), nullable=False)
    strategy_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=False)
    
    # Performance
    realized_pnl = db.Column(db.Float, nullable=False)
    pnl_percentage = db.Column(db.Float, nullable=False)
    holding_period_hours = db.Column(db.Float, nullable=False)
    
    # Execution Details
    broker_name = db.Column(db.String(50), nullable=False)
    total_charges = db.Column(db.Float, nullable=False)
    net_pnl = db.Column(db.Float, nullable=False)  # After charges
    
    # Result Classification
    trade_result = db.Column(db.String(10), nullable=False)  # WIN, LOSS, BREAKEVEN
    exit_reason = db.Column(db.String(20), nullable=False)  # TARGET, STOPLOSS, MANUAL, EXPIRY
    
    # Timestamps
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='trade_history')
    active_trade = db.relationship('ActiveTrade', backref='history_record', uselist=False)

class MarketAnalysis(db.Model):
    __tablename__ = 'market_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), nullable=False)
    analysis_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    # Market Direction
    trend_direction = db.Column(db.String(10), nullable=False)  # BULLISH, BEARISH, SIDEWAYS
    confidence_level = db.Column(db.Integer, nullable=False)  # 1-100
    
    # Technical Indicators
    ema_signal = db.Column(db.String(10), nullable=True)  # BUY, SELL, HOLD
    rsi_value = db.Column(db.Float, nullable=True)
    macd_signal = db.Column(db.String(10), nullable=True)
    supertrend_signal = db.Column(db.String(10), nullable=True)
    
    # Price Levels
    support_level = db.Column(db.Float, nullable=True)
    resistance_level = db.Column(db.Float, nullable=True)
    pivot_point = db.Column(db.Float, nullable=True)
    
    # Strategy Recommendations
    recommended_strategies = db.Column(db.Text, nullable=True)  # JSON array of strategy IDs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatConversation(db.Model):
    """Chat conversation history for AI Investment Chatbot"""
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # UUID for grouping messages
    title = db.Column(db.String(200), nullable=True)  # Auto-generated conversation title
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='chat_conversations')
    messages = db.relationship('ChatMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_recent_messages(self, limit=10):
        """Get recent messages in chronological order"""
        # Query messages directly to avoid SQLAlchemy relationship issues
        from sqlalchemy.orm import Session
        messages = ChatMessage.query.filter_by(conversation_id=self.id).order_by(ChatMessage.created_at.asc()).limit(limit).all()
        return messages
    
    def __repr__(self):
        return f'<ChatConversation {self.session_id} - {self.title}>'


class ChatMessage(db.Model):
    """Individual chat messages in conversations"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    context_data = db.Column(db.Text, nullable=True)  # JSON data for portfolio/stock context
    tokens_used = db.Column(db.Integer, nullable=True)  # OpenAI token usage tracking
    processing_time = db.Column(db.Float, nullable=True)  # Response time in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    
    def get_context_json(self):
        """Parse context data as JSON"""
        if self.context_data:
            try:
                import json
                return json.loads(self.context_data)
            except:
                return {}
        return {}
    
    def set_context_json(self, data):
        """Set context data as JSON string"""
        if data:
            import json
            self.context_data = json.dumps(data)
    
    def __repr__(self):
        return f'<ChatMessage {self.message_type}: {self.content[:50]}...>'


class ChatbotKnowledgeBase(db.Model):
    """Knowledge base for chatbot learning and context"""
    __tablename__ = 'chatbot_knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # investment_basics, market_terms, etc.
    topic = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=True)  # Comma-separated search keywords
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_keywords_list(self):
        """Get keywords as list"""
        if self.keywords:
            return [kw.strip().lower() for kw in self.keywords.split(',')]
        return []
    
    def __repr__(self):
        return f'<Knowledge {self.category}: {self.topic}>'


# Legacy Trading Models completely removed to avoid schema conflicts


class DailyTradingSignal(db.Model):
    __tablename__ = 'daily_trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_date = db.Column(db.Date, nullable=False)
    signal_type = db.Column(db.String(20), nullable=False)  # Stocks, Options, Futures
    symbol = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # BUY, SELL, HOLD
    entry_price = db.Column(db.Float, nullable=True)
    target_price = db.Column(db.Float, nullable=True)
    stop_loss = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    strategy = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=True)  # 0-100
    risk_level = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    time_frame = db.Column(db.String(20), nullable=True)  # Intraday, Short Term, Long Term
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)




# Admin Models for Trading Signal Management
class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    active = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


# Enhanced Trading Signal Model
class TradingSignal(db.Model):
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_type = db.Column(db.String(20), nullable=False)  # 'stock', 'strategy', 'index_future', 'option'
    symbol = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    action = db.Column(db.String(10), nullable=False)  # 'BUY', 'SELL', 'HOLD'
    entry_price = db.Column(db.Numeric(10, 2), nullable=True)
    target_price = db.Column(db.Numeric(10, 2), nullable=True)
    stop_loss = db.Column(db.Numeric(10, 2), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(10), nullable=True)  # 'LOW', 'MEDIUM', 'HIGH'
    time_frame = db.Column(db.String(20), nullable=True)  # 'INTRADAY', 'SWING', 'POSITIONAL'
    strategy_name = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='ACTIVE')  # 'ACTIVE', 'EXPIRED', 'ACHIEVED', 'STOPPED'
    
    # Filtering and categorization
    sector = db.Column(db.String(100), nullable=True)  # 'Technology', 'Banking', 'Pharma', etc.
    category = db.Column(db.String(50), nullable=True)  # 'Large Cap', 'Mid Cap', 'Small Cap'
    
    # Admin who created the signal
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # WhatsApp/Telegram sharing
    shared_whatsapp = db.Column(db.Boolean, default=False)
    shared_telegram = db.Column(db.Boolean, default=False)
    whatsapp_shared_at = db.Column(db.DateTime, nullable=True)
    telegram_shared_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    admin = db.relationship('Admin', backref='trading_signals')
    
    @property
    def potential_return(self):
        """Calculate potential return percentage"""
        if self.entry_price and self.target_price:
            return ((float(self.target_price) - float(self.entry_price)) / float(self.entry_price)) * 100
        return 0
    
    @property
    def risk_amount(self):
        """Calculate risk amount per share"""
        if self.entry_price and self.stop_loss:
            return float(self.entry_price) - float(self.stop_loss)
        return 0
    
    @property
    def is_expired(self):
        """Check if signal is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


# Enhanced Broker Management - Update existing UserBroker model
# Note: We'll modify the existing UserBroker to add primary broker functionality
# Add these fields to the existing UserBroker model:
# - is_primary = db.Column(db.Boolean, default=False)
# - connection_status = db.Column(db.String(20), default='DISCONNECTED')

# Trade Execution Models
class ExecutedTrade(db.Model):
    __tablename__ = 'executed_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trading_signal_id = db.Column(db.Integer, db.ForeignKey('trading_signals.id'), nullable=False)
    broker_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=False)
    
    # Trade details
    symbol = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'BUY', 'SELL'
    quantity = db.Column(db.Integer, nullable=False)
    executed_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Broker order details
    broker_order_id = db.Column(db.String(100), nullable=True)
    order_status = db.Column(db.String(20), default='PENDING')  # 'PENDING', 'EXECUTED', 'CANCELLED', 'REJECTED'
    
    # P&L tracking
    current_price = db.Column(db.Numeric(10, 2), nullable=True)
    unrealized_pnl = db.Column(db.Numeric(10, 2), default=0.0)
    realized_pnl = db.Column(db.Numeric(10, 2), default=0.0)
    
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='executed_trades')
    trading_signal = db.relationship('TradingSignal', backref='executions')
    broker = db.relationship('BrokerAccount', backref='executed_trades')
    
    @property
    def current_value(self):
        """Calculate current value of the position"""
        if self.current_price:
            return float(self.current_price) * self.quantity
        return float(self.executed_price) * self.quantity


# Payment Tracking for Admin Dashboard
class UserPayment(db.Model):
    __tablename__ = 'user_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='INR')
    plan = db.Column(db.String(20), nullable=False)  # 'TARGET_PLUS', 'TARGET_PRO', 'HNI'
    payment_method = db.Column(db.String(50), nullable=True)
    
    # Razorpay details
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    razorpay_signature = db.Column(db.String(200), nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='PENDING')  # 'PENDING', 'COMPLETED', 'FAILED', 'REFUNDED'
    
    # Subscription details
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='user_payments')
    
    @property
    def is_active_subscription(self):
        """Check if subscription is currently active"""
        if self.subscription_start and self.subscription_end:
            now = datetime.utcnow()
            return self.subscription_start <= now <= self.subscription_end
        return False


# ============================================================================
# RAG System and Research Assistant Models
# ============================================================================

class ResearchConversation(db.Model):
    """Stores research chat conversations for each user"""
    __tablename__ = 'research_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)  # Auto-generated from first query
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='research_conversations')
    messages = db.relationship('ResearchMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ResearchConversation {self.id} - {self.title}>'


class ResearchMessage(db.Model):
    """Individual messages in research conversations"""
    __tablename__ = 'research_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('research_conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Context used for this response
    portfolio_context = db.Column(db.JSON, nullable=True)  # Snapshot of user portfolio at query time
    market_context = db.Column(db.JSON, nullable=True)  # Market data at query time
    
    # Related citations
    citations = db.relationship('SourceCitation', backref='message', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ResearchMessage {self.id} - {self.role}>'


class VectorDocument(db.Model):
    """Stores documents and their vector embeddings for RAG"""
    __tablename__ = 'vector_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(50), nullable=False)  # 'stock_data', 'news', 'earnings', 'user_note'
    symbol = db.Column(db.String(50), nullable=True)  # Stock symbol if applicable
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Embedding (1536 dimensions for OpenAI embeddings)
    embedding = db.Column(db.String, nullable=True)  # Store as JSONB or use pgvector type
    
    # Metadata
    source_url = db.Column(db.String(500), nullable=True)
    published_date = db.Column(db.DateTime, nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    
    # User-specific documents
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NULL for public docs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='vector_documents')
    
    def __repr__(self):
        return f'<VectorDocument {self.id} - {self.title}>'


class SourceCitation(db.Model):
    """Tracks sources cited in research responses"""
    __tablename__ = 'source_citations'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('research_messages.id'), nullable=False)
    vector_doc_id = db.Column(db.Integer, db.ForeignKey('vector_documents.id'), nullable=True)
    
    # Citation details
    source_type = db.Column(db.String(50), nullable=False)  # 'document', 'web', 'api'
    source_title = db.Column(db.String(300), nullable=False)
    source_url = db.Column(db.String(500), nullable=True)
    relevance_score = db.Column(db.Numeric(5, 4), nullable=True)  # Similarity score from vector search
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vector_document = db.relationship('VectorDocument', backref='citations')
    
    def __repr__(self):
        return f'<SourceCitation {self.id} - {self.source_title}>'


class SignalPerformance(db.Model):
    """Tracks performance of trading signals for accuracy metrics"""
    __tablename__ = 'signal_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    trading_signal_id = db.Column(db.Integer, db.ForeignKey('trading_signals.id'), nullable=False)
    
    # Outcome tracking
    outcome = db.Column(db.String(20), nullable=True)  # 'TARGET_HIT', 'STOP_LOSS_HIT', 'EXPIRED', 'MANUAL_EXIT'
    actual_exit_price = db.Column(db.Numeric(10, 2), nullable=True)
    actual_return_pct = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Performance metrics
    max_price_reached = db.Column(db.Numeric(10, 2), nullable=True)
    min_price_reached = db.Column(db.Numeric(10, 2), nullable=True)
    days_active = db.Column(db.Integer, nullable=True)
    
    # User feedback
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    user_feedback = db.Column(db.Text, nullable=True)
    
    outcome_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trading_signal = db.relationship('TradingSignal', backref='performance')
    
    @property
    def is_successful(self):
        """Check if signal was successful"""
        return self.outcome in ['TARGET_HIT', 'MANUAL_EXIT'] and self.actual_return_pct and self.actual_return_pct > 0
    
    def __repr__(self):
        return f'<SignalPerformance {self.id} - {self.outcome}>'


