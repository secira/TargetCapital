"""
Database Migration: Add broker_account_id to Manual Holdings Tables

This migration adds broker_account_id foreign key columns to all manual holdings
tables to enable broker-specific tracking, similar to broker-synced holdings.

Tables Updated:
- manual_equity_holdings
- manual_mutual_fund_holdings
- manual_fixed_deposit_holdings
- manual_real_estate_holdings
- manual_commodity_holdings
- manual_cryptocurrency_holdings
- manual_insurance_holdings
- manual_futures_options_holdings

The broker_account_id field is nullable for backward compatibility with existing data.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

def run_migration():
    """Execute the database migration"""
    engine = create_engine(DATABASE_URL)
    
    # List of manual holdings tables to update
    tables = [
        'manual_equity_holdings',
        'manual_mutual_fund_holdings',
        'manual_fixed_deposit_holdings',
        'manual_real_estate_holdings',
        'manual_commodity_holdings',
        'manual_cryptocurrency_holdings',
        'manual_insurance_holdings',
        'manual_futures_options_holdings'
    ]
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            for table in tables:
                print(f"\n{'='*60}")
                print(f"Processing table: {table}")
                print(f"{'='*60}")
                
                # Check if column already exists
                check_query = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name 
                    AND column_name = 'broker_account_id'
                """)
                
                result = conn.execute(check_query, {"table_name": table})
                exists = result.fetchone()
                
                if exists:
                    print(f"✓ Column 'broker_account_id' already exists in {table}")
                    continue
                
                # Add broker_account_id column
                print(f"→ Adding 'broker_account_id' column to {table}...")
                add_column_query = text(f"""
                    ALTER TABLE {table}
                    ADD COLUMN broker_account_id INTEGER
                """)
                conn.execute(add_column_query)
                print(f"✓ Column added successfully")
                
                # Add foreign key constraint
                print(f"→ Adding foreign key constraint...")
                fk_constraint_name = f"fk_{table}_broker_account"
                add_fk_query = text(f"""
                    ALTER TABLE {table}
                    ADD CONSTRAINT {fk_constraint_name}
                    FOREIGN KEY (broker_account_id)
                    REFERENCES user_brokers(id)
                    ON DELETE SET NULL
                """)
                conn.execute(add_fk_query)
                print(f"✓ Foreign key constraint added: {fk_constraint_name}")
                
                # Create index for performance
                print(f"→ Creating index for performance...")
                index_name = f"idx_{table}_broker_account"
                create_index_query = text(f"""
                    CREATE INDEX {index_name}
                    ON {table}(broker_account_id)
                """)
                conn.execute(create_index_query)
                print(f"✓ Index created: {index_name}")
                
                print(f"✓ Table {table} updated successfully!")
            
            # Commit transaction
            trans.commit()
            print(f"\n{'='*60}")
            print("✓ MIGRATION COMPLETED SUCCESSFULLY")
            print(f"{'='*60}")
            print(f"\nAll {len(tables)} manual holdings tables now support broker tracking!")
            print("Users can now specify which broker holds their manually-entered holdings.")
            
        except SQLAlchemyError as e:
            # Rollback on error
            trans.rollback()
            print(f"\n{'='*60}")
            print("✗ MIGRATION FAILED")
            print(f"{'='*60}")
            print(f"Error: {str(e)}")
            raise

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DATABASE MIGRATION: Add Broker Tracking to Manual Holdings")
    print("="*60)
    print("\nThis migration will add broker_account_id to all manual holdings tables.")
    print("The field will be nullable for backward compatibility.\n")
    
    try:
        run_migration()
    except Exception as e:
        print(f"\nMigration failed with error: {str(e)}")
        exit(1)
