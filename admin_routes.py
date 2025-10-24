"""
Admin Routes for tCapital Trading Platform
Separate admin module with authentication and management features
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from models import Admin, User, PricingPlan
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
        
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Welcome to tCapital Admin Dashboard!', 'success')
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
        User.pricing_plan.in_(['target_pro', 'hni'])
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
            # TODO: Implement WhatsApp API integration
            signal.shared_whatsapp = True
            signal.whatsapp_shared_at = datetime.utcnow()
            message = "Signal shared to WhatsApp successfully!"
            
        elif platform == 'telegram':
            # TODO: Implement Telegram Bot API integration
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