"""
High-performance route optimizations
Async implementations for heavy operations
"""

import asyncio
import aiohttp
from functools import wraps
from flask import jsonify, request
import logging

logger = logging.getLogger(__name__)

def async_route(f):
    """Decorator to run Flask routes asynchronously"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, f(*args, **kwargs))
                    return future.result(timeout=30)
            else:
                return asyncio.run(f(*args, **kwargs))
        except Exception as e:
            logger.error(f"Async route error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper

# Async helper functions for heavy operations
async def fetch_multiple_apis(urls):
    """Fetch multiple APIs concurrently"""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def fetch_url(session, url):
    """Fetch a single URL with error handling"""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {'error': f'HTTP {response.status}'}
    except Exception as e:
        return {'error': str(e)}

# Performance monitoring middleware
def monitor_performance(f):
    """Monitor route performance"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # Log slow routes
                logger.warning(f"Slow route detected: {request.endpoint} took {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Route error in {request.endpoint} after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper

# Batch processing utilities
class BatchProcessor:
    """Process multiple operations in batches for better performance"""
    
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
    
    async def process_batch(self, items, process_func):
        """Process items in batches"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await self._process_batch_chunk(batch, process_func)
            results.extend(batch_results)
        return results
    
    async def _process_batch_chunk(self, batch, process_func):
        """Process a single batch chunk"""
        tasks = [process_func(item) for item in batch]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Database query optimization helpers
def optimize_db_query(query_func):
    """Optimize database queries with caching and batching"""
    @wraps(query_func)
    def wrapper(*args, **kwargs):
        # Add query result caching here
        cache_key = f"db_query_{query_func.__name__}_{hash(str(args) + str(kwargs))}"
        
        # Try to get from cache first
        from caching.redis_cache import RedisCache
        cache = RedisCache()
        
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute query and cache result
        result = query_func(*args, **kwargs)
        cache.set(cache_key, result, expiry=300)  # 5 minute cache
        
        return result
    
    return wrapper