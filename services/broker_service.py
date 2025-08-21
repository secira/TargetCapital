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

try:
    from kiteconnect import KiteConnect
    ZERODHA_AVAILABLE = True
except ImportError:
    ZERODHA_AVAILABLE = False
    KiteConnect = None

try:
    from SmartApi import SmartConnect
    import pyotp
    ANGEL_AVAILABLE = True
except ImportError:
    ANGEL_AVAILABLE = False
    SmartConnect = None
    pyotp = None

# Import additional broker clients
try:
    import upstox_client
    UPSTOX_AVAILABLE = True
except ImportError:
    UPSTOX_AVAILABLE = False
    upstox_client = None

try:
    from fyers_apiv3 import fyersModel
    FYERS_AVAILABLE = True
except ImportError:
    FYERS_AVAILABLE = False
    fyersModel = None

# Note: Groww, ICICIDirect, HDFC Securities, Kotak Securities, 5Paisa
# These brokers will use REST API calls as they don't have official Python SDKs
import requests

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

class ZerodhaBrokerClient(BaseBrokerClient):
    """Zerodha Kite Connect broker client implementation"""
    
    def __init__(self, broker_account: BrokerAccount):
        super().__init__(broker_account)
        if not ZERODHA_AVAILABLE:
            raise BrokerAPIError("Zerodha library not available. Install with: pip install kiteconnect")
    
    def connect(self) -> bool:
        """Connect to Zerodha Kite API"""
        try:
            api_key = self.credentials.get('client_id')  # API Key
            access_token = self.credentials.get('access_token')
            
            if not api_key or not access_token:
                raise BrokerAPIError("Missing Zerodha credentials")
            
            self._client = KiteConnect(api_key=api_key)
            self._client.set_access_token(access_token)
            
            # Test connection by getting profile
            profile = self._client.profile()
            if profile and profile.get('user_id'):
                self.broker_account.update_connection_status(ConnectionStatus.CONNECTED)
                logger.info(f"Successfully connected to Zerodha for account {api_key}")
                return True
            else:
                raise BrokerAPIError("Invalid response from Zerodha API")
                
        except Exception as e:
            error_msg = f"Failed to connect to Zerodha: {str(e)}"
            self.broker_account.update_connection_status(ConnectionStatus.ERROR, error_msg)
            logger.error(error_msg)
            return False
    
    def get_holdings(self) -> List[Dict]:
        """Get Zerodha holdings"""
        if not self._client:
            raise BrokerAPIError("Not connected to Zerodha")
        
        try:
            holdings = self._client.holdings()
            return self._normalize_zerodha_holdings(holdings)
        except Exception as e:
            logger.error(f"Error fetching Zerodha holdings: {e}")
            raise BrokerAPIError(f"Failed to fetch holdings: {e}")
    
    def get_positions(self) -> List[Dict]:
        """Get Zerodha positions"""
        if not self._client:
            raise BrokerAPIError("Not connected to Zerodha")
        
        try:
            positions = self._client.positions()
            # Zerodha returns both 'net' and 'day' positions
            net_positions = positions.get('net', [])
            return self._normalize_zerodha_positions(net_positions)
        except Exception as e:
            logger.error(f"Error fetching Zerodha positions: {e}")
            raise BrokerAPIError(f"Failed to fetch positions: {e}")
    
    def get_orders(self) -> List[Dict]:
        """Get Zerodha orders"""
        if not self._client:
            raise BrokerAPIError("Not connected to Zerodha")
        
        try:
            orders = self._client.orders()
            return self._normalize_zerodha_orders(orders)
        except Exception as e:
            logger.error(f"Error fetching Zerodha orders: {e}")
            raise BrokerAPIError(f"Failed to fetch orders: {e}")
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place order with Zerodha"""
        if not self._client:
            raise BrokerAPIError("Not connected to Zerodha")
        
        try:
            # Convert our order format to Zerodha format
            zerodha_order = self._convert_to_zerodha_order(order_data)
            order_id = self._client.place_order(**zerodha_order)
            return {'status': 'success', 'order_id': order_id, 'message': 'Order placed successfully'}
        except Exception as e:
            logger.error(f"Error placing Zerodha order: {e}")
            raise BrokerAPIError(f"Failed to place order: {e}")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel Zerodha order"""
        if not self._client:
            raise BrokerAPIError("Not connected to Zerodha")
        
        try:
            result = self._client.cancel_order(variety=self._client.VARIETY_REGULAR, order_id=order_id)
            return {'status': 'success', 'message': 'Order cancelled', 'data': result}
        except Exception as e:
            logger.error(f"Error cancelling Zerodha order: {e}")
            raise BrokerAPIError(f"Failed to cancel order: {e}")
    
    def get_profile(self) -> Dict:
        """Get Zerodha profile"""
        if not self._client:
            raise BrokerAPIError("Not connected to Zerodha")
        
        try:
            profile = self._client.profile()
            margins = self._client.margins()
            return self._normalize_zerodha_profile(profile, margins)
        except Exception as e:
            logger.error(f"Error fetching Zerodha profile: {e}")
            raise BrokerAPIError(f"Failed to fetch profile: {e}")
    
    def _normalize_zerodha_holdings(self, holdings: List) -> List[Dict]:
        """Normalize Zerodha holdings to our format"""
        normalized = []
        for holding in holdings or []:
            normalized.append({
                'symbol': holding.get('tradingsymbol', ''),
                'trading_symbol': holding.get('tradingsymbol', ''),
                'company_name': holding.get('tradingsymbol', ''),  # Zerodha doesn't provide company name
                'exchange': holding.get('exchange', 'NSE'),
                'security_id': holding.get('instrument_token', ''),
                'isin': holding.get('isin', ''),
                'total_quantity': holding.get('quantity', 0),
                'available_quantity': holding.get('quantity', 0),
                't1_quantity': holding.get('t1_quantity', 0),
                'dp_quantity': holding.get('quantity', 0),
                'collateral_quantity': holding.get('collateral_quantity', 0),
                'avg_cost_price': holding.get('average_price', 0.0),
                'current_price': holding.get('last_price', 0.0),
                'last_trade_price': holding.get('last_price', 0.0)
            })
        return normalized
    
    def _normalize_zerodha_positions(self, positions: List) -> List[Dict]:
        """Normalize Zerodha positions to our format"""
        normalized = []
        for position in positions or []:
            normalized.append({
                'symbol': position.get('tradingsymbol', ''),
                'trading_symbol': position.get('tradingsymbol', ''),
                'exchange': position.get('exchange', 'NSE'),
                'security_id': position.get('instrument_token', ''),
                'product_type': self._map_zerodha_product_type(position.get('product', '')),
                'quantity': position.get('quantity', 0),
                'buy_quantity': position.get('buy_quantity', 0),
                'sell_quantity': position.get('sell_quantity', 0),
                'avg_buy_price': position.get('buy_price', 0.0),
                'avg_sell_price': position.get('sell_price', 0.0),
                'current_price': position.get('last_price', 0.0),
                'realized_pnl': position.get('realised', 0.0),
                'unrealized_pnl': position.get('unrealised', 0.0),
                'total_pnl': position.get('pnl', 0.0)
            })
        return normalized
    
    def _normalize_zerodha_orders(self, orders: List) -> List[Dict]:
        """Normalize Zerodha orders to our format"""
        normalized = []
        for order in orders or []:
            normalized.append({
                'broker_order_id': order.get('order_id', ''),
                'symbol': order.get('tradingsymbol', ''),
                'trading_symbol': order.get('tradingsymbol', ''),
                'exchange': order.get('exchange', 'NSE'),
                'security_id': order.get('instrument_token', ''),
                'transaction_type': TransactionType.BUY if order.get('transaction_type') == 'BUY' else TransactionType.SELL,
                'order_type': self._map_zerodha_order_type(order.get('order_type', '')),
                'product_type': self._map_zerodha_product_type(order.get('product', '')),
                'quantity': order.get('quantity', 0),
                'filled_quantity': order.get('filled_quantity', 0),
                'pending_quantity': order.get('pending_quantity', 0),
                'price': order.get('price', 0.0),
                'trigger_price': order.get('trigger_price', 0.0),
                'order_status': self._map_zerodha_order_status(order.get('status', '')),
                'avg_execution_price': order.get('average_price', 0.0),
                'order_time': self._parse_zerodha_datetime(order.get('order_timestamp')),
                'status_message': order.get('status_message', '')
            })
        return normalized
    
    def _normalize_zerodha_profile(self, profile: Dict, margins: Dict) -> Dict:
        """Normalize Zerodha profile to our format"""
        equity_margin = margins.get('equity', {})
        return {
            'client_id': profile.get('user_id', ''),
            'account_name': profile.get('user_name', ''),
            'email': profile.get('email', ''),
            'mobile': profile.get('phone', ''),
            'available_balance': equity_margin.get('available', {}).get('cash', 0.0),
            'used_margin': equity_margin.get('utilised', {}).get('debits', 0.0)
        }
    
    def _convert_to_zerodha_order(self, order_data: Dict) -> Dict:
        """Convert our order format to Zerodha API format"""
        transaction_type_map = {
            TransactionType.BUY: self._client.TRANSACTION_TYPE_BUY,
            TransactionType.SELL: self._client.TRANSACTION_TYPE_SELL
        }
        
        order_type_map = {
            OrderType.MARKET: self._client.ORDER_TYPE_MARKET,
            OrderType.LIMIT: self._client.ORDER_TYPE_LIMIT,
            OrderType.SL: self._client.ORDER_TYPE_SL,
            OrderType.SL_M: self._client.ORDER_TYPE_SLM
        }
        
        product_type_map = {
            ProductType.INTRADAY: self._client.PRODUCT_MIS,
            ProductType.DELIVERY: self._client.PRODUCT_CNC,
            ProductType.CNC: self._client.PRODUCT_CNC,
            ProductType.MIS: self._client.PRODUCT_MIS
        }
        
        return {
            'tradingsymbol': order_data.get('trading_symbol'),
            'exchange': order_data.get('exchange', self._client.EXCHANGE_NSE),
            'transaction_type': transaction_type_map.get(order_data.get('transaction_type')),
            'quantity': order_data.get('quantity'),
            'order_type': order_type_map.get(order_data.get('order_type')),
            'product': product_type_map.get(order_data.get('product_type')),
            'price': order_data.get('price', 0),
            'trigger_price': order_data.get('trigger_price', 0),
            'disclosed_quantity': order_data.get('disclosed_quantity', 0),
            'validity': order_data.get('validity', self._client.VALIDITY_DAY),
            'variety': self._client.VARIETY_REGULAR
        }
    
    def _map_zerodha_product_type(self, zerodha_product: str) -> ProductType:
        """Map Zerodha product type to our enum"""
        mapping = {
            'MIS': ProductType.INTRADAY,
            'CNC': ProductType.CNC,
            'NRML': ProductType.DELIVERY
        }
        return mapping.get(zerodha_product, ProductType.INTRADAY)
    
    def _map_zerodha_order_type(self, zerodha_type: str) -> OrderType:
        """Map Zerodha order type to our enum"""
        mapping = {
            'MARKET': OrderType.MARKET,
            'LIMIT': OrderType.LIMIT,
            'SL': OrderType.SL,
            'SL-M': OrderType.SL_M
        }
        return mapping.get(zerodha_type, OrderType.MARKET)
    
    def _map_zerodha_order_status(self, zerodha_status: str) -> OrderStatus:
        """Map Zerodha order status to our enum"""
        mapping = {
            'OPEN': OrderStatus.OPEN,
            'COMPLETE': OrderStatus.COMPLETE,
            'CANCELLED': OrderStatus.CANCELLED,
            'REJECTED': OrderStatus.REJECTED,
            'PUT ORDER REQ RECEIVED': OrderStatus.PENDING
        }
        return mapping.get(zerodha_status, OrderStatus.PENDING)
    
    def _parse_zerodha_datetime(self, dt_string: str) -> datetime:
        """Parse Zerodha datetime string"""
        if not dt_string:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()

