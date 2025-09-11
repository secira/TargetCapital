"""
Production configuration management
Enhanced security, performance, and monitoring settings
"""
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ProductionConfig:
    """Production-ready configuration manager"""
    
    @staticmethod
    def validate_environment() -> Dict[str, Any]:
        """Validate all required environment variables for production"""
        required_vars = [
            'DATABASE_URL',
            'SESSION_SECRET',
            'REDIS_URL'  # Required for rate limiting in production
        ]
        
        # Conditionally required vars (require either OpenAI or Perplexity)
        ai_keys = ['OPENAI_API_KEY', 'PERPLEXITY_API_KEY']
        has_ai_key = any(os.environ.get(key) for key in ai_keys)
        
        optional_vars = [
            'SENDGRID_API_KEY',
            'RAZORPAY_KEY_ID',
            'RAZORPAY_KEY_SECRET'
        ]
        
        missing_vars = []
        warnings = []
        
        # Check required variables
        for var in required_vars:
            value = os.environ.get(var)
            if not value:
                missing_vars.append(var)
            elif var == 'SESSION_SECRET' and value == 'dev-secret-key-change-in-production':
                missing_vars.append(f"{var} (using development default)")
        
        # Check AI key requirement
        if not has_ai_key:
            missing_vars.append("AI_API_KEY (need either OPENAI_API_KEY or PERPLEXITY_API_KEY)")
        
        # Check optional variables
        for var in optional_vars:
            if not os.environ.get(var):
                warnings.append(f"Optional: {var} not set - some features may be limited")
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise EnvironmentError(error_msg)
        
        if warnings:
            for warning in warnings:
                logger.warning(warning)
        
        logger.info("✅ All required environment variables validated")
        return {
            'status': 'valid',
            'warnings': warnings,
            'checked_vars': len(required_vars) + len(optional_vars)
        }
    
    @staticmethod
    def get_logging_config(environment: str = 'production') -> Dict[str, Any]:
        """Get structured logging configuration"""
        if environment == 'production':
            level = logging.INFO
            format_string = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        else:
            level = logging.DEBUG
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': format_string,
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'simple': {
                    'format': '%(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': level,
                    'formatter': 'detailed',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': logging.WARNING,
                    'formatter': 'detailed',
                    'filename': 'logs/application.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                }
            },
            'loggers': {
                '': {  # root logger
                    'level': level,
                    'handlers': ['console', 'file'],
                    'propagate': False
                },
                'sqlalchemy.engine': {
                    'level': logging.WARNING,
                    'handlers': ['console'],
                    'propagate': False
                },
                'celery': {
                    'level': logging.INFO,
                    'handlers': ['console', 'file'],
                    'propagate': False
                }
            }
        }
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for production"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=self',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
        }
    
    @staticmethod
    def get_database_config() -> Dict[str, Any]:
        """Get production database configuration"""
        return {
            'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
            'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
            'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
            'pool_pre_ping': True,
            'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
            'echo': os.environ.get('DB_ECHO', 'false').lower() == 'true'
        }
    
    @staticmethod
    def get_rate_limit_config() -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            'global_limits': [
                "1000 per hour",
                "200 per minute"
            ],
            'api_limits': {
                'login': "5 per minute",
                'register': "3 per minute", 
                'password_reset': "2 per minute",
                'broker_api': "100 per minute",
                'market_data': "500 per minute"
            },
            'storage_uri': os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
        }
    
    @staticmethod
    def setup_production_monitoring():
        """Set up production monitoring and health checks"""
        import psutil
        
        # System resource monitoring
        def get_system_stats():
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'active_connections': len(psutil.net_connections())
            }
        
        # Database connection monitoring
        def check_database_health():
            try:
                from app import db
                db.session.execute('SELECT 1')
                return {'status': 'healthy', 'response_time_ms': 0}
            except Exception as e:
                return {'status': 'unhealthy', 'error': str(e)}
        
        # Redis monitoring
        def check_redis_health():
            try:
                from caching.redis_cache import cache
                if cache.is_available():
                    return {'status': 'healthy'}
                else:
                    return {'status': 'unhealthy', 'error': 'Connection failed'}
            except Exception as e:
                return {'status': 'unhealthy', 'error': str(e)}
        
        return {
            'system_stats': get_system_stats,
            'database_health': check_database_health,
            'redis_health': check_redis_health
        }

# Application startup validation
def validate_production_setup():
    """Validate production setup on application start"""
    try:
        environment = os.environ.get('ENVIRONMENT', 'development')
        
        if environment == 'production':
            logger.info("🚀 Starting production validation...")
            
            # Validate environment variables
            ProductionConfig.validate_environment()
            
            # Check system resources
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 1:
                logger.warning(f"⚠️ Low memory detected: {memory_gb:.1f}GB")
            
            # Validate database connection
            try:
                from app import db
                with db.engine.connect() as conn:
                    conn.execute('SELECT 1')
                logger.info("✅ Database connection validated")
            except Exception as e:
                logger.error(f"❌ Database validation failed: {e}")
                raise
            
            # Validate Redis connection  
            try:
                from caching.redis_cache import cache
                if cache.is_available():
                    logger.info("✅ Redis cache connection validated")
                else:
                    logger.warning("⚠️ Redis cache not available - some features may be limited")
            except Exception as e:
                logger.warning(f"⚠️ Redis validation warning: {e}")
            
            logger.info("🎯 Production validation completed successfully")
        
        else:
            logger.info(f"🔧 Running in {environment} mode")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Production validation failed: {e}")
        if environment == 'production':
            raise  # Fail fast in production
        return False