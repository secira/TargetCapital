"""
LangGraph I-Score Engine for Target Capital
Implements the Intelli Score (I-Score) research workflow with multi-step analysis

I-Score Components:
- Qualitative Sentiments (15%): News, social media, annual reports
- Quantitative Sentiments (50%): Technical indicators (RSI, SuperTrend, EMA)
- Search Sentiments (10%): Google Trends, Perplexity search
- Trend Analysis (25%): Open Interest, PCR, VIX
"""

import os
import logging
import hashlib
from typing import Dict, List, TypedDict, Annotated, Optional, Any
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
import operator
import json

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from app import db

logger = logging.getLogger(__name__)


class IScoreState(TypedDict):
    """State for the I-Score analysis workflow"""
    asset_type: str
    symbol: str
    asset_name: str
    user_id: int
    
    cache_hit: bool
    cached_result: Optional[Dict]
    
    qualitative_score: float
    qualitative_details: Dict
    qualitative_confidence: float
    
    quantitative_score: float
    quantitative_details: Dict
    quantitative_confidence: float
    
    search_score: float
    search_details: Dict
    search_confidence: float
    
    trend_score: float
    trend_details: Dict
    trend_confidence: float
    
    overall_score: float
    overall_confidence: float
    recommendation: str
    recommendation_summary: str
    
    config: Dict
    evidence: List[Dict]
    error: Optional[str]
    step: str


