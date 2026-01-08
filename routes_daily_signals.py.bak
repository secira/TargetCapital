"""
Routes for Daily Trading Signals
Handles display of daily analyst-generated trading signals with historical analysis
"""
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from models import DailyTradingSignal, PricingPlan
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


@app.route('/dashboard/daily-signals')
@login_required
def dashboard_daily_signals():
    """Daily trading signals page for users"""
    
    # Check subscription access
    if not current_user.is_authenticated or not current_user.can_access_menu('dashboard_trading_signals'):
        flash("This feature requires a Target Plus or higher subscription.", "warning")
        return redirect(url_for('pricing'))
        
    selected_date_str = request.args.get('date')
    asset_type_filter = request.args.get('asset_type', 'all')
    duration_filter = request.args.get('duration', 'all')
    status_filter = request.args.get('status', 'all')
    
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    query = DailyTradingSignal.query.filter(
        DailyTradingSignal.signal_date == selected_date
    )
    
    if asset_type_filter != 'all':
        query = query.filter(DailyTradingSignal.asset_type == asset_type_filter)
    
    if duration_filter != 'all':
        query = query.filter(DailyTradingSignal.trade_duration == duration_filter)
    
    if status_filter != 'all':
        query = query.filter(DailyTradingSignal.status == status_filter)
    
    signals = query.order_by(DailyTradingSignal.signal_number.asc()).all()
    
    date_range = []
    for i in range(30):
        d = date.today() - timedelta(days=i)
        date_range.append(d)
    
    summary_stats = calculate_daily_summary(selected_date)
    
    return render_template('dashboard/daily_signals.html', 
                         signals=signals,
                         selected_date=selected_date,
                         date_range=date_range,
                         asset_type_filter=asset_type_filter,
                         duration_filter=duration_filter,
                         status_filter=status_filter,
                         summary_stats=summary_stats)


@app.route('/dashboard/daily-signals/api')
@login_required
def daily_signals_api():
    """API endpoint for real-time daily signal updates"""
    
    selected_date_str = request.args.get('date')
    asset_type = request.args.get('asset_type', 'all')
    duration = request.args.get('duration', 'all')
    
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    query = DailyTradingSignal.query.filter(
        DailyTradingSignal.signal_date == selected_date
    )
    
    if asset_type != 'all':
        query = query.filter(DailyTradingSignal.asset_type == asset_type)
    
    if duration != 'all':
        query = query.filter(DailyTradingSignal.trade_duration == duration)
    
    signals = query.order_by(DailyTradingSignal.signal_number.asc()).all()
    
    signals_data = []
    for signal in signals:
        signals_data.append({
            'id': signal.id,
            'signal_number': signal.signal_number,
            'signal_date': signal.signal_date.isoformat(),
            'asset_type': signal.asset_type,
            'sub_type': signal.sub_type,
            'symbol': signal.symbol,
            'script': signal.script,
            'strike_price': float(signal.strike_price) if signal.strike_price else None,
            'strike_type': signal.strike_type,
            'trade_duration': signal.trade_duration,
            'duration_display': signal.duration_display,
            'action': signal.action,
            'buy_above': float(signal.buy_above),
            'stop_loss': float(signal.stop_loss),
            'target_1': float(signal.target_1) if signal.target_1 else None,
            'target_2': float(signal.target_2) if signal.target_2 else None,
            'target_3': float(signal.target_3) if signal.target_3 else None,
            'profit_points': float(signal.profit_points) if signal.profit_points else 0,
            'loss_points': float(signal.loss_points) if signal.loss_points else 0,
            'final_points': float(signal.final_points) if signal.final_points else 0,
            'trade_outcome': signal.trade_outcome,
            'status': signal.status,
            'risk_level': signal.risk_level,
            'potential_return_pct': round(signal.potential_return_pct, 2),
            'risk_pct': round(signal.risk_pct, 2),
            'risk_reward_ratio': round(signal.risk_reward_ratio, 2),
            'notes': signal.notes,
            'formatted_signal': signal.formatted_signal,
            'created_at': signal.created_at.isoformat() if signal.created_at else None
        })
    
    summary = calculate_daily_summary(selected_date)
    
    return jsonify({
        'signals': signals_data,
        'summary': summary,
        'date': selected_date.isoformat()
    })


@app.route('/dashboard/daily-signals/<int:signal_id>')
@login_required
def daily_signal_detail(signal_id):
    """View details of a specific daily signal"""
    
    signal = DailyTradingSignal.query.get_or_404(signal_id)
    
    return render_template('dashboard/daily_signal_detail.html', signal=signal)


@app.route('/dashboard/daily-signals/analysis')
@login_required
def daily_signals_analysis():
    """Historical analysis of daily signals performance"""
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = date.today() - timedelta(days=30)
    else:
        start_date = date.today() - timedelta(days=30)
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = date.today()
    else:
        end_date = date.today()
    
    signals = DailyTradingSignal.query.filter(
        DailyTradingSignal.signal_date >= start_date,
        DailyTradingSignal.signal_date <= end_date
    ).order_by(DailyTradingSignal.signal_date.desc(), DailyTradingSignal.signal_number.asc()).all()
    
    analysis_data = calculate_period_analysis(signals)
    
    daily_breakdown = {}
    for signal in signals:
        date_key = signal.signal_date.isoformat()
        if date_key not in daily_breakdown:
            daily_breakdown[date_key] = {
                'date': signal.signal_date,
                'total_signals': 0,
                'profitable': 0,
                'loss': 0,
                'total_points': 0
            }
        daily_breakdown[date_key]['total_signals'] += 1
        if signal.final_points and float(signal.final_points) > 0:
            daily_breakdown[date_key]['profitable'] += 1
        elif signal.final_points and float(signal.final_points) < 0:
            daily_breakdown[date_key]['loss'] += 1
        if signal.final_points:
            daily_breakdown[date_key]['total_points'] += float(signal.final_points)
    
    return render_template('dashboard/daily_signals_analysis.html',
                         signals=signals,
                         analysis_data=analysis_data,
                         daily_breakdown=list(daily_breakdown.values()),
                         start_date=start_date,
                         end_date=end_date)


