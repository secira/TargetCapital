import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
# Use secure environment configuration
try:
    from security.environment_config import setup_secure_environment
    secure_config = setup_secure_environment()
    app.secret_key = secure_config["session_secret"]
    logging.info("✅ Secure environment configuration loaded")
except ImportError:
    # Fallback for development without security module
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    if app.secret_key == "dev-secret-key-change-in-production":
        logging.warning("⚠️ Using default development secret key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database with enhanced security and connection pooling
try:
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
            "application_name": "tCapital-Flask"
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
        "pool_recycle": 300,
        "pool_pre_ping": True,
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
login_manager.login_view = 'login'
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

# Import routes
import routes
