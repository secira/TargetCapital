"""Add missing performance indexes for frequently accessed queries

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-11 07:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add missing performance indexes for frequently accessed data"""
    
    # Get database connection and inspector
    connection = op.get_bind()
    inspector = Inspector.from_engine(connection)
    
    # Helper function to safely create indexes
    def safe_create_index(index_name, table_name, columns):
        """Create index only if table exists and index doesn't already exist"""
        if not inspector.has_table(table_name):
            return
        
        # Check if all columns exist in the table
        table_columns = [col['name'] for col in inspector.get_columns(table_name)]
        for col in columns:
            if col not in table_columns:
                print(f"Warning: Column '{col}' does not exist in table '{table_name}', skipping index {index_name}")
                return
        
        existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
        if index_name not in existing_indexes:
            try:
                # Properly quote table names for PostgreSQL reserved words
                quoted_table = f'"{table_name}"' if table_name in ['user', 'order', 'group'] else table_name
                quoted_columns = ', '.join([f'"{col}"' if col in ['user', 'order', 'group'] else col for col in columns])
                op.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {quoted_table} ({quoted_columns})')
            except Exception as e:
                print(f"Warning: Could not create index {index_name}: {e}")
    
    # Add indexes for User table - frequently queried fields
    safe_create_index('ix_user_email', 'user', ['email'])
    safe_create_index('ix_user_username', 'user', ['username'])
    
    # Add indexes for main trading tables if they exist
    # Blog and content indexes
    safe_create_index('ix_blog_post_created_at', 'blog_post', ['created_at'])
    safe_create_index('ix_blog_post_published', 'blog_post', ['published'])
    safe_create_index('ix_blog_post_category', 'blog_post', ['category'])
    
    # Trading signal indexes
    safe_create_index('ix_trading_signal_symbol', 'trading_signal', ['symbol'])
    safe_create_index('ix_trading_signal_signal_type', 'trading_signal', ['signal_type'])
    safe_create_index('ix_trading_signal_created_at', 'trading_signal', ['created_at'])
    
    # AI analysis indexes
    safe_create_index('ix_ai_analysis_symbol', 'ai_analysis', ['symbol'])
    safe_create_index('ix_ai_analysis_analysis_type', 'ai_analysis', ['analysis_type'])
    safe_create_index('ix_ai_analysis_created_at', 'ai_analysis', ['created_at'])
    
    # Portfolio optimization indexes
    safe_create_index('ix_portfolio_optimization_user_id', 'portfolio_optimization', ['user_id'])
    safe_create_index('ix_portfolio_optimization_created_at', 'portfolio_optimization', ['created_at'])
    
    # Watchlist indexes
    safe_create_index('ix_watchlist_item_user_id', 'watchlist_item', ['user_id'])
    safe_create_index('ix_watchlist_item_symbol', 'watchlist_item', ['symbol'])
    safe_create_index('ix_watchlist_item_user_symbol', 'watchlist_item', ['user_id', 'symbol'])
    
    # Add composite indexes for common query patterns
    safe_create_index('ix_user_active_created', 'user', ['is_active', 'created_at'])
    safe_create_index('ix_trading_signal_user_time', 'trading_signal', ['user_id', 'created_at'])


def downgrade() -> None:
    """Remove the performance indexes"""
    
    # Drop indexes in reverse order
    indexes_to_drop = [
        ('ix_trading_signal_user_time', 'trading_signal'),
        ('ix_user_active_created', 'user'),
        ('ix_watchlist_item_user_symbol', 'watchlist_item'),
        ('ix_watchlist_item_symbol', 'watchlist_item'),
        ('ix_watchlist_item_user_id', 'watchlist_item'),
        ('ix_portfolio_optimization_created_at', 'portfolio_optimization'),
        ('ix_portfolio_optimization_user_id', 'portfolio_optimization'),
        ('ix_ai_analysis_created_at', 'ai_analysis'),
        ('ix_ai_analysis_analysis_type', 'ai_analysis'),
        ('ix_ai_analysis_symbol', 'ai_analysis'),
        ('ix_trading_signal_created_at', 'trading_signal'),
        ('ix_trading_signal_signal_type', 'trading_signal'),
        ('ix_trading_signal_symbol', 'trading_signal'),
        ('ix_blog_post_category', 'blog_post'),
        ('ix_blog_post_published', 'blog_post'),
        ('ix_blog_post_created_at', 'blog_post'),
        ('ix_user_username', 'user'),
        ('ix_user_email', 'user'),
    ]
    
    for index_name, table_name in indexes_to_drop:
        try:
            op.drop_index(index_name, table_name)
        except Exception:
            pass  # Index might not exist