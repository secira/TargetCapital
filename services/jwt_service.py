import os
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from app import db

logger = logging.getLogger(__name__)

class JWTService:
    """JWT authentication service for mobile apps"""
    
    def __init__(self):
        self.secret_key = os.environ.get('SESSION_SECRET')
        if not self.secret_key:
            environment = os.environ.get('ENVIRONMENT', 'development')
            if environment == 'production':
                raise ValueError("SESSION_SECRET is required for JWT authentication in production")
            logger.warning("⚠️ SESSION_SECRET not set - JWT authentication will fail")
            self.secret_key = 'INSECURE-DEV-ONLY-KEY'
        self.algorithm = 'HS256'
        self.access_token_expiry = timedelta(hours=24)
        self.refresh_token_expiry = timedelta(days=30)
    
    def generate_access_token(self, user_id, tenant_id='live'):
        """Generate a short-lived access token"""
        payload = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'type': 'access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + self.access_token_expiry
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def generate_refresh_token(self, user_id, tenant_id='live'):
        """Generate a long-lived refresh token"""
        payload = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + self.refresh_token_expiry
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def generate_tokens(self, user_id, tenant_id='live'):
        """Generate both access and refresh tokens"""
        return {
            'access_token': self.generate_access_token(user_id, tenant_id),
            'refresh_token': self.generate_refresh_token(user_id, tenant_id),
            'token_type': 'Bearer',
            'expires_in': int(self.access_token_expiry.total_seconds())
        }
    
    def verify_token(self, token, token_type='access'):
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != token_type:
                return None, f'Invalid token type. Expected {token_type}'
            
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Token has expired'
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None, 'Invalid token'
    
    def get_token_from_header(self):
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        return None
    
    def refresh_access_token(self, refresh_token):
        """Generate a new access token using a refresh token"""
        payload, error = self.verify_token(refresh_token, 'refresh')
        
        if error:
            return None, error
        
        user_id = payload.get('user_id')
        tenant_id = payload.get('tenant_id', 'live')
        
        return {
            'access_token': self.generate_access_token(user_id, tenant_id),
            'token_type': 'Bearer',
            'expires_in': int(self.access_token_expiry.total_seconds())
        }, None

jwt_service = JWTService()

def jwt_required(f):
    """Decorator to require JWT authentication for mobile API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = jwt_service.get_token_from_header()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authorization header missing or invalid',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        payload, error = jwt_service.verify_token(token, 'access')
        
        if error:
            return jsonify({
                'success': False,
                'error': error,
                'code': 'INVALID_TOKEN'
            }), 401
        
        from models import User
        user = User.query.get(payload.get('user_id'))
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'code': 'USER_NOT_FOUND'
            }), 401
        
        g.current_user = user
        g.tenant_id = payload.get('tenant_id', 'live')
        
        return f(*args, **kwargs)
    
    return decorated_function

def jwt_optional(f):
    """Decorator for optional JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = jwt_service.get_token_from_header()
        
        if token:
            payload, error = jwt_service.verify_token(token, 'access')
            
            if not error:
                from models import User
                user = User.query.get(payload.get('user_id'))
                g.current_user = user
                g.tenant_id = payload.get('tenant_id', 'live')
            else:
                g.current_user = None
                g.tenant_id = 'live'
        else:
            g.current_user = None
            g.tenant_id = 'live'
        
        return f(*args, **kwargs)
    
    return decorated_function
