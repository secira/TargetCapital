"""
Background tasks for broker operations
Async processing of broker API calls and data synchronization
"""
import logging
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_broker_holdings(self, broker_account_id):
    """Sync holdings from broker API for a specific account"""
    try:
        from app import app, db
        from models_broker import BrokerAccount, BrokerHolding
        # TODO: Implement broker service when ready
        # from services.broker_service import get_broker_service
        
        with app.app_context():
            # Get broker account
            broker_account = BrokerAccount.query.get(broker_account_id)
            if not broker_account:
                logger.error(f"Broker account {broker_account_id} not found")
                return {'error': 'Broker account not found'}
            
            # TODO: Implement broker service integration
            logger.info(f"Broker sync requested for account {broker_account_id} - service not implemented yet")
            return {'info': 'Broker service integration pending implementation'}
            
            # Update database
            updated_count = 0
            for holding_data in holdings_data:
                holding = BrokerHolding.query.filter_by(
                    broker_account_id=broker_account_id,
                    trading_symbol=holding_data['trading_symbol']
                ).first()
                
                if holding:
                    # Update existing holding
                    holding.total_quantity = holding_data.get('quantity', 0)
                    holding.current_price = holding_data.get('current_price', 0)
                    holding.last_updated = datetime.utcnow()
                    holding.calculate_pnl()
                else:
                    # Create new holding
                    holding = BrokerHolding(
                        broker_account_id=broker_account_id,
                        symbol=holding_data['symbol'],
                        trading_symbol=holding_data['trading_symbol'],
                        exchange=holding_data['exchange'],
                        total_quantity=holding_data.get('quantity', 0),
                        current_price=holding_data.get('current_price', 0),
                        avg_cost_price=holding_data.get('avg_price', 0),
                    )
                    holding.calculate_pnl()
                    db.session.add(holding)
                
                updated_count += 1
            
            # Update broker account sync status
            broker_account.last_sync_time = datetime.utcnow()
            broker_account.connection_status = 'connected'
            
            db.session.commit()
            
            logger.info(f"Successfully synced {updated_count} holdings for broker account {broker_account_id}")
            return {'success': True, 'updated_count': updated_count}
            
    except Exception as exc:
        logger.error(f"Error syncing broker holdings: {exc}")
        try:
            # Retry with exponential backoff
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for broker holdings sync: {broker_account_id}")
            return {'error': 'Max retries exceeded'}

@shared_task(bind=True, max_retries=3)
def sync_broker_orders(self, broker_account_id):
    """Sync recent orders from broker API"""
    try:
        from app import app, db
        from models_broker import BrokerAccount, BrokerOrder
        from services.broker_service import get_broker_service
        
        with app.app_context():
            broker_account = BrokerAccount.query.get(broker_account_id)
            if not broker_account:
                return {'error': 'Broker account not found'}
            
            service = get_broker_service(broker_account.broker_type)
            credentials = broker_account.get_credentials()
            
            # Get orders from last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            orders_data = service.get_orders(credentials, start_date, end_date)
            
            updated_count = 0
            for order_data in orders_data:
                order = BrokerOrder.query.filter_by(
                    broker_account_id=broker_account_id,
                    broker_order_id=order_data['order_id']
                ).first()
                
                if order:
                    # Update existing order
                    order.order_status = order_data.get('status', order.order_status)
                    order.filled_quantity = order_data.get('filled_quantity', 0)
                    order.avg_execution_price = order_data.get('avg_price', 0)
                    order.last_updated = datetime.utcnow()
                else:
                    # Create new order record
                    order = BrokerOrder(
                        broker_account_id=broker_account_id,
                        broker_order_id=order_data['order_id'],
                        symbol=order_data['symbol'],
                        trading_symbol=order_data['trading_symbol'],
                        exchange=order_data['exchange'],
                        quantity=order_data.get('quantity', 0),
                        price=order_data.get('price', 0),
                        order_status=order_data.get('status', 'PENDING')
                    )
                    db.session.add(order)
                
                updated_count += 1
            
            db.session.commit()
            logger.info(f"Successfully synced {updated_count} orders for broker account {broker_account_id}")
            return {'success': True, 'updated_count': updated_count}
            
    except Exception as exc:
        logger.error(f"Error syncing broker orders: {exc}")
        raise self.retry(countdown=120)

@shared_task
def sync_all_broker_data():
    """Sync data for all connected broker accounts"""
    from app import app, db
    from models_broker import BrokerAccount
    
    with app.app_context():
        # Get all connected broker accounts
        connected_accounts = BrokerAccount.query.filter_by(
            connection_status='connected'
        ).all()
        
        synced_count = 0
        for account in connected_accounts:
            # Queue individual sync tasks
            sync_broker_holdings.delay(account.id)
            sync_broker_orders.delay(account.id)
            synced_count += 1
        
        logger.info(f"Queued sync tasks for {synced_count} broker accounts")
        return {'success': True, 'accounts_synced': synced_count}

@shared_task(bind=True, max_retries=3)
def execute_broker_order(self, broker_account_id, order_params):
    """Execute an order through broker API"""
    try:
        from app import app, db
        from models_broker import BrokerAccount, BrokerOrder
        from services.broker_service import get_broker_service
        
        with app.app_context():
            broker_account = BrokerAccount.query.get(broker_account_id)
            service = get_broker_service(broker_account.broker_type)
            credentials = broker_account.get_credentials()
            
            # Execute order via broker API
            order_response = service.place_order(credentials, order_params)
            
            # Create order record in database
            order = BrokerOrder(
                broker_account_id=broker_account_id,
                broker_order_id=order_response.get('order_id'),
                symbol=order_params['symbol'],
                trading_symbol=order_params['trading_symbol'],
                exchange=order_params['exchange'],
                quantity=order_params['quantity'],
                price=order_params.get('price', 0),
                order_status='PENDING'
            )
            db.session.add(order)
            db.session.commit()
            
            logger.info(f"Order executed successfully: {order_response}")
            return {'success': True, 'order_id': order_response.get('order_id')}
            
    except Exception as exc:
        logger.error(f"Error executing broker order: {exc}")
        raise self.retry(countdown=30)