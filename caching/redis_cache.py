"""
Redis caching service for high-performance data access
Provides caching for market data, user sessions, and frequently accessed data
"""
import redis
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache manager with production-ready configuration"""
    
    def __init__(self):
        """Initialize Redis connection with fallback handling"""
        self.redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection with error handling"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                health_check_interval=30,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )
            # Test connection
            self.client.ping()
            logger.info("✅ Redis cache connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with JSON deserialization"""
        if not self.is_available():
            return None
        
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON, return raw string if fails
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, expiry: int = 300) -> bool:
        """Set value in cache with JSON serialization and expiry"""
        if not self.is_available():
            return False
        
        try:
            # Serialize to JSON if not a string
            if not isinstance(value, str):
                value = json.dumps(value, default=str)
            
            self.client.setex(key, expiry, value)
            return True
            
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_available():
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get cached market data for a symbol"""
        return self.get(f'stock_price:{symbol}')
    
    def set_market_data(self, symbol: str, data: Dict, expiry: int = 180) -> bool:
        """Cache market data for a symbol (3 minutes default)"""
        return self.set(f'stock_price:{symbol}', data, expiry)
    
    def get_market_indices(self) -> Optional[Dict]:
        """Get cached market indices data"""
        return self.get('market_indices')
    
    def set_market_indices(self, data: Dict, expiry: int = 300) -> bool:
        """Cache market indices data (5 minutes default)"""
        return self.set('market_indices', data, expiry)
    
    def get_user_portfolio(self, user_id: int) -> Optional[Dict]:
        """Get cached user portfolio data"""
        return self.get(f'user_portfolio:{user_id}')
    
    def set_user_portfolio(self, user_id: int, data: Dict, expiry: int = 900) -> bool:
        """Cache user portfolio data (15 minutes default)"""
        return self.set(f'user_portfolio:{user_id}', data, expiry)
    
    def get_broker_data(self, broker_account_id: int) -> Optional[Dict]:
        """Get cached broker account data"""
        return self.get(f'broker_data:{broker_account_id}')
    
    def set_broker_data(self, broker_account_id: int, data: Dict, expiry: int = 600) -> bool:
        """Cache broker account data (10 minutes default)"""
        return self.set(f'broker_data:{broker_account_id}', data, expiry)
    
    def invalidate_user_cache(self, user_id: int) -> bool:
        """Invalidate all cache entries for a user"""
        if not self.is_available():
            return False
        
        try:
            # Get all keys matching user patterns
            patterns = [
                f'user_portfolio:{user_id}',
                f'user_watchlist:{user_id}',
                f'user_analysis:{user_id}*'
            ]
            
            for pattern in patterns:
                keys = self.client.keys(pattern)
                if keys:
                    self.client.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.warning(f"Error invalidating user cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get Redis cache statistics"""
        if not self.is_available():
            return {'status': 'unavailable'}
        
        try:
            info = self.client.info()
            return {
                'status': 'connected',
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate percentage"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)

# Global cache instance
cache = RedisCache()

# Convenience functions for easy imports
def get_cache() -> RedisCache:
    """Get the global cache instance"""
    return cache

def cache_market_data(symbol: str, data: Dict, expiry: int = 180) -> bool:
    """Cache market data for quick access"""
    return cache.set_market_data(symbol, data, expiry)

def get_cached_market_data(symbol: str) -> Optional[Dict]:
    """Get cached market data"""
    return cache.get_market_data(symbol)