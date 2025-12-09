"""
Routes for Trading Signals Display and Management
Handles the user-facing trading signals functionality
"""
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from models import TradingSignal
from datetime import datetime, timezone

@app.route('/dashboard/trading-signals')
@login_required
def dashboard_trading_signals():
    """Trading signals page for users"""
    
    # Check if user has access to trading signals
    if current_user.pricing_plan == 'free':
        # Free users can see the page but with upgrade notice
        signals = []
    else:
        # Paid users can see active signals
        signals = TradingSignal.query.filter(
            TradingSignal.is_active == True,
            db.or_(
                TradingSignal.expires_at.is_(None),
                TradingSignal.expires_at > datetime.now(timezone.utc)
            )
        ).order_by(TradingSignal.created_at.desc()).all()
    
    return render_template('dashboard/trading_signals.html', signals=signals)

@app.route('/dashboard/trading-signals/api')
@login_required
def trading_signals_api():
    """API endpoint for real-time signal updates"""
    
    if current_user.pricing_plan == 'free':
        return jsonify({'error': 'Upgrade required', 'signals': []})
    
    # Get active signals
    signals = TradingSignal.query.filter(
        TradingSignal.is_active == True,
        db.or_(
            TradingSignal.expires_at.is_(None),
            TradingSignal.expires_at > datetime.now(timezone.utc)
        )
    ).order_by(TradingSignal.created_at.desc()).all()
    
    signals_data = []
    for signal in signals:
        signals_data.append({
            'id': signal.id,
            'symbol': signal.symbol,
            'company_name': signal.company_name,
            'signal_type': signal.signal_type,
            'action': signal.action,
            'entry_price': signal.entry_price,
            'target_price': signal.target_price,
            'stop_loss': signal.stop_loss,
            'quantity': signal.quantity,
            'time_frame': signal.time_frame,
            'risk_level': signal.risk_level,
            'strategy_name': signal.strategy_name,
            'notes': signal.notes,
            'potential_return': signal.potential_return,
            'created_at': signal.created_at.isoformat(),
            'expires_at': signal.expires_at.isoformat() if signal.expires_at else None
        })
    
    return jsonify({'signals': signals_data})

@app.route('/dashboard/trading-signals/<int:signal_id>/execute')
@login_required
def execute_trading_signal(signal_id):
    """Execute trading signal through connected broker"""
    
    # Check if user has trading access
    if current_user.pricing_plan not in ['target_pro', 'hni']:
        flash('Trading execution requires Target Pro or HNI subscription', 'error')
        return redirect(url_for('dashboard_trading_signals'))
    
    # Get the signal
    signal = TradingSignal.query.get_or_404(signal_id)
    
    # Check if signal is still active
    if not signal.is_active or (signal.expires_at and signal.expires_at < datetime.now(timezone.utc)):
        flash('This trading signal has expired', 'error')
        return redirect(url_for('dashboard_trading_signals'))
    
    # Redirect to Trade Now page with signal parameters
    return redirect(url_for('dashboard_trade_now', 
                          signal_id=signal_id,
                          symbol=signal.symbol,
                          action=signal.action,
                          entry_price=signal.entry_price,
                          target_price=signal.target_price,
                          stop_loss=signal.stop_loss,
                          quantity=signal.quantity))

# Add primary broker management routes
@app.route('/dashboard/broker-accounts/<int:broker_id>/set-primary', methods=['POST'])
@login_required  
def set_primary_broker(broker_id):
    """Set a broker as primary for trading"""
    
    from models_broker import BrokerAccount
    
    # Get the broker account
    broker = BrokerAccount.query.filter_by(
        id=broker_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Check if broker is connected
    if broker.connection_status != 'connected':
        return jsonify({
            'success': False, 
            'error': 'Cannot set disconnected broker as primary. Please connect first.'
        })
    
    try:
        # Remove primary status from all user's brokers
        BrokerAccount.query.filter_by(user_id=current_user.id).update({'is_primary': False})
        
        # Set this broker as primary
        broker.is_primary = True
        
        db.session.commit()
        
        flash(f'{broker.broker_name} set as primary broker for trading', 'success')
        return jsonify({'success': True, 'message': 'Primary broker updated'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dashboard/broker-accounts/<int:broker_id>/connect', methods=['POST'])
@login_required
def reconnect_broker(broker_id):
    """Reconnect a disconnected broker"""
    
    from models_broker import BrokerAccount
    from services.broker_service import BrokerService
    
    broker = BrokerAccount.query.filter_by(
        id=broker_id,
        user_id=current_user.id
    ).first_or_404()
    
    try:
        # Use broker service to test connection
        broker_service = BrokerService()
        connection_result = broker_service.test_broker_connection(broker)
        
        if connection_result['success']:
            broker.connection_status = 'connected'
            broker.last_connected = datetime.now(timezone.utc)
            db.session.commit()
            
            flash(f'Successfully reconnected to {broker.broker_name}', 'success')
            return jsonify({'success': True, 'message': 'Broker reconnected successfully'})
        else:
            return jsonify({'success': False, 'error': connection_result.get('error', 'Connection failed')})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_primary_broker_for_user(user_id):
    """Helper function to get user's primary broker"""
    from models_broker import BrokerAccount
    
    return BrokerAccount.query.filter_by(
        user_id=user_id,
        is_primary=True,
        connection_status='connected'
    ).first()