def calculate_daily_summary(signal_date):
    """Calculate summary statistics for a given date"""
    
    signals = DailyTradingSignal.query.filter(
        DailyTradingSignal.signal_date == signal_date
    ).all()
    
    if not signals:
        return {
            'total_signals': 0,
            'active': 0,
            'target_1_hit': 0,
            'target_2_hit': 0,
            'sl_hit': 0,
            'early_exit': 0,
            'total_profit_points': 0,
            'total_loss_points': 0,
            'net_points': 0,
            'success_rate': 0,
            'by_asset_type': {},
            'by_duration': {}
        }
    
    active = sum(1 for s in signals if s.status == 'ACTIVE')
    target_1_hit = sum(1 for s in signals if s.trade_outcome and '1st Target' in s.trade_outcome)
    target_2_hit = sum(1 for s in signals if s.trade_outcome and '2nd Target' in s.trade_outcome)
    sl_hit = sum(1 for s in signals if s.trade_outcome and 'Stop Loss' in s.trade_outcome)
    early_exit = sum(1 for s in signals if s.trade_outcome and 'Early Exit' in s.trade_outcome)
    
    total_profit = sum(float(s.profit_points) for s in signals if s.profit_points)
    total_loss = sum(float(s.loss_points) for s in signals if s.loss_points)
    net_points = sum(float(s.final_points) for s in signals if s.final_points)
    
    completed_signals = [s for s in signals if s.trade_outcome]
    profitable = sum(1 for s in completed_signals if s.final_points and float(s.final_points) > 0)
    success_rate = (profitable / len(completed_signals) * 100) if completed_signals else 0
    
    by_asset_type = {}
    for signal in signals:
        if signal.asset_type not in by_asset_type:
            by_asset_type[signal.asset_type] = 0
        by_asset_type[signal.asset_type] += 1
    
    by_duration = {}
    for signal in signals:
        if signal.trade_duration not in by_duration:
            by_duration[signal.trade_duration] = 0
        by_duration[signal.trade_duration] += 1
    
    return {
        'total_signals': len(signals),
        'active': active,
        'target_1_hit': target_1_hit,
        'target_2_hit': target_2_hit,
        'sl_hit': sl_hit,
        'early_exit': early_exit,
        'total_profit_points': round(total_profit, 2),
        'total_loss_points': round(total_loss, 2),
        'net_points': round(net_points, 2),
        'success_rate': round(success_rate, 1),
        'by_asset_type': by_asset_type,
        'by_duration': by_duration
    }


def calculate_period_analysis(signals):
    """Calculate analysis for a period of signals"""
    
    if not signals:
        return {
            'total_signals': 0,
            'total_profit_points': 0,
            'total_loss_points': 0,
            'net_points': 0,
            'success_rate': 0,
            'avg_points_per_trade': 0,
            'best_trade': None,
            'worst_trade': None,
            'by_asset_type': {},
            'by_sub_type': {},
            'by_duration': {}
        }
    
    total_profit = sum(float(s.profit_points) for s in signals if s.profit_points)
    total_loss = sum(float(s.loss_points) for s in signals if s.loss_points)
    net_points = sum(float(s.final_points) for s in signals if s.final_points)
    
    completed_signals = [s for s in signals if s.trade_outcome and s.final_points]
    profitable = sum(1 for s in completed_signals if float(s.final_points) > 0)
    success_rate = (profitable / len(completed_signals) * 100) if completed_signals else 0
    avg_points = net_points / len(completed_signals) if completed_signals else 0
    
    best_trade = max(completed_signals, key=lambda s: float(s.final_points)) if completed_signals else None
    worst_trade = min(completed_signals, key=lambda s: float(s.final_points)) if completed_signals else None
    
    by_asset_type = {}
    for signal in signals:
        if signal.asset_type not in by_asset_type:
            by_asset_type[signal.asset_type] = {'count': 0, 'net_points': 0}
        by_asset_type[signal.asset_type]['count'] += 1
        if signal.final_points:
            by_asset_type[signal.asset_type]['net_points'] += float(signal.final_points)
    
    by_sub_type = {}
    for signal in signals:
        if signal.sub_type not in by_sub_type:
            by_sub_type[signal.sub_type] = {'count': 0, 'net_points': 0}
        by_sub_type[signal.sub_type]['count'] += 1
        if signal.final_points:
            by_sub_type[signal.sub_type]['net_points'] += float(signal.final_points)
    
    by_duration = {}
    for signal in signals:
        if signal.trade_duration not in by_duration:
            by_duration[signal.trade_duration] = {'count': 0, 'net_points': 0}
        by_duration[signal.trade_duration]['count'] += 1
        if signal.final_points:
            by_duration[signal.trade_duration]['net_points'] += float(signal.final_points)
    
    return {
        'total_signals': len(signals),
        'total_profit_points': round(total_profit, 2),
        'total_loss_points': round(total_loss, 2),
        'net_points': round(net_points, 2),
        'success_rate': round(success_rate, 1),
        'avg_points_per_trade': round(avg_points, 2),
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'by_asset_type': by_asset_type,
        'by_sub_type': by_sub_type,
        'by_duration': by_duration
    }
