"""
Add composite indexes for multi-tenant query patterns
Revision: 0003
Revises: 0002
Create Date: 2026-01-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    """Add composite indexes for common multi-tenant query patterns"""
    
    connection = op.get_bind()
    inspector = Inspector.from_engine(connection)
    
    def safe_create_index(index_name, table_name, columns):
        """Create index only if table exists and index doesn't already exist"""
        if not inspector.has_table(table_name):
            print(f"Table '{table_name}' does not exist, skipping index {index_name}")
            return
        
        table_columns = [col['name'] for col in inspector.get_columns(table_name)]
        for col in columns:
            if col not in table_columns:
                print(f"Column '{col}' does not exist in '{table_name}', skipping index {index_name}")
                return
        
        existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
        if index_name in existing_indexes:
            print(f"Index {index_name} already exists, skipping")
            return
        
        try:
            quoted_table = f'"{table_name}"' if table_name in ['user', 'order', 'group'] else table_name
            quoted_columns = ', '.join([f'"{col}"' if col in ['user', 'order', 'group'] else col for col in columns])
            op.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {quoted_table} ({quoted_columns})')
            print(f"Created index {index_name}")
        except Exception as e:
            print(f"Could not create index {index_name}: {e}")
    
    safe_create_index('ix_manual_equity_user_tenant', 'manual_equity_holding', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_mf_user_tenant', 'manual_mutual_fund_holding', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_fd_user_tenant', 'manual_fixed_deposit_holding', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_realestate_user_tenant', 'manual_real_estate_holding', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_commodity_user_tenant', 'manual_commodity_holding', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_crypto_user_tenant', 'manual_cryptocurrency_holding', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_insurance_user_tenant', 'manual_insurance_holding', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_bank_user_tenant', 'manual_bank_account', ['user_id', 'tenant_id'])
    safe_create_index('ix_manual_fo_user_tenant', 'manual_futures_options_holding', ['user_id', 'tenant_id'])
    
    safe_create_index('ix_portfolio_user_tenant', 'portfolio', ['user_id', 'tenant_id'])
    safe_create_index('ix_chat_conversation_user_created', 'chat_conversation', ['user_id', 'created_at'])
    safe_create_index('ix_broker_account_user_active', 'broker_account', ['user_id', 'is_active'])
    safe_create_index('ix_payment_user_created', 'payment', ['user_id', 'created_at'])
    safe_create_index('ix_research_cache_key', 'research_cache', ['cache_key'])


def downgrade():
    """Remove composite indexes"""
    
    indexes_to_drop = [
        ('ix_manual_equity_user_tenant', 'manual_equity_holding'),
        ('ix_manual_mf_user_tenant', 'manual_mutual_fund_holding'),
        ('ix_manual_fd_user_tenant', 'manual_fixed_deposit_holding'),
        ('ix_manual_realestate_user_tenant', 'manual_real_estate_holding'),
        ('ix_manual_commodity_user_tenant', 'manual_commodity_holding'),
        ('ix_manual_crypto_user_tenant', 'manual_cryptocurrency_holding'),
        ('ix_manual_insurance_user_tenant', 'manual_insurance_holding'),
        ('ix_manual_bank_user_tenant', 'manual_bank_account'),
        ('ix_manual_fo_user_tenant', 'manual_futures_options_holding'),
        ('ix_portfolio_user_tenant', 'portfolio'),
        ('ix_chat_conversation_user_created', 'chat_conversation'),
        ('ix_broker_account_user_active', 'broker_account'),
        ('ix_payment_user_created', 'payment'),
        ('ix_research_cache_key', 'research_cache'),
    ]
    
    for index_name, table_name in indexes_to_drop:
        try:
            op.drop_index(index_name, table_name)
        except Exception:
            pass
