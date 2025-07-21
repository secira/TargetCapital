"""
Agentic AI Service for tCapital Platform
Implements multi-agent AI system for stock trading decisions, portfolio management, and market analysis.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAgent:
    """Core trading agent that makes buy/sell/hold decisions based on technical analysis"""
    
    def __init__(self):
        self.name = "Trading Agent"
        self.confidence_threshold = 0.7
        
    def analyze_stock(self, symbol: str, period: str = "3mo") -> Dict:
        """Analyze stock and provide trading recommendation"""
        try:
            # Fetch stock data
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            
            if data.empty:
                return {"error": "No data available for symbol"}
            
            # Calculate technical indicators
            signals = self._calculate_technical_signals(data)
            
            # Make trading decision
            decision = self._make_trading_decision(signals)
            
            return {
                "symbol": symbol,
                "recommendation": decision["action"],
                "confidence": decision["confidence"],
                "reasoning": decision["reasoning"],
                "current_price": float(data['Close'].iloc[-1]),
                "signals": signals,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trading Agent error for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_technical_signals(self, data: pd.DataFrame) -> Dict:
        """Calculate various technical indicators"""
        signals = {}
        
        # Moving averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        data['BB_Std'] = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
        data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
        
        # Get latest values (handle both Series and DataFrame)
        if hasattr(data, 'iloc'):
            latest = data.iloc[-1]
        else:
            latest = data[-1] if len(data) > 0 else {}
        
        signals = {
            "sma_trend": "bullish" if latest['Close'] > latest['SMA_20'] else "bearish",
            "golden_cross": latest['SMA_20'] > latest['SMA_50'],
            "rsi": float(latest['RSI']),
            "rsi_signal": "oversold" if latest['RSI'] < 30 else "overbought" if latest['RSI'] > 70 else "neutral",
            "macd_signal": "bullish" if latest['MACD'] > latest['MACD_Signal'] else "bearish",
            "bb_position": "upper" if latest['Close'] > latest['BB_Upper'] else "lower" if latest['Close'] < latest['BB_Lower'] else "middle",
            "volume_trend": "high" if latest['Volume'] > data['Volume'].rolling(20).mean().iloc[-1] else "normal"
        }
        
        return signals
    
    def _make_trading_decision(self, signals: Dict) -> Dict:
        """Make trading decision based on signals"""
        bullish_signals = 0
        bearish_signals = 0
        reasoning = []
        
        # Evaluate signals
        if signals["sma_trend"] == "bullish":
            bullish_signals += 1
            reasoning.append("Price above 20-day SMA")
        else:
            bearish_signals += 1
            reasoning.append("Price below 20-day SMA")
            
        if signals["golden_cross"]:
            bullish_signals += 1
            reasoning.append("Golden cross pattern")
            
        if signals["rsi_signal"] == "oversold":
            bullish_signals += 1
            reasoning.append("RSI indicates oversold condition")
        elif signals["rsi_signal"] == "overbought":
            bearish_signals += 1
            reasoning.append("RSI indicates overbought condition")
            
        if signals["macd_signal"] == "bullish":
            bullish_signals += 1
            reasoning.append("MACD bullish crossover")
        else:
            bearish_signals += 1
            reasoning.append("MACD bearish signal")
            
        if signals["volume_trend"] == "high":
            bullish_signals += 0.5
            reasoning.append("Above average volume")
            
        # Calculate confidence and make decision
        total_signals = bullish_signals + bearish_signals
        confidence = abs(bullish_signals - bearish_signals) / total_signals if total_signals > 0 else 0
        
        if bullish_signals > bearish_signals and confidence >= self.confidence_threshold:
            action = "BUY"
        elif bearish_signals > bullish_signals and confidence >= self.confidence_threshold:
            action = "SELL"
        else:
            action = "HOLD"
            
        return {
            "action": action,
            "confidence": round(confidence, 3),
            "reasoning": reasoning,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals
        }


class RiskAgent:
    """Risk management agent that evaluates portfolio risk and position sizing"""
    
    def __init__(self):
        self.name = "Risk Agent"
        self.max_position_size = 0.1  # 10% max position size
        self.max_portfolio_risk = 0.02  # 2% max portfolio risk
        
    def evaluate_risk(self, portfolio: Dict, new_position: Dict) -> Dict:
        """Evaluate risk for a new position"""
        try:
            total_value = portfolio.get('total_value', 100000)
            current_positions = portfolio.get('positions', [])
            
            # Calculate position size
            suggested_position_size = self._calculate_position_size(
                total_value, new_position.get('confidence', 0.5)
            )
            
            # Risk metrics
            risk_metrics = {
                "suggested_position_size": suggested_position_size,
                "position_risk": suggested_position_size / total_value,
                "diversification_score": self._calculate_diversification(current_positions),
                "risk_level": "LOW",
                "warnings": []
            }
            
            # Risk warnings
            if risk_metrics["position_risk"] > self.max_position_size:
                risk_metrics["warnings"].append("Position size exceeds maximum limit")
                risk_metrics["risk_level"] = "HIGH"
                
            if len(current_positions) < 5:
                risk_metrics["warnings"].append("Portfolio lacks diversification")
                
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Risk Agent error: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_position_size(self, total_value: float, confidence: float) -> float:
        """Calculate optimal position size based on Kelly Criterion principles"""
        base_position = total_value * 0.05  # 5% base position
        confidence_multiplier = min(confidence * 2, 2.0)  # Max 2x multiplier
        return min(base_position * confidence_multiplier, total_value * self.max_position_size)
    
    def _calculate_diversification(self, positions: List) -> float:
        """Calculate portfolio diversification score"""
        if not positions:
            return 0.0
        
        # Simple diversification score based on number of positions
        num_positions = len(positions)
        if num_positions >= 10:
            return 1.0
        elif num_positions >= 5:
            return 0.7
        elif num_positions >= 3:
            return 0.5
        else:
            return 0.3


class SentimentAgent:
    """Sentiment analysis agent that analyzes market sentiment and news"""
    
    def __init__(self):
        self.name = "Sentiment Agent"
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        
    def analyze_sentiment(self, symbol: str) -> Dict:
        """Analyze market sentiment for a symbol"""
        try:
            sentiment_data = {
                "symbol": symbol,
                "overall_sentiment": "NEUTRAL",
                "sentiment_score": 0.0,
                "news_sentiment": "NEUTRAL",
                "social_sentiment": "NEUTRAL",
                "confidence": 0.5,
                "factors": []
            }
            
            # Try to get news sentiment from Alpha Vantage
            if self.alpha_vantage_key:
                news_sentiment = self._get_news_sentiment(symbol)
                sentiment_data.update(news_sentiment)
            
            # Market sentiment indicators
            market_sentiment = self._analyze_market_sentiment(symbol)
            sentiment_data.update(market_sentiment)
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Sentiment Agent error for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _get_news_sentiment(self, symbol: str) -> Dict:
        """Get news sentiment from Alpha Vantage"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'apikey': self.alpha_vantage_key,
                'limit': 50
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'feed' in data:
                sentiments = []
                for item in data['feed'][:10]:  # Analyze top 10 news items
                    if 'ticker_sentiment' in item:
                        for ticker_data in item['ticker_sentiment']:
                            if ticker_data['ticker'] == symbol:
                                sentiments.append(float(ticker_data['ticker_sentiment_score']))
                
                if sentiments:
                    avg_sentiment = np.mean(sentiments)
                    sentiment_label = "POSITIVE" if avg_sentiment > 0.1 else "NEGATIVE" if avg_sentiment < -0.1 else "NEUTRAL"
                    
                    return {
                        "news_sentiment": sentiment_label,
                        "sentiment_score": round(avg_sentiment, 3),
                        "news_count": len(sentiments),
                        "factors": [f"News sentiment: {sentiment_label}"]
                    }
            
            return {"news_sentiment": "NEUTRAL", "sentiment_score": 0.0}
            
        except Exception as e:
            logger.error(f"News sentiment error: {str(e)}")
            return {"news_sentiment": "NEUTRAL", "sentiment_score": 0.0}
    
    def _analyze_market_sentiment(self, symbol: str) -> Dict:
        """Analyze overall market sentiment indicators"""
        try:
            # Get stock data for sentiment analysis
            stock = yf.Ticker(symbol)
            data = stock.history(period="1mo")
            
            if data.empty:
                return {"overall_sentiment": "NEUTRAL"}
            
            # Price momentum
            price_change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
            
            # Volume analysis
            avg_volume = data['Volume'].mean()
            recent_volume = data['Volume'].iloc[-5:].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            factors = []
            sentiment_score = 0
            
            if price_change > 0.05:
                sentiment_score += 0.3
                factors.append("Strong positive price momentum")
            elif price_change < -0.05:
                sentiment_score -= 0.3
                factors.append("Negative price momentum")
                
            if volume_ratio > 1.2:
                sentiment_score += 0.2
                factors.append("Higher than average volume")
                
            # Determine overall sentiment
            if sentiment_score > 0.2:
                overall_sentiment = "POSITIVE"
            elif sentiment_score < -0.2:
                overall_sentiment = "NEGATIVE"
            else:
                overall_sentiment = "NEUTRAL"
                
            return {
                "overall_sentiment": overall_sentiment,
                "market_momentum": round(price_change * 100, 2),
                "volume_ratio": round(volume_ratio, 2),
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"Market sentiment error: {str(e)}")
            return {"overall_sentiment": "NEUTRAL"}


