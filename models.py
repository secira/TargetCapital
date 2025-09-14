from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
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
    TRADER = "trader"
    TRADER_PLUS = "trader_plus"
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
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
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
        
        # Trader users can access Trade Now but have limited broker features
        elif self.pricing_plan == PricingPlan.TRADER:
            return menu_item not in []  # Trader can access all menus now
        
        # Trader Plus and HNI users can access everything
        elif self.pricing_plan in [PricingPlan.TRADER_PLUS, PricingPlan.HNI]:
            return True
            
        return False
    
    def get_plan_display_name(self):
        """Get human-readable plan name"""
        plan_names = {
            PricingPlan.FREE: "Free User",
            PricingPlan.TRADER: "Trader",
            PricingPlan.TRADER_PLUS: "Trader Plus",
            PricingPlan.HNI: "HNI Account"
        }
        return plan_names.get(self.pricing_plan, "Unknown")
    
    def get_plan_price(self):
        """Get monthly price for the current plan"""
        prices = {
            PricingPlan.FREE: 0,
            PricingPlan.TRADER: 1999,
            PricingPlan.TRADER_PLUS: 2999,
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

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    broker_account_id = db.Column(db.Integer, db.ForeignKey('user_brokers.id'), nullable=True)  # Proper foreign key to BrokerAccount
    ticker_symbol = db.Column(db.String(50), nullable=False)  # Increased length for longer symbols like F&O
    asset_name = db.Column(db.String(200), nullable=False)  # Renamed from stock_name for clarity
    asset_type = db.Column(db.Enum(AssetType), nullable=False)  # Using enum for asset types
    asset_category = db.Column(db.Enum(AssetCategory), nullable=True)  # Using enum for categories
    
    # F&O specific fields
    contract_type = db.Column(db.String(20), nullable=True)  # CALL, PUT, FUTURE (for F&O)
    strike_price = db.Column(db.Float, nullable=True)  # Strike price for options
    expiry_date = db.Column(db.Date, nullable=True)  # Expiry date for F&O contracts
    lot_size = db.Column(db.Integer, nullable=True)  # Lot size for F&O
    
    # NPS specific fields
    nps_scheme = db.Column(db.String(100), nullable=True)  # NPS scheme name
    pension_fund_manager = db.Column(db.String(100), nullable=True)  # PFM name
    
    # Real Estate specific fields
    property_type = db.Column(db.String(50), nullable=True)  # Residential, Commercial, Land
    property_location = db.Column(db.String(200), nullable=True)  # City/Area
    
    # Fixed Income specific fields
    maturity_date = db.Column(db.Date, nullable=True)  # Maturity for bonds/FDs
    interest_rate = db.Column(db.Float, nullable=True)  # Interest rate for fixed income
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
    broker_account = db.relationship('BrokerAccount', backref='portfolio_holdings', foreign_keys=[broker_account_id])
    
    def get_asset_type_display(self):
        """Get display name for asset type"""
        asset_type_names = {
            AssetType.EQUITIES: "Equities",
            AssetType.MUTUAL_FUNDS: "Mutual Funds", 
            AssetType.FIXED_INCOME: "Fixed Income",
            AssetType.FUTURES_OPTIONS: "Futures & Options",
            AssetType.NPS: "National Pension System",
            AssetType.REAL_ESTATE: "Real Estate",
            AssetType.GOLD: "Gold",
            AssetType.ETF: "ETFs",
            AssetType.CRYPTO: "Cryptocurrency",
            AssetType.ESOP: "ESOP",
            AssetType.PRIVATE_EQUITY: "Private Equity"
        }
        return asset_type_names.get(self.asset_type, str(self.asset_type.value))
    
    def get_broker_name(self):
        """Get broker name or 'Manual' if no broker"""
        if self.broker_account:
            return self.broker_account.broker_name
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


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")


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
    plan = db.Column(db.String(20), nullable=False)  # 'TRADER', 'TRADER_PLUS', 'HNI'
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


