"""enhance_portfolio_multiple_asset_classes

Revision ID: 778bfbd1fc03
Revises: 0002
Create Date: 2025-09-14 07:39:50.718441

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '778bfbd1fc03'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Enhance Portfolio model to support multiple asset classes"""
    
    # Create ENUM types for asset types and categories
    asset_type_enum = sa.Enum('equities', 'mutual_funds', 'fixed_income', 'futures_options', 
                              'nps', 'real_estate', 'gold', 'etf', 'crypto', 'esop', 
                              'private_equity', name='assettype')
    
    asset_category_enum = sa.Enum('equity', 'debt', 'commodities', 'alternative', 'hybrid', 
                                  name='assetcategory')
    
    asset_type_enum.create(op.get_bind())
    asset_category_enum.create(op.get_bind())
    
    # Check if portfolio table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if inspector.has_table('portfolio'):
        # Add new columns for multiple asset classes
        
        # F&O specific fields
        op.add_column('portfolio', sa.Column('contract_type', sa.String(20), nullable=True))
        op.add_column('portfolio', sa.Column('strike_price', sa.Float, nullable=True))
        op.add_column('portfolio', sa.Column('expiry_date', sa.Date, nullable=True))
        op.add_column('portfolio', sa.Column('lot_size', sa.Integer, nullable=True))
        
        # NPS specific fields
        op.add_column('portfolio', sa.Column('nps_scheme', sa.String(100), nullable=True))
        op.add_column('portfolio', sa.Column('pension_fund_manager', sa.String(100), nullable=True))
        
        # Real Estate specific fields
        op.add_column('portfolio', sa.Column('property_type', sa.String(50), nullable=True))
        op.add_column('portfolio', sa.Column('property_location', sa.String(200), nullable=True))
        
        # Fixed Income specific fields
        op.add_column('portfolio', sa.Column('maturity_date', sa.Date, nullable=True))
        op.add_column('portfolio', sa.Column('interest_rate', sa.Float, nullable=True))
        
        # Add broker_account_id as foreign key to BrokerAccount
        op.add_column('portfolio', sa.Column('broker_account_id', sa.Integer, nullable=True))
        
        # Create foreign key constraint if user_brokers table exists
        if inspector.has_table('user_brokers'):
            op.create_foreign_key('fk_portfolio_broker_account', 'portfolio', 'user_brokers', 
                                ['broker_account_id'], ['id'])
        
        # Rename stock_name to asset_name for clarity
        op.alter_column('portfolio', 'stock_name', new_column_name='asset_name')
        
        # Increase ticker_symbol length to accommodate F&O contracts
        op.alter_column('portfolio', 'ticker_symbol', type_=sa.String(50))
        
        # Temporarily allow nulls in asset_type for data migration
        op.add_column('portfolio', sa.Column('asset_type_new', asset_type_enum, nullable=True))
        op.add_column('portfolio', sa.Column('asset_category_new', asset_category_enum, nullable=True))
        
        # Migrate existing data - map old asset_type strings to enum values
        connection.execute(text("""
            UPDATE portfolio 
            SET asset_type_new = CASE 
                WHEN LOWER(asset_type) = 'stocks' THEN 'equities'
                WHEN LOWER(asset_type) = 'mf' THEN 'mutual_funds'
                WHEN LOWER(asset_type) = 'etf' THEN 'etf'
                WHEN LOWER(asset_type) = 'bonds' THEN 'fixed_income'
                WHEN LOWER(asset_type) = 'gold' THEN 'gold'
                WHEN LOWER(asset_type) = 'crypto' THEN 'crypto'
                WHEN LOWER(asset_type) = 'esop' THEN 'esop'
                WHEN LOWER(asset_type) = 'privateequity' THEN 'private_equity'
                ELSE 'equities'  -- Default fallback
            END
        """))
        
        # Set default asset categories based on asset types
        connection.execute(text("""
            UPDATE portfolio 
            SET asset_category_new = CASE 
                WHEN asset_type_new IN ('equities', 'etf', 'esop', 'private_equity') THEN 'equity'
                WHEN asset_type_new IN ('fixed_income') THEN 'debt'
                WHEN asset_type_new IN ('gold') THEN 'commodities'
                WHEN asset_type_new IN ('crypto', 'real_estate', 'nps') THEN 'alternative'
                WHEN asset_type_new IN ('mutual_funds') THEN 'hybrid'
                ELSE 'equity'
            END
        """))
        
        # Drop old columns and rename new ones
        op.drop_column('portfolio', 'asset_type')
        op.drop_column('portfolio', 'asset_category')
        op.alter_column('portfolio', 'asset_type_new', new_column_name='asset_type')
        op.alter_column('portfolio', 'asset_category_new', new_column_name='asset_category')
        
        # Make asset_type non-nullable now that data is migrated
        op.alter_column('portfolio', 'asset_type', nullable=False)
        
        # Try to migrate broker_id to broker_account_id if both columns exist
        try:
            # Check if broker_id column exists
            portfolio_columns = [col['name'] for col in inspector.get_columns('portfolio')]
            if 'broker_id' in portfolio_columns and inspector.has_table('user_brokers'):
                # Attempt to map broker_id strings to actual broker account IDs
                connection.execute(text("""
                    UPDATE portfolio 
                    SET broker_account_id = ub.id
                    FROM user_brokers ub 
                    WHERE portfolio.broker_id = ub.broker_name 
                    AND portfolio.user_id = ub.user_id
                """))
                
                # Drop the old broker_id column
                op.drop_column('portfolio', 'broker_id')
        except Exception as e:
            # If migration fails, continue - this is not critical
            print(f"Warning: Could not migrate broker_id data: {e}")
    
    # Add performance indexes for the new portfolio structure
    op.create_index('ix_portfolio_asset_type', 'portfolio', ['asset_type'])
    op.create_index('ix_portfolio_asset_category', 'portfolio', ['asset_category'])
    op.create_index('ix_portfolio_broker_account_id', 'portfolio', ['broker_account_id'])
    op.create_index('ix_portfolio_user_asset_type', 'portfolio', ['user_id', 'asset_type'])
    op.create_index('ix_portfolio_user_broker', 'portfolio', ['user_id', 'broker_account_id'])