class PortfolioAgent:
    """Portfolio optimization agent that manages asset allocation and rebalancing"""
    
    def __init__(self):
        self.name = "Portfolio Agent"
        self.target_allocations = {
            "large_cap": 0.4,
            "mid_cap": 0.3,
            "small_cap": 0.2,
            "international": 0.1
        }
        
    def optimize_portfolio(self, current_portfolio: Dict, market_conditions: Dict) -> Dict:
        """Optimize portfolio allocation based on current conditions"""
        try:
            recommendations = {
                "rebalance_needed": False,
                "suggested_actions": [],
                "risk_adjusted_allocation": self.target_allocations.copy(),
                "efficiency_score": 0.8,
                "diversification_gaps": []
            }
            
            # Analyze current allocation
            current_allocation = self._analyze_current_allocation(current_portfolio)
            
            # Check for rebalancing needs
            rebalance_needed = self._check_rebalancing_needs(current_allocation)
            recommendations["rebalance_needed"] = rebalance_needed
            
            if rebalance_needed:
                recommendations["suggested_actions"] = self._generate_rebalancing_actions(
                    current_allocation, market_conditions
                )
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Portfolio Agent error: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_current_allocation(self, portfolio: Dict) -> Dict:
        """Analyze current portfolio allocation"""
        positions = portfolio.get('positions', [])
        total_value = portfolio.get('total_value', 0)
        
        allocation = {
            "large_cap": 0,
            "mid_cap": 0,
            "small_cap": 0,
            "international": 0
        }
        
        # Categorize positions (simplified categorization)
        for position in positions:
            symbol = position.get('symbol', '')
            value = position.get('value', 0)
            weight = value / total_value if total_value > 0 else 0
            
            # Simple categorization logic (in real implementation, use market cap data)
            if symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']:
                allocation["large_cap"] += weight
            elif symbol.endswith('.NS'):  # NSE stocks as international
                allocation["international"] += weight
            else:
                allocation["mid_cap"] += weight
                
        return allocation
    
    def _check_rebalancing_needs(self, current_allocation: Dict) -> bool:
        """Check if portfolio needs rebalancing"""
        threshold = 0.05  # 5% threshold
        
        for category, target in self.target_allocations.items():
            current = current_allocation.get(category, 0)
            if abs(current - target) > threshold:
                return True
                
        return False
    
    def _generate_rebalancing_actions(self, current_allocation: Dict, market_conditions: Dict) -> List[str]:
        """Generate specific rebalancing actions"""
        actions = []
        
        for category, target in self.target_allocations.items():
            current = current_allocation.get(category, 0)
            difference = target - current
            
            if abs(difference) > 0.05:  # 5% threshold
                if difference > 0:
                    actions.append(f"Increase {category} allocation by {difference:.1%}")
                else:
                    actions.append(f"Reduce {category} allocation by {abs(difference):.1%}")
                    
        return actions