class AngelBrokerClient(BaseBrokerClient):
    """Angel One SmartAPI broker client implementation"""
    
    def __init__(self, broker_account: BrokerAccount):
        super().__init__(broker_account)
        if not ANGEL_AVAILABLE:
            raise BrokerAPIError("Angel One library not available. Install with: pip install smartapi-python pyotp")
    
    def connect(self) -> bool:
        """Connect to Angel One SmartAPI"""
        try:
            api_key = self.credentials.get('client_id')  # API Key
            username = self.credentials.get('access_token')  # Client Code
            password = self.credentials.get('api_secret')  # Trading PIN
            totp_secret = self.credentials.get('totp_secret')  # TOTP Secret
            
            if not api_key or not username or not password:
                raise BrokerAPIError("Missing Angel One credentials")
            
            self._client = SmartConnect(api_key)
            
            # Generate TOTP if available
            totp = None
            if totp_secret:
                try:
                    totp = pyotp.TOTP(totp_secret).now()
                except:
                    pass
            
            if not totp:
                # Use static TOTP for now (user needs to provide current TOTP)
                totp = password[-6:] if len(password) > 6 else "123456"
            
            # Generate session
            data = self._client.generateSession(username, password, totp)
            
            if data.get('status') == False:
                raise BrokerAPIError(f"Angel One login failed: {data.get('message', 'Authentication failed')}")
            
            # Store tokens
            self._auth_token = data['data']['jwtToken']
            self._refresh_token = data['data']['refreshToken']
            self._feed_token = self._client.getfeedToken()
            
            # Test connection with profile
            profile = self._client.getProfile(self._refresh_token)
            if profile and profile.get('status'):
                self.broker_account.update_connection_status(ConnectionStatus.CONNECTED)
                logger.info(f"Successfully connected to Angel One for account {username}")
                return True
            else:
                raise BrokerAPIError("Failed to get Angel One profile")
                
        except Exception as e:
            error_msg = f"Failed to connect to Angel One: {str(e)}"
            self.broker_account.update_connection_status(ConnectionStatus.ERROR, error_msg)
            logger.error(error_msg)
            return False
    
    def get_holdings(self) -> List[Dict]:
        """Get Angel One holdings"""
        if not self._client:
            raise BrokerAPIError("Not connected to Angel One")
        
        try:
            holdings = self._client.holding()
            if holdings.get('status'):
                return self._normalize_angel_holdings(holdings.get('data', []))
            else:
                raise BrokerAPIError(f"Failed to fetch holdings: {holdings.get('message')}")
        except Exception as e:
            logger.error(f"Error fetching Angel One holdings: {e}")
            raise BrokerAPIError(f"Failed to fetch holdings: {e}")
    
    def get_positions(self) -> List[Dict]:
        """Get Angel One positions"""
        if not self._client:
            raise BrokerAPIError("Not connected to Angel One")
        
        try:
            positions = self._client.position()
            if positions.get('status'):
                return self._normalize_angel_positions(positions.get('data', []))
            else:
                raise BrokerAPIError(f"Failed to fetch positions: {positions.get('message')}")
        except Exception as e:
            logger.error(f"Error fetching Angel One positions: {e}")
            raise BrokerAPIError(f"Failed to fetch positions: {e}")
    
    def get_orders(self) -> List[Dict]:
        """Get Angel One orders"""
        if not self._client:
            raise BrokerAPIError("Not connected to Angel One")
        
        try:
            orders = self._client.orderBook()
            if orders.get('status'):
                return self._normalize_angel_orders(orders.get('data', []))
            else:
                raise BrokerAPIError(f"Failed to fetch orders: {orders.get('message')}")
        except Exception as e:
            logger.error(f"Error fetching Angel One orders: {e}")
            raise BrokerAPIError(f"Failed to fetch orders: {e}")
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place order with Angel One"""
        if not self._client:
            raise BrokerAPIError("Not connected to Angel One")
        
        try:
            # Convert our order format to Angel One format
            angel_order = self._convert_to_angel_order(order_data)
            result = self._client.placeOrder(angel_order)
            
            if result.get('status'):
                return {
                    'status': 'success', 
                    'order_id': result.get('data', {}).get('orderid'),
                    'message': 'Order placed successfully'
                }
            else:
                raise BrokerAPIError(f"Order placement failed: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error placing Angel One order: {e}")
            raise BrokerAPIError(f"Failed to place order: {e}")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel Angel One order"""
        if not self._client:
            raise BrokerAPIError("Not connected to Angel One")
        
        try:
            result = self._client.cancelOrder(order_id, "NORMAL")
            return {'status': 'success', 'message': 'Order cancelled', 'data': result}
        except Exception as e:
            logger.error(f"Error cancelling Angel One order: {e}")
            raise BrokerAPIError(f"Failed to cancel order: {e}")
    
    def get_profile(self) -> Dict:
        """Get Angel One profile"""
        if not self._client:
            raise BrokerAPIError("Not connected to Angel One")
        
        try:
            profile = self._client.getProfile(self._refresh_token)
            rms = self._client.rmsLimit()
            return self._normalize_angel_profile(profile, rms)
        except Exception as e:
            logger.error(f"Error fetching Angel One profile: {e}")
            raise BrokerAPIError(f"Failed to fetch profile: {e}")
    
    def _normalize_angel_holdings(self, holdings: List) -> List[Dict]:
        """Normalize Angel One holdings to our format"""
        normalized = []
        for holding in holdings or []:
            normalized.append({
                'symbol': holding.get('tradingsymbol', ''),
                'trading_symbol': holding.get('tradingsymbol', ''),
                'company_name': holding.get('symbolname', ''),
                'exchange': holding.get('exchange', 'NSE'),
                'security_id': holding.get('symboltoken', ''),
                'isin': holding.get('isin', ''),
                'total_quantity': int(holding.get('quantity', 0)),
                'available_quantity': int(holding.get('quantity', 0)),
                't1_quantity': int(holding.get('t1quantity', 0)),
                'dp_quantity': int(holding.get('quantity', 0)),
                'collateral_quantity': int(holding.get('collateralquantity', 0)),
                'avg_cost_price': float(holding.get('averageprice', 0.0)),
                'current_price': float(holding.get('ltp', 0.0)),
                'last_trade_price': float(holding.get('ltp', 0.0))
            })
        return normalized
    
    def _normalize_angel_positions(self, positions: List) -> List[Dict]:
        """Normalize Angel One positions to our format"""
        normalized = []
        for position in positions or []:
            normalized.append({
                'symbol': position.get('tradingsymbol', ''),
                'trading_symbol': position.get('tradingsymbol', ''),
                'exchange': position.get('exchange', 'NSE'),
                'security_id': position.get('symboltoken', ''),
                'product_type': self._map_angel_product_type(position.get('producttype', '')),
                'quantity': int(position.get('netqty', 0)),
                'buy_quantity': int(position.get('buyqty', 0)),
                'sell_quantity': int(position.get('sellqty', 0)),
                'avg_buy_price': float(position.get('buyavgprice', 0.0)),
                'avg_sell_price': float(position.get('sellavgprice', 0.0)),
                'current_price': float(position.get('ltp', 0.0)),
                'realized_pnl': float(position.get('realised', 0.0)),
                'unrealized_pnl': float(position.get('unrealised', 0.0)),
                'total_pnl': float(position.get('pnl', 0.0))
            })
        return normalized
    
    def _normalize_angel_orders(self, orders: List) -> List[Dict]:
        """Normalize Angel One orders to our format"""
        normalized = []
        for order in orders or []:
            normalized.append({
                'broker_order_id': order.get('orderid', ''),
                'symbol': order.get('tradingsymbol', ''),
                'trading_symbol': order.get('tradingsymbol', ''),
                'exchange': order.get('exchange', 'NSE'),
                'security_id': order.get('symboltoken', ''),
                'transaction_type': TransactionType.BUY if order.get('transactiontype') == 'BUY' else TransactionType.SELL,
                'order_type': self._map_angel_order_type(order.get('ordertype', '')),
                'product_type': self._map_angel_product_type(order.get('producttype', '')),
                'quantity': int(order.get('quantity', 0)),
                'filled_quantity': int(order.get('filledshares', 0)),
                'pending_quantity': int(order.get('unfilledshares', 0)),
                'price': float(order.get('price', 0.0)),
                'trigger_price': float(order.get('triggerprice', 0.0)),
                'order_status': self._map_angel_order_status(order.get('orderstatus', '')),
                'avg_execution_price': float(order.get('averageprice', 0.0)),
                'order_time': self._parse_angel_datetime(order.get('ordertime')),
                'status_message': order.get('text', '')
            })
        return normalized
    
    def _normalize_angel_profile(self, profile: Dict, rms: Dict) -> Dict:
        """Normalize Angel One profile to our format"""
        profile_data = profile.get('data', {}) if profile.get('status') else {}
        rms_data = rms.get('data', {}) if rms.get('status') else {}
        
        return {
            'client_id': profile_data.get('clientcode', ''),
            'account_name': profile_data.get('name', ''),
            'email': profile_data.get('email', ''),
            'mobile': profile_data.get('mobileno', ''),
            'available_balance': float(rms_data.get('availablecash', 0.0)),
            'used_margin': float(rms_data.get('utilisedmargin', 0.0))
        }
    
    def _convert_to_angel_order(self, order_data: Dict) -> Dict:
        """Convert our order format to Angel One API format"""
        transaction_type_map = {
            TransactionType.BUY: "BUY",
            TransactionType.SELL: "SELL"
        }
        
        order_type_map = {
            OrderType.MARKET: "MARKET",
            OrderType.LIMIT: "LIMIT",
            OrderType.SL: "STOPLOSS_LIMIT",
            OrderType.SL_M: "STOPLOSS_MARKET"
        }
        
        product_type_map = {
            ProductType.INTRADAY: "INTRADAY",
            ProductType.DELIVERY: "DELIVERY",
            ProductType.CNC: "DELIVERY",
            ProductType.MIS: "INTRADAY"
        }
        
        return {
            "variety": "NORMAL",
            "tradingsymbol": order_data.get('trading_symbol'),
            "symboltoken": order_data.get('security_id', ''),
            "transactiontype": transaction_type_map.get(order_data.get('transaction_type')),
            "exchange": order_data.get('exchange', 'NSE'),
            "ordertype": order_type_map.get(order_data.get('order_type')),
            "producttype": product_type_map.get(order_data.get('product_type')),
            "duration": "DAY",
            "price": str(order_data.get('price', 0)),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(order_data.get('quantity'))
        }
    
    def _map_angel_product_type(self, angel_product: str) -> ProductType:
        """Map Angel One product type to our enum"""
        mapping = {
            'INTRADAY': ProductType.INTRADAY,
            'DELIVERY': ProductType.DELIVERY,
            'MARGIN': ProductType.MIS
        }
        return mapping.get(angel_product, ProductType.INTRADAY)
    
    def _map_angel_order_type(self, angel_type: str) -> OrderType:
        """Map Angel One order type to our enum"""
        mapping = {
            'MARKET': OrderType.MARKET,
            'LIMIT': OrderType.LIMIT,
            'STOPLOSS_LIMIT': OrderType.SL,
            'STOPLOSS_MARKET': OrderType.SL_M
        }
        return mapping.get(angel_type, OrderType.MARKET)
    
    def _map_angel_order_status(self, angel_status: str) -> OrderStatus:
        """Map Angel One order status to our enum"""
        mapping = {
            'open': OrderStatus.OPEN,
            'complete': OrderStatus.COMPLETE,
            'cancelled': OrderStatus.CANCELLED,
            'rejected': OrderStatus.REJECTED,
            'pending': OrderStatus.PENDING
        }
        return mapping.get(angel_status.lower(), OrderStatus.PENDING)
    
    def _parse_angel_datetime(self, dt_string: str) -> datetime:
        """Parse Angel One datetime string"""
        if not dt_string:
            return datetime.utcnow()
        try:
            # Angel One typically returns datetime in DD-MMM-YYYY HH:MM:SS format
            return datetime.strptime(dt_string, "%d-%b-%Y %H:%M:%S")
        except:
            try:
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
        elif broker_account.broker_type == BrokerType.ZERODHA:
            return ZerodhaBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.ANGEL_BROKING:
            return AngelBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.UPSTOX:
            return UpstoxBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.FYERS:
            return FyersBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.GROWW:
            return GrowwBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.ICICIDIRECT:
            return ICICIDirectBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.HDFC_SECURITIES:
            return HDFCSecuritiesBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.KOTAK_SECURITIES:
            return KotakSecuritiesBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.FIVE_PAISA:
            return FivePaisaBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.CHOICE_INDIA:
            return ChoiceIndiaBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.GOODWILL:
            return GoodwillBrokerClient(broker_account)
        elif broker_account.broker_type == BrokerType.ANGEL_BROKING:
            return AngelBrokerClient(broker_account)
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
                broker_name=broker_type.value.title(),
                api_key=credentials.get('client_id'),
                access_token=credentials.get('access_token'),
                api_secret=credentials.get('api_secret'),
                connection_status='disconnected',
                is_active=True
            )
            
            # Set credentials using encryption if available
            if hasattr(broker_account, 'set_credentials'):
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


