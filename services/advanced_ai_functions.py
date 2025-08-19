"""
Advanced AI Advisor Functions
Provides specialized investment analysis functions using Perplexity API
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from services.perplexity_service import PerplexityService

logger = logging.getLogger(__name__)

class AdvancedAIFunctions:
    def __init__(self):
        self.perplexity = PerplexityService()
    
    def news_impact_analyzer(self, stock_symbols: Optional[List[str]] = None, portfolio_stocks: Optional[List[str]] = None) -> Dict:
        """
        Analyze breaking news impact on specific stocks or portfolio
        """
        try:
            if portfolio_stocks:
                stocks_text = ", ".join(portfolio_stocks)
                query = f"Analyze today's breaking news impact on Indian stocks: {stocks_text}. Provide sentiment analysis, price impact predictions, and trading recommendations for each stock."
            elif stock_symbols:
                stocks_text = ", ".join(stock_symbols)
                query = f"What is the latest news impact analysis for Indian stocks: {stocks_text}? Include sentiment score, potential price movement, and investment implications."
            else:
                query = "Analyze today's major market-moving news in Indian stock market. Include top 5 stocks most affected by news, sentiment analysis, and trading opportunities."
            
            response, usage = self.perplexity.get_investment_advice(query, [])
            
            return {
                "analysis": response,
                "function": "News Impact Analyzer",
                "timestamp": datetime.now().isoformat(),
                "usage": usage,
                "stocks_analyzed": portfolio_stocks or stock_symbols or "Market-wide analysis"
            }
            
        except Exception as e:
            logger.error(f"Error in news impact analyzer: {e}")
            return {
                "error": "Unable to analyze news impact at this time",
                "function": "News Impact Analyzer",
                "timestamp": datetime.now().isoformat()
            }
    
    def competitive_stock_comparison(self, primary_stock: str, sector: Optional[str] = None) -> Dict:
        """
        Compare a stock against its top competitors with AI analysis
        """
        try:
            if sector:
                query = f"Compare {primary_stock} against its top 4 competitors in {sector} sector. Provide detailed comparison of financial metrics, growth rates, valuations (P/E, P/B, EV/EBITDA), market position, and AI recommendation on which offers better value for investment."
            else:
                query = f"Compare Indian stock {primary_stock} against its top 4 main competitors. Include financial metrics comparison, growth analysis, valuation ratios, competitive advantages, and AI-powered investment recommendation with reasoning."
            
            response, usage = self.perplexity.get_investment_advice(query, [])
            
            return {
                "comparison": response,
                "function": "Competitive Stock Comparison", 
                "primary_stock": primary_stock,
                "sector": sector,
                "timestamp": datetime.now().isoformat(),
                "usage": usage
            }
            
        except Exception as e:
            logger.error(f"Error in competitive analysis: {e}")
            return {
                "error": "Unable to perform competitive analysis at this time",
                "function": "Competitive Stock Comparison",
                "primary_stock": primary_stock,
                "timestamp": datetime.now().isoformat()
            }
    
    def sector_rotation_predictor(self, current_sectors: Optional[List[str]] = None) -> Dict:
        """
        Predict sector rotation opportunities and timing signals
        """
        try:
            if current_sectors:
                sectors_text = ", ".join(current_sectors)
                query = f"Analyze sector rotation predictions for Indian market. Current focus sectors: {sectors_text}. Which sectors are likely to outperform next 3-6 months? Include economic indicators, rotation timing signals, and top stock picks for each recommended sector."
            else:
                query = "Predict sector rotation opportunities in Indian stock market for next 3-6 months. Which sectors are poised to outperform? Include economic indicators driving rotation, timing signals, and top 2-3 stock recommendations per sector with reasoning."
            
            response, usage = self.perplexity.get_investment_advice(query, [])
            
            return {
                "prediction": response,
                "function": "Sector Rotation Predictor",
                "analyzed_sectors": current_sectors,
                "prediction_horizon": "3-6 months",
                "timestamp": datetime.now().isoformat(),
                "usage": usage
            }
            
        except Exception as e:
            logger.error(f"Error in sector rotation prediction: {e}")
            return {
                "error": "Unable to generate sector rotation predictions at this time",
                "function": "Sector Rotation Predictor",
                "timestamp": datetime.now().isoformat()
            }
    
    def market_crash_opportunity_scanner(self, risk_tolerance: str = "moderate") -> Dict:
        """
        Identify quality stocks at discounted prices during market downturns
        """
        try:
            query = f"Scan for market crash opportunities in Indian stock market. Identify quality large-cap and mid-cap stocks trading at significant discounts due to recent market corrections. Include 'buy the dip' recommendations with conviction levels, intrinsic value estimates, and recovery potential analysis. Risk tolerance: {risk_tolerance}."
            
            response, usage = self.perplexity.get_investment_advice(query, [])
            
            return {
                "opportunities": response,
                "function": "Market Crash Opportunity Scanner",
                "risk_tolerance": risk_tolerance,
                "scan_date": datetime.now().isoformat(),
                "usage": usage
            }
            
        except Exception as e:
            logger.error(f"Error in crash opportunity scanner: {e}")
            return {
                "error": "Unable to scan for crash opportunities at this time",
                "function": "Market Crash Opportunity Scanner",
                "timestamp": datetime.now().isoformat()
            }
    
    def ipo_new_listing_analyzer(self, specific_ipo: Optional[str] = None) -> Dict:
        """
        Analyze upcoming IPOs and new listings with AI assessment
        """
        try:
            if specific_ipo:
                query = f"Analyze the upcoming IPO: {specific_ipo}. Provide detailed analysis including business model, financial performance, valuation assessment, risk factors, fair value estimate, and investment recommendation with reasoning."
            else:
                query = "Analyze upcoming IPOs and new listings in Indian stock market for next 2-3 months. Include business analysis, valuation assessment, risk-reward analysis, fair value estimates, and investment recommendations for each IPO with conviction levels."
            
            response, usage = self.perplexity.get_investment_advice(query, [])
            
            return {
                "analysis": response,
                "function": "IPO & New Listing Analyzer",
                "specific_ipo": specific_ipo,
                "analysis_scope": "2-3 months ahead",
                "timestamp": datetime.now().isoformat(),
                "usage": usage
            }
            
        except Exception as e:
            logger.error(f"Error in IPO analysis: {e}")
            return {
                "error": "Unable to analyze IPOs at this time",
                "function": "IPO & New Listing Analyzer",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_functions(self) -> List[Dict]:
        """
        Return list of available advanced AI functions
        """
        return [
            {
                "id": "news_impact",
                "name": "News Impact Analyzer",
                "description": "Monitor breaking news and assess impact on your holdings",
                "icon": "📰"
            },
            {
                "id": "competitive_comparison", 
                "name": "Competitive Stock Comparison",
                "description": "Compare stocks against top competitors with AI analysis",
                "icon": "⚖️"
            },
            {
                "id": "sector_rotation",
                "name": "Sector Rotation Predictor", 
                "description": "Identify sectors likely to outperform next",
                "icon": "🔄"
            },
            {
                "id": "crash_opportunities",
                "name": "Market Crash Opportunity Scanner",
                "description": "Find quality stocks at discounted prices",
                "icon": "🎯"
            },
            {
                "id": "ipo_analyzer",
                "name": "IPO & New Listing Analyzer",
                "description": "Get AI analysis of upcoming IPOs and new listings", 
                "icon": "🚀"
            }
        ]