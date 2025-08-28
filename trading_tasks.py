"""
Celery Background Tasks for Trading Engine
Handles long-running tasks like portfolio analysis, risk calculations, and data processing
"""

from celery import Celery
from datetime import datetime, timedelta
import logging
import json
import redis
import os
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Celery Configuration
app = Celery('trading_tasks')
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
    task_routes={
        'trading_tasks.analyze_portfolio': {'queue': 'portfolio'},
        'trading_tasks.calculate_risk_metrics': {'queue': 'risk'},
        'trading_tasks.sync_broker_data': {'queue': 'broker'},
        'trading_tasks.generate_trading_signals': {'queue': 'signals'},
    }
)

def calculate_portfolio_health(portfolio_data: Dict) -> Dict:
    """Calculate portfolio health metrics"""
    try:
        holdings = portfolio_data.get('holdings', {})
        if not holdings:
            return {"score": 0, "status": "empty"}
        
        # Simple health calculation
        total_value = sum(holding.get('value', 0) for holding in holdings.values())
        diversification_score = min(len(holdings) * 20, 100)  # Max 100 for 5+ stocks
        
        health_score = min(diversification_score, 100)
        
        return {
            "score": health_score,
            "status": "healthy" if health_score > 70 else "moderate" if health_score > 40 else "poor",
            "total_value": total_value,
            "num_holdings": len(holdings)
        }
    except Exception as e:
        logger.error(f"Portfolio health calculation failed: {e}")
        return {"score": 0, "status": "error"}

def calculate_portfolio_risk(portfolio_data: Dict) -> Dict:
    """Calculate portfolio risk metrics"""
    try:
        holdings = portfolio_data.get('holdings', {})
        
        # Calculate concentration risk
        total_value = sum(holding.get('value', 0) for holding in holdings.values())
        max_holding_weight = max(holding.get('value', 0) / total_value for holding in holdings.values()) if total_value > 0 else 0
        
        # Calculate beta (simplified)
        portfolio_beta = calculate_portfolio_beta(holdings)
        
        # Calculate overall risk score
        risk_score = calculate_risk_score({
            'beta': portfolio_beta,
            'concentration_risk': max_holding_weight
        })
        
        return {
            "var_95": 0.05,  # Placeholder
            "var_99": 0.01,  # Placeholder
            "beta": portfolio_beta,
            "sharpe_ratio": 0.8,  # Placeholder
            "max_drawdown": 0.15,  # Placeholder
            "concentration_risk": max_holding_weight,
            "sector_allocation": {},
            "risk_score": risk_score
        }
    except Exception as e:
        logger.error(f"Risk calculation failed: {e}")
        return {}

