"""
Routes for Research & Signals by Asset Type
Provides in-depth research pages for each asset class
"""
from flask import render_template
from flask_login import login_required, current_user
from app import app, db
from models import TradingSignal
from datetime import datetime, timezone

ASSET_TYPES = {
    'stocks': {
        'name': 'Stocks',
        'title': 'Stocks Research & Signals',
        'subtitle': 'In-depth analysis and trading signals for Indian equities',
        'icon': 'fas fa-chart-bar',
        'description': 'Comprehensive research and real-time signals for NSE and BSE listed stocks.',
        'features': [
            {'icon': 'fas fa-search-dollar', 'title': 'Fundamental Analysis', 'desc': 'Deep-dive into financials, ratios, and company performance'},
            {'icon': 'fas fa-chart-line', 'title': 'Technical Signals', 'desc': 'AI-powered buy/sell signals based on chart patterns'},
            {'icon': 'fas fa-newspaper', 'title': 'Market News', 'desc': 'Real-time news and sentiment analysis'},
            {'icon': 'fas fa-bullseye', 'title': 'Price Targets', 'desc': 'AI-generated price targets with confidence levels'}
        ],
        'market_hours': 'NSE/BSE: 9:15 AM - 3:30 PM IST',
        'signal_type': 'STOCK'
    },
    'futures': {
        'name': 'Futures',
        'title': 'Futures Research & Signals',
        'subtitle': 'Advanced analysis for Index and Stock Futures trading',
        'icon': 'fas fa-calendar-alt',
        'description': 'Professional-grade research for NIFTY, BANKNIFTY, and stock futures with expiry-based strategies.',
        'features': [
            {'icon': 'fas fa-layer-group', 'title': 'Open Interest Analysis', 'desc': 'Track OI buildup and unwinding patterns'},
            {'icon': 'fas fa-arrows-alt-v', 'title': 'Rollover Data', 'desc': 'Monthly rollover percentages and trends'},
            {'icon': 'fas fa-balance-scale', 'title': 'Basis & Premium', 'desc': 'Futures premium/discount analysis'},
            {'icon': 'fas fa-clock', 'title': 'Expiry Strategies', 'desc': 'Time-decay aware trading signals'}
        ],
        'market_hours': 'NSE F&O: 9:15 AM - 3:30 PM IST',
        'signal_type': 'FUTURES'
    },
    'options': {
        'name': 'Options',
        'title': 'Options Research & Signals',
        'subtitle': 'Greeks-based analysis and strategy recommendations',
        'icon': 'fas fa-layer-group',
        'description': 'Sophisticated options analysis with Greeks, IV, and strategy builder for informed trading decisions.',
        'features': [
            {'icon': 'fas fa-chart-area', 'title': 'Implied Volatility', 'desc': 'IV percentile and skew analysis'},
            {'icon': 'fas fa-calculator', 'title': 'Options Greeks', 'desc': 'Delta, Gamma, Theta, Vega tracking'},
            {'icon': 'fas fa-project-diagram', 'title': 'Strategy Builder', 'desc': 'Multi-leg strategy recommendations'},
            {'icon': 'fas fa-fire', 'title': 'Max Pain Analysis', 'desc': 'Weekly max pain levels and trends'}
        ],
        'market_hours': 'NSE F&O: 9:15 AM - 3:30 PM IST',
        'signal_type': 'OPTIONS'
    },
    'commodities': {
        'name': 'Commodities',
        'title': 'Commodities Research & Signals',
        'subtitle': 'MCX trading signals for Gold, Silver, Crude and more',
        'icon': 'fas fa-cubes',
        'description': 'Real-time analysis and trading signals for MCX commodities including precious metals and energy.',
        'features': [
            {'icon': 'fas fa-coins', 'title': 'Precious Metals', 'desc': 'Gold, Silver analysis with global cues'},
            {'icon': 'fas fa-oil-can', 'title': 'Energy', 'desc': 'Crude Oil, Natural Gas signals'},
            {'icon': 'fas fa-seedling', 'title': 'Agri Commodities', 'desc': 'Agricultural commodities research'},
            {'icon': 'fas fa-globe', 'title': 'Global Correlation', 'desc': 'International market linkages'}
        ],
        'market_hours': 'MCX: 9:00 AM - 11:30 PM IST',
        'signal_type': 'COMMODITY'
    },
    'currency': {
        'name': 'Currency',
        'title': 'Currency Research & Signals',
        'subtitle': 'Forex analysis for INR pairs and cross-currency trading',
        'icon': 'fas fa-rupee-sign',
        'description': 'Expert analysis on USD/INR, EUR/INR and other currency pairs with RBI policy insights.',
        'features': [
            {'icon': 'fas fa-dollar-sign', 'title': 'USD/INR Focus', 'desc': 'Primary pair analysis with technicals'},
            {'icon': 'fas fa-university', 'title': 'RBI Policy', 'desc': 'Central bank intervention tracking'},
            {'icon': 'fas fa-exchange-alt', 'title': 'Cross Rates', 'desc': 'EUR/INR, GBP/INR, JPY/INR'},
            {'icon': 'fas fa-globe-asia', 'title': 'Global FX', 'desc': 'DXY and emerging market correlations'}
        ],
        'market_hours': 'NSE Currency: 9:00 AM - 5:00 PM IST',
        'signal_type': 'CURRENCY'
    },
    'bonds': {
        'name': 'Bonds',
        'title': 'Bonds Research & Signals',
        'subtitle': 'Fixed income analysis for G-Secs and Corporate Bonds',
        'icon': 'fas fa-file-contract',
        'description': 'Yield curve analysis, G-Sec trading signals, and corporate bond recommendations.',
        'features': [
            {'icon': 'fas fa-landmark', 'title': 'G-Sec Analysis', 'desc': 'Government securities yield tracking'},
            {'icon': 'fas fa-chart-line', 'title': 'Yield Curve', 'desc': 'Yield curve shape and movements'},
            {'icon': 'fas fa-building', 'title': 'Corporate Bonds', 'desc': 'Credit rating based recommendations'},
            {'icon': 'fas fa-percentage', 'title': 'Rate Outlook', 'desc': 'RBI rate decision impact analysis'}
        ],
        'market_hours': 'RBI Retail Direct: 9:00 AM - 5:00 PM IST',
        'signal_type': 'BOND'
    },
    'mutual_funds': {
        'name': 'Mutual Funds',
        'title': 'Mutual Funds Research & Signals',
        'subtitle': 'Fund analysis, SIP recommendations and portfolio insights',
        'icon': 'fas fa-piggy-bank',
        'description': 'Comprehensive mutual fund research with category comparisons and SIP timing signals.',
        'features': [
            {'icon': 'fas fa-star', 'title': 'Fund Ratings', 'desc': 'Performance-based fund rankings'},
            {'icon': 'fas fa-sync', 'title': 'SIP Timing', 'desc': 'Optimal SIP entry signals'},
            {'icon': 'fas fa-th-large', 'title': 'Category Analysis', 'desc': 'Sector and thematic fund insights'},
            {'icon': 'fas fa-user-tie', 'title': 'Fund Manager', 'desc': 'Track record and style analysis'}
        ],
        'market_hours': 'AMC: 9:30 AM - 3:00 PM IST (NAV cut-off)',
        'signal_type': 'MF'
    }
}


