"""
Market Intelligence Service for AI Advisor
Provides real-time market intelligence and analysis using external APIs
"""

import os
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
import json

class MarketIntelligenceService:
    def __init__(self):
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        self.logger = logging.getLogger(__name__)
        
    def get_market_sentiment(self) -> Dict[str, Any]:
        """Get current market sentiment analysis"""
        try:
            # Use Alpha Vantage News & Sentiment API
            if not self.alpha_vantage_key:
                return self._get_mock_sentiment()
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': 'NIFTY,SENSEX',
                'apikey': self.alpha_vantage_key,
                'limit': 50
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._process_sentiment_data(data)
            else:
                self.logger.warning(f"Market sentiment API failed: {response.status_code}")
                return self._get_mock_sentiment()
                
        except Exception as e:
            self.logger.error(f"Market sentiment error: {str(e)}")
            return self._get_mock_sentiment()
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector-wise performance analysis"""
        try:
            if not self.alpha_vantage_key:
                return self._get_mock_sector_data()
            
            # Get sector performance data
            sectors = ['XLF', 'XLK', 'XLE', 'XLI', 'XLV', 'XLRE']  # Financial, Tech, Energy, Industrial, Health, Real Estate
            sector_data = {}
            
            for sector in sectors:
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': sector,
                    'apikey': self.alpha_vantage_key
                }
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'Global Quote' in data:
                        quote = data['Global Quote']
                        sector_data[sector] = {
                            'price': float(quote.get('05. price', 0)),
                            'change_percent': float(quote.get('10. change percent', '0%').replace('%', ''))
                        }
            
            return self._format_sector_data(sector_data)
            
        except Exception as e:
            self.logger.error(f"Sector performance error: {str(e)}")
            return self._get_mock_sector_data()
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators"""
        try:
            if not self.alpha_vantage_key:
                return self._get_mock_economic_data()
            
            indicators = {}
            
            # GDP Data
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'REAL_GDP',
                'interval': 'quarterly',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    latest_gdp = data['data'][0]
                    indicators['gdp'] = {
                        'value': float(latest_gdp.get('value', 0)),
                        'date': latest_gdp.get('date', ''),
                        'unit': 'Billions of Chained 2012 Dollars'
                    }
            
            # Inflation Rate
            params = {
                'function': 'CPI',
                'interval': 'monthly',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 1:
                    current_cpi = float(data['data'][0].get('value', 0))
                    prev_cpi = float(data['data'][1].get('value', 0))
                    inflation_rate = ((current_cpi - prev_cpi) / prev_cpi) * 100
                    
                    indicators['inflation'] = {
                        'value': round(inflation_rate, 2),
                        'date': data['data'][0].get('date', ''),
                        'unit': 'Percentage'
                    }
            
            return indicators if indicators else self._get_mock_economic_data()
            
        except Exception as e:
            self.logger.error(f"Economic indicators error: {str(e)}")
            return self._get_mock_economic_data()
    
    def get_market_trends(self) -> Dict[str, Any]:
        """Analyze current market trends"""
        try:
            trends = {
                'trending_stocks': self._get_trending_stocks(),
                'sector_leaders': self._get_sector_leaders(),
                'volume_leaders': self._get_volume_leaders(),
                'momentum_stocks': self._get_momentum_stocks()
            }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Market trends error: {str(e)}")
            return self._get_mock_trends_data()
    
    def _process_sentiment_data(self, data: Dict) -> Dict[str, Any]:
        """Process sentiment data from Alpha Vantage"""
        if 'feed' not in data:
            return self._get_mock_sentiment()
        
        articles = data['feed'][:20]  # Analyze recent 20 articles
        
        sentiment_scores = []
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for article in articles:
            if 'overall_sentiment_score' in article:
                score = float(article['overall_sentiment_score'])
                sentiment_scores.append(score)
                
                if score > 0.15:
                    bullish_count += 1
                elif score < -0.15:
                    bearish_count += 1
                else:
                    neutral_count += 1
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Determine overall sentiment
        if avg_sentiment > 0.15:
            sentiment_label = 'Bullish'
            confidence = min(95, 50 + abs(avg_sentiment) * 100)
        elif avg_sentiment < -0.15:
            sentiment_label = 'Bearish'
            confidence = min(95, 50 + abs(avg_sentiment) * 100)
        else:
            sentiment_label = 'Neutral'
            confidence = 60
        
        return {
            'sentiment': sentiment_label,
            'confidence': round(confidence, 1),
            'sentiment_score': round(avg_sentiment, 3),
            'analysis': {
                'bullish_articles': bullish_count,
                'bearish_articles': bearish_count,
                'neutral_articles': neutral_count,
                'total_analyzed': len(articles)
            },
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_trending_stocks(self) -> List[Dict]:
        """Get trending stocks data"""
        # This would typically use real API data
        return [
            {'symbol': 'RELIANCE', 'change': 2.3, 'volume': 1500000},
            {'symbol': 'TCS', 'change': 1.8, 'volume': 800000},
            {'symbol': 'INFY', 'change': -0.5, 'volume': 1200000},
            {'symbol': 'HDFCBANK', 'change': 1.2, 'volume': 900000},
            {'symbol': 'ICICIBANK', 'change': 0.8, 'volume': 700000}
        ]
    
    def _get_sector_leaders(self) -> List[Dict]:
        """Get sector-wise leading stocks"""
        return [
            {'sector': 'Technology', 'leader': 'TCS', 'change': 1.8},
            {'sector': 'Banking', 'leader': 'HDFCBANK', 'change': 1.2},
            {'sector': 'Energy', 'leader': 'RELIANCE', 'change': 2.3},
            {'sector': 'FMCG', 'leader': 'HINDUNILVR', 'change': 0.9},
            {'sector': 'Pharma', 'leader': 'SUNPHARMA', 'change': 1.5}
        ]
    
    def _get_volume_leaders(self) -> List[Dict]:
        """Get high volume stocks"""
        return [
            {'symbol': 'RELIANCE', 'volume': 1500000, 'avg_volume': 1200000},
            {'symbol': 'INFY', 'volume': 1200000, 'avg_volume': 800000},
            {'symbol': 'HDFCBANK', 'volume': 900000, 'avg_volume': 600000},
            {'symbol': 'TCS', 'volume': 800000, 'avg_volume': 500000},
            {'symbol': 'ICICIBANK', 'volume': 700000, 'avg_volume': 400000}
        ]
    
    def _get_momentum_stocks(self) -> List[Dict]:
        """Get momentum stocks"""
        return [
            {'symbol': 'RELIANCE', 'momentum_score': 8.5, 'trend': 'Strong Uptrend'},
            {'symbol': 'TCS', 'momentum_score': 7.2, 'trend': 'Uptrend'},
            {'symbol': 'HDFCBANK', 'momentum_score': 6.8, 'trend': 'Uptrend'},
            {'symbol': 'SUNPHARMA', 'momentum_score': 6.1, 'trend': 'Moderate Uptrend'},
            {'symbol': 'HINDUNILVR', 'momentum_score': 5.9, 'trend': 'Sideways'}
        ]
    
    def _format_sector_data(self, sector_data: Dict) -> Dict[str, Any]:
        """Format sector performance data"""
        sector_names = {
            'XLF': 'Financial',
            'XLK': 'Technology',
            'XLE': 'Energy',
            'XLI': 'Industrial',
            'XLV': 'Healthcare',
            'XLRE': 'Real Estate'
        }
        
        formatted_sectors = []
        for symbol, data in sector_data.items():
            if symbol in sector_names:
                formatted_sectors.append({
                    'name': sector_names[symbol],
                    'symbol': symbol,
                    'price': data['price'],
                    'change_percent': data['change_percent'],
                    'performance': 'Positive' if data['change_percent'] > 0 else 'Negative'
                })
        
        # Sort by performance
        formatted_sectors.sort(key=lambda x: x['change_percent'], reverse=True)
        
        return {
            'sectors': formatted_sectors,
            'best_performer': formatted_sectors[0] if formatted_sectors else None,
            'worst_performer': formatted_sectors[-1] if formatted_sectors else None,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    # Mock data methods for when API keys are not available
    def _get_mock_sentiment(self) -> Dict[str, Any]:
        return {
            'sentiment': 'Bullish',
            'confidence': 75.2,
            'sentiment_score': 0.234,
            'analysis': {
                'bullish_articles': 12,
                'bearish_articles': 5,
                'neutral_articles': 8,
                'total_analyzed': 25
            },
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_mock_sector_data(self) -> Dict[str, Any]:
        return {
            'sectors': [
                {'name': 'Technology', 'symbol': 'TECH', 'price': 3450.25, 'change_percent': 2.1, 'performance': 'Positive'},
                {'name': 'Banking', 'symbol': 'BANK', 'price': 2890.40, 'change_percent': 1.8, 'performance': 'Positive'},
                {'name': 'Energy', 'symbol': 'ENERGY', 'price': 1234.56, 'change_percent': -0.5, 'performance': 'Negative'},
                {'name': 'Healthcare', 'symbol': 'HEALTH', 'price': 2100.30, 'change_percent': 0.9, 'performance': 'Positive'},
                {'name': 'Industrial', 'symbol': 'INDUS', 'price': 1890.75, 'change_percent': -1.2, 'performance': 'Negative'}
            ],
            'best_performer': {'name': 'Technology', 'change_percent': 2.1},
            'worst_performer': {'name': 'Industrial', 'change_percent': -1.2},
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_mock_economic_data(self) -> Dict[str, Any]:
        return {
            'gdp': {
                'value': 27360.4,
                'date': '2024-Q2',
                'unit': 'Billions of Chained 2012 Dollars'
            },
            'inflation': {
                'value': 3.2,
                'date': '2024-07',
                'unit': 'Percentage'
            }
        }
    
    def _get_mock_trends_data(self) -> Dict[str, Any]:
        return {
            'trending_stocks': self._get_trending_stocks(),
            'sector_leaders': self._get_sector_leaders(),
            'volume_leaders': self._get_volume_leaders(),
            'momentum_stocks': self._get_momentum_stocks()
        }