def downgrade() -> None:
    """Reverse the portfolio enhancements"""
    
    # Drop indexes
    op.drop_index('ix_portfolio_user_broker', 'portfolio')
    op.drop_index('ix_portfolio_user_asset_type', 'portfolio')
    op.drop_index('ix_portfolio_broker_account_id', 'portfolio')
    op.drop_index('ix_portfolio_asset_category', 'portfolio')
    op.drop_index('ix_portfolio_asset_type', 'portfolio')
    
    # Check if portfolio table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if inspector.has_table('portfolio'):
        # Drop foreign key constraint
        try:
            op.drop_constraint('fk_portfolio_broker_account', 'portfolio', type_='foreignkey')
        except Exception:
            pass
        
        # Revert column names
        op.alter_column('portfolio', 'asset_name', new_column_name='stock_name')
        op.alter_column('portfolio', 'ticker_symbol', type_=sa.String(20))
        
        # Add back old string columns for asset_type and asset_category
        op.add_column('portfolio', sa.Column('asset_type_old', sa.String(20), nullable=True))
        op.add_column('portfolio', sa.Column('asset_category_old', sa.String(50), nullable=True))
        
        # Migrate enum data back to strings
        connection.execute(text("""
            UPDATE portfolio 
            SET asset_type_old = CASE 
                WHEN asset_type = 'equities' THEN 'Stocks'
                WHEN asset_type = 'mutual_funds' THEN 'MF'
                WHEN asset_type = 'etf' THEN 'ETF'
                WHEN asset_type = 'fixed_income' THEN 'Bonds'
                WHEN asset_type = 'gold' THEN 'Gold'
                WHEN asset_type = 'crypto' THEN 'Crypto'
                WHEN asset_type = 'esop' THEN 'ESOP'
                WHEN asset_type = 'private_equity' THEN 'PrivateEquity'
                ELSE 'Stocks'
            END
        """))
        
        # Drop enum columns and rename string columns
        op.drop_column('portfolio', 'asset_type')
        op.drop_column('portfolio', 'asset_category')
        op.alter_column('portfolio', 'asset_type_old', new_column_name='asset_type')
        op.alter_column('portfolio', 'asset_category_old', new_column_name='asset_category')
        
        # Drop asset-specific columns
        op.drop_column('portfolio', 'interest_rate')
        op.drop_column('portfolio', 'maturity_date')
        op.drop_column('portfolio', 'property_location')
        op.drop_column('portfolio', 'property_type')
        op.drop_column('portfolio', 'pension_fund_manager')
        op.drop_column('portfolio', 'nps_scheme')
        op.drop_column('portfolio', 'lot_size')
        op.drop_column('portfolio', 'expiry_date')
        op.drop_column('portfolio', 'strike_price')
        op.drop_column('portfolio', 'contract_type')
        op.drop_column('portfolio', 'broker_account_id')
    
    # Drop ENUM types
    sa.Enum(name='assetcategory').drop(op.get_bind())
    sa.Enum(name='assettype').drop(op.get_bind())