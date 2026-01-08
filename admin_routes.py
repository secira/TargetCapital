"""
Admin Routes for Target Capital Trading Platform
Separate admin module with authentication and management features
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from models import Admin, User, PricingPlan, ResearchList, UserPayment
from models_broker import BrokerAccount

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin authentication decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def admin_decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return admin_decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username, active=True).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Welcome to Target Capital Admin Dashboard!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@admin_required
def logout():
    """Admin logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    total_users = User.query.count()
    research_stocks = ResearchList.query.filter_by(is_active=True).count()
    analyzed_stocks = ResearchList.query.filter(ResearchList.i_score.isnot(None), ResearchList.is_active == True).count()
    today_payments = UserPayment.query.filter(
        func.date(UserPayment.created_at) == datetime.utcnow().date(),
        UserPayment.status == 'COMPLETED'
    ).count()
    
    current_month = datetime.utcnow().replace(day=1)
    monthly_revenue = db.session.query(func.sum(UserPayment.amount)).filter(
        UserPayment.created_at >= current_month,
        UserPayment.status == 'COMPLETED'
    ).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         research_stocks=research_stocks,
                         analyzed_stocks=analyzed_stocks,
                         today_payments=today_payments,
                         monthly_revenue=monthly_revenue)

@admin_bp.route('/users')
@admin_bp.route('/users/<int:page>')
@admin_required
def users(page=1):
    """User management page"""
    per_page = 20
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    """User detail page with payment history"""
    user = User.query.get_or_404(user_id)
    payments = UserPayment.query.filter_by(user_id=user_id).order_by(desc(UserPayment.created_at)).limit(10).all()
    brokers = BrokerAccount.query.filter_by(user_id=user_id).all()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         payments=payments,
                         brokers=brokers)