def get_signals_for_asset(signal_type):
    """Get active signals for a specific asset type"""
    plan = current_user.pricing_plan
    plan_value = plan.value if hasattr(plan, 'value') else str(plan)
    if plan_value == 'free':
        return []
    
    signals = TradingSignal.query.filter(
        TradingSignal.status == 'ACTIVE',
        TradingSignal.signal_type == signal_type,
        db.or_(
            TradingSignal.expires_at.is_(None),
            TradingSignal.expires_at > datetime.now(timezone.utc)
        )
    ).order_by(TradingSignal.created_at.desc()).limit(10).all()
    
    return signals


@app.route('/dashboard/research/stocks')
@login_required
def research_stocks():
    """Stocks research and signals page"""
    asset = ASSET_TYPES['stocks']
    signals = get_signals_for_asset(asset['signal_type'])
    return render_template('dashboard/research/asset_research.html', 
                          asset=asset, signals=signals, asset_key='stocks')


@app.route('/dashboard/research/futures')
@login_required
def research_futures():
    """Futures research and signals page"""
    asset = ASSET_TYPES['futures']
    signals = get_signals_for_asset(asset['signal_type'])
    return render_template('dashboard/research/asset_research.html', 
                          asset=asset, signals=signals, asset_key='futures')


@app.route('/dashboard/research/options')
@login_required
def research_options():
    """Options research and signals page"""
    asset = ASSET_TYPES['options']
    signals = get_signals_for_asset(asset['signal_type'])
    return render_template('dashboard/research/asset_research.html', 
                          asset=asset, signals=signals, asset_key='options')


@app.route('/dashboard/research/commodities')
@login_required
def research_commodities():
    """Commodities research and signals page"""
    asset = ASSET_TYPES['commodities']
    signals = get_signals_for_asset(asset['signal_type'])
    return render_template('dashboard/research/asset_research.html', 
                          asset=asset, signals=signals, asset_key='commodities')


@app.route('/dashboard/research/currency')
@login_required
def research_currency():
    """Currency research and signals page"""
    asset = ASSET_TYPES['currency']
    signals = get_signals_for_asset(asset['signal_type'])
    return render_template('dashboard/research/asset_research.html', 
                          asset=asset, signals=signals, asset_key='currency')


@app.route('/dashboard/research/bonds')
@login_required
def research_bonds():
    """Bonds research and signals page"""
    asset = ASSET_TYPES['bonds']
    signals = get_signals_for_asset(asset['signal_type'])
    return render_template('dashboard/research/asset_research.html', 
                          asset=asset, signals=signals, asset_key='bonds')


@app.route('/dashboard/research/mutual-funds')
@login_required
def research_mutual_funds():
    """Mutual Funds research and signals page"""
    asset = ASSET_TYPES['mutual_funds']
    signals = get_signals_for_asset(asset['signal_type'])
    return render_template('dashboard/research/asset_research.html', 
                          asset=asset, signals=signals, asset_key='mutual_funds')
