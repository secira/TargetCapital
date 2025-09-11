"""Add performance indexes for broker models

Revision ID: 0001
Revises: 
Create Date: 2025-09-11 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes to broker models"""
    
    # Create indexes for BrokerHolding table
    op.create_index('ix_broker_holdings_broker_account_id', 'broker_holdings', ['broker_account_id'])
    op.create_index('ix_broker_holdings_symbol', 'broker_holdings', ['symbol'])
    op.create_index('ix_broker_holdings_trading_symbol', 'broker_holdings', ['trading_symbol'])
    op.create_index('ix_broker_holdings_exchange', 'broker_holdings', ['exchange'])
    
    # Create indexes for BrokerPosition table
    op.create_index('ix_broker_positions_broker_account_id', 'broker_positions', ['broker_account_id'])
    op.create_index('ix_broker_positions_symbol', 'broker_positions', ['symbol'])
    op.create_index('ix_broker_positions_trading_symbol', 'broker_positions', ['trading_symbol'])
    op.create_index('ix_broker_positions_exchange', 'broker_positions', ['exchange'])
    op.create_index('ix_broker_positions_product_type', 'broker_positions', ['product_type'])
    op.create_index('ix_broker_positions_position_date', 'broker_positions', ['position_date'])
    op.create_index('ix_broker_positions_created_at', 'broker_positions', ['created_at'])
    
    # Create indexes for BrokerOrder table
    op.create_index('ix_broker_orders_broker_account_id', 'broker_orders', ['broker_account_id'])
    op.create_index('ix_broker_orders_symbol', 'broker_orders', ['symbol'])
    op.create_index('ix_broker_orders_trading_symbol', 'broker_orders', ['trading_symbol'])
    op.create_index('ix_broker_orders_exchange', 'broker_orders', ['exchange'])
    op.create_index('ix_broker_orders_order_status', 'broker_orders', ['order_status'])
    op.create_index('ix_broker_orders_order_time', 'broker_orders', ['order_time'])
    op.create_index('ix_broker_orders_execution_time', 'broker_orders', ['execution_time'])
    
    # Create composite indexes for common query patterns
    op.create_index('ix_broker_holdings_account_symbol', 'broker_holdings', ['broker_account_id', 'trading_symbol'])
    op.create_index('ix_broker_holdings_account_symbol_exchange', 'broker_holdings', ['broker_account_id', 'trading_symbol', 'exchange'])
    op.create_index('ix_broker_positions_account_symbol', 'broker_positions', ['broker_account_id', 'trading_symbol'])
    op.create_index('ix_broker_positions_account_symbol_exchange', 'broker_positions', ['broker_account_id', 'trading_symbol', 'exchange'])
    op.create_index('ix_broker_orders_account_status', 'broker_orders', ['broker_account_id', 'order_status'])
    op.create_index('ix_broker_orders_account_status_time', 'broker_orders', ['broker_account_id', 'order_status', 'order_time'])
    op.create_index('ix_broker_orders_account_time', 'broker_orders', ['broker_account_id', 'order_time'])


def downgrade() -> None:
    """Remove performance indexes"""
    
    # Drop composite indexes
    op.drop_index('ix_broker_orders_account_time', 'broker_orders')
    op.drop_index('ix_broker_orders_account_status_time', 'broker_orders')
    op.drop_index('ix_broker_orders_account_status', 'broker_orders')
    op.drop_index('ix_broker_positions_account_symbol_exchange', 'broker_positions')
    op.drop_index('ix_broker_positions_account_symbol', 'broker_positions')
    op.drop_index('ix_broker_holdings_account_symbol_exchange', 'broker_holdings')
    op.drop_index('ix_broker_holdings_account_symbol', 'broker_holdings')
    
    # Drop BrokerOrder indexes
    op.drop_index('ix_broker_orders_execution_time', 'broker_orders')
    op.drop_index('ix_broker_orders_order_time', 'broker_orders')
    op.drop_index('ix_broker_orders_order_status', 'broker_orders')
    op.drop_index('ix_broker_orders_exchange', 'broker_orders')
    op.drop_index('ix_broker_orders_trading_symbol', 'broker_orders')
    op.drop_index('ix_broker_orders_symbol', 'broker_orders')
    op.drop_index('ix_broker_orders_broker_account_id', 'broker_orders')
    
    # Drop BrokerPosition indexes
    op.drop_index('ix_broker_positions_created_at', 'broker_positions')
    op.drop_index('ix_broker_positions_position_date', 'broker_positions')
    op.drop_index('ix_broker_positions_product_type', 'broker_positions')
    op.drop_index('ix_broker_positions_exchange', 'broker_positions')
    op.drop_index('ix_broker_positions_trading_symbol', 'broker_positions')
    op.drop_index('ix_broker_positions_symbol', 'broker_positions')
    op.drop_index('ix_broker_positions_broker_account_id', 'broker_positions')
    
    # Drop BrokerHolding indexes
    op.drop_index('ix_broker_holdings_exchange', 'broker_holdings')
    op.drop_index('ix_broker_holdings_trading_symbol', 'broker_holdings')
    op.drop_index('ix_broker_holdings_symbol', 'broker_holdings')
    op.drop_index('ix_broker_holdings_broker_account_id', 'broker_holdings')
    
    print("✅ Performance indexes removed successfully")