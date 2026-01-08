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
from models import Admin, User, PricingPlan, DailyTradingSignal
from models_broker import BrokerAccount
# Import with safe fallback for optional models
try:
    from models import TradingSignal, UserPayment, ExecutedTrade
    TRADING_SIGNALS_AVAILABLE = True
except ImportError:
    TRADING_SIGNALS_AVAILABLE = False
    TradingSignal = UserPayment = ExecutedTrade = None

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
    # Get statistics for dashboard
    total_users = User.query.count()
    active_signals = TradingSignal.query.filter_by(status='ACTIVE').count()
    today_payments = UserPayment.query.filter(
        func.date(UserPayment.created_at) == datetime.utcnow().date(),
        UserPayment.status == 'COMPLETED'
    ).count()
    
    # Recent trading signals
    recent_signals = TradingSignal.query.order_by(desc(TradingSignal.created_at)).limit(5).all()
    
    # Payment summary for current month
    current_month = datetime.utcnow().replace(day=1)
    monthly_revenue = db.session.query(func.sum(UserPayment.amount)).filter(
        UserPayment.created_at >= current_month,
        UserPayment.status == 'COMPLETED'
    ).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_signals=active_signals,
                         today_payments=today_payments,
                         recent_signals=recent_signals,
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
    """User detail page with payment and trade history"""
    user = User.query.get_or_404(user_id)
    payments = UserPayment.query.filter_by(user_id=user_id).order_by(desc(UserPayment.created_at)).limit(10).all()
    executed_trades = ExecutedTrade.query.filter_by(user_id=user_id).order_by(desc(ExecutedTrade.executed_at)).limit(10).all()
    brokers = UserBroker.query.filter_by(user_id=user_id).all()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         payments=payments,
                         executed_trades=executed_trades,
                         brokers=brokers)

