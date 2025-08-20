"""
Broker Service - Multi-broker integration service
Supports Dhan, Zerodha, Angel Broking, and other brokers
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
import time

# Import broker-specific clients
try:
    from dhanhq import dhanhq
    DHAN_AVAILABLE = True
except ImportError:
    DHAN_AVAILABLE = False
    dhanhq = None

from models_broker import (
    BrokerAccount, BrokerHolding, BrokerPosition, BrokerOrder, BrokerSyncLog,
    BrokerType, ConnectionStatus, OrderStatus, TransactionType, 
    ProductType, OrderType
)
from app import db

logger = logging.getLogger(__name__)

class BrokerAPIError(Exception):
    """Custom exception for broker API errors"""
    pass

class BaseBrokerClient(ABC):
    """Abstract base class for broker clients"""
    
    def __init__(self, broker_account: BrokerAccount):
        self.broker_account = broker_account
        self.credentials = broker_account.get_credentials()
        self._client = None
        
    @abstractmethod
    def connect(self) -> bool:
        """Connect to broker API"""
        pass
        
    @abstractmethod
    def get_holdings(self) -> List[Dict]:
        """Get user holdings"""
        pass
        
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """Get user positions"""
        pass
        
    @abstractmethod
    def get_orders(self) -> List[Dict]:
        """Get user orders"""
        pass
        
    @abstractmethod
    def place_order(self, order_data: Dict) -> Dict:
        """Place an order"""
        pass
        
    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        pass
        
    @abstractmethod
    def get_profile(self) -> Dict:
        """Get user profile/account info"""
        pass

class DhanBrokerClient(BaseBrokerClient):
    """Dhan broker client implementation"""
    
    def __init__(self, broker_account: BrokerAccount):
        super().__init__(broker_account)
        if not DHAN_AVAILABLE:
            raise BrokerAPIError("Dhan library not available. Install with: pip install dhanhq")
    
    def connect(self) -> bool:
        """Connect to Dhan API"""
        try:
            client_id = self.credentials.get('client_id')
            access_token = self.credentials.get('access_token')
            
            if not client_id or not access_token:
                raise BrokerAPIError("Missing Dhan credentials")
            
            self._client = dhanhq(client_id, access_token)
            
            # Test connection by getting profile
            profile = self._client.get_profile()
            if profile and profile.get('clientId'):
                self.broker_account.update_connection_status(ConnectionStatus.CONNECTED)
                logger.info(f"Successfully connected to Dhan for account {client_id}")
                return True
            else:
                raise BrokerAPIError("Invalid response from Dhan API")
                
        except Exception as e:
            error_msg = f"Failed to connect to Dhan: {str(e)}"
            self.broker_account.update_connection_status(ConnectionStatus.ERROR, error_msg)
            logger.error(error_msg)
            return False
    
    def get_holdings(self) -> List[Dict]:
        """Get Dhan holdings"""
        if not self._client:
            raise BrokerAPIError("Not connected to Dhan")
        
        try:
            holdings = self._client.get_holdings()
            return self._normalize_holdings(holdings)
        except Exception as e:
            logger.error(f"Error fetching Dhan holdings: {e}")
            raise BrokerAPIError(f"Failed to fetch holdings: {e}")
    
    def get_positions(self) -> List[Dict]:
        """Get Dhan positions"""
        if not self._client:
            raise BrokerAPIError("Not connected to Dhan")
        
        try:
            positions = self._client.get_positions()
            return self._normalize_positions(positions)
        except Exception as e:
            logger.error(f"Error fetching Dhan positions: {e}")
            raise BrokerAPIError(f"Failed to fetch positions: {e}")
    
    def get_orders(self) -> List[Dict]:
        """Get Dhan orders"""
        if not self._client:
            raise BrokerAPIError("Not connected to Dhan")
        
        try:
            orders = self._client.get_order_list()
            return self._normalize_orders(orders)
        except Exception as e:
            logger.error(f"Error fetching Dhan orders: {e}")
            raise BrokerAPIError(f"Failed to fetch orders: {e}")
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place order with Dhan"""
        if not self._client:
            raise BrokerAPIError("Not connected to Dhan")
        
        try:
            # Convert our order format to Dhan format
            dhan_order = self._convert_to_dhan_order(order_data)
            result = self._client.place_order(**dhan_order)
            return self._normalize_order_response(result)
        except Exception as e:
            logger.error(f"Error placing Dhan order: {e}")
            raise BrokerAPIError(f"Failed to place order: {e}")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel Dhan order"""
        if not self._client:
            raise BrokerAPIError("Not connected to Dhan")
        
        try:
            result = self._client.cancel_order(order_id)
            return {'status': 'success', 'message': 'Order cancelled', 'data': result}
        except Exception as e:
            logger.error(f"Error cancelling Dhan order: {e}")
            raise BrokerAPIError(f"Failed to cancel order: {e}")
    
    def get_profile(self) -> Dict:
        """Get Dhan profile"""
        if not self._client:
            raise BrokerAPIError("Not connected to Dhan")
        
        try:
            profile = self._client.get_profile()
            return self._normalize_profile(profile)
        except Exception as e:
            logger.error(f"Error fetching Dhan profile: {e}")
            raise BrokerAPIError(f"Failed to fetch profile: {e}")
    
    def _normalize_holdings(self, holdings: List) -> List[Dict]:
        """Normalize Dhan holdings to our format"""
        normalized = []
        for holding in holdings or []:
            normalized.append({
                'symbol': holding.get('tradingSymbol', ''),
                'trading_symbol': holding.get('tradingSymbol', ''),
                'company_name': holding.get('companyName', ''),
                'exchange': holding.get('exchange', 'NSE'),
                'security_id': holding.get('securityId', ''),
                'isin': holding.get('isin', ''),
                'total_quantity': holding.get('totalQty', 0),
                'available_quantity': holding.get('availableQty', 0),
                't1_quantity': holding.get('t1Qty', 0),
                'dp_quantity': holding.get('dpQty', 0),
                'collateral_quantity': holding.get('collateralQty', 0),
                'avg_cost_price': holding.get('avgCostPrice', 0.0),
                'current_price': holding.get('ltp', 0.0),
                'last_trade_price': holding.get('ltp', 0.0)
            })
        return normalized
    
    def _normalize_positions(self, positions: List) -> List[Dict]:
        """Normalize Dhan positions to our format"""
        normalized = []
        for position in positions or []:
            normalized.append({
                'symbol': position.get('tradingSymbol', ''),
                'trading_symbol': position.get('tradingSymbol', ''),
                'exchange': position.get('exchangeSegment', 'NSE'),
                'security_id': position.get('securityId', ''),
                'product_type': self._map_dhan_product_type(position.get('productType', '')),
                'quantity': position.get('netQty', 0),
                'buy_quantity': position.get('buyQty', 0),
                'sell_quantity': position.get('sellQty', 0),
                'avg_buy_price': position.get('buyAvg', 0.0),
                'avg_sell_price': position.get('sellAvg', 0.0),
                'current_price': position.get('ltp', 0.0),
                'realized_pnl': position.get('realizedPnl', 0.0),
                'unrealized_pnl': position.get('unrealizedPnl', 0.0),
                'total_pnl': position.get('totalPnl', 0.0)
            })
        return normalized
    
    def _normalize_orders(self, orders: List) -> List[Dict]:
        """Normalize Dhan orders to our format"""
        normalized = []
        for order in orders or []:
            normalized.append({
                'broker_order_id': order.get('orderId', ''),
                'symbol': order.get('tradingSymbol', ''),
                'trading_symbol': order.get('tradingSymbol', ''),
                'exchange': order.get('exchangeSegment', 'NSE'),
                'security_id': order.get('securityId', ''),
                'transaction_type': TransactionType.BUY if order.get('transactionType') == 'BUY' else TransactionType.SELL,
                'order_type': self._map_dhan_order_type(order.get('orderType', '')),
                'product_type': self._map_dhan_product_type(order.get('productType', '')),
                'quantity': order.get('quantity', 0),
                'filled_quantity': order.get('filledQty', 0),
                'pending_quantity': order.get('pendingQty', 0),
                'price': order.get('price', 0.0),
                'trigger_price': order.get('triggerPrice', 0.0),
                'order_status': self._map_dhan_order_status(order.get('orderStatus', '')),
                'avg_execution_price': order.get('avgExecutionPrice', 0.0),
                'order_time': self._parse_dhan_datetime(order.get('createTime')),
                'status_message': order.get('orderStatusText', '')
            })
        return normalized
    
    def _normalize_profile(self, profile: Dict) -> Dict:
        """Normalize Dhan profile to our format"""
        return {
            'client_id': profile.get('clientId', ''),
            'account_name': profile.get('clientName', ''),
            'email': profile.get('emailId', ''),
            'mobile': profile.get('mobileNo', ''),
            'exchange_enabled': profile.get('exchangeEnabled', []),
            'product_enabled': profile.get('productEnabled', [])
        }
    
    def _convert_to_dhan_order(self, order_data: Dict) -> Dict:
        """Convert our order format to Dhan API format"""
        # Map our enums to Dhan constants
        transaction_type_map = {
            TransactionType.BUY: 'BUY',
            TransactionType.SELL: 'SELL'
        }
        
        order_type_map = {
            OrderType.MARKET: 'MARKET',
            OrderType.LIMIT: 'LIMIT',
            OrderType.SL: 'SL',
            OrderType.SL_M: 'SL-M'
        }
        
        product_type_map = {
            ProductType.INTRADAY: 'INTRA',
            ProductType.DELIVERY: 'CNC',
            ProductType.CNC: 'CNC',
            ProductType.MIS: 'MIS'
        }
        
        return {
            'security_id': order_data.get('security_id'),
            'exchange_segment': order_data.get('exchange', 'NSE_EQ'),
            'transaction_type': transaction_type_map.get(order_data.get('transaction_type')),
            'quantity': order_data.get('quantity'),
            'order_type': order_type_map.get(order_data.get('order_type')),
            'product_type': product_type_map.get(order_data.get('product_type')),
            'price': order_data.get('price', 0),
            'trigger_price': order_data.get('trigger_price', 0),
            'disclosed_quantity': order_data.get('disclosed_quantity', 0),
            'after_market_order': order_data.get('after_market_order', False),
            'validity': order_data.get('validity', 'DAY'),
            'bo_profit_value': order_data.get('bo_profit_value', 0),
            'bo_stop_loss_value': order_data.get('bo_stop_loss_value', 0)
        }
    
    def _normalize_order_response(self, response: Dict) -> Dict:
        """Normalize Dhan order response"""
        return {
            'status': 'success' if response.get('orderId') else 'error',
            'order_id': response.get('orderId'),
            'message': response.get('remarks', 'Order placed successfully'),
            'data': response
        }
    
    def _map_dhan_product_type(self, dhan_product: str) -> ProductType:
        """Map Dhan product type to our enum"""
        mapping = {
            'INTRA': ProductType.INTRADAY,
            'CNC': ProductType.CNC,
            'MIS': ProductType.MIS
        }
        return mapping.get(dhan_product, ProductType.INTRADAY)
    
    def _map_dhan_order_type(self, dhan_type: str) -> OrderType:
        """Map Dhan order type to our enum"""
        mapping = {
            'MARKET': OrderType.MARKET,
            'LIMIT': OrderType.LIMIT,
            'SL': OrderType.SL,
            'SL-M': OrderType.SL_M
        }
        return mapping.get(dhan_type, OrderType.MARKET)
    
    def _map_dhan_order_status(self, dhan_status: str) -> OrderStatus:
        """Map Dhan order status to our enum"""
        mapping = {
            'PENDING': OrderStatus.PENDING,
            'OPEN': OrderStatus.OPEN,
            'COMPLETE': OrderStatus.COMPLETE,
            'CANCELLED': OrderStatus.CANCELLED,
            'REJECTED': OrderStatus.REJECTED
        }
        return mapping.get(dhan_status, OrderStatus.PENDING)
    
    def _parse_dhan_datetime(self, dt_string: str) -> datetime:
        """Parse Dhan datetime string"""
        if not dt_string:
            return datetime.utcnow()
        try:
            # Dhan typically returns datetime in ISO format
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()

class BrokerService:
    """Main service for managing multiple broker connections"""
    
    @staticmethod
    def get_broker_client(broker_account: BrokerAccount) -> BaseBrokerClient:
        """Get appropriate broker client for account"""
        if broker_account.broker_type == BrokerType.DHAN:
            return DhanBrokerClient(broker_account)
        # Add other brokers here
        # elif broker_account.broker_type == BrokerType.ZERODHA:
        #     return ZerodhaBrokerClient(broker_account)
        else:
            raise BrokerAPIError(f"Unsupported broker type: {broker_account.broker_type}")
    
    @staticmethod
    def add_broker_account(user_id: int, broker_type: BrokerType, credentials: Dict) -> BrokerAccount:
        """Add a new broker account for user"""
        try:
            # Create broker account
            broker_account = BrokerAccount(
                user_id=user_id,
                broker_type=broker_type,
                broker_name=broker_type.value.title()
            )
            
            # Set credentials
            broker_account.set_credentials(
                client_id=credentials.get('client_id'),
                access_token=credentials.get('access_token'),
                api_secret=credentials.get('api_secret')
            )
            
            # Save to database
            db.session.add(broker_account)
            db.session.commit()
            
            # Test connection
            client = BrokerService.get_broker_client(broker_account)
            if client.connect():
                # If this is the first broker account, make it primary
                user_accounts = BrokerAccount.query.filter_by(user_id=user_id).all()
                if len(user_accounts) == 1:
                    broker_account.set_as_primary()
                
                logger.info(f"Successfully added {broker_type.value} account for user {user_id}")
                return broker_account
            else:
                # Connection failed, remove account
                db.session.delete(broker_account)
                db.session.commit()
                raise BrokerAPIError("Failed to connect to broker")
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding broker account: {e}")
            raise BrokerAPIError(f"Failed to add broker account: {e}")
    
    @staticmethod
    def sync_broker_data(broker_account: BrokerAccount, data_types: List[str] = None) -> Dict:
        """Sync data from broker for given account"""
        if data_types is None:
            data_types = ['holdings', 'positions', 'orders', 'profile']
        
        client = BrokerService.get_broker_client(broker_account)
        if not client.connect():
            raise BrokerAPIError("Failed to connect to broker")
        
        results = {}
        start_time = time.time()
        
        try:
            # Sync holdings
            if 'holdings' in data_types:
                holdings_data = client.get_holdings()
                BrokerService._sync_holdings(broker_account, holdings_data)
                results['holdings'] = len(holdings_data)
            
            # Sync positions
            if 'positions' in data_types:
                positions_data = client.get_positions()
                BrokerService._sync_positions(broker_account, positions_data)
                results['positions'] = len(positions_data)
            
            # Sync orders
            if 'orders' in data_types:
                orders_data = client.get_orders()
                BrokerService._sync_orders(broker_account, orders_data)
                results['orders'] = len(orders_data)
            
            # Sync profile
            if 'profile' in data_types:
                profile_data = client.get_profile()
                BrokerService._sync_profile(broker_account, profile_data)
                results['profile'] = 1
            
            # Update last sync time
            broker_account.last_sync = datetime.utcnow()
            db.session.commit()
            
            # Log successful sync
            sync_duration = time.time() - start_time
            total_records = sum(results.values())
            
            sync_log = BrokerSyncLog(
                broker_account_id=broker_account.id,
                sync_type=','.join(data_types),
                sync_status='success',
                records_synced=total_records,
                sync_duration=sync_duration
            )
            db.session.add(sync_log)
            db.session.commit()
            
            logger.info(f"Successfully synced {total_records} records for {broker_account.broker_name}")
            return results
            
        except Exception as e:
            db.session.rollback()
            
            # Log failed sync
            sync_duration = time.time() - start_time
            sync_log = BrokerSyncLog(
                broker_account_id=broker_account.id,
                sync_type=','.join(data_types),
                sync_status='error',
                error_message=str(e),
                sync_duration=sync_duration
            )
            db.session.add(sync_log)
            db.session.commit()
            
            logger.error(f"Failed to sync broker data: {e}")
            raise BrokerAPIError(f"Sync failed: {e}")
    
    @staticmethod
    def _sync_holdings(broker_account: BrokerAccount, holdings_data: List[Dict]):
        """Sync holdings data to database"""
        # Clear existing holdings
        BrokerHolding.query.filter_by(broker_account_id=broker_account.id).delete()
        
        # Add new holdings
        for holding_data in holdings_data:
            holding = BrokerHolding(
                broker_account_id=broker_account.id,
                **holding_data
            )
            holding.calculate_pnl()
            db.session.add(holding)
    
    @staticmethod
    def _sync_positions(broker_account: BrokerAccount, positions_data: List[Dict]):
        """Sync positions data to database"""
        # Clear existing positions for today
        today = datetime.utcnow().date()
        BrokerPosition.query.filter_by(
            broker_account_id=broker_account.id,
            position_date=today
        ).delete()
        
        # Add new positions
        for position_data in positions_data:
            position = BrokerPosition(
                broker_account_id=broker_account.id,
                position_date=today,
                **position_data
            )
            db.session.add(position)
    
    @staticmethod
    def _sync_orders(broker_account: BrokerAccount, orders_data: List[Dict]):
        """Sync orders data to database"""
        for order_data in orders_data:
            # Check if order already exists
            existing_order = BrokerOrder.query.filter_by(
                broker_account_id=broker_account.id,
                broker_order_id=order_data.get('broker_order_id')
            ).first()
            
            if existing_order:
                # Update existing order
                for key, value in order_data.items():
                    if hasattr(existing_order, key):
                        setattr(existing_order, key, value)
            else:
                # Create new order
                order = BrokerOrder(
                    broker_account_id=broker_account.id,
                    **order_data
                )
                db.session.add(order)
    
    @staticmethod
    def _sync_profile(broker_account: BrokerAccount, profile_data: Dict):
        """Sync profile data to broker account"""
        broker_account.account_name = profile_data.get('account_name', broker_account.account_name)
        # Update other profile fields as needed
    
    @staticmethod
    def place_order_via_broker(broker_account: BrokerAccount, order_data: Dict) -> BrokerOrder:
        """Place order through broker and save to database"""
        client = BrokerService.get_broker_client(broker_account)
        if not client.connect():
            raise BrokerAPIError("Failed to connect to broker")
        
        try:
            # Place order with broker
            response = client.place_order(order_data)
            
            if response.get('status') == 'success':
                # Create order record in database
                order = BrokerOrder(
                    broker_account_id=broker_account.id,
                    broker_order_id=response.get('order_id'),
                    correlation_id=order_data.get('correlation_id'),
                    symbol=order_data.get('symbol'),
                    trading_symbol=order_data.get('trading_symbol'),
                    exchange=order_data.get('exchange'),
                    security_id=order_data.get('security_id'),
                    transaction_type=order_data.get('transaction_type'),
                    order_type=order_data.get('order_type'),
                    product_type=order_data.get('product_type'),
                    quantity=order_data.get('quantity'),
                    price=order_data.get('price', 0.0),
                    trigger_price=order_data.get('trigger_price', 0.0),
                    disclosed_quantity=order_data.get('disclosed_quantity', 0),
                    order_status=OrderStatus.PENDING,
                    trading_signal_id=order_data.get('trading_signal_id')
                )
                
                db.session.add(order)
                db.session.commit()
                
                logger.info(f"Order placed successfully: {response.get('order_id')}")
                return order
            else:
                raise BrokerAPIError(f"Order placement failed: {response.get('message')}")
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error placing order: {e}")
            raise BrokerAPIError(f"Failed to place order: {e}")
    
    @staticmethod
    def get_user_portfolio_summary(user_id: int) -> Dict:
        """Get consolidated portfolio summary for user across all brokers"""
        broker_accounts = BrokerAccount.query.filter_by(user_id=user_id, is_active=True).all()
        
        summary = {
            'total_value': 0.0,
            'total_investment': 0.0,
            'total_pnl': 0.0,
            'total_pnl_percentage': 0.0,
            'holdings_count': 0,
            'brokers_count': len(broker_accounts),
            'broker_accounts': []
        }
        
        for account in broker_accounts:
            holdings = BrokerHolding.query.filter_by(broker_account_id=account.id).all()
            
            account_value = sum(h.total_value for h in holdings)
            account_investment = sum(h.investment_value for h in holdings)
            account_pnl = sum(h.pnl for h in holdings)
            
            summary['total_value'] += account_value
            summary['total_investment'] += account_investment
            summary['total_pnl'] += account_pnl
            summary['holdings_count'] += len(holdings)
            
            summary['broker_accounts'].append({
                'broker_name': account.broker_name,
                'account_value': account_value,
                'holdings_count': len(holdings),
                'connection_status': account.connection_status.value,
                'last_sync': account.last_sync
            })
        
        if summary['total_investment'] > 0:
            summary['total_pnl_percentage'] = (summary['total_pnl'] / summary['total_investment']) * 100
        
        return summary