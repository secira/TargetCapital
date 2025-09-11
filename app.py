import os
import logging
from flask import Flask, g
from flask.helpers import send_from_directory
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Configure structured logging with production configuration
def setup_logging():
    """Setup structured logging based on environment"""
    environment = os.environ.get("ENVIRONMENT", "development")
    
    try:
        from config.production_config import ProductionConfig
        from logging.config import dictConfig
        
        logging_config = ProductionConfig.get_logging_config(environment)
        dictConfig(logging_config)
        logging.info("✅ Structured logging configured successfully")
    except ImportError:
        # Fallback to basic logging if production config not available
        log_level = logging.INFO if environment == "production" else logging.DEBUG
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.warning("⚠️ Using fallback logging configuration")

setup_logging()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)

# Initialize Flask-Compress for production-grade compression
compress = Compress(app)
# Use secure environment configuration
secure_config = None
try:
    from security.environment_config import setup_secure_environment
    secure_config = setup_secure_environment()
    app.secret_key = secure_config["session_secret"]
    logging.info("✅ Secure environment configuration loaded")
except ImportError:
    # Fallback for development without security module
    session_secret = os.environ.get("SESSION_SECRET")
    if not session_secret:
        # Fail-fast in production
        environment = os.environ.get("ENVIRONMENT", "development")
        if environment == "production":
            raise ValueError("SESSION_SECRET is required in production environment")
        session_secret = "dev-secret-key-change-in-production"
        logging.warning("⚠️ Using default development secret key")
    elif session_secret == "dev-secret-key-change-in-production" and os.environ.get("ENVIRONMENT") == "production":
        raise ValueError("Default development secret cannot be used in production")
    app.secret_key = session_secret
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1)  # x_for=1 for accurate client IP behind proxies

# Initialize security extensions
csrf = CSRFProtect(app)

# Configure secure session settings
environment = os.environ.get("ENVIRONMENT", "development")
is_production = environment == "production"

# Initialize rate limiter (require Redis in production)
redis_url = os.environ.get("REDIS_URL")
if is_production and not redis_url:
    raise ValueError("REDIS_URL is required for rate limiting in production")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["300 per minute"],
    storage_uri=redis_url or "memory://"
)

if secure_config and "security_settings" in secure_config:
    security_settings = secure_config["security_settings"]
    app.config['SESSION_COOKIE_SECURE'] = security_settings.get('session_cookie_secure', is_production)
    app.config['SESSION_COOKIE_HTTPONLY'] = security_settings.get('session_cookie_httponly', True)
    app.config['SESSION_COOKIE_SAMESITE'] = security_settings.get('session_cookie_samesite', 'Lax')  # Lax for OAuth compatibility
else:
    # Fallback secure configuration
    app.config['SESSION_COOKIE_SECURE'] = is_production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Lax for OAuth compatibility

# Initialize security headers with Talisman
if is_production:
    csp_policy = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://kit.fontawesome.com',
        ],
        'style-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            'https://fonts.googleapis.com',
            'https://kit.fontawesome.com',
        ],
        'font-src': [
            "'self'",
            'https://fonts.gstatic.com',
            'https://ka-f.fontawesome.com',
        ],
        'img-src': [
            "'self'",
            'data:',
            'https:',
        ],
        'connect-src': [
            "'self'",
            'wss:',  # Only secure WebSocket in production
        ],
        'frame-ancestors': "'none'",
    }
    
    Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        content_security_policy=csp_policy,
        content_security_policy_nonce_in=['script-src'],
        referrer_policy='strict-origin-when-cross-origin',
        feature_policy={
            'camera': "'none'",
            'microphone': "'none'",
            'geolocation': "'self'",
        }
    )
else:
    # Development mode - minimal Talisman
    Talisman(
        app,
        force_https=False,
        strict_transport_security=False,
        content_security_policy=False
    )

# Configure the database with enhanced security and connection pooling
try:
    if secure_config is None:
        raise KeyError("secure_config is None")
    database_config = secure_config["database_config"]
    database_url = database_config["url"]
    
    # Fix SSL issues for PostgreSQL
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
        if 'sslmode=' not in database_url:
            database_url += '&sslmode=require' if '?' in database_url else '?sslmode=require'
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": database_config["pool_size"],
        "max_overflow": database_config["max_overflow"],
        "pool_recycle": database_config["pool_recycle"],
        "pool_pre_ping": True,
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 10,
            "application_name": "Target-Capital-Flask"
        } if database_url.startswith('postgresql+psycopg2://') else {}
    }
    
    logging.info("✅ Enhanced database configuration loaded")
    
except (NameError, KeyError):
    # Fallback configuration
    database_url = os.environ.get("DATABASE_URL", "sqlite:///stock_trading.db")
    
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
        if 'sslmode=' not in database_url:
            database_url += '&sslmode=require' if '?' in database_url else '?sslmode=require'
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,  # Optimize connection pool size
        "max_overflow": 20,  # Allow overflow connections
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 30,  # Connection timeout
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 10
        } if database_url.startswith('postgresql+psycopg2://') else {}
    }
    
    logging.warning("⚠️ Using fallback database configuration")

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models
    import models
    import models_broker  # Import broker models too
    db.create_all()

# Import OAuth blueprints and register them
from oauth_auth import google_bp, facebook_bp
app.register_blueprint(google_bp, url_prefix="/auth")
app.register_blueprint(facebook_bp, url_prefix="/auth")

# Register admin blueprint (import after routes to avoid conflicts)
try:
    from admin_routes import admin_bp
    app.register_blueprint(admin_bp)
except ImportError as e:
    logging.warning(f"Admin blueprint not available: {e}")

# Register WebSocket API routes
try:
    from routes_websocket import register_websocket_apis
    register_websocket_apis(app)
except ImportError as e:
    logging.warning(f"WebSocket API routes not available: {e}")

# Performance optimizations - Caching and security headers
@app.after_request
def enable_caching_and_security(response):
    """Enable aggressive caching and security headers"""
    
    # Aggressive caching for static assets
    if request.endpoint == 'static':
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'  # 1 year
    
    # Security headers for all responses  
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

# Import request for the after_request function
from flask import request

# Import routes
import routes