@admin_bp.route('/research-list')
@admin_bp.route('/research-list/<int:page>')
@admin_required
def research_list(page=1):
    """Research List management - Pre-computed I-Score for top 500 stocks"""
    per_page = 25
    asset_type_filter = request.args.get('asset_type', '')
    recommendation_filter = request.args.get('recommendation', '')
    search_query = request.args.get('search', '')
    
    query = ResearchList.query.filter_by(is_active=True)
    
    if asset_type_filter:
        query = query.filter(ResearchList.asset_type == asset_type_filter)
    if recommendation_filter:
        query = query.filter(ResearchList.recommendation == recommendation_filter)
    if search_query:
        query = query.filter(
            (ResearchList.symbol.ilike(f'%{search_query}%')) | 
            (ResearchList.company_name.ilike(f'%{search_query}%'))
        )
    
    stocks = query.order_by(ResearchList.i_score.desc().nullslast()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    total_count = ResearchList.query.filter_by(is_active=True).count()
    analyzed_count = ResearchList.query.filter(ResearchList.i_score.isnot(None), ResearchList.is_active==True).count()
    
    return render_template('admin/research_list.html', 
                          stocks=stocks,
                          total_count=total_count,
                          analyzed_count=analyzed_count,
                          asset_type_filter=asset_type_filter,
                          recommendation_filter=recommendation_filter,
                          search_query=search_query)

@admin_bp.route('/research-list/add', methods=['GET', 'POST'])
@admin_required
def add_research_stock():
    """Add new stock to Research List"""
    if request.method == 'POST':
        try:
            symbol = request.form.get('symbol', '').upper().strip()
            
            existing = ResearchList.query.filter_by(symbol=symbol).first()
            if existing:
                flash(f'{symbol} already exists in Research List!', 'warning')
                return redirect(url_for('admin.research_list'))
            
            stock = ResearchList(
                symbol=symbol,
                company_name=request.form.get('company_name', ''),
                asset_type=request.form.get('asset_type', 'stocks'),
                sector=request.form.get('sector', ''),
                is_active=True,
                tenant_id='live'
            )
            
            db.session.add(stock)
            db.session.commit()
            
            flash(f'{symbol} added to Research List! Click "Compute I-Score" to analyze.', 'success')
            return redirect(url_for('admin.research_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding stock: {str(e)}', 'error')
    
    return render_template('admin/add_research_stock.html')

@admin_bp.route('/research-list/<int:stock_id>/refresh', methods=['POST'])
@admin_required
def refresh_research_stock(stock_id):
    """Refresh I-Score for a stock using LangGraph engine"""
    stock = ResearchList.query.get_or_404(stock_id)
    
    try:
        from services.langgraph_iscore_engine import IScoreEngine
        engine = IScoreEngine()
        
        result = engine.compute_iscore(
            symbol=stock.symbol,
            asset_type=stock.asset_type
        )
        
        if result and result.get('overall_score') is not None:
            stock.update_from_iscore_result(result)
            stock.computation_source = 'manual'
            db.session.commit()
            flash(f'I-Score updated for {stock.symbol}: {result.get("overall_score", 0):.1f}', 'success')
        else:
            flash(f'Could not compute I-Score for {stock.symbol}', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error computing I-Score: {str(e)}', 'error')
    
    return redirect(url_for('admin.research_list'))

@admin_bp.route('/research-list/<int:stock_id>/details')
@admin_required
def research_stock_details(stock_id):
    """Get detailed I-Score breakdown for a stock (AJAX)"""
    stock = ResearchList.query.get_or_404(stock_id)
    
    return jsonify({
        'symbol': stock.symbol,
        'company_name': stock.company_name,
        'asset_type': stock.asset_type,
        'sector': stock.sector,
        'i_score': float(stock.i_score) if stock.i_score else None,
        'recommendation': stock.recommendation,
        'confidence': float(stock.confidence) if stock.confidence else None,
        'qualitative_score': float(stock.qualitative_score) if stock.qualitative_score else None,
        'quantitative_score': float(stock.quantitative_score) if stock.quantitative_score else None,
        'search_score': float(stock.search_score) if stock.search_score else None,
        'trend_score': float(stock.trend_score) if stock.trend_score else None,
        'qualitative_details': stock.qualitative_details or {},
        'quantitative_details': stock.quantitative_details or {},
        'search_details': stock.search_details or {},
        'trend_details': stock.trend_details or {},
        'current_price': float(stock.current_price) if stock.current_price else None,
        'previous_close': float(stock.previous_close) if stock.previous_close else None,
        'price_change_pct': float(stock.price_change_pct) if stock.price_change_pct else None,
        'recommendation_summary': stock.recommendation_summary,
        'last_computed_at': stock.last_computed_at.isoformat() if stock.last_computed_at else None,
        'score_age_hours': stock.score_age_hours,
        'is_stale': stock.is_stale
    })

@admin_bp.route('/research-list/<int:stock_id>/delete', methods=['POST'])
@admin_required
def delete_research_stock(stock_id):
    """Delete stock from Research List"""
    stock = ResearchList.query.get_or_404(stock_id)
    
    try:
        db.session.delete(stock)
        db.session.commit()
        flash(f'{stock.symbol} removed from Research List!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing stock: {str(e)}', 'error')
    
    return redirect(url_for('admin.research_list'))

@admin_bp.route('/payments')
@admin_bp.route('/payments/<view_type>')
@admin_required
def payments(view_type='daily'):
    """Payment management with daily/weekly/monthly views"""
    today = datetime.utcnow().date()
    
    if view_type == 'weekly':
        start_date = today - timedelta(days=7)
    elif view_type == 'monthly':
        start_date = today.replace(day=1)
    else:  # daily
        start_date = today
    
    payments = UserPayment.query.filter(
        func.date(UserPayment.created_at) >= start_date
    ).order_by(desc(UserPayment.created_at)).all()
    
    # Calculate summary
    total_amount = sum(p.amount for p in payments if p.status == 'COMPLETED')
    total_count = len([p for p in payments if p.status == 'COMPLETED'])
    
    return render_template('admin/payments.html',
                         payments=payments,
                         view_type=view_type,
                         total_amount=total_amount,
                         total_count=total_count)

@admin_bp.route('/account-handling')
@admin_bp.route('/account-handling/<int:page>')
@admin_required
def account_handling(page=1):
    """Premium user account handling with P&L tracking"""
    per_page = 20
    
    # Get premium users (Target Pro and HNI plans)
    premium_users = User.query.filter(
        User.pricing_plan.in_(['TARGET_PRO', 'HNI'])
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate daily P&L for each user
    today = datetime.utcnow().date()
    user_pnl = {}
    
    for user in premium_users.items:
        trades_today = ExecutedTrade.query.filter(
            ExecutedTrade.user_id == user.id,
            func.date(ExecutedTrade.executed_at) == today
        ).all()
        
        daily_pnl = sum(trade.unrealized_pnl + trade.realized_pnl for trade in trades_today)
        user_pnl[user.id] = {
            'daily_pnl': daily_pnl,
            'trades_count': len(trades_today)
        }
    
    return render_template('admin/account_handling.html',
                         premium_users=premium_users,
                         user_pnl=user_pnl)

# API endpoints for admin dashboard
@admin_bp.route('/api/signals/today')
@admin_required
def api_signals_today():
    """API endpoint for today's signals"""
    today = datetime.utcnow().date()
    signals = TradingSignal.query.filter(
        func.date(TradingSignal.created_at) == today
    ).all()
    
    return jsonify([{
        'id': s.id,
        'symbol': s.symbol,
        'action': s.action,
        'signal_type': s.signal_type,
        'created_at': s.created_at.isoformat()
    } for s in signals])

@admin_bp.route('/api/share-signal/<int:signal_id>', methods=['POST'])
@admin_required
def api_share_signal(signal_id):
    """API endpoint to share signal to WhatsApp/Telegram"""
    signal = TradingSignal.query.get_or_404(signal_id)
    platform = request.json.get('platform')  # 'whatsapp' or 'telegram'
    
    try:
        if platform == 'whatsapp':
            signal.shared_whatsapp = True
            signal.whatsapp_shared_at = datetime.utcnow()
            message = "Signal shared to WhatsApp successfully!"
            
        elif platform == 'telegram':
            signal.shared_telegram = True
            signal.telegram_shared_at = datetime.utcnow()
            message = "Signal shared to Telegram successfully!"
        else:
            return jsonify({'success': False, 'message': 'Invalid platform'}), 400
        
        db.session.commit()
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# I-SCORE RESEARCH CONFIGURATION
# ============================================================================

@admin_bp.route('/research-config')
@admin_required
def research_config():
    """I-Score research configuration page"""
    from models import ResearchWeightConfig, ResearchThresholdConfig
    
    weight_config = ResearchWeightConfig.get_active_config() or ResearchWeightConfig()
    threshold_config = ResearchThresholdConfig.get_active_config() or ResearchThresholdConfig()
    
    tech_params = weight_config.tech_params or {
        'rsi_period': 14,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'supertrend_period': 10,
        'supertrend_multiplier': 3,
        'ema_short': 9,
        'ema_long': 20
    }
    
    trend_params = weight_config.trend_params or {
        'oi_change_threshold': 5,
        'pcr_bullish_threshold': 0.7,
        'pcr_bearish_threshold': 1.3,
        'vix_low': 15,
        'vix_high': 25
    }
    
    qualitative_sources = weight_config.qualitative_sources or {
        'annual_reports': True,
        'twitter': True,
        'moneycontrol': True,
        'economic_times': True,
        'nse_india': True,
        'bse_india': True,
        'screener': True,
        'glassdoor': True
    }
    
    return render_template('admin/research_config.html',
                          weight_config=weight_config,
                          threshold_config=threshold_config,
                          tech_params=tech_params,
                          trend_params=trend_params,
                          qualitative_sources=qualitative_sources)


@admin_bp.route('/save-research-weights', methods=['POST'])
@admin_required
def admin_save_research_weights():
    """Save I-Score weight configuration"""
    from models import ResearchWeightConfig
    
    try:
        qualitative_pct = int(request.form.get('qualitative_pct', 15))
        quantitative_pct = int(request.form.get('quantitative_pct', 50))
        search_pct = int(request.form.get('search_pct', 10))
        trend_pct = int(request.form.get('trend_pct', 25))
        
        total = qualitative_pct + quantitative_pct + search_pct + trend_pct
        if total != 100:
            flash(f'Weights must sum to 100%. Current total: {total}%', 'error')
            return redirect(url_for('admin.research_config'))
        
        existing = ResearchWeightConfig.get_active_config()
        if existing:
            existing.is_active = False
        
        new_config = ResearchWeightConfig(
            qualitative_pct=qualitative_pct,
            quantitative_pct=quantitative_pct,
            search_pct=search_pct,
            trend_pct=trend_pct,
            tech_params=existing.tech_params if existing else None,
            trend_params=existing.trend_params if existing else None,
            qualitative_sources=existing.qualitative_sources if existing else None,
            version=(existing.version + 1) if existing else 1,
            is_active=True,
            created_by=session.get('admin_id')
        )
        
        db.session.add(new_config)
        db.session.commit()
        
        flash('I-Score weight configuration saved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving configuration: {str(e)}', 'error')
    
    return redirect(url_for('admin.research_config'))


@admin_bp.route('/save-tech-params', methods=['POST'])
@admin_required
def admin_save_tech_params():
    """Save technical indicator parameters"""
    from models import ResearchWeightConfig
    
    try:
        tech_params = {
            'rsi_period': int(request.form.get('rsi_period', 14)),
            'rsi_overbought': int(request.form.get('rsi_overbought', 70)),
            'rsi_oversold': int(request.form.get('rsi_oversold', 30)),
            'supertrend_period': int(request.form.get('supertrend_period', 10)),
            'supertrend_multiplier': float(request.form.get('supertrend_multiplier', 3)),
            'ema_short': int(request.form.get('ema_short', 9)),
            'ema_long': int(request.form.get('ema_long', 20))
        }
        
        config = ResearchWeightConfig.get_active_config()
        if config:
            config.tech_params = tech_params
            config.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Technical indicator parameters saved!', 'success')
        else:
            new_config = ResearchWeightConfig(
                tech_params=tech_params,
                is_active=True
            )
            db.session.add(new_config)
            db.session.commit()
            flash('Technical indicator parameters saved!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving parameters: {str(e)}', 'error')
    
    return redirect(url_for('admin.research_config'))


@admin_bp.route('/save-threshold-config', methods=['POST'])
@admin_required
def admin_save_threshold_config():
    """Save I-Score recommendation thresholds"""
    from models import ResearchThresholdConfig
    
    try:
        strong_buy = int(request.form.get('strong_buy_threshold', 80))
        buy = int(request.form.get('buy_threshold', 65))
        hold_low = int(request.form.get('hold_low', 45))
        hold_high = int(request.form.get('hold_high', 64))
        sell = int(request.form.get('sell_threshold', 30))
        min_confidence = float(request.form.get('min_confidence', 0.6))
        
        existing = ResearchThresholdConfig.get_active_config()
        if existing:
            existing.strong_buy_threshold = strong_buy
            existing.buy_threshold = buy
            existing.hold_low = hold_low
            existing.hold_high = hold_high
            existing.sell_threshold = sell
            existing.min_confidence = min_confidence
            existing.updated_at = datetime.utcnow()
        else:
            new_config = ResearchThresholdConfig(
                strong_buy_threshold=strong_buy,
                buy_threshold=buy,
                hold_low=hold_low,
                hold_high=hold_high,
                sell_threshold=sell,
                min_confidence=min_confidence,
                is_active=True,
                created_by=session.get('admin_id')
            )
            db.session.add(new_config)
        
        db.session.commit()
        flash('I-Score thresholds saved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving thresholds: {str(e)}', 'error')
    
    return redirect(url_for('admin.research_config'))


@admin_bp.route('/save-qualitative-sources', methods=['POST'])
@admin_required
def admin_save_qualitative_sources():
    """Save qualitative data source configuration"""
    from models import ResearchWeightConfig
    
    try:
        sources = {
            'annual_reports': 'annual_reports' in request.form,
            'twitter': 'twitter' in request.form,
            'moneycontrol': 'moneycontrol' in request.form,
            'economic_times': 'economic_times' in request.form,
            'nse_india': 'nse_india' in request.form,
            'bse_india': 'bse_india' in request.form,
            'screener': 'screener' in request.form,
            'glassdoor': 'glassdoor' in request.form,
            'zerodha_varsity': 'zerodha_varsity' in request.form,
            'investing_com': 'investing_com' in request.form,
            'stockedge': 'stockedge' in request.form,
            'groww': 'groww' in request.form,
            'upstox': 'upstox' in request.form,
            'angelone': 'angelone' in request.form
        }
        
        config = ResearchWeightConfig.get_active_config()
        if config:
            config.qualitative_sources = sources
            config.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Qualitative data sources saved!', 'success')
        else:
            new_config = ResearchWeightConfig(
                qualitative_sources=sources,
                is_active=True
            )
            db.session.add(new_config)
            db.session.commit()
            flash('Qualitative data sources saved!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving sources: {str(e)}', 'error')
    
    return redirect(url_for('admin.research_config'))


@admin_bp.route('/save-trend-params', methods=['POST'])
@admin_required
def admin_save_trend_params():
    """Save trend analysis parameters"""
    from models import ResearchWeightConfig
    
    try:
        trend_params = {
            'oi_change_threshold': float(request.form.get('oi_change_threshold', 5)),
            'pcr_bullish_threshold': float(request.form.get('pcr_bullish_threshold', 0.7)),
            'pcr_bearish_threshold': float(request.form.get('pcr_bearish_threshold', 1.3)),
            'vix_low': float(request.form.get('vix_low', 15)),
            'vix_high': float(request.form.get('vix_high', 25))
        }
        
        config = ResearchWeightConfig.get_active_config()
        if config:
            config.trend_params = trend_params
            config.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Trend analysis parameters saved!', 'success')
        else:
            new_config = ResearchWeightConfig(
                trend_params=trend_params,
                is_active=True
            )
            db.session.add(new_config)
            db.session.commit()
            flash('Trend analysis parameters saved!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving parameters: {str(e)}', 'error')
    
    return redirect(url_for('admin.research_config'))


