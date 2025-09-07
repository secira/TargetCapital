"""
CDN and Static Asset Optimization Configuration
Implements caching strategies and static asset delivery optimization
"""

import os
import logging
import hashlib
import mimetypes
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import redis.asyncio as redis
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

class CDNConfig:
    """CDN and static asset configuration"""
    
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        self.cdn_enabled = os.environ.get("CDN_ENABLED", "false").lower() == "true"
        self.cdn_url = os.environ.get("CDN_URL", "")
        self.static_path = Path("static")
        self.cache_duration = {
            # Cache durations in seconds
            "css": 86400 * 7,      # 7 days
            "js": 86400 * 7,       # 7 days
            "images": 86400 * 30,  # 30 days
            "fonts": 86400 * 30,   # 30 days
            "videos": 86400 * 7,   # 7 days
            "documents": 3600,     # 1 hour
            "api": 300,            # 5 minutes
            "default": 3600        # 1 hour
        }
        self.compression_types = {
            "text/html", "text/css", "text/javascript", 
            "application/javascript", "application/json",
            "text/xml", "application/xml", "text/plain"
        }
    
    def get_cache_duration(self, file_extension: str) -> int:
        """Get cache duration for file type"""
        extension_mapping = {
            "css": "css",
            "js": "js", 
            "png": "images", "jpg": "images", "jpeg": "images", 
            "gif": "images", "svg": "images", "ico": "images",
            "woff": "fonts", "woff2": "fonts", "ttf": "fonts", "eot": "fonts",
            "mp4": "videos", "webm": "videos", "ogg": "videos",
            "pdf": "documents", "txt": "documents"
        }
        
        category = extension_mapping.get(file_extension.lower(), "default")
        return self.cache_duration.get(category, self.cache_duration["default"])

class StaticAssetHandler:
    """Enhanced static asset handler with caching and optimization"""
    
    def __init__(self, cdn_config: CDNConfig):
        self.config = cdn_config
        self.redis_client = None
        self.asset_hashes = {}
        
    async def init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis.from_url(
                self.config.redis_url,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ CDN Redis cache connected")
        except Exception as e:
            logger.error(f"❌ CDN Redis connection failed: {e}")
            self.redis_client = None
    
    async def generate_asset_hash(self, file_path: Path) -> str:
        """Generate hash for asset versioning"""
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
                return hashlib.md5(content).hexdigest()[:8]
        except Exception as e:
            logger.error(f"Failed to generate hash for {file_path}: {e}")
            return "default"
    
    async def get_versioned_url(self, asset_path: str) -> str:
        """Get versioned URL for asset"""
        if self.config.cdn_enabled and self.config.cdn_url:
            # Use CDN URL
            file_path = Path(asset_path)
            if file_path.exists():
                file_hash = await self.generate_asset_hash(file_path)
                filename = file_path.stem
                extension = file_path.suffix
                versioned_filename = f"{filename}.{file_hash}{extension}"
                return f"{self.config.cdn_url.rstrip('/')}/{versioned_filename}"
        
        # Local serving with version parameter
        file_path = Path(asset_path)
        if file_path.exists():
            file_hash = await self.generate_asset_hash(file_path)
            return f"/{asset_path}?v={file_hash}"
        
        return f"/{asset_path}"
    
    async def serve_static_file(self, file_path: str, request: Request) -> Response:
        """Serve static file with caching headers"""
        full_path = Path(file_path)
        
        if not full_path.exists():
            return Response(status_code=404)
        
        # Get file info
        file_stat = full_path.stat()
        file_size = file_stat.st_size
        last_modified = datetime.fromtimestamp(file_stat.st_mtime)
        etag = f'"{file_stat.st_mtime}-{file_size}"'
        
        # Check if-none-match (ETag)
        if_none_match = request.headers.get('if-none-match')
        if if_none_match == etag:
            return Response(status_code=304)
        
        # Check if-modified-since
        if_modified_since = request.headers.get('if-modified-since')
        if if_modified_since:
            try:
                if_modified_date = datetime.strptime(
                    if_modified_since, 
                    '%a, %d %b %Y %H:%M:%S GMT'
                )
                if last_modified <= if_modified_date:
                    return Response(status_code=304)
            except ValueError:
                pass
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(full_path))
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Get cache duration
        file_extension = full_path.suffix.lstrip('.')
        cache_duration = self.config.get_cache_duration(file_extension)
        
        # Create response
        response = FileResponse(
            str(full_path),
            media_type=content_type,
            headers={
                'Cache-Control': f'public, max-age={cache_duration}',
                'ETag': etag,
                'Last-Modified': last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'Expires': (datetime.utcnow() + timedelta(seconds=cache_duration)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
        )
        
        return response

class APIResponseCache:
    """API response caching with Redis"""
    
    def __init__(self, cdn_config: CDNConfig):
        self.config = cdn_config
        self.redis_client = None
    
    async def init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis.from_url(
                self.config.redis_url,
                decode_responses=False  # Keep binary for API responses
            )
            await self.redis_client.ping()
        except Exception as e:
            logger.error(f"API cache Redis connection failed: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        # Include URL, query parameters, and relevant headers
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items())),
            request.headers.get('accept', ''),
            request.headers.get('accept-encoding', '')
        ]
        
        cache_key = hashlib.md5(
            '|'.join(key_parts).encode()
        ).hexdigest()
        
        return f"api_cache:{cache_key}"
    
    async def get_cached_response(self, request: Request) -> Optional[bytes]:
        """Get cached response if available"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(request)
            cached_data = await self.redis_client.get(cache_key)
            return cached_data
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None
    
    async def cache_response(self, request: Request, response_content: bytes, 
                           cache_duration: int = 300) -> bool:
        """Cache API response"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(request)
            await self.redis_client.setex(cache_key, cache_duration, response_content)
            return True
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cached responses matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(f"api_cache:*{pattern}*")
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to invalidate cache pattern {pattern}: {e}")
            return 0