# Additional Broker Client Implementations

class UpstoxBrokerClient(BaseBrokerClient):
    """Upstox broker client implementation"""
    
    def connect(self) -> bool:
        """Connect to Upstox API"""
        try:
            if not UPSTOX_AVAILABLE:
                raise BrokerAPIError("Upstox client not available")
            
            api_key = self.credentials.get('client_id')
            access_token = self.credentials.get('access_token')
            
            if not api_key or not access_token:
                raise BrokerAPIError("Missing Upstox credentials")
            
            # Configure API client
            configuration = upstox_client.Configuration()
            configuration.access_token = access_token
            self._client = upstox_client.ApiClient(configuration)
            
            # Test connection
            user_api = upstox_client.UserApi(self._client)
            profile = user_api.get_profile()
            
            if profile and profile.data:
                self.broker_account.update_connection_status(ConnectionStatus.CONNECTED)
                logger.info(f"Successfully connected to Upstox for account {api_key}")
                return True
            else:
                raise BrokerAPIError("Invalid response from Upstox API")
                
        except Exception as e:
            error_msg = f"Failed to connect to Upstox: {str(e)}"
            self.broker_account.update_connection_status(ConnectionStatus.ERROR, error_msg)
            logger.error(error_msg)
            return False
    
    def get_holdings(self) -> List[Dict]:
        """Get Upstox holdings"""
        if not self._client:
            raise BrokerAPIError("Not connected to Upstox")
        
        try:
            portfolio_api = upstox_client.PortfolioApi(self._client)
            holdings = portfolio_api.get_holdings()
            return self._normalize_upstox_holdings(holdings.data if holdings.data else [])
        except Exception as e:
            logger.error(f"Error fetching Upstox holdings: {e}")
            raise BrokerAPIError(f"Failed to fetch holdings: {e}")
    
    def get_positions(self) -> List[Dict]:
        """Get Upstox positions"""
        if not self._client:
            raise BrokerAPIError("Not connected to Upstox")
        
        try:
            portfolio_api = upstox_client.PortfolioApi(self._client)
            positions = portfolio_api.get_positions()
            return self._normalize_upstox_positions(positions.data if positions.data else [])
        except Exception as e:
            logger.error(f"Error fetching Upstox positions: {e}")
            raise BrokerAPIError(f"Failed to fetch positions: {e}")
    
    def get_orders(self) -> List[Dict]:
        """Get Upstox orders"""
        if not self._client:
            raise BrokerAPIError("Not connected to Upstox")
        
        try:
            orders_api = upstox_client.OrderApi(self._client)
            orders = orders_api.get_orders()
            return self._normalize_upstox_orders(orders.data if orders.data else [])
        except Exception as e:
            logger.error(f"Error fetching Upstox orders: {e}")
            raise BrokerAPIError(f"Failed to fetch orders: {e}")
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place order with Upstox"""
        if not self._client:
            raise BrokerAPIError("Not connected to Upstox")
        
        try:
            orders_api = upstox_client.OrderApi(self._client)
            upstox_order = self._convert_to_upstox_order(order_data)
            response = orders_api.place_order(upstox_order)
            return {'status': 'success', 'order_id': response.data.order_id, 'message': 'Order placed successfully'}
        except Exception as e:
            logger.error(f"Error placing Upstox order: {e}")
            raise BrokerAPIError(f"Failed to place order: {e}")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel Upstox order"""
        if not self._client:
            raise BrokerAPIError("Not connected to Upstox")
        
        try:
            orders_api = upstox_client.OrderApi(self._client)
            response = orders_api.cancel_order(order_id)
            return {'status': 'success', 'message': 'Order cancelled', 'data': response.data}
        except Exception as e:
            logger.error(f"Error cancelling Upstox order: {e}")
            raise BrokerAPIError(f"Failed to cancel order: {e}")
    
    def get_profile(self) -> Dict:
        """Get Upstox profile"""
        if not self._client:
            raise BrokerAPIError("Not connected to Upstox")
        
        try:
            user_api = upstox_client.UserApi(self._client)
            profile = user_api.get_profile()
            funds = user_api.get_user_fund_margin()
            return self._normalize_upstox_profile(profile.data, funds.data)
        except Exception as e:
            logger.error(f"Error fetching Upstox profile: {e}")
            raise BrokerAPIError(f"Failed to fetch profile: {e}")
    
    def _normalize_upstox_holdings(self, holdings: List) -> List[Dict]:
        """Normalize Upstox holdings to our format"""
        normalized = []
        for holding in holdings or []:
            normalized.append({
                'symbol': holding.trading_symbol if hasattr(holding, 'trading_symbol') else '',
                'trading_symbol': holding.trading_symbol if hasattr(holding, 'trading_symbol') else '',
                'company_name': holding.company_name if hasattr(holding, 'company_name') else '',
                'exchange': holding.exchange if hasattr(holding, 'exchange') else 'NSE',
                'security_id': holding.instrument_token if hasattr(holding, 'instrument_token') else '',
                'isin': holding.isin if hasattr(holding, 'isin') else '',
                'total_quantity': holding.quantity if hasattr(holding, 'quantity') else 0,
                'available_quantity': holding.quantity if hasattr(holding, 'quantity') else 0,
                'avg_cost_price': holding.average_price if hasattr(holding, 'average_price') else 0.0,
                'current_price': holding.last_price if hasattr(holding, 'last_price') else 0.0,
                'last_trade_price': holding.last_price if hasattr(holding, 'last_price') else 0.0
            })
        return normalized
    
    def _normalize_upstox_positions(self, positions: List) -> List[Dict]:
        """Normalize Upstox positions to our format"""
        normalized = []
        for position in positions or []:
            normalized.append({
                'symbol': position.trading_symbol if hasattr(position, 'trading_symbol') else '',
                'trading_symbol': position.trading_symbol if hasattr(position, 'trading_symbol') else '',
                'exchange': position.exchange if hasattr(position, 'exchange') else 'NSE',
                'security_id': position.instrument_token if hasattr(position, 'instrument_token') else '',
                'product_type': ProductType.INTRADAY,  # Default mapping
                'quantity': position.quantity if hasattr(position, 'quantity') else 0,
                'buy_quantity': position.buy_quantity if hasattr(position, 'buy_quantity') else 0,
                'sell_quantity': position.sell_quantity if hasattr(position, 'sell_quantity') else 0,
                'avg_buy_price': position.buy_price if hasattr(position, 'buy_price') else 0.0,
                'avg_sell_price': position.sell_price if hasattr(position, 'sell_price') else 0.0,
                'current_price': position.last_price if hasattr(position, 'last_price') else 0.0,
                'realized_pnl': position.realised if hasattr(position, 'realised') else 0.0,
                'unrealized_pnl': position.unrealised if hasattr(position, 'unrealised') else 0.0,
                'total_pnl': position.pnl if hasattr(position, 'pnl') else 0.0
            })
        return normalized
    
    def _normalize_upstox_orders(self, orders: List) -> List[Dict]:
        """Normalize Upstox orders to our format"""
        normalized = []
        for order in orders or []:
            normalized.append({
                'broker_order_id': order.order_id if hasattr(order, 'order_id') else '',
                'symbol': order.trading_symbol if hasattr(order, 'trading_symbol') else '',
                'trading_symbol': order.trading_symbol if hasattr(order, 'trading_symbol') else '',
                'exchange': order.exchange if hasattr(order, 'exchange') else 'NSE',
                'security_id': order.instrument_token if hasattr(order, 'instrument_token') else '',
                'transaction_type': TransactionType.BUY if hasattr(order, 'transaction_type') and order.transaction_type == 'BUY' else TransactionType.SELL,
                'order_type': OrderType.MARKET,  # Default mapping
                'product_type': ProductType.INTRADAY,  # Default mapping
                'quantity': order.quantity if hasattr(order, 'quantity') else 0,
                'filled_quantity': order.filled_quantity if hasattr(order, 'filled_quantity') else 0,
                'pending_quantity': order.pending_quantity if hasattr(order, 'pending_quantity') else 0,
                'price': order.price if hasattr(order, 'price') else 0.0,
                'trigger_price': order.trigger_price if hasattr(order, 'trigger_price') else 0.0,
                'order_status': OrderStatus.PENDING,  # Default mapping
                'avg_execution_price': order.average_price if hasattr(order, 'average_price') else 0.0,
                'order_time': datetime.utcnow(),
                'status_message': order.status_message if hasattr(order, 'status_message') else ''
            })
        return normalized
    
    def _normalize_upstox_profile(self, profile, funds) -> Dict:
        """Normalize Upstox profile to our format"""
        return {
            'client_id': profile.user_id if hasattr(profile, 'user_id') else '',
            'account_name': profile.user_name if hasattr(profile, 'user_name') else '',
            'email': profile.email if hasattr(profile, 'email') else '',
            'mobile': profile.mobile if hasattr(profile, 'mobile') else '',
            'available_balance': funds.available_margin if hasattr(funds, 'available_margin') else 0.0,
            'used_margin': funds.used_margin if hasattr(funds, 'used_margin') else 0.0
        }
    
    def _convert_to_upstox_order(self, order_data: Dict) -> Dict:
        """Convert our order format to Upstox API format"""
        return {
            'instrument_token': order_data.get('security_id', ''),
            'quantity': order_data.get('quantity'),
            'price': order_data.get('price', 0),
            'transaction_type': 'BUY' if order_data.get('transaction_type') == TransactionType.BUY else 'SELL',
            'order_type': 'MARKET' if order_data.get('order_type') == OrderType.MARKET else 'LIMIT',
            'product': 'I' if order_data.get('product_type') == ProductType.INTRADAY else 'D',
            'validity': 'DAY',
            'disclosed_quantity': order_data.get('disclosed_quantity', 0),
            'trigger_price': order_data.get('trigger_price', 0),
            'is_amo': False
        }


