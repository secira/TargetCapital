"""
Comprehensive Input Validation and Sanitization
Implements security measures against common attacks
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, validator, ValidationError
from fastapi import HTTPException
import bleach

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Comprehensive input validation and sanitization"""
    
    # Dangerous patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\b(or|and)\s+\w+\s*=\s*\w+)",
        r"(\b(or|and)\s+1\s*=\s*1)"
    ]
    
    XSS_PATTERNS = [
        r"<\s*script[^>]*>.*?<\s*\/\s*script\s*>",
        r"javascript:",
        r"on\w+\s*=",
        r"<\s*iframe[^>]*>",
        r"<\s*object[^>]*>",
        r"<\s*embed[^>]*>"
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$()]",
        r"\b(cat|ls|pwd|whoami|id|uname|netstat|ps|top|kill|rm|mv|cp|chmod|chown)\b"
    ]
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Limit length
        if len(text) > max_length:
            raise ValueError(f"Input too long. Maximum {max_length} characters allowed")
        
        # HTML escape
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Check for dangerous patterns
        SecurityValidator._check_dangerous_patterns(text)
        
        return text.strip()
    
    @staticmethod
    def sanitize_html(html_content: str, allowed_tags: Optional[List[str]] = None) -> str:
        """Sanitize HTML content"""
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
        
        return bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes={},
            strip=True
        )
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        email = email.strip().lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        if len(email) > 254:  # RFC 5321 limit
            raise ValueError("Email address too long")
        
        return email
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate phone number"""
        # Remove all non-digit characters
        phone_digits = re.sub(r'\D', '', phone)
        
        # Check length (assuming international format)
        if len(phone_digits) < 10 or len(phone_digits) > 15:
            raise ValueError("Invalid phone number length")
        
        return phone_digits
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> str:
        """Validate stock symbol"""
        symbol = symbol.upper().strip()
        
        # Basic format validation
        if not re.match(r'^[A-Z0-9&.-]{1,20}$', symbol):
            raise ValueError("Invalid stock symbol format")
        
        return symbol
    
    @staticmethod
    def validate_numeric(value: Union[str, int, float], 
                         min_value: Optional[float] = None,
                         max_value: Optional[float] = None,
                         decimal_places: Optional[int] = None) -> float:
        """Validate numeric input"""
        try:
            if isinstance(value, str):
                # Remove spaces and convert
                value = value.strip()
                if decimal_places is not None:
                    numeric_value = float(Decimal(value).quantize(Decimal('0.' + '0' * decimal_places)))
                else:
                    numeric_value = float(value)
            else:
                numeric_value = float(value)
                
        except (ValueError, InvalidOperation):
            raise ValueError("Invalid numeric value")
        
        # Range validation
        if min_value is not None and numeric_value < min_value:
            raise ValueError(f"Value must be at least {min_value}")
        
        if max_value is not None and numeric_value > max_value:
            raise ValueError(f"Value must not exceed {max_value}")
        
        return numeric_value
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> tuple:
        """Validate date range"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        if start > end:
            raise ValueError("Start date must be before end date")
        
        if start < date(2000, 1, 1):
            raise ValueError("Start date cannot be before 2000-01-01")
        
        if end > date.today():
            raise ValueError("End date cannot be in the future")
        
        return start, end
    
    @staticmethod
    def _check_dangerous_patterns(text: str):
        """Check for dangerous patterns in input"""
        text_lower = text.lower()
        
        # SQL Injection
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential SQL injection attempt: {pattern}")
                raise ValueError("Invalid input detected")
        
        # XSS
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential XSS attempt: {pattern}")
                raise ValueError("Invalid input detected")
        
        # Command Injection
        for pattern in SecurityValidator.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential command injection attempt: {pattern}")
                raise ValueError("Invalid input detected")

# Pydantic validators for common use cases
class SecureBaseModel(BaseModel):
    """Base model with security validations"""
    
    @validator('*', pre=True)
    def validate_strings(cls, v):
        if isinstance(v, str):
            return SecurityValidator.sanitize_string(v)
        return v

class UserRegistrationModel(SecureBaseModel):
    """Secure user registration model"""
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        v = SecurityValidator.sanitize_string(v, max_length=50)
        if not re.match(r'^[a-zA-Z0-9_.-]{3,50}$', v):
            raise ValueError("Username must be 3-50 characters, alphanumeric, dash, dot, underscore only")
        return v
    
    @validator('email')
    def validate_email_field(cls, v):
        return SecurityValidator.validate_email(v)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @validator('phone')
    def validate_phone_field(cls, v):
        if v:
            return SecurityValidator.validate_phone(v)
        return v

class TradingOrderModel(SecureBaseModel):
    """Secure trading order model"""
    symbol: str
    quantity: int
    price: Optional[float] = None
    order_type: str = "MARKET"
    transaction_type: str
    
    @validator('symbol')
    def validate_symbol_field(cls, v):
        return SecurityValidator.validate_stock_symbol(v)
    
    @validator('quantity')
    def validate_quantity_field(cls, v):
        return int(SecurityValidator.validate_numeric(v, min_value=1, max_value=100000))
    
    @validator('price')
    def validate_price_field(cls, v):
        if v is not None:
            return SecurityValidator.validate_numeric(v, min_value=0.01, max_value=100000, decimal_places=2)
        return v
    
    @validator('order_type')
    def validate_order_type_field(cls, v):
        allowed_types = ['MARKET', 'LIMIT', 'SL', 'SL-M']
        if v.upper() not in allowed_types:
            raise ValueError(f"Order type must be one of: {allowed_types}")
        return v.upper()
    
    @validator('transaction_type')
    def validate_transaction_type_field(cls, v):
        if v.upper() not in ['BUY', 'SELL']:
            raise ValueError("Transaction type must be BUY or SELL")
        return v.upper()

class MarketDataRequestModel(SecureBaseModel):
    """Secure market data request model"""
    symbols: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    @validator('symbols')
    def validate_symbols_field(cls, v):
        if not v or len(v) > 50:
            raise ValueError("Must provide 1-50 symbols")
        
        validated_symbols = []
        for symbol in v:
            validated_symbols.append(SecurityValidator.validate_stock_symbol(symbol))
        
        return validated_symbols
    
    @validator('end_date')
    def validate_date_range_field(cls, v, values):
        if v and values.get('start_date'):
            start, end = SecurityValidator.validate_date_range(values['start_date'], v)
            return end.isoformat()
        return v

# FastAPI exception handler for validation errors
def validation_exception_handler(request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error from {request.client.host}: {exc}")
    
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return HTTPException(
        status_code=422,
        detail={
            "message": "Input validation failed",
            "errors": errors
        }
    )