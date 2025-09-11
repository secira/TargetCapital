"""
Background tasks for market data processing and caching
Real-time market data updates and NSE data synchronization
"""
import logging
from celery import shared_task
from datetime import datetime, timedelta
import redis
import json

logger = logging.getLogger(__name__)

# Redis client for caching
def get_redis_client():
    """Get Redis client for caching"""
    import os
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    return redis.from_url(redis_url, decode_responses=True)

@shared_task
def update_market_indices():
    """Update NSE market indices and cache results"""
    try:
        from services.nse_service import NSEService
        
        nse_service = NSEService()
        
        # Fetch major indices
        indices = [
            'NIFTY 50', 'NIFTY BANK', 'NIFTY IT', 'NIFTY PHARMA',
            'NIFTY AUTO', 'NIFTY METAL', 'NIFTY ENERGY'
        ]
        
        market_data = {}
        for index in indices:
            try:
                data = nse_service.get_index_data(index)
                market_data[index] = {
                    'current_value': data.get('last_price', 0),
                    'change': data.get('change', 0),
                    'change_percent': data.get('pChange', 0),
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.warning(f"Failed to fetch data for {index}: {e}")
                continue
        
        # Cache the data in Redis
        redis_client = get_redis_client()
        redis_client.setex(
            'market_indices',
            300,  # 5 minutes expiry
            json.dumps(market_data)
        )
        
        logger.info(f"Updated market data for {len(market_data)} indices")
        return {'success': True, 'indices_updated': len(market_data)}
        
    except Exception as exc:
        logger.error(f"Error updating market indices: {exc}")
        return {'error': str(exc)}

@shared_task
def update_stock_prices(symbols):
    """Update stock prices for given symbols and cache results"""
    try:
        from services.nse_service import NSEService
        
        nse_service = NSEService()
        redis_client = get_redis_client()
        
        updated_count = 0
        for symbol in symbols:
            try:
                stock_data = nse_service.get_stock_data(symbol)
                
                price_info = {
                    'symbol': symbol,
                    'current_price': stock_data.get('lastPrice', 0),
                    'change': stock_data.get('change', 0),
                    'change_percent': stock_data.get('pChange', 0),
                    'high': stock_data.get('dayHigh', 0),
                    'low': stock_data.get('dayLow', 0),
                    'volume': stock_data.get('totalTradedVolume', 0),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Cache individual stock data
                redis_client.setex(
                    f'stock_price:{symbol}',
                    180,  # 3 minutes expiry
                    json.dumps(price_info)
                )
                
                updated_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to update price for {symbol}: {e}")
                continue
        
        logger.info(f"Updated prices for {updated_count} stocks")
        return {'success': True, 'stocks_updated': updated_count}
        
    except Exception as exc:
        logger.error(f"Error updating stock prices: {exc}")
        return {'error': str(exc)}

@shared_task
def cache_popular_stocks():
    """Cache data for popular/trending stocks"""
    try:
        # Popular stocks to cache
        popular_stocks = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'HINDUNILVR',
            'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'LT',
            'ASIANPAINT', 'MARUTI', 'TITAN', 'ULTRACEMCO', 'NESTLEIND'
        ]
        
        # Queue stock price updates
        update_stock_prices.delay(popular_stocks)
        
        return {'success': True, 'popular_stocks_queued': len(popular_stocks)}
        
    except Exception as exc:
        logger.error(f"Error caching popular stocks: {exc}")
        return {'error': str(exc)}

@shared_task
def cleanup_expired_cache():
    """Clean up expired cache entries"""
    try:
        redis_client = get_redis_client()
        
        # Get keys matching our patterns
        patterns = ['stock_price:*', 'market_indices', 'user_portfolio:*']
        deleted_count = 0
        
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            for key in keys:
                # Check if key exists and has no TTL (expired)
                if redis_client.ttl(key) == -1:
                    redis_client.delete(key)
                    deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} expired cache entries")
        return {'success': True, 'deleted_count': deleted_count}
        
    except Exception as exc:
        logger.error(f"Error cleaning up cache: {exc}")
        return {'error': str(exc)}

@shared_task
def generate_market_summary():
    """Generate and cache market summary for dashboard"""
    try:
        redis_client = get_redis_client()
        
        # Get cached market indices
        market_data = redis_client.get('market_indices')
        if not market_data:
            # Trigger market data update if not available
            update_market_indices.delay()
            return {'info': 'Market data update triggered'}
        
        indices_data = json.loads(market_data)
        
        # Calculate market summary
        summary = {
            'market_status': 'OPEN' if datetime.now().hour < 16 else 'CLOSED',
            'major_indices': {},
            'market_sentiment': 'NEUTRAL',
            'top_gainers_count': 0,
            'top_losers_count': 0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Process major indices
        gainers = 0
        losers = 0
        
        for index, data in indices_data.items():
            summary['major_indices'][index] = {
                'value': data['current_value'],
                'change': data['change'],
                'change_percent': data['change_percent']
            }
            
            if data['change'] > 0:
                gainers += 1
            elif data['change'] < 0:
                losers += 1
        
        # Determine market sentiment
        if gainers > losers:
            summary['market_sentiment'] = 'BULLISH'
        elif losers > gainers:
            summary['market_sentiment'] = 'BEARISH'
        
        # Cache market summary
        redis_client.setex(
            'market_summary',
            300,  # 5 minutes expiry
            json.dumps(summary)
        )
        
        logger.info("Generated market summary")
        return {'success': True, 'summary_generated': True}
        
    except Exception as exc:
        logger.error(f"Error generating market summary: {exc}")
        return {'error': str(exc)}