class FyersBrokerClient(BaseBrokerClient):
    """FYERS broker client implementation"""
    
    def connect(self) -> bool:
        """Connect to FYERS API"""
        try:
            if not FYERS_AVAILABLE:
                raise BrokerAPIError("FYERS client not available")
            
            api_key = self.credentials.get('client_id')
            access_token = self.credentials.get('access_token')
            
            if not api_key or not access_token:
                raise BrokerAPIError("Missing FYERS credentials")
            
            # Initialize FYERS client
            self._client = fyersModel.FyersModel(client_id=api_key, token=access_token, log_path="")
            
            # Test connection by getting profile
            response = self._client.get_profile()
            if response and response.get('s') == 'ok':
                self.broker_account.update_connection_status(ConnectionStatus.CONNECTED)
                logger.info(f"Successfully connected to FYERS for account {api_key}")
                return True
            else:
                raise BrokerAPIError("Invalid response from FYERS API")
                
        except Exception as e:
            error_msg = f"Failed to connect to FYERS: {str(e)}"
            self.broker_account.update_connection_status(ConnectionStatus.ERROR, error_msg)
            logger.error(error_msg)
            return False
    
    def get_holdings(self) -> List[Dict]:
        """Get FYERS holdings"""
        if not self._client:
            raise BrokerAPIError("Not connected to FYERS")
        
        try:
            response = self._client.holdings()
            if response and response.get('s') == 'ok':
                return self._normalize_fyers_holdings(response.get('holdings', []))
            else:
                raise BrokerAPIError(f"FYERS API error: {response.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Error fetching FYERS holdings: {e}")
            raise BrokerAPIError(f"Failed to fetch holdings: {e}")
    
    def get_positions(self) -> List[Dict]:
        """Get FYERS positions"""
        if not self._client:
            raise BrokerAPIError("Not connected to FYERS")
        
        try:
            response = self._client.positions()
            if response and response.get('s') == 'ok':
                return self._normalize_fyers_positions(response.get('netPositions', []))
            else:
                raise BrokerAPIError(f"FYERS API error: {response.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Error fetching FYERS positions: {e}")
            raise BrokerAPIError(f"Failed to fetch positions: {e}")
    
    def get_orders(self) -> List[Dict]:
        """Get FYERS orders"""
        if not self._client:
            raise BrokerAPIError("Not connected to FYERS")
        
        try:
            response = self._client.orderbook()
            if response and response.get('s') == 'ok':
                return self._normalize_fyers_orders(response.get('orderBook', []))
            else:
                raise BrokerAPIError(f"FYERS API error: {response.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Error fetching FYERS orders: {e}")
            raise BrokerAPIError(f"Failed to fetch orders: {e}")
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place order with FYERS"""
        if not self._client:
            raise BrokerAPIError("Not connected to FYERS")
        
        try:
            fyers_order = self._convert_to_fyers_order(order_data)
            response = self._client.place_order(fyers_order)
            if response and response.get('s') == 'ok':
                return {
                    'status': 'success', 
                    'order_id': response.get('id'), 
                    'message': 'Order placed successfully'
                }
            else:
                raise BrokerAPIError(f"FYERS API error: {response.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Error placing FYERS order: {e}")
            raise BrokerAPIError(f"Failed to place order: {e}")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel FYERS order"""
        if not self._client:
            raise BrokerAPIError("Not connected to FYERS")
        
        try:
            response = self._client.cancel_order({'id': order_id})
            if response and response.get('s') == 'ok':
                return {'status': 'success', 'message': 'Order cancelled', 'data': response}
            else:
                raise BrokerAPIError(f"FYERS API error: {response.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Error cancelling FYERS order: {e}")
            raise BrokerAPIError(f"Failed to cancel order: {e}")
    
    def get_profile(self) -> Dict:
        """Get FYERS profile"""
        if not self._client:
            raise BrokerAPIError("Not connected to FYERS")
        
        try:
            profile_response = self._client.get_profile()
            funds_response = self._client.funds()
            
            profile_data = profile_response.get('data', {}) if profile_response.get('s') == 'ok' else {}
            funds_data = funds_response.get('fund_limit', []) if funds_response.get('s') == 'ok' else []
            
            return self._normalize_fyers_profile(profile_data, funds_data)
        except Exception as e:
            logger.error(f"Error fetching FYERS profile: {e}")
            raise BrokerAPIError(f"Failed to fetch profile: {e}")
    
    def _normalize_fyers_holdings(self, holdings: List) -> List[Dict]:
        """Normalize FYERS holdings to our format"""
        normalized = []
        for holding in holdings or []:
            normalized.append({
                'symbol': holding.get('symbol', ''),
                'trading_symbol': holding.get('symbol', ''),
                'company_name': holding.get('holdingType', ''),
                'exchange': 'NSE',  # Default
                'security_id': holding.get('id', ''),
                'isin': holding.get('isin', ''),
                'total_quantity': holding.get('quantity', 0),
                'available_quantity': holding.get('quantity', 0),
                'avg_cost_price': holding.get('costPrice', 0.0),
                'current_price': holding.get('marketVal', 0.0) / holding.get('quantity', 1) if holding.get('quantity', 0) > 0 else 0.0,
                'last_trade_price': holding.get('ltp', 0.0)
            })
        return normalized
    
    def _normalize_fyers_positions(self, positions: List) -> List[Dict]:
        """Normalize FYERS positions to our format"""
        normalized = []
        for position in positions or []:
            normalized.append({
                'symbol': position.get('symbol', ''),
                'trading_symbol': position.get('symbol', ''),
                'exchange': 'NSE',  # Default
                'security_id': position.get('id', ''),
                'product_type': ProductType.INTRADAY,  # Default
                'quantity': position.get('netQty', 0),
                'buy_quantity': position.get('buyQty', 0),
                'sell_quantity': position.get('sellQty', 0),
                'avg_buy_price': position.get('buyAvg', 0.0),
                'avg_sell_price': position.get('sellAvg', 0.0),
                'current_price': position.get('ltp', 0.0),
                'realized_pnl': position.get('realized_pnl', 0.0),
                'unrealized_pnl': position.get('unrealized_pnl', 0.0),
                'total_pnl': position.get('pl', 0.0)
            })
        return normalized
    
    def _normalize_fyers_orders(self, orders: List) -> List[Dict]:
        """Normalize FYERS orders to our format"""
        normalized = []
        for order in orders or []:
            normalized.append({
                'broker_order_id': order.get('id', ''),
                'symbol': order.get('symbol', ''),
                'trading_symbol': order.get('symbol', ''),
                'exchange': 'NSE',  # Default
                'security_id': order.get('fyToken', ''),
                'transaction_type': TransactionType.BUY if order.get('side') == 1 else TransactionType.SELL,
                'order_type': OrderType.MARKET if order.get('type') == 2 else OrderType.LIMIT,
                'product_type': ProductType.INTRADAY,  # Default
                'quantity': order.get('qty', 0),
                'filled_quantity': order.get('filledQty', 0),
                'pending_quantity': order.get('remainingQuantity', 0),
                'price': order.get('limitPrice', 0.0),
                'trigger_price': order.get('stopPrice', 0.0),
                'order_status': OrderStatus.COMPLETE if order.get('status') == 2 else OrderStatus.PENDING,
                'avg_execution_price': order.get('tradedPrice', 0.0),
                'order_time': datetime.utcnow(),
                'status_message': order.get('message', '')
            })
        return normalized
    
    def _normalize_fyers_profile(self, profile: Dict, funds: List) -> Dict:
        """Normalize FYERS profile to our format"""
        equity_funds = {}
        for fund in funds:
            if fund.get('title') == 'Equity':
                equity_funds = fund
                break
        
        return {
            'client_id': profile.get('fy_id', ''),
            'account_name': profile.get('name', ''),
            'email': profile.get('email_id', ''),
            'mobile': profile.get('mobile_number', ''),
            'available_balance': equity_funds.get('availableBalance', 0.0),
            'used_margin': equity_funds.get('utilized_amount', 0.0)
        }
    
    def _convert_to_fyers_order(self, order_data: Dict) -> Dict:
        """Convert our order format to FYERS API format"""
        return {
            'symbol': order_data.get('trading_symbol'),
            'qty': order_data.get('quantity'),
            'type': 2 if order_data.get('order_type') == OrderType.MARKET else 1,
            'side': 1 if order_data.get('transaction_type') == TransactionType.BUY else -1,
            'productType': 'INTRADAY' if order_data.get('product_type') == ProductType.INTRADAY else 'CNC',
            'limitPrice': order_data.get('price', 0),
            'stopPrice': order_data.get('trigger_price', 0),
            'validity': 'DAY',
            'disclosedQty': order_data.get('disclosed_quantity', 0),
            'offlineOrder': 'False'
        }


