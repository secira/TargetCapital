"""fix_portfolio_schema_mismatches

Revision ID: 20250914_090000
Revises: 20250914_082049
Create Date: 2025-09-14 09:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250914_090000'
down_revision = '20250914_082049'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Fix Portfolio model-database schema mismatches"""
    
    # Check if portfolio table exists before proceeding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if not inspector.has_table('portfolio'):
        print("Portfolio table not found. Skipping migration.")
        return
    
    # Get existing columns to check what needs to be modified
    existing_columns = [col['name'] for col in inspector.get_columns('portfolio')]
    
    # 1. Fix asset_type column length (increase from 20 to 50 to match model)
    if 'asset_type' in existing_columns:
        op.alter_column('portfolio', 'asset_type',
                       type_=sa.String(50),
                       existing_type=sa.String(20),
                       nullable=True,  # Also fix nullability to match model
                       existing_nullable=False)
    
    # 2. Add performance indexes for frequently queried fields
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('portfolio')]
    
    # Index for user_id + asset_type (common query pattern)
    if 'idx_portfolio_user_asset_type' not in existing_indexes:
        op.create_index('idx_portfolio_user_asset_type', 'portfolio', ['user_id', 'asset_type'])
    
    # Index for user_id + date_purchased (for date-based portfolio analysis)
    if 'idx_portfolio_user_date_purchased' not in existing_indexes:
        op.create_index('idx_portfolio_user_date_purchased', 'portfolio', ['user_id', 'date_purchased'])
    
    # Index for expiry_date (for F&O contract management)
    if 'idx_portfolio_expiry_date' not in existing_indexes:
        op.create_index('idx_portfolio_expiry_date', 'portfolio', ['expiry_date'])
    
    # Index for maturity_date (for fixed income management)
    if 'idx_portfolio_maturity_date' not in existing_indexes:
        op.create_index('idx_portfolio_maturity_date', 'portfolio', ['maturity_date'])
    
    # Index for property_location (for real estate queries)
    if 'idx_portfolio_property_location' not in existing_indexes:
        op.create_index('idx_portfolio_property_location', 'portfolio', ['property_location'])
    
    # Index for asset_category (for asset allocation analysis)
    if 'idx_portfolio_asset_category' not in existing_indexes:
        op.create_index('idx_portfolio_asset_category', 'portfolio', ['asset_category'])
    
    # Composite index for broker_id + asset_type (for broker-based filtering)
    if 'idx_portfolio_broker_asset_type' not in existing_indexes:
        op.create_index('idx_portfolio_broker_asset_type', 'portfolio', ['broker_id', 'asset_type'])
    
    print("Successfully fixed Portfolio schema mismatches and added performance indexes")


def downgrade() -> None:
    """Revert Portfolio schema fixes"""
    
    # Check if portfolio table exists before proceeding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if not inspector.has_table('portfolio'):
        print("Portfolio table not found. Skipping downgrade.")
        return
    
    # Drop the performance indexes we added
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('portfolio')]
    
    indexes_to_drop = [
        'idx_portfolio_broker_asset_type',
        'idx_portfolio_asset_category', 
        'idx_portfolio_property_location',
        'idx_portfolio_maturity_date',
        'idx_portfolio_expiry_date',
        'idx_portfolio_user_date_purchased',
        'idx_portfolio_user_asset_type'
    ]
    
    for index_name in indexes_to_drop:
        if index_name in existing_indexes:
            op.drop_index(index_name, 'portfolio')
    
    # Revert asset_type column changes
    existing_columns = [col['name'] for col in inspector.get_columns('portfolio')]
    
    if 'asset_type' in existing_columns:
        op.alter_column('portfolio', 'asset_type',
                       type_=sa.String(20),
                       existing_type=sa.String(50),
                       nullable=False,  # Revert to NOT NULL
                       existing_nullable=True)
    
    print("Successfully reverted Portfolio schema changes")