class CompressionHandler:
    """Handle response compression"""
    
    @staticmethod
    def should_compress(content_type: str, content_length: int) -> bool:
        """Determine if response should be compressed"""
        if content_length < 1024:  # Don't compress small responses
            return False
        
        compressible_types = {
            "text/html", "text/css", "text/javascript",
            "application/javascript", "application/json",
            "text/xml", "application/xml", "text/plain",
            "application/rss+xml", "image/svg+xml"
        }
        
        return any(content_type.startswith(t) for t in compressible_types)

def setup_cdn_middleware(app: FastAPI):
    """Setup CDN and caching middleware for FastAPI"""
    
    cdn_config = CDNConfig()
    static_handler = StaticAssetHandler(cdn_config)
    api_cache = APIResponseCache(cdn_config)
    
    @app.middleware("http")
    async def cdn_middleware(request: Request, call_next):
        """CDN and caching middleware"""
        
        # Initialize Redis connections if needed
        if not static_handler.redis_client:
            await static_handler.init_redis()
        if not api_cache.redis_client:
            await api_cache.init_redis()
        
        # Handle static files
        if request.url.path.startswith('/static/'):
            file_path = request.url.path[1:]  # Remove leading /
            return await static_handler.serve_static_file(file_path, request)
        
        # Handle API responses
        if request.url.path.startswith('/api/'):
            # Check cache first
            cached_response = await api_cache.get_cached_response(request)
            if cached_response:
                return Response(
                    content=cached_response,
                    headers={
                        'X-Cache': 'HIT',
                        'Cache-Control': f'public, max-age={cdn_config.cache_duration["api"]}'
                    }
                )
        
        # Process request
        response = await call_next(request)
        
        # Cache API responses
        if (request.url.path.startswith('/api/') and 
            response.status_code == 200 and 
            request.method == 'GET'):
            
            # Get response content for caching
            if hasattr(response, 'body'):
                await api_cache.cache_response(
                    request, 
                    response.body, 
                    cdn_config.cache_duration["api"]
                )
                response.headers['X-Cache'] = 'MISS'
        
        return response
    
    # Mount static files with caching
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return cdn_config, static_handler, api_cache

# Template functions for asset URLs
class TemplateHelpers:
    """Template helper functions for asset management"""
    
    def __init__(self, static_handler: StaticAssetHandler):
        self.static_handler = static_handler
    
    async def asset_url(self, asset_path: str) -> str:
        """Generate versioned asset URL for templates"""
        return await self.static_handler.get_versioned_url(f"static/{asset_path}")
    
    async def css_url(self, css_file: str) -> str:
        """Generate CSS file URL"""
        return await self.asset_url(f"css/{css_file}")
    
    async def js_url(self, js_file: str) -> str:
        """Generate JavaScript file URL"""
        return await self.asset_url(f"js/{js_file}")
    
    async def img_url(self, img_file: str) -> str:
        """Generate image file URL"""
        return await self.asset_url(f"images/{img_file}")

# Cache warming functionality
class CacheWarmer:
    """Pre-warm cache with frequently accessed data"""
    
    def __init__(self, api_cache: APIResponseCache):
        self.api_cache = api_cache
    
    async def warm_market_data_cache(self):
        """Pre-warm market data cache"""
        try:
            # Simulate requests for popular endpoints
            popular_endpoints = [
                "/api/market/overview",
                "/api/market/quote/RELIANCE",
                "/api/market/quote/TCS",
                "/api/market/quote/INFY",
                "/api/market/sectors"
            ]
            
            # This would typically make real requests to warm the cache
            # Implementation depends on your specific caching strategy
            logger.info(f"Cache warmer would pre-load {len(popular_endpoints)} endpoints")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")

# Performance monitoring
class CDNMetrics:
    """CDN and caching performance metrics"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            if not self.redis_client:
                return {"error": "Redis not available"}
            
            info = await self.redis_client.info()
            
            # Count cache keys by type
            api_keys = await self.redis_client.keys("api_cache:*")
            asset_keys = await self.redis_client.keys("asset_cache:*")
            
            return {
                "redis_memory_used": info.get("used_memory_human", "unknown"),
                "redis_hits": info.get("keyspace_hits", 0),
                "redis_misses": info.get("keyspace_misses", 0),
                "api_cache_keys": len(api_keys) if api_keys else 0,
                "asset_cache_keys": len(asset_keys) if asset_keys else 0,
                "hit_ratio": self._calculate_hit_ratio(info.get("keyspace_hits", 0), info.get("keyspace_misses", 0))
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
    
    def _calculate_hit_ratio(self, hits: int, misses: int) -> float:
        """Calculate cache hit ratio"""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0