@app.task(bind=True, retry_on=(Exception,), default_retry_delay=60, max_retries=3)
def analyze_portfolio(self, user_id: str, portfolio_data: Dict) -> Dict:
    """
    Comprehensive portfolio analysis task
    """
    try:
        logger.info(f"Starting portfolio analysis for user {user_id}")
        
        # Import AI services
        from services.ai_agent_service import AgenticAICoordinator
        
        # Initialize services
        ai_coordinator = AgenticAICoordinator()
        
        # Perform comprehensive analysis
        analysis_result = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "portfolio_health": {},
            "risk_metrics": {},
            "ai_recommendations": {},
            "rebalancing_suggestions": []
        }
        
        # Calculate portfolio health score
        analysis_result["portfolio_health"] = calculate_portfolio_health(portfolio_data)
        
        # Calculate risk metrics
        analysis_result["risk_metrics"] = calculate_portfolio_risk(portfolio_data)
        
        # Get AI-powered recommendations
        for symbol in portfolio_data.get('holdings', {}):
            try:
                ai_analysis = ai_coordinator.analyze_with_agentic_ai(symbol, "comprehensive")
                analysis_result["ai_recommendations"][symbol] = ai_analysis
            except Exception as e:
                logger.warning(f"AI analysis failed for {symbol}: {e}")
        
        # Generate rebalancing suggestions
        analysis_result["rebalancing_suggestions"] = generate_rebalancing_suggestions(portfolio_data, analysis_result["risk_metrics"])
        
        # Cache results
        cache_key = f"portfolio_analysis:{user_id}"
        redis_client.setex(cache_key, 3600, json.dumps(analysis_result))  # Cache for 1 hour
        
        logger.info(f"Portfolio analysis completed for user {user_id}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Portfolio analysis failed for user {user_id}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True)
def calculate_risk_metrics(self, portfolio_data: Dict) -> Dict:
    """
    Calculate comprehensive risk metrics for portfolio
    """
    try:
        import numpy as np
        import pandas as pd
        
        holdings = portfolio_data.get('holdings', {})
        
        # Calculate portfolio-level risk metrics
        risk_metrics = {
            "var_95": 0,  # Value at Risk (95%)
            "var_99": 0,  # Value at Risk (99%)
            "beta": 0,    # Portfolio beta
            "sharpe_ratio": 0,  # Sharpe ratio
            "max_drawdown": 0,  # Maximum drawdown
            "concentration_risk": 0,  # Concentration risk
            "sector_allocation": {},  # Sector-wise allocation
            "risk_score": 0  # Overall risk score (1-10)
        }
        
        if not holdings:
            return risk_metrics
        
        # Calculate concentration risk
        total_value = sum(holding.get('value', 0) for holding in holdings.values())
        max_holding_weight = max(holding.get('value', 0) / total_value for holding in holdings.values()) if total_value > 0 else 0
        risk_metrics["concentration_risk"] = max_holding_weight
        
        # Calculate portfolio beta (simplified)
        portfolio_beta = calculate_portfolio_beta(holdings)
        risk_metrics["beta"] = portfolio_beta
        
        # Calculate overall risk score
        risk_score = calculate_risk_score(risk_metrics)
        risk_metrics["risk_score"] = risk_score
        
        return risk_metrics
        
    except Exception as e:
        logger.error(f"Risk calculation failed: {e}")
        return {}

def calculate_portfolio_beta(holdings: Dict) -> float:
    """Calculate portfolio beta"""
    try:
        # Simplified beta calculation
        # In production, use historical price data and market index correlation
        
        total_value = sum(holding.get('value', 0) for holding in holdings.values())
        if total_value == 0:
            return 1.0
        
        weighted_beta = 0
        for symbol, holding in holdings.items():
            weight = holding.get('value', 0) / total_value
            # Use sector-based beta estimates (simplified)
            sector_betas = {
                'TECHNOLOGY': 1.3,
                'FINANCE': 1.1,
                'HEALTHCARE': 0.9,
                'CONSUMER': 1.0,
                'ENERGY': 1.4,
                'DEFAULT': 1.0
            }
            
            sector = holding.get('sector', 'DEFAULT')
            beta = sector_betas.get(sector, 1.0)
            weighted_beta += weight * beta
        
        return round(weighted_beta, 2)
        
    except Exception as e:
        logger.error(f"Beta calculation failed: {e}")
        return 1.0

def calculate_risk_score(risk_metrics: Dict) -> int:
    """Calculate overall risk score (1-10)"""
    try:
        score = 5  # Base score
        
        # Adjust based on beta
        beta = risk_metrics.get('beta', 1.0)
        if beta > 1.5:
            score += 2
        elif beta > 1.2:
            score += 1
        elif beta < 0.8:
            score -= 1
        
        # Adjust based on concentration risk
        concentration = risk_metrics.get('concentration_risk', 0)
        if concentration > 0.5:  # More than 50% in single stock
            score += 2
        elif concentration > 0.3:  # More than 30% in single stock
            score += 1
        
        # Ensure score is within bounds
        return max(1, min(10, score))
        
    except Exception as e:
        logger.error(f"Risk score calculation failed: {e}")
        return 5

def generate_rebalancing_suggestions(portfolio_data: Dict, risk_metrics: Dict) -> List[Dict]:
    """Generate portfolio rebalancing suggestions"""
    try:
        suggestions = []
        holdings = portfolio_data.get('holdings', {})
        
        if not holdings:
            return suggestions
        
        total_value = sum(holding.get('value', 0) for holding in holdings.values())
        
        # Check for over-concentration
        for symbol, holding in holdings.items():
            weight = holding.get('value', 0) / total_value if total_value > 0 else 0
            
            if weight > 0.3:  # More than 30% in single stock
                suggestions.append({
                    "type": "REDUCE_POSITION",
                    "symbol": symbol,
                    "current_weight": round(weight * 100, 1),
                    "suggested_weight": 25.0,
                    "reason": "Reduce concentration risk",
                    "priority": "HIGH"
                })
        
        # Suggest diversification if portfolio has < 5 stocks
        if len(holdings) < 5:
            suggestions.append({
                "type": "DIVERSIFY",
                "reason": "Add more positions for better diversification",
                "suggested_sectors": ["TECHNOLOGY", "HEALTHCARE", "FINANCE"],
                "priority": "MEDIUM"
            })
        
        # Risk-based suggestions
        risk_score = risk_metrics.get('risk_score', 5)
        if risk_score > 7:
            suggestions.append({
                "type": "REDUCE_RISK",
                "reason": "Portfolio risk is high, consider defensive stocks",
                "suggested_actions": ["Add defensive stocks", "Reduce high-beta positions"],
                "priority": "HIGH"
            })
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Rebalancing suggestions failed: {e}")
        return []

@app.task(bind=True)
def sync_broker_data(self, user_id: str, broker_ids: List[str]) -> Dict:
    """
    Sync data from multiple brokers for a user
    """
    try:
        logger.info(f"Starting broker data sync for user {user_id}")
        
        sync_results = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "brokers_synced": 0,
            "total_brokers": len(broker_ids),
            "holdings": {},
            "positions": {},
            "orders": {},
            "sync_errors": []
        }
        
        for broker_id in broker_ids:
            try:
                # Placeholder for broker sync - implement based on your broker service
                sync_results["holdings"][broker_id] = []
                sync_results["positions"][broker_id] = []
                sync_results["orders"][broker_id] = []
                
                sync_results["brokers_synced"] += 1
                
            except Exception as e:
                error_msg = f"Broker {broker_id} sync failed: {str(e)}"
                sync_results["sync_errors"].append(error_msg)
                logger.warning(error_msg)
        
        # Cache consolidated data
        cache_key = f"broker_sync:{user_id}"
        redis_client.setex(cache_key, 1800, json.dumps(sync_results))  # Cache for 30 minutes
        
        logger.info(f"Broker sync completed for user {user_id}. Synced {sync_results['brokers_synced']}/{sync_results['total_brokers']} brokers")
        return sync_results
        
    except Exception as e:
        logger.error(f"Broker sync failed for user {user_id}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True)
def generate_trading_signals(self, symbols: List[str]) -> Dict:
    """
    Generate AI-powered trading signals for given symbols
    """
    try:
        logger.info(f"Generating trading signals for {len(symbols)} symbols")
        
        from services.ai_agent_service import AgenticAICoordinator
        
        ai_coordinator = AgenticAICoordinator()
        signals = {
            "timestamp": datetime.now().isoformat(),
            "signals": {},
            "market_sentiment": "NEUTRAL",
            "generated_count": 0
        }
        
        for symbol in symbols:
            try:
                # Get AI analysis
                analysis = ai_coordinator.analyze_with_agentic_ai(symbol, "trading_signal")
                
                if analysis and not analysis.get('error'):
                    # Extract trading signal
                    signal = extract_trading_signal(analysis)
                    if signal:
                        signals["signals"][symbol] = signal
                        signals["generated_count"] += 1
                        
            except Exception as e:
                logger.warning(f"Signal generation failed for {symbol}: {e}")
        
        # Determine overall market sentiment
        signals["market_sentiment"] = determine_market_sentiment(signals["signals"])
        
        # Cache signals
        cache_key = "trading_signals:latest"
        redis_client.setex(cache_key, 900, json.dumps(signals))  # Cache for 15 minutes
        
        logger.info(f"Generated {signals['generated_count']} trading signals")
        return signals
        
    except Exception as e:
        logger.error(f"Trading signal generation failed: {e}")
        raise self.retry(exc=e)

def extract_trading_signal(analysis: Dict) -> Optional[Dict]:
    """Extract trading signal from AI analysis"""
    try:
        # This would extract structured signals from AI analysis
        # Simplified implementation
        
        recommendation = analysis.get('recommendation', {})
        if not recommendation:
            return None
        
        signal = {
            "action": recommendation.get('action', 'HOLD'),
            "confidence": recommendation.get('confidence', 0),
            "target_price": recommendation.get('target_price'),
            "stop_loss": recommendation.get('stop_loss'),
            "time_horizon": recommendation.get('time_horizon', 'SHORT'),
            "reasoning": recommendation.get('reasoning', ''),
            "risk_level": recommendation.get('risk_level', 'MEDIUM')
        }
        
        # Only return signal if confidence is reasonable
        if signal["confidence"] > 60:
            return signal
        
        return None
        
    except Exception as e:
        logger.error(f"Signal extraction failed: {e}")
        return None

def determine_market_sentiment(signals: Dict) -> str:
    """Determine overall market sentiment from signals"""
    try:
        if not signals:
            return "NEUTRAL"
        
        buy_count = sum(1 for signal in signals.values() if signal.get('action') == 'BUY')
        sell_count = sum(1 for signal in signals.values() if signal.get('action') == 'SELL')
        total_signals = len(signals)
        
        if buy_count > total_signals * 0.6:
            return "BULLISH"
        elif sell_count > total_signals * 0.6:
            return "BEARISH"
        else:
            return "NEUTRAL"
            
    except Exception as e:
        logger.error(f"Sentiment determination failed: {e}")
        return "NEUTRAL"

# Periodic tasks
@app.task
def update_market_cache():
    """Update market data cache periodically"""
    try:
        from services.nse_realtime_service import NSERealTimeService
        
        nse_service = NSERealTimeService()
        
        # Update indices data
        indices_data = nse_service.get_nse_indices()
        if indices_data.get('success'):
            redis_client.setex("market:indices", 300, json.dumps(indices_data))
        
        # Update popular stocks
        popular_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
        for symbol in popular_stocks:
            stock_data = nse_service.get_stock_data(symbol)
            if stock_data.get('success'):
                redis_client.setex(f"market:stock:{symbol}", 300, json.dumps(stock_data))
        
        logger.info("Market cache updated successfully")
        
    except Exception as e:
        logger.error(f"Market cache update failed: {e}")

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-market-cache': {
        'task': 'trading_tasks.update_market_cache',
        'schedule': 60.0,  # Every minute during market hours
    },
}

if __name__ == '__main__':
    app.start()