@admin_bp.route('/trading-signals')
@admin_bp.route('/trading-signals/<int:page>')
@admin_required
def trading_signals(page=1):
    """Trading signals management page"""
    per_page = 20
    signals = TradingSignal.query.order_by(desc(TradingSignal.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/trading_signals.html', signals=signals)

@admin_bp.route('/trading-signals/add', methods=['GET', 'POST'])
@admin_required
def add_trading_signal():
    """Add new trading signal"""
    if request.method == 'POST':
        try:
            signal = TradingSignal(
                signal_type=request.form.get('signal_type'),
                symbol=request.form.get('symbol').upper(),
                company_name=request.form.get('company_name'),
                action=request.form.get('action'),
                entry_price=float(request.form.get('entry_price')) if request.form.get('entry_price') else None,
                target_price=float(request.form.get('target_price')) if request.form.get('target_price') else None,
                stop_loss=float(request.form.get('stop_loss')) if request.form.get('stop_loss') else None,
                quantity=int(request.form.get('quantity')) if request.form.get('quantity') else None,
                risk_level=request.form.get('risk_level'),
                time_frame=request.form.get('time_frame'),
                strategy_name=request.form.get('strategy_name'),
                notes=request.form.get('notes'),
                created_by=session['admin_id']
            )
            
            # Set expiration if provided
            expires_date = request.form.get('expires_date')
            if expires_date:
                signal.expires_at = datetime.strptime(expires_date, '%Y-%m-%d')
            
            db.session.add(signal)
            db.session.commit()
            
            flash(f'Trading signal for {signal.symbol} created successfully!', 'success')
            
            # Handle WhatsApp/Telegram sharing
            if request.form.get('share_whatsapp'):
                # TODO: Implement WhatsApp sharing
                signal.shared_whatsapp = True
                signal.whatsapp_shared_at = datetime.utcnow()
            
            if request.form.get('share_telegram'):
                # TODO: Implement Telegram sharing
                signal.shared_telegram = True
                signal.telegram_shared_at = datetime.utcnow()
            
            db.session.commit()
            
            return redirect(url_for('admin.trading_signals'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating trading signal: {str(e)}', 'error')
    
    return render_template('admin/add_trading_signal.html')

@admin_bp.route('/trading-signals/<int:signal_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_trading_signal(signal_id):
    """Edit existing trading signal"""
    signal = TradingSignal.query.get_or_404(signal_id)
    
    if request.method == 'POST':
        try:
            signal.signal_type = request.form.get('signal_type')
            signal.symbol = request.form.get('symbol').upper()
            signal.company_name = request.form.get('company_name')
            signal.action = request.form.get('action')
            signal.entry_price = float(request.form.get('entry_price')) if request.form.get('entry_price') else None
            signal.target_price = float(request.form.get('target_price')) if request.form.get('target_price') else None
            signal.stop_loss = float(request.form.get('stop_loss')) if request.form.get('stop_loss') else None
            signal.quantity = int(request.form.get('quantity')) if request.form.get('quantity') else None
            signal.risk_level = request.form.get('risk_level')
            signal.time_frame = request.form.get('time_frame')
            signal.strategy_name = request.form.get('strategy_name')
            signal.notes = request.form.get('notes')
            signal.status = request.form.get('status')
            signal.updated_at = datetime.utcnow()
            
            expires_date = request.form.get('expires_date')
            if expires_date:
                signal.expires_at = datetime.strptime(expires_date, '%Y-%m-%d')
            
            db.session.commit()
            flash(f'Trading signal for {signal.symbol} updated successfully!', 'success')
            return redirect(url_for('admin.trading_signals'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating trading signal: {str(e)}', 'error')
    
    return render_template('admin/edit_trading_signal.html', signal=signal)

@admin_bp.route('/trading-signals/<int:signal_id>/delete', methods=['POST'])
@admin_required
def delete_trading_signal(signal_id):
    """Delete trading signal"""
    signal = TradingSignal.query.get_or_404(signal_id)
    
    try:
        db.session.delete(signal)
        db.session.commit()
        flash(f'Trading signal for {signal.symbol} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting trading signal: {str(e)}', 'error')
    
    return redirect(url_for('admin.trading_signals'))

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


# ============================================================================
# DAILY TRADING SIGNALS MANAGEMENT
# ============================================================================

@admin_bp.route('/daily-signals')
@admin_bp.route('/daily-signals/<int:page>')
@admin_required
def daily_signals(page=1):
    """List and manage daily trading signals"""
    per_page = 20
    
    # Get filter parameters
    date_filter = request.args.get('date')
    asset_type_filter = request.args.get('asset_type', 'all')
    status_filter = request.args.get('status', 'all')
    
    # Build query
    query = DailyTradingSignal.query
    
    if date_filter:
        from datetime import datetime as dt
        try:
            filter_date = dt.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(DailyTradingSignal.signal_date == filter_date)
        except ValueError:
            pass
    
    if asset_type_filter != 'all':
        query = query.filter(DailyTradingSignal.asset_type == asset_type_filter)
    
    if status_filter != 'all':
        query = query.filter(DailyTradingSignal.status == status_filter)
    
    # Order by date descending, then signal number
    signals = query.order_by(
        desc(DailyTradingSignal.signal_date),
        DailyTradingSignal.signal_number
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/daily_signals.html',
                          signals=signals,
                          date_filter=date_filter,
                          asset_type_filter=asset_type_filter,
                          status_filter=status_filter)


@admin_bp.route('/daily-signals/add', methods=['GET', 'POST'])
@admin_required
def add_daily_signal():
    """Add new daily trading signal"""
    if request.method == 'POST':
        try:
            # Parse form data
            signal_date_str = request.form.get('signal_date')
            signal_date = datetime.strptime(signal_date_str, '%Y-%m-%d').date() if signal_date_str else datetime.utcnow().date()
            
            # Get next signal number for this date
            last_signal = DailyTradingSignal.query.filter_by(signal_date=signal_date).order_by(
                desc(DailyTradingSignal.signal_number)
            ).first()
            signal_number = (last_signal.signal_number + 1) if last_signal else 1
            
            # Build script name based on asset type
            asset_type = request.form.get('asset_type')
            sub_type = request.form.get('sub_type')
            symbol = request.form.get('symbol', '').upper()
            strike_price = request.form.get('strike_price')
            
            if asset_type in ['NIFTY', 'BANKNIFTY', 'SENSEX', 'FINNIFTY']:
                if sub_type in ['CE', 'PE']:
                    script = f"{asset_type}-{strike_price}-{sub_type}"
                else:
                    script = f"{asset_type}-FUT"
            else:
                if sub_type in ['CE', 'PE']:
                    script = f"{symbol}-{strike_price}-{sub_type}"
                elif sub_type == 'FUT':
                    script = f"{symbol}-FUT"
                else:
                    script = symbol
            
            # Create new signal
            new_signal = DailyTradingSignal(
                signal_number=signal_number,
                signal_date=signal_date,
                asset_type=asset_type,
                sub_type=sub_type,
                symbol=symbol if asset_type == 'STOCK' else asset_type,
                strike_price=float(strike_price) if strike_price else None,
                strike_type=request.form.get('strike_type'),
                script=script,
                trade_duration=request.form.get('trade_duration'),
                action=request.form.get('action', 'BUY'),
                buy_above=float(request.form.get('buy_above')),
                stop_loss=float(request.form.get('stop_loss')),
                target_1=float(request.form.get('target_1')) if request.form.get('target_1') else None,
                target_2=float(request.form.get('target_2')) if request.form.get('target_2') else None,
                target_3=float(request.form.get('target_3')) if request.form.get('target_3') else None,
                risk_level=request.form.get('risk_level', 'MEDIUM'),
                notes=request.form.get('notes'),
                created_by=session.get('admin_id'),
                analyst_name=session.get('admin_username'),
                status='ACTIVE'
            )
            
            db.session.add(new_signal)
            db.session.commit()
            
            flash(f'Daily Signal #{signal_number} created successfully for {signal_date}!', 'success')
            return redirect(url_for('admin.daily_signals'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating signal: {str(e)}', 'error')
    
    # Get today's date for default
    today = datetime.utcnow().date()
    
    return render_template('admin/add_daily_signal.html', today=today)


@admin_bp.route('/daily-signals/edit/<int:signal_id>', methods=['GET', 'POST'])
@admin_required
def edit_daily_signal(signal_id):
    """Edit existing daily trading signal"""
    signal = DailyTradingSignal.query.get_or_404(signal_id)
    
    if request.method == 'POST':
        try:
            # Update signal fields
            signal.asset_type = request.form.get('asset_type')
            signal.sub_type = request.form.get('sub_type')
            signal.symbol = request.form.get('symbol', '').upper()
            signal.strike_price = float(request.form.get('strike_price')) if request.form.get('strike_price') else None
            signal.strike_type = request.form.get('strike_type')
            signal.trade_duration = request.form.get('trade_duration')
            signal.action = request.form.get('action', 'BUY')
            signal.buy_above = float(request.form.get('buy_above'))
            signal.stop_loss = float(request.form.get('stop_loss'))
            signal.target_1 = float(request.form.get('target_1')) if request.form.get('target_1') else None
            signal.target_2 = float(request.form.get('target_2')) if request.form.get('target_2') else None
            signal.target_3 = float(request.form.get('target_3')) if request.form.get('target_3') else None
            signal.risk_level = request.form.get('risk_level', 'MEDIUM')
            signal.notes = request.form.get('notes')
            signal.status = request.form.get('status', signal.status)
            
            # Rebuild script name
            asset_type = signal.asset_type
            sub_type = signal.sub_type
            strike_price = signal.strike_price
            symbol = signal.symbol
            
            if asset_type in ['NIFTY', 'BANKNIFTY', 'SENSEX', 'FINNIFTY']:
                if sub_type in ['CE', 'PE']:
                    signal.script = f"{asset_type}-{strike_price}-{sub_type}"
                else:
                    signal.script = f"{asset_type}-FUT"
            else:
                if sub_type in ['CE', 'PE']:
                    signal.script = f"{symbol}-{strike_price}-{sub_type}"
                elif sub_type == 'FUT':
                    signal.script = f"{symbol}-FUT"
                else:
                    signal.script = symbol
            
            db.session.commit()
            flash(f'Signal #{signal.signal_number} updated successfully!', 'success')
            return redirect(url_for('admin.daily_signals'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating signal: {str(e)}', 'error')
    
    return render_template('admin/edit_daily_signal.html', signal=signal)


@admin_bp.route('/daily-signals/delete/<int:signal_id>', methods=['POST'])
@admin_required
def delete_daily_signal(signal_id):
    """Delete a daily trading signal"""
    signal = DailyTradingSignal.query.get_or_404(signal_id)
    
    try:
        db.session.delete(signal)
        db.session.commit()
        flash(f'Signal #{signal.signal_number} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting signal: {str(e)}', 'error')
    
    return redirect(url_for('admin.daily_signals'))


@admin_bp.route('/daily-signals/update-status/<int:signal_id>', methods=['POST'])
@admin_required
def update_signal_status(signal_id):
    """Update signal status (target hit, stop loss, etc.)"""
    signal = DailyTradingSignal.query.get_or_404(signal_id)
    
    try:
        new_status = request.form.get('status')
        trade_outcome = request.form.get('trade_outcome')
        profit_points = request.form.get('profit_points')
        loss_points = request.form.get('loss_points')
        
        signal.status = new_status
        signal.trade_outcome = trade_outcome
        
        if profit_points:
            signal.profit_points = float(profit_points)
        if loss_points:
            signal.loss_points = float(loss_points)
        
        if new_status in ['TARGET_1_HIT', 'TARGET_2_HIT', 'SL_HIT', 'CLOSED', 'EXPIRED']:
            signal.closed_at = datetime.utcnow()
        
        db.session.commit()
        flash(f'Signal #{signal.signal_number} status updated to {new_status}!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('admin.daily_signals'))