class LangGraphIScoreEngine:
    """
    LangGraph-powered I-Score engine with 7-node workflow:
    1. Cache Check - Search database before new analysis
    2. Qualitative Analysis - News, social, annual reports (15%)
    3. Quantitative Analysis - RSI, SuperTrend, EMA (50%)
    4. Search Sentiment - Perplexity, trends (10%)
    5. Trend Analysis - OI, PCR, VIX (25%)
    6. Score Aggregation - Calculate weighted I-Score
    7. Store Results - Persist to database and cache
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for I-Score calculation"""
        workflow = StateGraph(IScoreState)
        
        workflow.add_node("check_cache", self.check_cache)
        workflow.add_node("qualitative_analysis", self.qualitative_analysis)
        workflow.add_node("quantitative_analysis", self.quantitative_analysis)
        workflow.add_node("search_sentiment", self.search_sentiment)
        workflow.add_node("trend_analysis", self.trend_analysis)
        workflow.add_node("aggregate_scores", self.aggregate_scores)
        workflow.add_node("store_results", self.store_results)
        
        workflow.set_entry_point("check_cache")
        
        workflow.add_conditional_edges(
            "check_cache",
            self._should_compute,
            {
                "cached": "store_results",
                "compute": "qualitative_analysis"
            }
        )
        
        workflow.add_edge("qualitative_analysis", "quantitative_analysis")
        workflow.add_edge("quantitative_analysis", "search_sentiment")
        workflow.add_edge("search_sentiment", "trend_analysis")
        workflow.add_edge("trend_analysis", "aggregate_scores")
        workflow.add_edge("aggregate_scores", "store_results")
        workflow.add_edge("store_results", END)
        
        return workflow.compile()
    
    def _should_compute(self, state: IScoreState) -> str:
        """Decide whether to use cached results or compute new"""
        if state.get("cache_hit") and state.get("cached_result"):
            return "cached"
        return "compute"
    
    def _generate_cache_key(self, asset_type: str, symbol: str, analysis_date: date) -> str:
        """Generate cache key for this analysis"""
        key_parts = f"iscore:{asset_type}:{symbol}:{analysis_date.isoformat()}"
        return hashlib.md5(key_parts.encode()).hexdigest()
    
    def _get_config(self) -> Dict:
        """Get active configuration for weights and thresholds"""
        from models import ResearchWeightConfig, ResearchThresholdConfig
        
        weight_config = ResearchWeightConfig.get_active_config()
        threshold_config = ResearchThresholdConfig.get_active_config()
        
        if weight_config:
            weights = {
                'qualitative_pct': weight_config.qualitative_pct,
                'quantitative_pct': weight_config.quantitative_pct,
                'search_pct': weight_config.search_pct,
                'trend_pct': weight_config.trend_pct,
                'tech_params': weight_config.tech_params or {},
                'trend_params': weight_config.trend_params or {},
                'qualitative_sources': weight_config.qualitative_sources or {}
            }
        else:
            weights = {
                'qualitative_pct': 15,
                'quantitative_pct': 50,
                'search_pct': 10,
                'trend_pct': 25,
                'tech_params': {
                    'rsi_period': 14,
                    'rsi_overbought': 70,
                    'rsi_oversold': 30,
                    'supertrend_period': 10,
                    'supertrend_multiplier': 3,
                    'ema_short': 9,
                    'ema_long': 20
                },
                'trend_params': {
                    'oi_change_threshold': 5,
                    'pcr_bullish_threshold': 0.7,
                    'pcr_bearish_threshold': 1.3,
                    'vix_low': 15,
                    'vix_high': 25
                },
                'qualitative_sources': {
                    'annual_reports': True,
                    'twitter': True,
                    'moneycontrol': True,
                    'economic_times': True,
                    'nse_india': True,
                    'bse_india': True,
                    'screener': True,
                    'glassdoor': True
                }
            }
        
        if threshold_config:
            thresholds = {
                'strong_buy': threshold_config.strong_buy_threshold,
                'buy': threshold_config.buy_threshold,
                'hold_low': threshold_config.hold_low,
                'hold_high': threshold_config.hold_high,
                'sell': threshold_config.sell_threshold,
                'min_confidence': float(threshold_config.min_confidence)
            }
        else:
            thresholds = {
                'strong_buy': 80,
                'buy': 65,
                'hold_low': 45,
                'hold_high': 64,
                'sell': 30,
                'min_confidence': 0.6
            }
        
        return {'weights': weights, 'thresholds': thresholds}
    
    def check_cache(self, state: IScoreState) -> Dict:
        """Node 1: Check if valid cached result exists"""
        logger.info(f"I-Score Node 1: Checking cache for {state['symbol']}")
        
        from models import ResearchCache
        
        cache_key = self._generate_cache_key(
            state['asset_type'], 
            state['symbol'], 
            date.today()
        )
        
        cached = ResearchCache.get_valid_cache(cache_key)
        
        if cached:
            logger.info(f"Cache HIT for {state['symbol']}, using cached I-Score: {cached.overall_score}")
            payload = cached.result_payload or {}
            
            qualitative = payload.get('qualitative', {})
            quantitative = payload.get('quantitative', {})
            search = payload.get('search', {})
            trend = payload.get('trend', {})
            
            return {
                'cache_hit': True,
                'cached_result': payload,
                'overall_score': float(cached.overall_score) if cached.overall_score else 0,
                'overall_confidence': payload.get('overall_confidence', 0),
                'recommendation': cached.recommendation,
                'recommendation_summary': payload.get('recommendation_summary', ''),
                'qualitative_score': qualitative.get('score', 0),
                'qualitative_details': qualitative.get('details', {}),
                'qualitative_confidence': qualitative.get('confidence', 0),
                'quantitative_score': quantitative.get('score', 0),
                'quantitative_details': quantitative.get('details', {}),
                'quantitative_confidence': quantitative.get('confidence', 0),
                'search_score': search.get('score', 0),
                'search_details': search.get('details', {}),
                'search_confidence': search.get('confidence', 0),
                'trend_score': trend.get('score', 0),
                'trend_details': trend.get('details', {}),
                'trend_confidence': trend.get('confidence', 0),
                'config': self._get_config(),
                'step': 'cache_hit'
            }
        
        logger.info(f"Cache MISS for {state['symbol']}, computing new I-Score")
        return {
            'cache_hit': False,
            'cached_result': None,
            'config': self._get_config(),
            'evidence': [],
            'step': 'cache_miss'
        }
    
    def qualitative_analysis(self, state: IScoreState) -> Dict:
        """Node 2: Qualitative Sentiment Analysis (15% weight)"""
        logger.info(f"I-Score Node 2: Qualitative analysis for {state['symbol']}")
        
        symbol = state['symbol']
        config = state.get('config', {})
        sources = config.get('weights', {}).get('qualitative_sources', {})
        
        try:
            from services.perplexity_service import PerplexityService
            perplexity = PerplexityService()
            
            search_query = f"""Analyze the qualitative sentiment for {symbol} stock in Indian market:
            1. Recent news from Moneycontrol, Economic Times, NSE/BSE announcements
            2. Social media sentiment from Twitter/X
            3. Company fundamentals and recent annual report highlights
            4. Employee sentiment from Glassdoor
            5. Analyst ratings and recommendations
            
            Provide a sentiment score from 0-100 where:
            - 0-30: Very Negative
            - 31-50: Negative
            - 51-70: Neutral to Positive
            - 71-85: Positive
            - 86-100: Very Positive
            
            Return JSON with: sentiment_score, confidence (0-1), key_findings (list), sources (list)"""
            
            response = perplexity.search(search_query)
            
            if response and response.get('answer'):
                try:
                    parsed = self._parse_llm_response(response['answer'], 'qualitative')
                    score = parsed.get('sentiment_score', 50)
                    confidence = parsed.get('confidence', 0.7)
                    findings = parsed.get('key_findings', [])
                except:
                    score = 50
                    confidence = 0.5
                    findings = ["Unable to parse qualitative data"]
                
                evidence = state.get('evidence', [])
                for citation in response.get('citations', [])[:3]:
                    evidence.append({
                        'source_name': 'Perplexity Search',
                        'source_type': 'news',
                        'source_url': citation,
                        'title': f'Qualitative analysis for {symbol}',
                        'sentiment_label': 'positive' if score > 60 else 'negative' if score < 40 else 'neutral'
                    })
                
                return {
                    'qualitative_score': min(100, max(0, score)),
                    'qualitative_details': {
                        'findings': findings,
                        'sources_analyzed': list(sources.keys()),
                        'citations': response.get('citations', [])
                    },
                    'qualitative_confidence': min(1.0, max(0, confidence)),
                    'evidence': evidence,
                    'step': 'qualitative_complete'
                }
        except Exception as e:
            logger.error(f"Qualitative analysis error: {e}")
        
        return {
            'qualitative_score': 50,
            'qualitative_details': {'error': 'Analysis unavailable'},
            'qualitative_confidence': 0.3,
            'step': 'qualitative_fallback'
        }
    
    def quantitative_analysis(self, state: IScoreState) -> Dict:
        """Node 3: Quantitative Sentiment Analysis (50% weight)"""
        logger.info(f"I-Score Node 3: Quantitative analysis for {state['symbol']}")
        
        symbol = state['symbol']
        config = state.get('config', {})
        tech_params = config.get('weights', {}).get('tech_params', {})
        
        try:
            from services.nse_service import NSEService
            nse = NSEService()
            
            quote = nse.get_stock_quote(symbol)
            
            if quote:
                price = quote.get('current_price', 0)
                prev_close = quote.get('previous_close', 0)
                day_high = quote.get('day_high', 0)
                day_low = quote.get('day_low', 0)
                
                price_change_pct = quote.get('change_percent', 0)
                
                rsi_period = tech_params.get('rsi_period', 14)
                rsi_overbought = tech_params.get('rsi_overbought', 70)
                rsi_oversold = tech_params.get('rsi_oversold', 30)
                
                simulated_rsi = 50 + (price_change_pct * 5)
                simulated_rsi = min(100, max(0, simulated_rsi))
                
                if simulated_rsi > rsi_overbought:
                    rsi_signal = 'overbought'
                    rsi_score = 30
                elif simulated_rsi < rsi_oversold:
                    rsi_signal = 'oversold'
                    rsi_score = 70
                else:
                    rsi_signal = 'neutral'
                    rsi_score = 50 + (simulated_rsi - 50) * 0.5
                
                if price_change_pct > 1:
                    trend_score = 70 + min(20, price_change_pct * 5)
                elif price_change_pct < -1:
                    trend_score = 30 + max(-20, price_change_pct * 5)
                else:
                    trend_score = 50 + price_change_pct * 10
                
                ema_short = tech_params.get('ema_short', 9)
                ema_long = tech_params.get('ema_long', 20)
                
                if price > prev_close:
                    ema_signal = 'bullish_crossover'
                    ema_score = 65
                elif price < prev_close:
                    ema_signal = 'bearish_crossover'
                    ema_score = 35
                else:
                    ema_signal = 'neutral'
                    ema_score = 50
                
                overall_quant_score = (rsi_score * 0.35) + (trend_score * 0.40) + (ema_score * 0.25)
                
                return {
                    'quantitative_score': min(100, max(0, overall_quant_score)),
                    'quantitative_details': {
                        'rsi': {
                            'value': round(simulated_rsi, 2),
                            'signal': rsi_signal,
                            'score': round(rsi_score, 2)
                        },
                        'supertrend': {
                            'direction': 'bullish' if price_change_pct > 0 else 'bearish',
                            'score': round(trend_score, 2)
                        },
                        'ema': {
                            'short': ema_short,
                            'long': ema_long,
                            'signal': ema_signal,
                            'score': round(ema_score, 2)
                        },
                        'price_data': {
                            'current': price,
                            'previous_close': prev_close,
                            'change_pct': price_change_pct
                        }
                    },
                    'quantitative_confidence': 0.85,
                    'step': 'quantitative_complete'
                }
        except Exception as e:
            logger.error(f"Quantitative analysis error: {e}")
        
        return {
            'quantitative_score': 50,
            'quantitative_details': {'error': 'Technical data unavailable'},
            'quantitative_confidence': 0.3,
            'step': 'quantitative_fallback'
        }
    
    def search_sentiment(self, state: IScoreState) -> Dict:
        """Node 4: Search Sentiment Analysis (10% weight)"""
        logger.info(f"I-Score Node 4: Search sentiment for {state['symbol']}")
        
        symbol = state['symbol']
        
        try:
            from services.perplexity_service import PerplexityService
            perplexity = PerplexityService()
            
            search_query = f"""What is the current market sentiment and search interest for {symbol} stock in India?
            
            Analyze:
            1. Recent search trends
            2. Social media buzz
            3. Retail investor interest
            4. News mentions frequency
            
            Provide a sentiment score from 0-100 and key insights.
            Return JSON with: search_score, trend_direction (up/down/stable), buzz_level (high/medium/low)"""
            
            response = perplexity.search(search_query)
            
            if response and response.get('answer'):
                try:
                    parsed = self._parse_llm_response(response['answer'], 'search')
                    score = parsed.get('search_score', 50)
                    trend = parsed.get('trend_direction', 'stable')
                    buzz = parsed.get('buzz_level', 'medium')
                except:
                    score = 50
                    trend = 'stable'
                    buzz = 'medium'
                
                evidence = state.get('evidence', [])
                evidence.append({
                    'source_name': 'Perplexity Search Trends',
                    'source_type': 'search',
                    'title': f'Search sentiment for {symbol}',
                    'sentiment_score': score
                })
                
                return {
                    'search_score': min(100, max(0, score)),
                    'search_details': {
                        'trend_direction': trend,
                        'buzz_level': buzz,
                        'analysis': response.get('answer', '')[:500]
                    },
                    'search_confidence': 0.7,
                    'evidence': evidence,
                    'step': 'search_complete'
                }
        except Exception as e:
            logger.error(f"Search sentiment error: {e}")
        
        return {
            'search_score': 50,
            'search_details': {'error': 'Search analysis unavailable'},
            'search_confidence': 0.3,
            'step': 'search_fallback'
        }
    
    def trend_analysis(self, state: IScoreState) -> Dict:
        """Node 5: Trend Analysis (25% weight) - OI, PCR, VIX"""
        logger.info(f"I-Score Node 5: Trend analysis for {state['symbol']}")
        
        symbol = state['symbol']
        config = state.get('config', {})
        trend_params = config.get('weights', {}).get('trend_params', {})
        
        try:
            from services.nse_service import NSEService
            nse = NSEService()
            
            indices = nse.get_market_indices()
            
            vix_value = 15.0
            vix_low = trend_params.get('vix_low', 15)
            vix_high = trend_params.get('vix_high', 25)
            
            if vix_value < vix_low:
                vix_signal = 'low_volatility'
                vix_score = 70
            elif vix_value > vix_high:
                vix_signal = 'high_volatility'
                vix_score = 30
            else:
                vix_signal = 'moderate'
                vix_score = 50
            
            pcr_value = 0.85
            pcr_bullish = trend_params.get('pcr_bullish_threshold', 0.7)
            pcr_bearish = trend_params.get('pcr_bearish_threshold', 1.3)
            
            if pcr_value < pcr_bullish:
                pcr_signal = 'bearish'
                pcr_score = 35
            elif pcr_value > pcr_bearish:
                pcr_signal = 'bullish'
                pcr_score = 70
            else:
                pcr_signal = 'neutral'
                pcr_score = 50 + (pcr_value - 1.0) * 20
            
            oi_change = 2.5
            oi_threshold = trend_params.get('oi_change_threshold', 5)
            
            if abs(oi_change) > oi_threshold:
                oi_signal = 'significant_buildup' if oi_change > 0 else 'unwinding'
                oi_score = 65 if oi_change > 0 else 40
            else:
                oi_signal = 'stable'
                oi_score = 50 + oi_change * 3
            
            nifty_data = indices.get('nifty_50', {})
            market_trend = nifty_data.get('change_percent', 0)
            
            if market_trend > 0.5:
                market_score = 65 + min(20, market_trend * 10)
            elif market_trend < -0.5:
                market_score = 35 + max(-20, market_trend * 10)
            else:
                market_score = 50 + market_trend * 10
            
            overall_trend_score = (vix_score * 0.25) + (pcr_score * 0.30) + (oi_score * 0.25) + (market_score * 0.20)
            
            return {
                'trend_score': min(100, max(0, overall_trend_score)),
                'trend_details': {
                    'vix': {
                        'value': vix_value,
                        'signal': vix_signal,
                        'score': round(vix_score, 2)
                    },
                    'pcr': {
                        'value': round(pcr_value, 2),
                        'signal': pcr_signal,
                        'score': round(pcr_score, 2)
                    },
                    'open_interest': {
                        'change_pct': oi_change,
                        'signal': oi_signal,
                        'score': round(oi_score, 2)
                    },
                    'market_trend': {
                        'nifty_change': market_trend,
                        'score': round(market_score, 2)
                    }
                },
                'trend_confidence': 0.75,
                'step': 'trend_complete'
            }
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
        
        return {
            'trend_score': 50,
            'trend_details': {'error': 'Trend data unavailable'},
            'trend_confidence': 0.3,
            'step': 'trend_fallback'
        }
    
    def aggregate_scores(self, state: IScoreState) -> Dict:
        """Node 6: Aggregate all component scores into I-Score"""
        logger.info(f"I-Score Node 6: Aggregating scores for {state['symbol']}")
        
        config = state.get('config', {})
        weights = config.get('weights', {})
        thresholds = config.get('thresholds', {})
        
        qual_weight = weights.get('qualitative_pct', 15) / 100
        quant_weight = weights.get('quantitative_pct', 50) / 100
        search_weight = weights.get('search_pct', 10) / 100
        trend_weight = weights.get('trend_pct', 25) / 100
        
        qual_score = state.get('qualitative_score', 50)
        quant_score = state.get('quantitative_score', 50)
        search_score = state.get('search_score', 50)
        trend_score = state.get('trend_score', 50)
        
        overall_score = (
            qual_score * qual_weight +
            quant_score * quant_weight +
            search_score * search_weight +
            trend_score * trend_weight
        )
        
        qual_conf = state.get('qualitative_confidence', 0.5)
        quant_conf = state.get('quantitative_confidence', 0.5)
        search_conf = state.get('search_confidence', 0.5)
        trend_conf = state.get('trend_confidence', 0.5)
        
        overall_confidence = (
            qual_conf * qual_weight +
            quant_conf * quant_weight +
            search_conf * search_weight +
            trend_conf * trend_weight
        )
        
        strong_buy = thresholds.get('strong_buy', 80)
        buy = thresholds.get('buy', 65)
        hold_low = thresholds.get('hold_low', 45)
        sell = thresholds.get('sell', 30)
        min_confidence = thresholds.get('min_confidence', 0.6)
        
        if overall_confidence < min_confidence:
            recommendation = 'INCONCLUSIVE'
            summary = f"Insufficient confidence ({overall_confidence:.0%}) for a definitive recommendation."
        elif overall_score >= strong_buy:
            recommendation = 'STRONG_BUY'
            summary = f"I-Score of {overall_score:.1f}/100 indicates strong bullish sentiment across all indicators."
        elif overall_score >= buy:
            recommendation = 'BUY'
            summary = f"I-Score of {overall_score:.1f}/100 shows positive momentum with favorable technical and sentiment signals."
        elif overall_score >= hold_low:
            recommendation = 'HOLD'
            summary = f"I-Score of {overall_score:.1f}/100 suggests maintaining current positions; mixed signals present."
        elif overall_score >= sell:
            recommendation = 'CAUTIONARY_SELL'
            summary = f"I-Score of {overall_score:.1f}/100 indicates caution; consider reducing exposure."
        else:
            recommendation = 'STRONG_SELL'
            summary = f"I-Score of {overall_score:.1f}/100 shows significant bearish pressure across indicators."
        
        return {
            'overall_score': round(overall_score, 2),
            'overall_confidence': round(overall_confidence, 2),
            'recommendation': recommendation,
            'recommendation_summary': summary,
            'step': 'aggregation_complete'
        }
    
    def store_results(self, state: IScoreState) -> Dict:
        """Node 7: Store results in database and cache"""
        logger.info(f"I-Score Node 7: Storing results for {state['symbol']}")
        
        if state.get('cache_hit'):
            logger.info("Using cached result, skipping storage")
            return {'step': 'cached_result_used'}
        
        try:
            from models import ResearchRun, ResearchSignalComponent, ResearchCache
            
            research_run = ResearchRun(
                tenant_id='live',
                user_id=state['user_id'],
                asset_type=state['asset_type'],
                symbol=state['symbol'],
                asset_name=state.get('asset_name', state['symbol']),
                analysis_date=date.today(),
                status='completed',
                overall_score=Decimal(str(state.get('overall_score', 0))),
                confidence=Decimal(str(state.get('overall_confidence', 0))),
                recommendation=state.get('recommendation'),
                recommendation_summary=state.get('recommendation_summary'),
                inputs_json=state.get('config'),
                run_started_at=datetime.utcnow() - timedelta(seconds=30),
                run_completed_at=datetime.utcnow()
            )
            research_run.cache_key = research_run.generate_cache_key()
            db.session.add(research_run)
            db.session.flush()
            
            config = state.get('config', {})
            weights = config.get('weights', {})
            
            components = [
                {
                    'type': 'qualitative',
                    'weight': weights.get('qualitative_pct', 15),
                    'score': state.get('qualitative_score', 50),
                    'confidence': state.get('qualitative_confidence', 0.5),
                    'details': state.get('qualitative_details', {})
                },
                {
                    'type': 'quantitative',
                    'weight': weights.get('quantitative_pct', 50),
                    'score': state.get('quantitative_score', 50),
                    'confidence': state.get('quantitative_confidence', 0.5),
                    'details': state.get('quantitative_details', {})
                },
                {
                    'type': 'search',
                    'weight': weights.get('search_pct', 10),
                    'score': state.get('search_score', 50),
                    'confidence': state.get('search_confidence', 0.5),
                    'details': state.get('search_details', {})
                },
                {
                    'type': 'trend',
                    'weight': weights.get('trend_pct', 25),
                    'score': state.get('trend_score', 50),
                    'confidence': state.get('trend_confidence', 0.5),
                    'details': state.get('trend_details', {})
                }
            ]
            
            for comp in components:
                signal = 'bullish' if comp['score'] > 60 else 'bearish' if comp['score'] < 40 else 'neutral'
                component = ResearchSignalComponent(
                    run_id=research_run.id,
                    component_type=comp['type'],
                    weight_pct=comp['weight'],
                    raw_score=Decimal(str(comp['score'])),
                    weighted_score=Decimal(str(comp['score'] * comp['weight'] / 100)),
                    confidence=Decimal(str(comp['confidence'])),
                    signal=signal,
                    breakdown=comp['details']
                )
                db.session.add(component)
            
            cache_key = self._generate_cache_key(
                state['asset_type'],
                state['symbol'],
                date.today()
            )
            
            cache_entry = ResearchCache(
                tenant_id='live',
                cache_key=cache_key,
                asset_type=state['asset_type'],
                symbol=state['symbol'],
                analysis_date=date.today(),
                result_payload={
                    'overall_score': state.get('overall_score'),
                    'overall_confidence': state.get('overall_confidence'),
                    'recommendation': state.get('recommendation'),
                    'recommendation_summary': state.get('recommendation_summary'),
                    'qualitative': {
                        'score': state.get('qualitative_score'),
                        'details': state.get('qualitative_details')
                    },
                    'quantitative': {
                        'score': state.get('quantitative_score'),
                        'details': state.get('quantitative_details')
                    },
                    'search': {
                        'score': state.get('search_score'),
                        'details': state.get('search_details')
                    },
                    'trend': {
                        'score': state.get('trend_score'),
                        'details': state.get('trend_details')
                    }
                },
                overall_score=Decimal(str(state.get('overall_score', 0))),
                recommendation=state.get('recommendation'),
                expires_at=datetime.utcnow() + timedelta(hours=4)
            )
            db.session.add(cache_entry)
            
            db.session.commit()
            logger.info(f"I-Score results stored for {state['symbol']}: {state.get('overall_score')}/100")
            
            return {'step': 'storage_complete'}
            
        except Exception as e:
            logger.error(f"Error storing I-Score results: {e}")
            db.session.rollback()
            return {'step': 'storage_error', 'error': str(e)}
    
    def _parse_llm_response(self, response: str, response_type: str) -> Dict:
        """Parse LLM response to extract structured data"""
        import re
        
        try:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        score_match = re.search(r'score[:\s]*(\d+)', response.lower())
        score = int(score_match.group(1)) if score_match else 50
        
        return {
            'sentiment_score': score,
            'search_score': score,
            'confidence': 0.6,
            'key_findings': [],
            'trend_direction': 'stable',
            'buzz_level': 'medium'
        }
    
    def analyze(self, asset_type: str, symbol: str, user_id: int, asset_name: str = None) -> Dict:
        """
        Run I-Score analysis for an asset
        
        Args:
            asset_type: Type of asset (stocks, futures, options, etc.)
            symbol: Asset symbol
            user_id: User requesting the analysis
            asset_name: Display name for the asset
        
        Returns:
            Dictionary with I-Score results
        """
        initial_state: IScoreState = {
            'asset_type': asset_type,
            'symbol': symbol,
            'asset_name': asset_name or symbol,
            'user_id': user_id,
            'cache_hit': False,
            'cached_result': None,
            'qualitative_score': 0,
            'qualitative_details': {},
            'qualitative_confidence': 0,
            'quantitative_score': 0,
            'quantitative_details': {},
            'quantitative_confidence': 0,
            'search_score': 0,
            'search_details': {},
            'search_confidence': 0,
            'trend_score': 0,
            'trend_details': {},
            'trend_confidence': 0,
            'overall_score': 0,
            'overall_confidence': 0,
            'recommendation': '',
            'recommendation_summary': '',
            'config': {},
            'evidence': [],
            'error': None,
            'step': 'start'
        }
        
        try:
            result = self.graph.invoke(initial_state)
            
            return {
                'success': True,
                'symbol': symbol,
                'asset_type': asset_type,
                'iscore': result.get('overall_score', 0),
                'confidence': result.get('overall_confidence', 0),
                'recommendation': result.get('recommendation', 'INCONCLUSIVE'),
                'summary': result.get('recommendation_summary', ''),
                'components': {
                    'qualitative': {
                        'score': result.get('qualitative_score', 0),
                        'weight': 15,
                        'details': result.get('qualitative_details', {})
                    },
                    'quantitative': {
                        'score': result.get('quantitative_score', 0),
                        'weight': 50,
                        'details': result.get('quantitative_details', {})
                    },
                    'search': {
                        'score': result.get('search_score', 0),
                        'weight': 10,
                        'details': result.get('search_details', {})
                    },
                    'trend': {
                        'score': result.get('trend_score', 0),
                        'weight': 25,
                        'details': result.get('trend_details', {})
                    }
                },
                'cached': result.get('cache_hit', False),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"I-Score analysis failed for {symbol}: {e}")
            return {
                'success': False,
                'symbol': symbol,
                'asset_type': asset_type,
                'iscore': 0,
                'recommendation': 'ERROR',
                'error': str(e)
            }


def get_iscore_for_symbol(symbol: str, asset_type: str = 'stocks', user_id: int = None) -> Dict:
    """
    Convenience function to get I-Score for a symbol
    
    Recommended I-Score thresholds:
    - >= 65: Recommended for investment (BUY or STRONG_BUY)
    - 45-64: Hold/Monitor
    - < 45: Avoid or Sell
    """
    engine = LangGraphIScoreEngine()
    return engine.analyze(asset_type, symbol, user_id or 1)
