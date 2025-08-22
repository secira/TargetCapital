"""
Unified Portfolio Analyzer Service
Implements comprehensive portfolio analysis, risk profiling, and AI-based recommendations
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from sqlalchemy import func, and_
from models import Portfolio, RiskProfile, PortfolioAnalysis, PortfolioRecommendation, User, BrokerAccount
from app import db
import requests
import os

class PortfolioAnalyzerService:
    """Comprehensive portfolio analysis and optimization service"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        
    def sync_broker_data(self) -> Dict:
        """Sync portfolio data from connected broker accounts"""
        try:
            broker_accounts = BrokerAccount.query.filter_by(user_id=self.user_id).all()
            sync_results = {
                'success': True,
                'synced_brokers': [],
                'total_holdings': 0,
                'errors': []
            }
            
            for broker in broker_accounts:
                try:
                    # Import broker service dynamically
                    from services.broker_service import BrokerService
                    broker_service = BrokerService()
                    
                    # Get holdings from broker
                    holdings = broker_service.get_holdings(broker.broker_name, broker.get_credentials())
                    
                    if holdings:
                        # Update or create portfolio entries
                        for holding in holdings:
                            existing_holding = Portfolio.query.filter_by(
                                user_id=self.user_id,
                                broker_id=broker.broker_name,
                                ticker_symbol=holding.get('symbol', '')
                            ).first()
                            
                            if existing_holding:
                                # Update existing holding
                                existing_holding.quantity = holding.get('quantity', 0)
                                existing_holding.current_price = holding.get('current_price', 0)
                                existing_holding.current_value = holding.get('current_value', 0)
                                existing_holding.last_sync_date = datetime.utcnow()
                            else:
                                # Create new holding
                                new_holding = Portfolio(
                                    user_id=self.user_id,
                                    broker_id=broker.broker_name,
                                    ticker_symbol=holding.get('symbol', ''),
                                    stock_name=holding.get('company_name', ''),
                                    asset_type='Stocks',
                                    asset_category='Equity',
                                    quantity=holding.get('quantity', 0),
                                    date_purchased=holding.get('purchase_date', date.today()),
                                    purchase_price=holding.get('average_price', 0),
                                    purchased_value=holding.get('invested_value', 0),
                                    current_price=holding.get('current_price', 0),
                                    current_value=holding.get('current_value', 0),
                                    sector=holding.get('sector', 'Unknown'),
                                    exchange=holding.get('exchange', 'NSE'),
                                    trade_type='long_term',
                                    data_source='broker',
                                    last_sync_date=datetime.utcnow()
                                )
                                db.session.add(new_holding)
                        
                        sync_results['synced_brokers'].append(broker.broker_name)
                        sync_results['total_holdings'] += len(holdings)
                        
                except Exception as e:
                    sync_results['errors'].append(f"{broker.broker_name}: {str(e)}")
            
            db.session.commit()
            return sync_results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'synced_brokers': [],
                'total_holdings': 0
            }
    
    def upload_manual_holdings(self, holdings_data: List[Dict]) -> Dict:
        """Process manually uploaded holdings data"""
        try:
            processed_count = 0
            skipped_count = 0
            errors = []
            
            for holding_data in holdings_data:
                try:
                    # Check for duplicates
                    existing = Portfolio.query.filter_by(
                        user_id=self.user_id,
                        ticker_symbol=holding_data.get('symbol', '').upper(),
                        broker_id=None  # Manual uploads have no broker_id
                    ).first()
                    
                    if existing:
                        # Update existing manual entry
                        existing.quantity = float(holding_data.get('quantity', 0))
                        existing.purchase_price = float(holding_data.get('purchase_price', 0))
                        existing.purchased_value = existing.quantity * existing.purchase_price
                        existing.updated_at = datetime.utcnow()
                        processed_count += 1
                    else:
                        # Create new manual entry
                        new_holding = Portfolio(
                            user_id=self.user_id,
                            broker_id=None,  # Manual upload
                            ticker_symbol=holding_data.get('symbol', '').upper(),
                            stock_name=holding_data.get('company_name', ''),
                            asset_type=holding_data.get('asset_type', 'Stocks'),
                            asset_category=self._get_asset_category(holding_data.get('asset_type', 'Stocks')),
                            quantity=float(holding_data.get('quantity', 0)),
                            date_purchased=datetime.strptime(holding_data.get('purchase_date', ''), '%Y-%m-%d').date(),
                            purchase_price=float(holding_data.get('purchase_price', 0)),
                            purchased_value=float(holding_data.get('quantity', 0)) * float(holding_data.get('purchase_price', 0)),
                            sector=holding_data.get('sector', 'Unknown'),
                            exchange=holding_data.get('exchange', 'NSE'),
                            trade_type=holding_data.get('trade_type', 'long_term'),
                            data_source='manual_upload'
                        )
                        db.session.add(new_holding)
                        processed_count += 1
                        
                except Exception as e:
                    errors.append(f"Row error: {str(e)}")
                    skipped_count += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'processed': processed_count,
                'skipped': skipped_count,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed': 0,
                'skipped': 0
            }
    
    def _get_asset_category(self, asset_type: str) -> str:
        """Map asset type to category"""
        mapping = {
            'Stocks': 'Equity',
            'MF': 'Equity',  # Mutual Funds
            'ETF': 'Equity',
            'Bonds': 'Debt',
            'Gold': 'Commodities',
            'Crypto': 'Alternative',
            'ESOP': 'Alternative',
            'PrivateEquity': 'Alternative'
        }
        return mapping.get(asset_type, 'Equity')
    
    def analyze_portfolio(self) -> Dict:
        """Comprehensive portfolio analysis with AI insights"""
        try:
            # Get all user holdings
            holdings = Portfolio.query.filter_by(user_id=self.user_id).all()
            
            if not holdings:
                return self._generate_empty_portfolio_analysis()
            
            # Calculate basic metrics
            total_invested = sum(h.purchased_value for h in holdings)
            total_current = sum(h.current_value or h.purchased_value for h in holdings)
            total_pnl = total_current - total_invested
            total_pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            # Sector analysis
            sector_allocation = self._calculate_sector_allocation(holdings)
            asset_allocation = self._calculate_asset_allocation(holdings)
            top_holdings = self._get_top_holdings(holdings)
            
            # Risk analysis
            risk_metrics = self._calculate_risk_metrics(holdings)
            
            # AI-based health assessment
            ai_assessment = self._generate_ai_assessment(holdings, sector_allocation, asset_allocation, risk_metrics)
            
            # Create analysis record
            analysis = PortfolioAnalysis(
                user_id=self.user_id,
                analysis_date=date.today(),
                total_portfolio_value=total_current,
                total_invested_amount=total_invested,
                total_pnl=total_pnl,
                total_pnl_percentage=total_pnl_percentage,
                number_of_holdings=len(holdings),
                number_of_brokers=len(set(h.broker_id for h in holdings if h.broker_id)),
                portfolio_volatility=risk_metrics.get('volatility'),
                sharpe_ratio=risk_metrics.get('sharpe_ratio'),
                portfolio_beta=risk_metrics.get('beta'),
                max_drawdown=risk_metrics.get('max_drawdown'),
                sector_concentration=json.dumps(sector_allocation),
                asset_allocation=json.dumps(asset_allocation),
                top_holdings=json.dumps(top_holdings),
                concentration_risk=ai_assessment.get('concentration_risk', False),
                under_diversified=ai_assessment.get('under_diversified', False),
                high_volatility_warning=ai_assessment.get('high_volatility', False),
                sector_over_concentration=ai_assessment.get('sector_concentration', False),
                ai_health_score=ai_assessment.get('health_score', 75),
                ai_risk_assessment=ai_assessment.get('risk_level', 'Medium'),
                ai_suggestions=json.dumps(ai_assessment.get('suggestions', [])),
                rebalance_recommendations=json.dumps(ai_assessment.get('rebalance_actions', []))
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            return {
                'success': True,
                'analysis': {
                    'portfolio_summary': {
                        'total_value': total_current,
                        'total_invested': total_invested,
                        'total_pnl': total_pnl,
                        'total_pnl_percentage': total_pnl_percentage,
                        'holdings_count': len(holdings),
                        'brokers_count': len(set(h.broker_id for h in holdings if h.broker_id))
                    },
                    'sector_allocation': sector_allocation,
                    'asset_allocation': asset_allocation,
                    'top_holdings': top_holdings,
                    'risk_metrics': risk_metrics,
                    'ai_assessment': ai_assessment,
                    'analysis_id': analysis.id
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_sector_allocation(self, holdings: List[Portfolio]) -> Dict:
        """Calculate sector-wise allocation"""
        sector_totals = defaultdict(float)
        total_value = sum(h.current_value or h.purchased_value for h in holdings)
        
        for holding in holdings:
            value = holding.current_value or holding.purchased_value
            sector_totals[holding.sector or 'Unknown'] += value
        
        return {
            sector: round((value / total_value) * 100, 2)
            for sector, value in sector_totals.items()
        }
    
    def _calculate_asset_allocation(self, holdings: List[Portfolio]) -> Dict:
        """Calculate asset type allocation"""
        asset_totals = defaultdict(float)
        total_value = sum(h.current_value or h.purchased_value for h in holdings)
        
        for holding in holdings:
            value = holding.current_value or holding.purchased_value
            asset_totals[holding.asset_category or 'Equity'] += value
        
        return {
            asset_type: round((value / total_value) * 100, 2)
            for asset_type, value in asset_totals.items()
        }
    
    def _get_top_holdings(self, holdings: List[Portfolio]) -> List[Dict]:
        """Get top holdings by value"""
        total_value = sum(h.current_value or h.purchased_value for h in holdings)
        
        holdings_with_percentage = []
        for holding in holdings:
            value = holding.current_value or holding.purchased_value
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            
            holdings_with_percentage.append({
                'symbol': holding.ticker_symbol,
                'company_name': holding.stock_name,
                'value': value,
                'percentage': round(percentage, 2),
                'pnl': holding.pnl_amount,
                'pnl_percentage': holding.pnl_percentage
            })
        
        # Sort by percentage and return top 10
        return sorted(holdings_with_percentage, key=lambda x: x['percentage'], reverse=True)[:10]
    
    def _calculate_risk_metrics(self, holdings: List[Portfolio]) -> Dict:
        """Calculate portfolio risk metrics"""
        # Simplified risk calculations (in production, would use historical data)
        try:
            values = [h.current_value or h.purchased_value for h in holdings]
            total_value = sum(values)
            
            # Portfolio concentration (Herfindahl index)
            weights = [v / total_value for v in values]
            concentration = sum(w ** 2 for w in weights)
            
            # Estimate volatility based on sector diversification
            sectors = set(h.sector for h in holdings if h.sector)
            diversification_factor = min(len(sectors) / 10, 1.0)  # More sectors = lower volatility
            estimated_volatility = 0.25 * (1 - diversification_factor * 0.3)  # 25% base, reduced by diversification
            
            return {
                'volatility': round(estimated_volatility, 3),
                'concentration_index': round(concentration, 3),
                'sharpe_ratio': round(1.2 * diversification_factor, 2),  # Simplified
                'beta': round(1.0 + (concentration - 0.1), 2),  # Simplified
                'max_drawdown': round(estimated_volatility * 2, 2)  # Simplified
            }
            
        except Exception:
            return {
                'volatility': 0.20,
                'concentration_index': 0.15,
                'sharpe_ratio': 1.0,
                'beta': 1.0,
                'max_drawdown': 0.15
            }
    
    def _generate_ai_assessment(self, holdings: List[Portfolio], sector_allocation: Dict, 
                               asset_allocation: Dict, risk_metrics: Dict) -> Dict:
        """Generate AI-based portfolio assessment"""
        try:
            # Analyze concentration risks
            max_sector_allocation = max(sector_allocation.values()) if sector_allocation else 0
            max_holding_allocation = max([h['percentage'] for h in self._get_top_holdings(holdings)]) if holdings else 0
            
            # Risk flags
            concentration_risk = max_holding_allocation > 15  # Single holding > 15%
            sector_concentration = max_sector_allocation > 40  # Single sector > 40%
            under_diversified = len(holdings) < 10  # Less than 10 holdings
            high_volatility = risk_metrics.get('volatility', 0) > 0.30
            
            # Calculate health score
            health_score = 100
            if concentration_risk: health_score -= 15
            if sector_concentration: health_score -= 20
            if under_diversified: health_score -= 15
            if high_volatility: health_score -= 10
            health_score = max(health_score, 30)  # Minimum score 30
            
            # Generate suggestions
            suggestions = []
            rebalance_actions = []
            
            if concentration_risk:
                suggestions.append("Consider reducing concentration in top holdings (>15% allocation)")
                rebalance_actions.append({
                    'action': 'REDUCE',
                    'reason': 'Concentration risk',
                    'priority': 'HIGH'
                })
            
            if sector_concentration:
                suggestions.append("Diversify across more sectors to reduce concentration risk")
                rebalance_actions.append({
                    'action': 'DIVERSIFY',
                    'reason': 'Sector concentration',
                    'priority': 'MEDIUM'
                })
            
            if under_diversified:
                suggestions.append("Increase number of holdings for better diversification")
                rebalance_actions.append({
                    'action': 'ADD_HOLDINGS',
                    'reason': 'Under-diversified portfolio',
                    'priority': 'MEDIUM'
                })
            
            # Risk level assessment
            risk_level = 'Low'
            if concentration_risk or sector_concentration:
                risk_level = 'High'
            elif under_diversified or high_volatility:
                risk_level = 'Medium'
            
            return {
                'health_score': health_score,
                'risk_level': risk_level,
                'concentration_risk': concentration_risk,
                'sector_concentration': sector_concentration,
                'under_diversified': under_diversified,
                'high_volatility': high_volatility,
                'suggestions': suggestions,
                'rebalance_actions': rebalance_actions
            }
            
        except Exception:
            return {
                'health_score': 75,
                'risk_level': 'Medium',
                'concentration_risk': False,
                'sector_concentration': False,
                'under_diversified': False,
                'high_volatility': False,
                'suggestions': ['Portfolio analysis requires more data for detailed insights'],
                'rebalance_actions': []
            }
    
    def _generate_empty_portfolio_analysis(self) -> Dict:
        """Generate analysis for empty portfolio"""
        return {
            'success': True,
            'analysis': {
                'portfolio_summary': {
                    'total_value': 0,
                    'total_invested': 0,
                    'total_pnl': 0,
                    'total_pnl_percentage': 0,
                    'holdings_count': 0,
                    'brokers_count': 0
                },
                'sector_allocation': {},
                'asset_allocation': {},
                'top_holdings': [],
                'risk_metrics': {
                    'volatility': 0,
                    'concentration_index': 0,
                    'sharpe_ratio': 0,
                    'beta': 0,
                    'max_drawdown': 0
                },
                'ai_assessment': {
                    'health_score': 0,
                    'risk_level': 'Unknown',
                    'suggestions': ['Connect broker accounts or upload holdings to start portfolio analysis'],
                    'rebalance_actions': []
                }
            }
        }
    
    def generate_risk_aligned_recommendations(self, risk_profile: RiskProfile) -> List[Dict]:
        """Generate investment recommendations based on user's risk profile"""
        try:
            recommendations = []
            
            # Conservative recommendations
            if risk_profile.risk_category == 'Conservative':
                recommendations.extend([
                    {
                        'symbol': 'HDFCBANK',
                        'company_name': 'HDFC Bank Limited',
                        'recommendation': 'BUY',
                        'reasoning': 'Stable banking stock suitable for conservative investors',
                        'target_allocation': 15.0,
                        'risk_alignment': True
                    },
                    {
                        'symbol': 'TCS',
                        'company_name': 'Tata Consultancy Services',
                        'recommendation': 'BUY',
                        'reasoning': 'Blue-chip IT stock with steady growth',
                        'target_allocation': 12.0,
                        'risk_alignment': True
                    }
                ])
            
            # Balanced recommendations
            elif risk_profile.risk_category == 'Balanced':
                recommendations.extend([
                    {
                        'symbol': 'RELIANCE',
                        'company_name': 'Reliance Industries Limited',
                        'recommendation': 'BUY',
                        'reasoning': 'Diversified conglomerate suitable for balanced portfolios',
                        'target_allocation': 18.0,
                        'risk_alignment': True
                    },
                    {
                        'symbol': 'INFY',
                        'company_name': 'Infosys Limited',
                        'recommendation': 'BUY',
                        'reasoning': 'Quality IT stock with growth potential',
                        'target_allocation': 15.0,
                        'risk_alignment': True
                    }
                ])
            
            # Aggressive recommendations
            else:  # Aggressive
                recommendations.extend([
                    {
                        'symbol': 'ADANIPORTS',
                        'company_name': 'Adani Ports and SEZ Limited',
                        'recommendation': 'BUY',
                        'reasoning': 'High growth infrastructure stock for aggressive investors',
                        'target_allocation': 20.0,
                        'risk_alignment': True
                    },
                    {
                        'symbol': 'BAJFINANCE',
                        'company_name': 'Bajaj Finance Limited',
                        'recommendation': 'BUY',
                        'reasoning': 'High growth NBFC suitable for aggressive portfolios',
                        'target_allocation': 18.0,
                        'risk_alignment': True
                    }
                ])
            
            return recommendations
            
        except Exception:
            return []
    
    def get_latest_analysis(self) -> Optional[PortfolioAnalysis]:
        """Get the most recent portfolio analysis"""
        return PortfolioAnalysis.query.filter_by(user_id=self.user_id).order_by(
            PortfolioAnalysis.created_at.desc()
        ).first()