class AgenticAICoordinator:
    """Main coordinator that orchestrates all AI agents"""
    
    def __init__(self):
        self.trading_agent = TradingAgent()
        self.risk_agent = RiskAgent()
        self.sentiment_agent = SentimentAgent()
        self.portfolio_agent = PortfolioAgent()
        
    def analyze_stock_comprehensive(self, symbol: str, portfolio: Dict = None) -> Dict:
        """Comprehensive stock analysis using all agents"""
        try:
            results = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "agents_analysis": {}
            }
            
            # Trading Agent Analysis
            trading_analysis = self.trading_agent.analyze_stock(symbol)
            results["agents_analysis"]["trading"] = trading_analysis
            
            # Sentiment Agent Analysis
            sentiment_analysis = self.sentiment_agent.analyze_sentiment(symbol)
            results["agents_analysis"]["sentiment"] = sentiment_analysis
            
            # Risk Agent Analysis (if portfolio provided)
            if portfolio:
                risk_analysis = self.risk_agent.evaluate_risk(portfolio, trading_analysis)
                results["agents_analysis"]["risk"] = risk_analysis
            else:
                results["agents_analysis"]["risk"] = {"risk_level": "MEDIUM"}
            
            # Final Recommendation
            final_recommendation = self._synthesize_recommendations(results["agents_analysis"])
            results["final_recommendation"] = final_recommendation
            
            return results
            
        except Exception as e:
            logger.error(f"Agentic AI Coordinator error: {str(e)}")
            return {"error": str(e)}
    
    def optimize_portfolio_comprehensive(self, portfolio: Dict) -> Dict:
        """Comprehensive portfolio optimization"""
        try:
            market_conditions = {"volatility": "MEDIUM", "trend": "NEUTRAL"}  # Simplified
            
            portfolio_optimization = self.portfolio_agent.optimize_portfolio(
                portfolio, market_conditions
            )
            
            return {
                "timestamp": datetime.now().isoformat(),
                "optimization": portfolio_optimization,
                "market_conditions": market_conditions
            }
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {str(e)}")
            return {"error": str(e)}
    
    def _synthesize_recommendations(self, agents_analysis: Dict) -> Dict:
        """Synthesize recommendations from all agents"""
        trading = agents_analysis.get("trading", {})
        sentiment = agents_analysis.get("sentiment", {})
        risk = agents_analysis.get("risk", {})
        
        # Weight different factors
        trading_weight = 0.4
        sentiment_weight = 0.3
        risk_weight = 0.3
        
        # Calculate overall confidence
        trading_confidence = trading.get("confidence", 0.5)
        sentiment_confidence = sentiment.get("confidence", 0.5)
        
        overall_confidence = (
            trading_confidence * trading_weight +
            sentiment_confidence * sentiment_weight
        )
        
        # Risk adjustment
        risk_level = risk.get("risk_level", "MEDIUM")
        if risk_level == "HIGH":
            overall_confidence *= 0.7
            
        # Final recommendation
        trading_action = trading.get("recommendation", "HOLD")
        sentiment_trend = sentiment.get("overall_sentiment", "NEUTRAL")
        
        if trading_action == "BUY" and sentiment_trend in ["POSITIVE", "NEUTRAL"] and overall_confidence > 0.6:
            final_action = "STRONG_BUY"
        elif trading_action == "BUY":
            final_action = "BUY"
        elif trading_action == "SELL" and sentiment_trend in ["NEGATIVE", "NEUTRAL"] and overall_confidence > 0.6:
            final_action = "STRONG_SELL"
        elif trading_action == "SELL":
            final_action = "SELL"
        else:
            final_action = "HOLD"
            
        return {
            "action": final_action,
            "confidence": round(overall_confidence, 3),
            "reasoning": f"Trading: {trading_action}, Sentiment: {sentiment_trend}, Risk: {risk_level}",
            "risk_level": risk_level
        }