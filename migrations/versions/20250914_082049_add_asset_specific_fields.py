"""add_asset_specific_fields

Revision ID: 20250914_082049
Revises: 0002
Create Date: 2025-09-14 08:20:49

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20250914_082049'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add asset-specific columns to portfolio table for multiple asset classes"""
    
    # Check if portfolio table exists before proceeding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if not inspector.has_table('portfolio'):
        print("Portfolio table not found. Skipping migration.")
        return
    
    # Get existing columns to avoid duplicate additions
    existing_columns = [col['name'] for col in inspector.get_columns('portfolio')]
    
    # F&O (Futures & Options) specific fields
    if 'contract_type' not in existing_columns:
        op.add_column('portfolio', sa.Column('contract_type', sa.String(20), nullable=True, 
                                            comment='CALL, PUT, FUTURE for F&O contracts'))
    
    if 'strike_price' not in existing_columns:
        op.add_column('portfolio', sa.Column('strike_price', sa.Float, nullable=True,
                                            comment='Strike price for options contracts'))
    
    if 'expiry_date' not in existing_columns:
        op.add_column('portfolio', sa.Column('expiry_date', sa.Date, nullable=True,
                                            comment='Expiry date for F&O contracts'))
    
    if 'lot_size' not in existing_columns:
        op.add_column('portfolio', sa.Column('lot_size', sa.Integer, nullable=True,
                                            comment='Lot size for F&O contracts'))
    
    if 'option_type' not in existing_columns:
        op.add_column('portfolio', sa.Column('option_type', sa.String(20), nullable=True,
                                            comment='CE, PE for options'))
    
    # NPS (National Pension System) specific fields
    if 'nps_scheme' not in existing_columns:
        op.add_column('portfolio', sa.Column('nps_scheme', sa.String(100), nullable=True,
                                            comment='NPS scheme name'))
    
    if 'pension_fund_manager' not in existing_columns:
        op.add_column('portfolio', sa.Column('pension_fund_manager', sa.String(100), nullable=True,
                                            comment='Pension Fund Manager name'))
    
    if 'tier' not in existing_columns:
        op.add_column('portfolio', sa.Column('tier', sa.String(10), nullable=True,
                                            comment='NPS Tier - Tier 1 or Tier 2'))
    
    # Real Estate specific fields
    if 'property_type' not in existing_columns:
        op.add_column('portfolio', sa.Column('property_type', sa.String(50), nullable=True,
                                            comment='Residential, Commercial, Land, etc.'))
    
    if 'property_location' not in existing_columns:
        op.add_column('portfolio', sa.Column('property_location', sa.String(200), nullable=True,
                                            comment='City/Area of the property'))
    
    if 'area_sqft' not in existing_columns:
        op.add_column('portfolio', sa.Column('area_sqft', sa.Float, nullable=True,
                                            comment='Area of property in square feet'))
    
    # Fixed Income specific fields (Bonds, FDs, etc.)
    if 'maturity_date' not in existing_columns:
        op.add_column('portfolio', sa.Column('maturity_date', sa.Date, nullable=True,
                                            comment='Maturity date for bonds/FDs'))
    
    if 'interest_rate' not in existing_columns:
        op.add_column('portfolio', sa.Column('interest_rate', sa.Float, nullable=True,
                                            comment='Interest rate for fixed income'))
    
    if 'coupon_rate' not in existing_columns:
        op.add_column('portfolio', sa.Column('coupon_rate', sa.Float, nullable=True,
                                            comment='Coupon rate for bonds'))
    
    if 'face_value' not in existing_columns:
        op.add_column('portfolio', sa.Column('face_value', sa.Float, nullable=True,
                                            comment='Face value of bond/FD'))
    
    # Gold specific fields
    if 'gold_form' not in existing_columns:
        op.add_column('portfolio', sa.Column('gold_form', sa.String(50), nullable=True,
                                            comment='Physical, Digital, ETF, Coins, etc.'))
    
    if 'gold_purity' not in existing_columns:
        op.add_column('portfolio', sa.Column('gold_purity', sa.String(20), nullable=True,
                                            comment='22K, 24K, etc.'))
    
    if 'grams' not in existing_columns:
        op.add_column('portfolio', sa.Column('grams', sa.Float, nullable=True,
                                            comment='Weight in grams for physical gold'))
    
    # General field for asset categorization (if not exists)
    if 'asset_category' not in existing_columns:
        op.add_column('portfolio', sa.Column('asset_category', sa.String(50), nullable=True,
                                            comment='Equity, Debt, Commodities, Alternative, Hybrid'))
    
    # Create performance indexes for better query performance
    # Check if indexes exist before creating them
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('portfolio')]
    
    # Index for user_id and asset_type combination (most common query pattern)
    if 'idx_portfolio_user_asset_type' not in existing_indexes:
        op.create_index('idx_portfolio_user_asset_type', 'portfolio', ['user_id', 'asset_type'])
    
    # Index for expiry_date (useful for F&O contracts)
    if 'idx_portfolio_expiry_date' not in existing_indexes:
        op.create_index('idx_portfolio_expiry_date', 'portfolio', ['expiry_date'])
    
    # Index for asset_category
    if 'idx_portfolio_asset_category' not in existing_indexes:
        op.create_index('idx_portfolio_asset_category', 'portfolio', ['asset_category'])
    
    # Index for property_location (useful for real estate)
    if 'idx_portfolio_property_location' not in existing_indexes:
        op.create_index('idx_portfolio_property_location', 'portfolio', ['property_location'])
    
    # Index for maturity_date (useful for bonds/FDs)
    if 'idx_portfolio_maturity_date' not in existing_indexes:
        op.create_index('idx_portfolio_maturity_date', 'portfolio', ['maturity_date'])
    
    print("Successfully added asset-specific columns and indexes to portfolio table")


