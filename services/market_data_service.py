"""
Real-time market data service integrating multiple APIs
Provides live stock prices, market data, and technical indicators
"""

import os
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import yfinance as yf
from services.nse_service import NSEService

class MarketDataService:
    def __init__(self):
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        self.alpha_vantage_base = 'https://www.alphavantage.co/query'
        self.nse_service = NSEService()
        self.session = requests.Session()
        
        # Set request headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_stock_quote(self, symbol: str, exchange: str = 'US') -> Optional[Dict[str, Any]]:
        """
        Get real-time stock quote with fallback to multiple sources
        """
        try:
            # Try Alpha Vantage first for US stocks
            if exchange.upper() == 'US' and self.alpha_vantage_key:
                quote = self._get_alpha_vantage_quote(symbol)
                if quote:
                    return quote
            
            # Try Yahoo Finance as fallback for all markets
            quote = self._get_yahoo_finance_quote(symbol, exchange)
            if quote:
                return quote
                
            # Try NSE for Indian stocks
            if exchange.upper() in ['NSE', 'BSE', 'IN', 'INDIA']:
                quote = self._get_nse_quote(symbol)
                if quote:
                    return quote
                    
        except Exception as e:
            logging.error(f"Error fetching quote for {symbol}: {str(e)}")
            
        return None
    
    def _get_alpha_vantage_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote from Alpha Vantage API"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = self.session.get(self.alpha_vantage_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Global Quote' in data and data['Global Quote']:
                quote_data = data['Global Quote']
                
                return {
                    'symbol': quote_data.get('01. symbol', symbol),
                    'company_name': symbol,  # Alpha Vantage doesn't provide company name in this endpoint
                    'current_price': float(quote_data.get('05. price', 0)),
                    'change': float(quote_data.get('09. change', 0)),
                    'change_percent': quote_data.get('10. change percent', '0%').replace('%', ''),
                    'open': float(quote_data.get('02. open', 0)),
                    'high': float(quote_data.get('03. high', 0)),
                    'low': float(quote_data.get('04. low', 0)),
                    'previous_close': float(quote_data.get('08. previous close', 0)),
                    'volume': int(quote_data.get('06. volume', 0)),
                    'latest_trading_day': quote_data.get('07. latest trading day'),
                    'source': 'Alpha Vantage',
                    'currency': 'USD',
                    'exchange': 'US',
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logging.error(f"Alpha Vantage API error for {symbol}: {str(e)}")
            
        return None
    
    def _get_yahoo_finance_quote(self, symbol: str, exchange: str = 'US') -> Optional[Dict[str, Any]]:
        """Get quote from Yahoo Finance using yfinance"""
        try:
            # Format symbol for different exchanges
            if exchange.upper() in ['NSE', 'IN', 'INDIA']:
                ticker_symbol = f"{symbol}.NS"
            elif exchange.upper() == 'BSE':
                ticker_symbol = f"{symbol}.BO"
            else:
                ticker_symbol = symbol
                
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                
                # Get current price from info or latest history
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or latest['Close']
                previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                
                if previous_close:
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                else:
                    change = 0
                    change_percent = 0
                
                return {
                    'symbol': symbol,
                    'company_name': info.get('longName', info.get('shortName', symbol)),
                    'current_price': float(current_price),
                    'change': float(change),
                    'change_percent': f"{change_percent:.2f}",
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'previous_close': float(previous_close) if previous_close else float(latest['Close']),
                    'volume': int(latest['Volume']),
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE'),
                    'source': 'Yahoo Finance',
                    'currency': info.get('currency', 'USD'),
                    'exchange': exchange,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logging.error(f"Yahoo Finance error for {symbol}: {str(e)}")
            
        return None
    
    def _get_nse_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote from NSE service"""
        try:
            quote_data = self.nse_service.get_quote(symbol)
            if quote_data and 'priceInfo' in quote_data:
                price_info = quote_data['priceInfo']
                
                return {
                    'symbol': symbol,
                    'company_name': quote_data.get('info', {}).get('companyName', symbol),
                    'current_price': float(price_info.get('lastPrice', 0)),
                    'change': float(price_info.get('change', 0)),
                    'change_percent': f"{price_info.get('pChange', 0):.2f}",
                    'open': float(price_info.get('open', 0)),
                    'high': float(price_info.get('intraDayHighLow', {}).get('max', 0)),
                    'low': float(price_info.get('intraDayHighLow', {}).get('min', 0)),
                    'previous_close': float(price_info.get('previousClose', 0)),
                    'volume': int(price_info.get('totalTradedVolume', 0)),
                    'source': 'NSE India',
                    'currency': 'INR',
                    'exchange': 'NSE',
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logging.error(f"NSE error for {symbol}: {str(e)}")
            
        return None
    
    def get_market_indices(self) -> List[Dict[str, Any]]:
        """Get major market indices"""
        indices = []
        
        # Major US indices
        us_indices = [
            ('SPY', 'S&P 500'),
            ('^GSPC', 'S&P 500'),
            ('^DJI', 'Dow Jones'),
            ('^IXIC', 'NASDAQ'),
            ('^VIX', 'VIX')
        ]
        
        # Major Indian indices
        indian_indices = [
            ('NIFTY', 'NIFTY 50'),
            ('BANKNIFTY', 'BANK NIFTY'),
            ('SENSEX', 'BSE SENSEX')
        ]
        
        # Fetch US indices
        for symbol, name in us_indices:
            try:
                quote = self._get_yahoo_finance_quote(symbol, 'US')
                if quote:
                    quote['index_name'] = name
                    indices.append(quote)
            except:
                continue
                
        # Fetch Indian indices
        for symbol, name in indian_indices:
            try:
                # Try NSE first
                nse_data = self.nse_service.get_indices()
                if nse_data:
                    for index_data in nse_data.get('data', []):
                        if symbol.lower() in index_data.get('index', '').lower():
                            indices.append({
                                'symbol': symbol,
                                'index_name': name,
                                'current_price': float(index_data.get('last', 0)),
                                'change': float(index_data.get('variation', 0)),
                                'change_percent': f"{index_data.get('percentChange', 0):.2f}",
                                'source': 'NSE India',
                                'exchange': 'NSE',
                                'last_updated': datetime.now(timezone.utc).isoformat()
                            })
                            break
                
                # Fallback to Yahoo Finance for Indian indices
                if not any(idx['symbol'] == symbol for idx in indices):
                    quote = self._get_yahoo_finance_quote(f"^{symbol}", 'India')
                    if quote:
                        quote['index_name'] = name
                        indices.append(quote)
            except:
                continue
                
        return indices
    
    def get_trending_stocks(self, market: str = 'US', limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending/most active stocks"""
        trending = []
        
        try:
            if market.upper() == 'US':
                # Popular US stocks
                symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V']
                
                for symbol in symbols[:limit]:
                    quote = self.get_stock_quote(symbol, 'US')
                    if quote:
                        trending.append(quote)
                        
            elif market.upper() in ['INDIA', 'NSE']:
                # Popular Indian stocks
                symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'LT']
                
                for symbol in symbols[:limit]:
                    quote = self.get_stock_quote(symbol, 'NSE')
                    if quote:
                        trending.append(quote)
                        
        except Exception as e:
            logging.error(f"Error fetching trending stocks: {str(e)}")
            
        return trending
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for stocks by symbol or company name"""
        results = []
        
        try:
            # Try Alpha Vantage symbol search if available
            if self.alpha_vantage_key:
                av_results = self._search_alpha_vantage(query, limit)
                results.extend(av_results)
            
            # Try NSE search for Indian stocks
            nse_results = self._search_nse_stocks(query, limit)
            results.extend(nse_results)
            
            # Remove duplicates and limit results
            seen = set()
            unique_results = []
            for result in results:
                key = (result['symbol'], result.get('exchange', ''))
                if key not in seen:
                    seen.add(key)
                    unique_results.append(result)
                    
            return unique_results[:limit]
            
        except Exception as e:
            logging.error(f"Error searching stocks: {str(e)}")
            
        return []
    
    def _search_alpha_vantage(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search stocks using Alpha Vantage"""
        try:
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': query,
                'apikey': self.alpha_vantage_key
            }
            
            response = self.session.get(self.alpha_vantage_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for match in data.get('bestMatches', [])[:limit]:
                results.append({
                    'symbol': match.get('1. symbol'),
                    'company_name': match.get('2. name'),
                    'type': match.get('3. type'),
                    'region': match.get('4. region'),
                    'currency': match.get('8. currency'),
                    'exchange': 'US',
                    'source': 'Alpha Vantage'
                })
                
            return results
            
        except Exception as e:
            logging.error(f"Alpha Vantage search error: {str(e)}")
            
        return []
    
    def _search_nse_stocks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search NSE stocks"""
        try:
            # Get NSE stock list and filter by query
            stocks = self.nse_service.get_all_stocks()
            results = []
            
            if stocks:
                query_lower = query.lower()
                for stock in stocks[:50]:  # Limit initial search
                    symbol = stock.get('symbol', '')
                    name = stock.get('companyName', '')
                    
                    if (query_lower in symbol.lower() or 
                        query_lower in name.lower()):
                        results.append({
                            'symbol': symbol,
                            'company_name': name,
                            'exchange': 'NSE',
                            'currency': 'INR',
                            'source': 'NSE India'
                        })
                        
                        if len(results) >= limit:
                            break
                            
            return results
            
        except Exception as e:
            logging.error(f"NSE search error: {str(e)}")
            
        return []

# Global instance
market_data_service = MarketDataService()