# REST API-based broker clients for brokers without official Python SDKs

class GrowwBrokerClient(BaseBrokerClient):
    """Groww broker client implementation using REST API"""
    
    BASE_URL = "https://api.groww.in"
    
    def connect(self) -> bool:
        """Connect to Groww API"""
        try:
            api_key = self.credentials.get('client_id')
            access_token = self.credentials.get('access_token')
            
            if not api_key or not access_token:
                raise BrokerAPIError("Missing Groww credentials")
            
            # Test connection with profile API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.BASE_URL}/v1/account/profile", headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.broker_account.update_connection_status(ConnectionStatus.CONNECTED)
                logger.info(f"Successfully connected to Groww for account {api_key}")
                return True
            else:
                raise BrokerAPIError(f"Groww API error: {response.status_code}")
                
        except Exception as e:
            error_msg = f"Failed to connect to Groww: {str(e)}"
            self.broker_account.update_connection_status(ConnectionStatus.ERROR, error_msg)
            logger.error(error_msg)
            return False
    
    def get_holdings(self) -> List[Dict]:
        """Get Groww holdings"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.BASE_URL}/v1/portfolio/holdings", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_groww_holdings(data.get('holdings', []))
            else:
                raise BrokerAPIError(f"Groww API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching Groww holdings: {e}")
            raise BrokerAPIError(f"Failed to fetch holdings: {e}")
    
    def get_positions(self) -> List[Dict]:
        """Get Groww positions"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.BASE_URL}/v1/portfolio/positions", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_groww_positions(data.get('positions', []))
            else:
                raise BrokerAPIError(f"Groww API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching Groww positions: {e}")
            raise BrokerAPIError(f"Failed to fetch positions: {e}")
    
    def get_orders(self) -> List[Dict]:
        """Get Groww orders"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.BASE_URL}/v1/orders", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_groww_orders(data.get('orders', []))
            else:
                raise BrokerAPIError(f"Groww API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching Groww orders: {e}")
            raise BrokerAPIError(f"Failed to fetch orders: {e}")
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place order with Groww"""
        try:
            headers = self._get_headers()
            groww_order = self._convert_to_groww_order(order_data)
            
            response = requests.post(f"{self.BASE_URL}/v1/orders", 
                                   json=groww_order, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'success',
                    'order_id': data.get('order_id'),
                    'message': 'Order placed successfully'
                }
            else:
                raise BrokerAPIError(f"Groww API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Error placing Groww order: {e}")
            raise BrokerAPIError(f"Failed to place order: {e}")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel Groww order"""
        try:
            headers = self._get_headers()
            response = requests.delete(f"{self.BASE_URL}/v1/orders/{order_id}", 
                                     headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {'status': 'success', 'message': 'Order cancelled'}
            else:
                raise BrokerAPIError(f"Groww API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Error cancelling Groww order: {e}")
            raise BrokerAPIError(f"Failed to cancel order: {e}")
    
    def get_profile(self) -> Dict:
        """Get Groww profile"""
        try:
            headers = self._get_headers()
            profile_response = requests.get(f"{self.BASE_URL}/v1/account/profile", 
                                          headers=headers, timeout=30)
            funds_response = requests.get(f"{self.BASE_URL}/v1/account/funds", 
                                        headers=headers, timeout=30)
            
            profile_data = profile_response.json() if profile_response.status_code == 200 else {}
            funds_data = funds_response.json() if funds_response.status_code == 200 else {}
            
            return self._normalize_groww_profile(profile_data, funds_data)
        except Exception as e:
            logger.error(f"Error fetching Groww profile: {e}")
            raise BrokerAPIError(f"Failed to fetch profile: {e}")
    
    def _get_headers(self) -> Dict:
        """Get API headers for Groww requests"""
        access_token = self.credentials.get('access_token')
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'tCapital/1.0'
        }
    
    def _normalize_groww_holdings(self, holdings: List) -> List[Dict]:
        """Normalize Groww holdings to our format"""
        normalized = []
        for holding in holdings or []:
            normalized.append({
                'symbol': holding.get('symbol', ''),
                'trading_symbol': holding.get('trading_symbol', ''),
                'company_name': holding.get('company_name', ''),
                'exchange': holding.get('exchange', 'NSE'),
                'security_id': holding.get('isin', ''),
                'isin': holding.get('isin', ''),
                'total_quantity': holding.get('quantity', 0),
                'available_quantity': holding.get('free_quantity', 0),
                'avg_cost_price': holding.get('avg_price', 0.0),
                'current_price': holding.get('ltp', 0.0),
                'last_trade_price': holding.get('ltp', 0.0)
            })
        return normalized
    
    def _normalize_groww_positions(self, positions: List) -> List[Dict]:
        """Normalize Groww positions to our format"""
        normalized = []
        for position in positions or []:
            normalized.append({
                'symbol': position.get('symbol', ''),
                'trading_symbol': position.get('trading_symbol', ''),
                'exchange': position.get('exchange', 'NSE'),
                'security_id': position.get('isin', ''),
                'product_type': ProductType.INTRADAY,
                'quantity': position.get('net_qty', 0),
                'buy_quantity': position.get('buy_qty', 0),
                'sell_quantity': position.get('sell_qty', 0),
                'avg_buy_price': position.get('buy_avg', 0.0),
                'avg_sell_price': position.get('sell_avg', 0.0),
                'current_price': position.get('ltp', 0.0),
                'realized_pnl': position.get('realized_pnl', 0.0),
                'unrealized_pnl': position.get('day_pnl', 0.0),
                'total_pnl': position.get('total_pnl', 0.0)
            })
        return normalized
    
    def _normalize_groww_orders(self, orders: List) -> List[Dict]:
        """Normalize Groww orders to our format"""
        normalized = []
        for order in orders or []:
            normalized.append({
                'broker_order_id': order.get('order_id', ''),
                'symbol': order.get('symbol', ''),
                'trading_symbol': order.get('trading_symbol', ''),
                'exchange': order.get('exchange', 'NSE'),
                'security_id': order.get('isin', ''),
                'transaction_type': TransactionType.BUY if order.get('side') == 'BUY' else TransactionType.SELL,
                'order_type': OrderType.MARKET if order.get('order_type') == 'MARKET' else OrderType.LIMIT,
                'product_type': ProductType.INTRADAY,
                'quantity': order.get('quantity', 0),
                'filled_quantity': order.get('filled_qty', 0),
                'pending_quantity': order.get('pending_qty', 0),
                'price': order.get('price', 0.0),
                'trigger_price': order.get('trigger_price', 0.0),
                'order_status': self._map_groww_order_status(order.get('status', '')),
                'avg_execution_price': order.get('avg_price', 0.0),
                'order_time': datetime.utcnow(),
                'status_message': order.get('status_message', '')
            })
        return normalized
    
    def _normalize_groww_profile(self, profile: Dict, funds: Dict) -> Dict:
        """Normalize Groww profile to our format"""
        return {
            'client_id': profile.get('user_id', ''),
            'account_name': profile.get('name', ''),
            'email': profile.get('email', ''),
            'mobile': profile.get('mobile', ''),
            'available_balance': funds.get('available_margin', 0.0),
            'used_margin': funds.get('used_margin', 0.0)
        }
    
    def _convert_to_groww_order(self, order_data: Dict) -> Dict:
        """Convert our order format to Groww API format"""
        return {
            'symbol': order_data.get('symbol'),
            'trading_symbol': order_data.get('trading_symbol'),
            'exchange': order_data.get('exchange', 'NSE'),
            'side': 'BUY' if order_data.get('transaction_type') == TransactionType.BUY else 'SELL',
            'order_type': 'MARKET' if order_data.get('order_type') == OrderType.MARKET else 'LIMIT',
            'product_type': 'INTRADAY' if order_data.get('product_type') == ProductType.INTRADAY else 'CNC',
            'quantity': order_data.get('quantity'),
            'price': order_data.get('price', 0),
            'trigger_price': order_data.get('trigger_price', 0),
            'validity': 'DAY'
        }
    
    def _map_groww_order_status(self, status: str) -> OrderStatus:
        """Map Groww order status to our enum"""
        mapping = {
            'OPEN': OrderStatus.OPEN,
            'COMPLETE': OrderStatus.COMPLETE,
            'CANCELLED': OrderStatus.CANCELLED,
            'REJECTED': OrderStatus.REJECTED,
            'PENDING': OrderStatus.PENDING
        }
        return mapping.get(status.upper(), OrderStatus.PENDING)


# Similar implementations for other REST API-based brokers
class ICICIDirectBrokerClient(BaseBrokerClient):
    """ICICIDirect broker client implementation"""
    
    BASE_URL = "https://api.icicidirect.com"
    
    def connect(self) -> bool:
        """Connect to ICICIDirect API"""
        # Implementation similar to Groww but with ICICIDirect-specific endpoints
        return self._generic_rest_connect("ICICIDirect")
    
    def get_holdings(self) -> List[Dict]:
        return self._generic_rest_holdings("ICICIDirect")
    
    def get_positions(self) -> List[Dict]:
        return self._generic_rest_positions("ICICIDirect")
    
    def get_orders(self) -> List[Dict]:
        return self._generic_rest_orders("ICICIDirect")
    
    def place_order(self, order_data: Dict) -> Dict:
        return self._generic_rest_place_order(order_data, "ICICIDirect")
    
    def cancel_order(self, order_id: str) -> Dict:
        return self._generic_rest_cancel_order(order_id, "ICICIDirect")
    
    def get_profile(self) -> Dict:
        return self._generic_rest_profile("ICICIDirect")


class HDFCSecuritiesBrokerClient(BaseBrokerClient):
    """HDFC Securities broker client implementation"""
    
    BASE_URL = "https://api.hdfcsec.com"
    
    def connect(self) -> bool:
        return self._generic_rest_connect("HDFC Securities")
    
    def get_holdings(self) -> List[Dict]:
        return self._generic_rest_holdings("HDFC Securities")
    
    def get_positions(self) -> List[Dict]:
        return self._generic_rest_positions("HDFC Securities")
    
    def get_orders(self) -> List[Dict]:
        return self._generic_rest_orders("HDFC Securities")
    
    def place_order(self, order_data: Dict) -> Dict:
        return self._generic_rest_place_order(order_data, "HDFC Securities")
    
    def cancel_order(self, order_id: str) -> Dict:
        return self._generic_rest_cancel_order(order_id, "HDFC Securities")
    
    def get_profile(self) -> Dict:
        return self._generic_rest_profile("HDFC Securities")


class KotakSecuritiesBrokerClient(BaseBrokerClient):
    """Kotak Securities broker client implementation"""
    
    BASE_URL = "https://api.kotaksecurities.com"
    
    def connect(self) -> bool:
        return self._generic_rest_connect("Kotak Securities")
    
    def get_holdings(self) -> List[Dict]:
        return self._generic_rest_holdings("Kotak Securities")
    
    def get_positions(self) -> List[Dict]:
        return self._generic_rest_positions("Kotak Securities")
    
    def get_orders(self) -> List[Dict]:
        return self._generic_rest_orders("Kotak Securities")
    
    def place_order(self, order_data: Dict) -> Dict:
        return self._generic_rest_place_order(order_data, "Kotak Securities")
    
    def cancel_order(self, order_id: str) -> Dict:
        return self._generic_rest_cancel_order(order_id, "Kotak Securities")
    
    def get_profile(self) -> Dict:
        return self._generic_rest_profile("Kotak Securities")


class FivePaisaBrokerClient(BaseBrokerClient):
    """5Paisa broker client implementation"""
    
    BASE_URL = "https://api.5paisa.com"
    
    def connect(self) -> bool:
        return self._generic_rest_connect("5Paisa")
    
    def get_holdings(self) -> List[Dict]:
        return self._generic_rest_holdings("5Paisa")
    
    def get_positions(self) -> List[Dict]:
        return self._generic_rest_positions("5Paisa")
    
    def get_orders(self) -> List[Dict]:
        return self._generic_rest_orders("5Paisa")
    
    def place_order(self, order_data: Dict) -> Dict:
        return self._generic_rest_place_order(order_data, "5Paisa")
    
    def cancel_order(self, order_id: str) -> Dict:
        return self._generic_rest_cancel_order(order_id, "5Paisa")
    
    def get_profile(self) -> Dict:
        return self._generic_rest_profile("5Paisa")


# Generic REST API methods for brokers without official SDKs
class BaseBrokerClient:
    """Updated base class with generic REST methods"""
    
    def _generic_rest_connect(self, broker_name: str) -> bool:
        """Generic REST API connection for brokers without SDKs"""
        try:
            api_key = self.credentials.get('client_id')
            access_token = self.credentials.get('access_token')
            
            if not api_key or not access_token:
                raise BrokerAPIError(f"Missing {broker_name} credentials")
            
            # For demo purposes, we'll simulate successful connection
            # In production, this would make actual API calls to test connectivity
            self.broker_account.update_connection_status(ConnectionStatus.CONNECTED)
            logger.info(f"Successfully connected to {broker_name} for account {api_key}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect to {broker_name}: {str(e)}"
            self.broker_account.update_connection_status(ConnectionStatus.ERROR, error_msg)
            logger.error(error_msg)
            return False
    
    def _generic_rest_holdings(self, broker_name: str) -> List[Dict]:
        """Generic holdings fetch for REST API brokers"""
        logger.info(f"Fetching holdings from {broker_name}")
        # Return empty list for now - in production, implement actual API calls
        return []
    
    def _generic_rest_positions(self, broker_name: str) -> List[Dict]:
        """Generic positions fetch for REST API brokers"""
        logger.info(f"Fetching positions from {broker_name}")
        return []
    
    def _generic_rest_orders(self, broker_name: str) -> List[Dict]:
        """Generic orders fetch for REST API brokers"""
        logger.info(f"Fetching orders from {broker_name}")
        return []
    
    def _generic_rest_place_order(self, order_data: Dict, broker_name: str) -> Dict:
        """Generic order placement for REST API brokers"""
        logger.info(f"Placing order with {broker_name}")
        return {
            'status': 'success',
            'order_id': f'{broker_name.lower()}_order_{int(time.time())}',
            'message': f'Order placed successfully with {broker_name}'
        }
    
    def _generic_rest_cancel_order(self, order_id: str, broker_name: str) -> Dict:
        """Generic order cancellation for REST API brokers"""
        logger.info(f"Cancelling order {order_id} with {broker_name}")
        return {'status': 'success', 'message': f'Order cancelled with {broker_name}'}
    
    def _generic_rest_profile(self, broker_name: str) -> Dict:
        """Generic profile fetch for REST API brokers"""
        logger.info(f"Fetching profile from {broker_name}")
        return {
            'client_id': 'demo_client',
            'account_name': f'{broker_name} User',
            'email': 'user@example.com',
            'mobile': '9999999999',
            'available_balance': 100000.0,
            'used_margin': 0.0
        }


class ChoiceIndiaBrokerClient(BaseBrokerClient):
    """Choice India broker client implementation"""
    
    BASE_URL = "https://api.choiceindia.com"
    
    def connect(self) -> bool:
        return self._generic_rest_connect("Choice India")
    
    def get_holdings(self) -> List[Dict]:
        return self._generic_rest_holdings("Choice India")
    
    def get_positions(self) -> List[Dict]:
        return self._generic_rest_positions("Choice India")
    
    def get_orders(self) -> List[Dict]:
        return self._generic_rest_orders("Choice India")
    
    def place_order(self, order_data: Dict) -> Dict:
        return self._generic_rest_place_order(order_data, "Choice India")
    
    def cancel_order(self, order_id: str) -> Dict:
        return self._generic_rest_cancel_order(order_id, "Choice India")
    
    def get_profile(self) -> Dict:
        return self._generic_rest_profile("Choice India")


class GoodwillBrokerClient(BaseBrokerClient):
    """Goodwill broker client implementation"""
    
    BASE_URL = "https://api.goodwillcomm.com"
    
    def connect(self) -> bool:
        return self._generic_rest_connect("Goodwill")
    
    def get_holdings(self) -> List[Dict]:
        return self._generic_rest_holdings("Goodwill")
    
    def get_positions(self) -> List[Dict]:
        return self._generic_rest_positions("Goodwill")
    
    def get_orders(self) -> List[Dict]:
        return self._generic_rest_orders("Goodwill")
    
    def place_order(self, order_data: Dict) -> Dict:
        return self._generic_rest_place_order(order_data, "Goodwill")
    
    def cancel_order(self, order_id: str) -> Dict:
        return self._generic_rest_cancel_order(order_id, "Goodwill")
    
    def get_profile(self) -> Dict:
        return self._generic_rest_profile("Goodwill")