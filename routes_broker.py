"""
Broker Routes - Handle broker connections, portfolio sync, and trading
"""

from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from models_broker import (
    BrokerAccount, BrokerHolding, BrokerPosition, BrokerOrder,
    BrokerType, ConnectionStatus, OrderStatus, TransactionType,
    ProductType, OrderType
)
from services.broker_service import BrokerService, BrokerAPIError
import logging

logger = logging.getLogger(__name__)

# Main broker routes - integrated into existing dashboard pages

@app.route('/dashboard/broker-accounts')
@login_required
def dashboard_broker_accounts():
    """Broker accounts management page - Available to all users"""
    
    broker_accounts = BrokerAccount.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard/broker_accounts.html',
                         broker_accounts=broker_accounts,
                         broker_types=BrokerType)

@app.route('/api/broker/add-account', methods=['POST'])
@login_required
def api_add_broker_account():
    """Add new broker account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['broker_type', 'client_id', 'access_token']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing {field}'}), 400
        
        # Check if broker type is valid
        try:
            broker_type = BrokerType(data['broker_type'])
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid broker type'}), 400
        
        # Prepare credentials based on broker type
        credentials = {
            'client_id': data['client_id'],
            'access_token': data['access_token'],
            'api_secret': data.get('api_secret'),
            'totp_secret': data.get('totp_secret')
        }
        
        # Check if user already has an account with this broker
        existing_account = BrokerAccount.query.filter_by(
            user_id=current_user.id, 
            broker_type=broker_type.value
        ).first()
        
        if existing_account:
            return jsonify({
                'success': False,
                'message': 'User can create only connection with each broker'
            }), 400
        
        # Check broker limits based on pricing plan
        from models import PricingPlan
        if current_user.pricing_plan == PricingPlan.TRADER:
            # Trader users can only have one broker
            existing_brokers_count = BrokerAccount.query.filter_by(user_id=current_user.id).count()
            if existing_brokers_count >= 1:
                return jsonify({
                    'success': False,
                    'message': 'Trader plan allows only one broker connection. Upgrade to Trader Plus for multiple brokers.'
                }), 400
        
        # Add broker account
        broker_account = BrokerService.add_broker_account(
            user_id=current_user.id,
            broker_type=broker_type,
            credentials=credentials
        )
        
        return jsonify({
            'success': True,
            'message': f'{broker_type.value.title()} account connected successfully. You can sync data manually using the sync button.',
            'account_id': broker_account.id
        })
            
    except Exception as e:
            logger.error(f"Unexpected error in add_broker_account: {str(e)}")
            return jsonify({
                'success': False, 
                'message': f'Unexpected error: {str(e)}'
            }), 500
            
    except BrokerAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding broker account: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/broker/sync-account/<int:account_id>', methods=['POST'])
@login_required
def api_sync_broker_account(account_id):
    """Sync broker account data"""
    try:
        broker_account = BrokerAccount.query.filter_by(
            id=account_id, 
            user_id=current_user.id
        ).first()
        
        if not broker_account:
            return jsonify({'success': False, 'message': 'Broker account not found'}), 404
        
        # Get sync types from request
        data = request.get_json() or {}
        sync_types = data.get('sync_types', ['holdings', 'positions', 'orders'])
        
        # Perform sync
        sync_results = BrokerService.sync_broker_data(broker_account, sync_types)
        
        return jsonify({
            'success': True,
            'message': 'Account synced successfully',
            'sync_results': sync_results
        })
        
    except BrokerAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error syncing broker account: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/broker/remove-account/<int:account_id>', methods=['DELETE'])
@login_required
def api_remove_broker_account(account_id):
    """Remove broker account"""
    try:
        broker_account = BrokerAccount.query.filter_by(
            id=account_id, 
            user_id=current_user.id
        ).first()
        
        if not broker_account:
            return jsonify({'success': False, 'message': 'Broker account not found'}), 404
        
        broker_name = broker_account.broker_name
        
        # Delete account and all related data (cascade delete)
        db.session.delete(broker_account)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{broker_name} account removed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing broker account: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/broker/set-primary/<int:account_id>', methods=['POST'])
@login_required
def api_set_primary_broker(account_id):
    """Set primary broker account"""
    try:
        broker_account = BrokerAccount.query.filter_by(
            id=account_id, 
            user_id=current_user.id
        ).first()
        
        if not broker_account:
            return jsonify({'success': False, 'message': 'Broker account not found'}), 404
        
        broker_account.set_as_primary()
        
        return jsonify({
            'success': True,
            'message': f'{broker_account.broker_name} set as primary broker'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error setting primary broker: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/dashboard/live-portfolio')
@login_required
def dashboard_live_portfolio():
    """Live portfolio with real broker data"""
    # Check subscription access
    from models import PricingPlan
    if current_user.pricing_plan not in [PricingPlan.TRADER, PricingPlan.TRADER_PLUS, PricingPlan.PREMIUM]:
        flash('Live portfolio access requires Trader subscription or higher.', 'warning')
        return redirect(url_for('pricing'))
    
    # Get portfolio summary with error handling
    try:
        from services.broker_service_helpers import get_portfolio_summary
        portfolio_summary = get_portfolio_summary(current_user.id)
    except:
        portfolio_summary = {
            'total_value': 0,
            'total_pnl': 0, 
            'holdings_count': 0,
            'brokers_count': 0,
            'broker_accounts': []
        }
    
    # Get all holdings across brokers
    broker_accounts = BrokerAccount.query.filter_by(user_id=current_user.id, is_active=True).all()
    all_holdings = []
    
    for account in broker_accounts:
        holdings = BrokerHolding.query.filter_by(broker_account_id=account.id).all()
        for holding in holdings:
            holding.broker_name = account.broker_name
            all_holdings.append(holding)
    
    # Sort by total value
    all_holdings.sort(key=lambda x: x.total_value, reverse=True)
    
    return render_template('dashboard/live_portfolio.html',
                         portfolio_summary=portfolio_summary,
                         holdings=all_holdings,
                         broker_accounts=broker_accounts)

@app.route('/api/broker/place-order', methods=['POST'])
@login_required
def api_place_broker_order():
    """Place order through broker"""
    try:
        data = request.get_json()
        
        # Get broker account (use primary if not specified)
        account_id = data.get('broker_account_id')
        if account_id:
            broker_account = BrokerAccount.query.filter_by(
                id=account_id, 
                user_id=current_user.id
            ).first()
        else:
            broker_account = BrokerAccount.query.filter_by(
                user_id=current_user.id, 
                is_primary=True
            ).first()
        
        if not broker_account:
            return jsonify({'success': False, 'message': 'No broker account found'}), 404
        
        # Validate order data
        required_fields = ['symbol', 'transaction_type', 'quantity', 'order_type', 'product_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing {field}'}), 400
        
        # Prepare order data
        order_data = {
            'symbol': data['symbol'],
            'trading_symbol': data.get('trading_symbol', data['symbol']),
            'exchange': data.get('exchange', 'NSE'),
            'security_id': data.get('security_id'),
            'transaction_type': TransactionType(data['transaction_type']),
            'order_type': OrderType(data['order_type']),
            'product_type': ProductType(data['product_type']),
            'quantity': int(data['quantity']),
            'price': float(data.get('price', 0)),
            'trigger_price': float(data.get('trigger_price', 0)),
            'disclosed_quantity': int(data.get('disclosed_quantity', 0)),
            'correlation_id': data.get('correlation_id'),
            'trading_signal_id': data.get('trading_signal_id')
        }
        
        # Place order
        order = BrokerService.place_order_via_broker(broker_account, order_data)
        
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order.id,
            'broker_order_id': order.broker_order_id
        })
        
    except BrokerAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/broker/orders')
@login_required
def api_get_broker_orders():
    """Get user's broker orders"""
    try:
        # Get orders from all user's broker accounts
        broker_accounts = BrokerAccount.query.filter_by(user_id=current_user.id).all()
        account_ids = [account.id for account in broker_accounts]
        
        orders = BrokerOrder.query.filter(
            BrokerOrder.broker_account_id.in_(account_ids)
        ).order_by(BrokerOrder.order_time.desc()).limit(50).all()
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'broker_order_id': order.broker_order_id,
                'symbol': order.symbol,
                'transaction_type': order.transaction_type.value,
                'order_type': order.order_type.value,
                'product_type': order.product_type.value,
                'quantity': order.quantity,
                'filled_quantity': order.filled_quantity,
                'price': order.price,
                'order_status': order.order_status.value,
                'order_time': order.order_time.isoformat(),
                'broker_name': order.broker_account.broker_name,
                'avg_execution_price': order.avg_execution_price,
                'status_message': order.status_message
            })
        
        return jsonify({
            'success': True,
            'orders': orders_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/dashboard/broker-trading')
@login_required
def dashboard_broker_trading():
    """Broker trading interface"""
    # Check subscription access
    from models import PricingPlan
    if current_user.pricing_plan not in [PricingPlan.TRADER_PLUS, PricingPlan.PREMIUM]:
        flash('Broker trading requires Trader Plus or Premium subscription.', 'warning')
        return redirect(url_for('pricing'))
    
    broker_accounts = BrokerAccount.query.filter_by(
        user_id=current_user.id, 
        is_active=True,
        connection_status=ConnectionStatus.CONNECTED
    ).all()
    
    # Get recent orders
    if broker_accounts:
        account_ids = [account.id for account in broker_accounts]
        recent_orders = BrokerOrder.query.filter(
            BrokerOrder.broker_account_id.in_(account_ids)
        ).order_by(BrokerOrder.order_time.desc()).limit(10).all()
    else:
        recent_orders = []
    
    return render_template('dashboard/broker_trading.html',
                         broker_accounts=broker_accounts,
                         recent_orders=recent_orders)

@app.route('/api/broker/test-connection/<int:account_id>', methods=['POST'])
@login_required
def api_test_broker_connection(account_id):
    """Test broker connection"""
    try:
        broker_account = BrokerAccount.query.filter_by(
            id=account_id, 
            user_id=current_user.id
        ).first()
        
        if not broker_account:
            return jsonify({'success': False, 'message': 'Broker account not found'}), 404
        
        # Test connection
        client = BrokerService.get_broker_client(broker_account)
        if client.connect():
            return jsonify({
                'success': True,
                'message': 'Connection successful',
                'status': broker_account.connection_status.value,
                'last_connected': broker_account.last_connected.isoformat() if broker_account.last_connected else None
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Connection failed',
                'error': broker_account.connection_error
            })
            
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/broker/sync-all', methods=['POST'])
@login_required
def api_sync_all_brokers():
    """Sync all user's broker accounts"""
    try:
        broker_accounts = BrokerAccount.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
        
        if not broker_accounts:
            return jsonify({'success': False, 'message': 'No broker accounts found'}), 404
        
        results = {}
        for account in broker_accounts:
            try:
                from services.broker_service_helpers import sync_broker_data
                sync_result = sync_broker_data(account)
                results[account.broker_name] = sync_result
            except Exception as e:
                results[account.broker_name] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'message': f'Synced {len(broker_accounts)} broker accounts',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error syncing all brokers: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/broker/cancel-order/<order_id>', methods=['POST'])
@login_required
def api_cancel_broker_order(order_id):
    """Cancel order by broker order ID"""
    try:
        # Find the order
        order = BrokerOrder.query.join(BrokerAccount).filter(
            BrokerOrder.broker_order_id == order_id,
            BrokerAccount.user_id == current_user.id
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Get broker client and cancel order
        client = BrokerService.get_broker_client(order.broker_account)
        if not client.connect():
            return jsonify({'success': False, 'message': 'Failed to connect to broker'}), 400
        
        result = client.cancel_order(order_id)
        
        if result.get('status') == 'success':
            # Update order status in database
            order.update_status(OrderStatus.CANCELLED, 'Order cancelled by user')
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Order cancelled successfully'
            })
        else:
            return jsonify({'success': False, 'message': result.get('message', 'Failed to cancel order')}), 400
            
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500