def downgrade() -> None:
    """Remove asset-specific columns and indexes from portfolio table"""
    
    # Check if portfolio table exists before proceeding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if not inspector.has_table('portfolio'):
        print("Portfolio table not found. Skipping downgrade.")
        return
    
    # Drop indexes first (if they exist)
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('portfolio')]
    
    if 'idx_portfolio_maturity_date' in existing_indexes:
        op.drop_index('idx_portfolio_maturity_date', 'portfolio')
    
    if 'idx_portfolio_property_location' in existing_indexes:
        op.drop_index('idx_portfolio_property_location', 'portfolio')
    
    if 'idx_portfolio_asset_category' in existing_indexes:
        op.drop_index('idx_portfolio_asset_category', 'portfolio')
    
    if 'idx_portfolio_expiry_date' in existing_indexes:
        op.drop_index('idx_portfolio_expiry_date', 'portfolio')
    
    if 'idx_portfolio_user_asset_type' in existing_indexes:
        op.drop_index('idx_portfolio_user_asset_type', 'portfolio')
    
    # Get existing columns to check what needs to be dropped
    existing_columns = [col['name'] for col in inspector.get_columns('portfolio')]
    
    # Drop asset-specific columns (only if they exist)
    columns_to_drop = [
        'grams', 'gold_purity', 'gold_form',  # Gold fields
        'face_value', 'coupon_rate', 'interest_rate', 'maturity_date',  # Fixed Income fields
        'area_sqft', 'property_location', 'property_type',  # Real Estate fields
        'tier', 'pension_fund_manager', 'nps_scheme',  # NPS fields
        'option_type', 'lot_size', 'expiry_date', 'strike_price', 'contract_type'  # F&O fields
    ]
    
    for column in columns_to_drop:
        if column in existing_columns:
            op.drop_column('portfolio', column)
    
    # Note: We don't drop asset_category as it might have been added by a different migration
    # or might contain important data. This preserves backward compatibility.
    
    print("Successfully removed asset-specific columns and indexes from portfolio table")