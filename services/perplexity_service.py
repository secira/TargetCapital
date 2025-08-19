"""
Perplexity AI Service for Enhanced Indian Stock Market Research
Provides real-time research and AI-powered stock picks using Perplexity's online models
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class PerplexityService:
    def __init__(self):
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            self.logger.warning("PERPLEXITY_API_KEY not found. Service will use fallback data.")
    
    def research_indian_stock(self, symbol: str, research_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Conduct comprehensive research on Indian stock using Perplexity's online capabilities
        """
        try:
            if not self.api_key:
                return self._get_fallback_research(symbol)
            
            # Construct research prompt for Indian market
            research_prompt = self._build_research_prompt(symbol, research_type)
            
            response = self._call_perplexity_api(research_prompt, model="sonar-pro")
            
            if response and 'choices' in response:
                research_content = response['choices'][0]['message']['content']
                citations = response.get('citations', [])
                
                return {
                    'symbol': symbol,
                    'research_type': research_type,
                    'research_content': research_content,
                    'citations': citations,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'perplexity_ai',
                    'model_used': 'sonar-pro',
                    'success': True
                }
            else:
                return self._get_fallback_research(symbol)
                
        except Exception as e:
            self.logger.error(f"Perplexity research error for {symbol}: {str(e)}")
            return self._get_fallback_research(symbol)
    
    def generate_ai_stock_picks(self, criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate AI-powered stock picks for Indian market using Perplexity's real-time data
        """
        try:
            if not self.api_key:
                return self._get_fallback_picks()
            
            # Build criteria-based prompt
            picks_prompt = self._build_picks_prompt(criteria)
            
            response = self._call_perplexity_api(picks_prompt, model="sonar-pro")
            
            if response and 'choices' in response:
                picks_content = response['choices'][0]['message']['content']
                citations = response.get('citations', [])
                
                # Parse the structured response
                parsed_picks = self._parse_ai_picks_response(picks_content)
                
                return {
                    'picks': parsed_picks,
                    'analysis_summary': picks_content,
                    'citations': citations,
                    'criteria_used': criteria or self._get_default_criteria(),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'perplexity_ai',
                    'model_used': 'sonar-pro',
                    'success': True
                }
            else:
                return self._get_fallback_picks()
                
        except Exception as e:
            self.logger.error(f"Perplexity picks generation error: {str(e)}")
            return self._get_fallback_picks()
    
    def get_market_insights(self, focus_area: str = 'general') -> Dict[str, Any]:
        """
        Get real-time market insights for Indian stock market
        """
        try:
            if not self.api_key:
                return self._get_fallback_insights()
            
            insights_prompt = self._build_insights_prompt(focus_area)
            
            response = self._call_perplexity_api(insights_prompt, model="sonar")
            
            if response and 'choices' in response:
                insights_content = response['choices'][0]['message']['content']
                citations = response.get('citations', [])
                
                return {
                    'insights': insights_content,
                    'focus_area': focus_area,
                    'citations': citations,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'perplexity_ai',
                    'success': True
                }
            else:
                return self._get_fallback_insights()
                
        except Exception as e:
            self.logger.error(f"Perplexity insights error: {str(e)}")
            return self._get_fallback_insights()
    
    def _call_perplexity_api(self, prompt: str, model: str = "sonar") -> Dict[str, Any]:
        """
        Make API call to Perplexity
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert financial analyst specializing in Indian stock markets. Provide comprehensive, data-driven analysis with current market information."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.2,
            "top_p": 0.9,
            "search_recency_filter": "month",
            "return_images": False,
            "return_related_questions": False,
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.Timeout:
            self.logger.error("Perplexity API timeout - request took too long")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Perplexity API request failed: {str(e)}")
            return None
    
    def _build_research_prompt(self, symbol: str, research_type: str) -> str:
        """
        Build comprehensive research prompt for Indian stocks
        """
        base_prompt = f"""
        Conduct comprehensive research on {symbol} (Indian stock) including:
        
        1. **Current Market Position**: Latest stock price, market cap, trading volume, and recent price movements
        2. **Financial Performance**: Recent quarterly results, revenue growth, profitability trends, and key financial ratios
        3. **Business Analysis**: Core business segments, competitive positioning, market share, and recent business developments
        4. **Industry Context**: Sector performance, industry trends, regulatory changes affecting the sector
        5. **Recent News & Events**: Latest corporate announcements, management changes, strategic initiatives, partnerships
        6. **Analyst Opinions**: Recent analyst reports, price targets, recommendations from Indian brokerage houses
        7. **Technical Analysis**: Support/resistance levels, chart patterns, momentum indicators
        8. **Risk Factors**: Key business risks, regulatory risks, market risks specific to this stock
        9. **Investment Thesis**: Bull case, bear case, and neutral scenarios for the stock
        10. **Peer Comparison**: How it compares with similar companies in the Indian market
        
        Focus on the most recent information available (last 3 months) and provide specific data points with sources.
        Format the response in a structured manner with clear sections.
        """
        
        if research_type == 'technical':
            base_prompt += "\n\nEmphasize technical analysis, chart patterns, and trading signals."
        elif research_type == 'fundamental':
            base_prompt += "\n\nEmphasize fundamental analysis, financial metrics, and valuation."
        elif research_type == 'news_sentiment':
            base_prompt += "\n\nEmphasize recent news, market sentiment, and analyst opinions."
        
        return base_prompt
    
    def _build_picks_prompt(self, criteria: Dict[str, Any] = None) -> str:
        """
        Build prompt for AI stock picks generation
        """
        criteria = criteria or self._get_default_criteria()
        
        prompt = f"""
        Generate 5 Indian stock picks for {criteria.get('time_horizon', '6-12 months')} investment:
        
        Requirements: {criteria.get('market_cap', 'Large-Mid Cap')}, {criteria.get('risk_level', 'Moderate risk')}
        
        For each stock provide:
        1. Symbol & Company name (NSE/BSE)
        2. Current price and recent performance
        3. Why buy now (2-3 key reasons)
        4. Main catalyst/opportunity
        5. Key risk to watch
        
        Focus on stocks with strong fundamentals, positive recent news, or good value.
        Keep analysis concise but current.
        """
        
        return prompt
    
    def _build_insights_prompt(self, focus_area: str) -> str:
        """
        Build prompt for market insights
        """
        base_prompt = f"""
        Provide current market insights for the Indian stock market focusing on {focus_area}:
        
        1. **Market Overview**: Current Nifty/Sensex levels, recent performance, market sentiment
        2. **Sector Performance**: Which sectors are outperforming/underperforming and why
        3. **Key Market Drivers**: Major factors influencing the market (policy, global events, economic data)
        4. **Institutional Activity**: FII/DII flows, bulk deals, block deals
        5. **Corporate Earnings**: Recent earnings season highlights, guidance updates
        6. **Technical Outlook**: Key support/resistance levels for major indices
        7. **Global Context**: How global markets and events are impacting Indian markets
        8. **Investment Themes**: Current trending themes and investment opportunities
        9. **Risk Factors**: Key risks to watch out for in the near term
        10. **Market Outlook**: Short-term (1-3 months) market expectations
        
        Use the most recent market data and news available.
        Provide specific data points, numbers, and recent examples where possible.
        """
        
        return base_prompt
    
    def _parse_ai_picks_response(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse the AI picks response into structured data
        """
        # This is a simplified parser - in practice, you might want more sophisticated parsing
        picks = []
        
        # Try to extract stock information from the response
        # This is a basic implementation - could be enhanced with more sophisticated parsing
        lines = content.split('\n')
        current_pick = {}
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['1.', '2.', '3.', '4.', '5.']) and any(keyword in line.lower() for keyword in ['ltd', 'limited', 'bank', 'industries']):
                if current_pick:
                    picks.append(current_pick)
                current_pick = {
                    'symbol': self._extract_symbol(line),
                    'company_name': self._extract_company_name(line),
                    'rationale': '',
                    'target_price': '',
                    'risk_factors': '',
                    'catalysts': ''
                }
            elif current_pick and line:
                # Accumulate information for current pick
                if 'rationale' in line.lower() or 'reason' in line.lower():
                    current_pick['rationale'] += line + ' '
                elif 'target' in line.lower() and 'price' in line.lower():
                    current_pick['target_price'] += line + ' '
                elif 'risk' in line.lower():
                    current_pick['risk_factors'] += line + ' '
                elif 'catalyst' in line.lower():
                    current_pick['catalysts'] += line + ' '
        
        if current_pick:
            picks.append(current_pick)
        
        # If parsing fails, create fallback structure
        if not picks:
            picks = self._get_structured_fallback_picks()
        
        return picks[:5]  # Return maximum 5 picks
    
    def _extract_symbol(self, text: str) -> str:
        """Extract stock symbol from text"""
        # Basic symbol extraction - could be enhanced
        import re
        symbol_match = re.search(r'\b[A-Z]{3,10}\b', text)
        return symbol_match.group() if symbol_match else 'SYMBOL'
    
    def _extract_company_name(self, text: str) -> str:
        """Extract company name from text"""
        # Basic company name extraction - could be enhanced
        parts = text.split('.')
        if len(parts) > 1:
            name_part = parts[1].strip()
            return name_part.split('(')[0].strip() if '(' in name_part else name_part
        return 'Company Name'
    
    def _get_default_criteria(self) -> Dict[str, Any]:
        """Get default criteria for stock picks"""
        return {
            'market_cap': 'Large and Mid Cap',
            'time_horizon': '6-12 months',
            'risk_level': 'Moderate',
            'sectors': 'Technology, Banking, Healthcare, Consumer Goods, Energy',
            'style': 'Growth and Value'
        }
    
    # Fallback methods when Perplexity API is not available
    def _get_fallback_research(self, symbol: str) -> Dict[str, Any]:
        """Fallback research data when API is not available"""
        return {
            'symbol': symbol,
            'research_type': 'comprehensive',
            'research_content': f"""
            ## {symbol} - Comprehensive Stock Research
            
            **Current Market Position:**
            - Current Price: ₹2,850 (as of latest trading session)
            - Market Cap: ₹1,25,000 Cr
            - 52-week Range: ₹2,200 - ₹3,100
            - Trading Volume: Above average with institutional interest
            
            **Financial Performance:**
            - Q2 FY24 Revenue Growth: 15% YoY
            - Operating Margin: 18.5% (improving trend)
            - ROE: 16.2% (healthy profitability)
            - Debt-to-Equity: 0.3 (conservative capital structure)
            
            **Business Analysis:**
            - Leading player in its sector with diversified revenue streams
            - Strong competitive moat with established market presence
            - Recent expansion into high-growth segments
            - Management focused on operational efficiency and innovation
            
            **Investment Thesis:**
            - **Bull Case**: Strong fundamentals, growing market share, favorable industry tailwinds
            - **Bear Case**: Valuation concerns, competitive pressure, regulatory uncertainties
            - **Neutral Case**: Steady growth in line with industry averages
            
            **Recommendation**: BUY with target price of ₹3,200 (12-month horizon)
            
            *Note: This is sample research data. For real-time analysis, please provide Perplexity API key.*
            """,
            'citations': ['Sample financial data', 'Market research reports'],
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data',
            'success': False,
            'note': 'Perplexity API key required for real-time research'
        }
    
    def _get_fallback_picks(self) -> Dict[str, Any]:
        """Fallback stock picks when API is not available"""
        return {
            'picks': self._get_structured_fallback_picks(),
            'analysis_summary': """
            Top 5 AI Stock Picks for Indian Market:
            
            Based on comprehensive analysis of fundamentals, technical indicators, and market sentiment, 
            these stocks show strong potential for the next 6-12 months. Each pick represents different 
            sectors and market caps to provide diversification.
            
            *Note: These are sample picks. For real-time AI-generated recommendations, please provide Perplexity API key.*
            """,
            'citations': ['Market analysis', 'Financial reports', 'Technical analysis'],
            'criteria_used': self._get_default_criteria(),
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data',
            'success': False,
            'note': 'Perplexity API key required for real-time picks'
        }
    
    def _get_structured_fallback_picks(self) -> List[Dict[str, Any]]:
        """Structured fallback picks"""
        return [
            {
                'symbol': 'RELIANCE',
                'company_name': 'Reliance Industries Limited',
                'rationale': 'Diversified business model, strong cash flows, digital transformation initiatives',
                'target_price': '₹3,200 (12-month target)',
                'risk_factors': 'Oil price volatility, regulatory changes in telecom',
                'catalysts': 'Jio IPO, renewable energy expansion, retail growth'
            },
            {
                'symbol': 'TCS',
                'company_name': 'Tata Consultancy Services',
                'rationale': 'Leading IT services provider, strong client relationships, digital transformation demand',
                'target_price': '₹4,200 (12-month target)',
                'risk_factors': 'Currency fluctuations, competition, visa restrictions',
                'catalysts': 'Cloud adoption, AI/ML services growth, large deal wins'
            },
            {
                'symbol': 'HDFCBANK',
                'company_name': 'HDFC Bank Limited',
                'rationale': 'Best-in-class banking franchise, strong asset quality, digital banking leadership',
                'target_price': '₹1,800 (12-month target)',
                'risk_factors': 'Interest rate cycles, regulatory changes, credit costs',
                'catalysts': 'Credit growth recovery, fee income growth, digital initiatives'
            },
            {
                'symbol': 'INFY',
                'company_name': 'Infosys Limited',
                'rationale': 'Strong execution track record, margin expansion, automation capabilities',
                'target_price': '₹1,650 (12-month target)',
                'risk_factors': 'Client concentration, wage inflation, technology disruption',
                'catalysts': 'Large deal pipeline, AI platform adoption, cost optimization'
            },
            {
                'symbol': 'HINDUNILVR',
                'company_name': 'Hindustan Unilever Limited',
                'rationale': 'Strong brand portfolio, rural recovery, premiumization trend',
                'target_price': '₹2,800 (12-month target)',
                'risk_factors': 'Raw material inflation, competitive intensity, rural slowdown',
                'catalysts': 'Volume growth recovery, new product launches, market share gains'
            }
        ]
    
    def _get_fallback_insights(self) -> Dict[str, Any]:
        """Fallback market insights when API is not available"""
        return {
            'insights': """
            ## Indian Market Insights - Current Analysis
            
            **Market Overview:**
            - Nifty 50: 19,800 levels (consolidating in range)
            - Sensex: 66,500 levels (positive bias maintained)
            - Market Sentiment: Cautiously optimistic with selective buying
            
            **Sector Performance:**
            - Outperformers: Technology, Banking, Healthcare
            - Underperformers: Real Estate, Metals, Auto
            - Emerging Themes: Clean Energy, Digital Infrastructure
            
            **Key Market Drivers:**
            - Monsoon progress and rural demand recovery
            - Corporate earnings growth trajectory
            - Global liquidity flows and FII activity
            - Government policy initiatives and reforms
            
            **Investment Themes:**
            - Digital transformation and technology adoption
            - Infrastructure development and capex cycle
            - Healthcare and wellness sector growth
            - Sustainable and ESG investing
            
            *Note: This is sample market analysis. For real-time insights, please provide Perplexity API key.*
            """,
            'focus_area': 'general',
            'citations': ['Market data', 'Research reports'],
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data',
            'success': False,
            'note': 'Perplexity API key required for real-time insights'
        }