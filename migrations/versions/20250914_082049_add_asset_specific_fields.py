"""add_additional_asset_specific_fields

Revision ID: 20250914_082049
Revises: 778bfbd1fc03
Create Date: 2025-09-14 08:20:49

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20250914_082049'
down_revision = '778bfbd1fc03'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add additional asset-specific columns to portfolio table (builds on previous migration)"""
    
    # Check if portfolio table exists before proceeding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if not inspector.has_table('portfolio'):
        print("Portfolio table not found. Skipping migration.")
        return
    
    # Get existing columns to avoid duplicate additions
    existing_columns = [col['name'] for col in inspector.get_columns('portfolio')]
    
    # Additional F&O (Futures & Options) specific fields
    # Note: Core F&O fields (contract_type, strike_price, expiry_date, lot_size) already added by previous migration
    
    if 'option_type' not in existing_columns:
        op.add_column('portfolio', sa.Column('option_type', sa.String(20), nullable=True,
                                            comment='CE, PE for options'))
    
    # Additional NPS (National Pension System) specific fields
    # Note: Core NPS fields (nps_scheme, pension_fund_manager) already added by previous migration
    
    if 'tier' not in existing_columns:
        op.add_column('portfolio', sa.Column('tier', sa.String(10), nullable=True,
                                            comment='NPS Tier - Tier 1 or Tier 2'))
    
    # Additional Real Estate specific fields
    # Note: Core real estate fields (property_type, property_location) already added by previous migration
    
    if 'area_sqft' not in existing_columns:
        op.add_column('portfolio', sa.Column('area_sqft', sa.Float, nullable=True,
                                            comment='Area of property in square feet'))
    
    # Additional Fixed Income specific fields (Bonds, FDs, etc.)
    # Note: Core fixed income fields (maturity_date, interest_rate) already added by previous migration
    
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
    
    # Note: asset_category field already added as ENUM by previous migration
    # This migration focuses on additional asset-specific fields not covered by the enum-based approach
    
    # Create performance indexes for better query performance
    # Check if indexes exist before creating them
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('portfolio')]
    
    # Additional indexes for the new fields (core indexes already created by previous migration)
    
    # Index for gold_form (useful for gold asset queries)
    if 'idx_portfolio_gold_form' not in existing_indexes:
        op.create_index('idx_portfolio_gold_form', 'portfolio', ['gold_form'])
    
    # Index for tier (useful for NPS queries)
    if 'idx_portfolio_tier' not in existing_indexes:
        op.create_index('idx_portfolio_tier', 'portfolio', ['tier'])
    
    # Index for option_type (useful for F&O option queries)
    if 'idx_portfolio_option_type' not in existing_indexes:
        op.create_index('idx_portfolio_option_type', 'portfolio', ['option_type'])
    
    print("Successfully added additional asset-specific columns and indexes to portfolio table")


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
    
    # Drop additional asset-specific columns added by this migration only
    # Note: Core asset fields are managed by the previous migration (778bfbd1fc03)
    columns_to_drop = [
        'grams', 'gold_purity', 'gold_form',  # Gold fields (this migration)
        'face_value', 'coupon_rate',  # Additional Fixed Income fields (this migration)
        'area_sqft',  # Additional Real Estate field (this migration)
        'tier',  # Additional NPS field (this migration)
        'option_type'  # Additional F&O field (this migration)
    ]
    
    for column in columns_to_drop:
        if column in existing_columns:
            op.drop_column('portfolio', column)
    
    # Drop additional indexes added by this migration
    if 'idx_portfolio_option_type' in existing_indexes:
        op.drop_index('idx_portfolio_option_type', 'portfolio')
    
    if 'idx_portfolio_tier' in existing_indexes:
        op.drop_index('idx_portfolio_tier', 'portfolio')
    
    if 'idx_portfolio_gold_form' in existing_indexes:
        op.drop_index('idx_portfolio_gold_form', 'portfolio')
    
    # Note: Core portfolio enhancements (asset_type enum, core asset fields, etc.)
    # are managed by the previous migration and will be preserved.
    
    print("Successfully removed additional asset-specific columns and indexes from portfolio table")