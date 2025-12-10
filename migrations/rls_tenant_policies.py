"""
PostgreSQL Row-Level Security (RLS) Policies for Multi-Tenant Architecture

This script creates RLS policies on all tenant-scoped tables to enforce
data isolation at the database level as a second layer of defense.

How it works:
1. Each connection sets a session variable: SET LOCAL app.tenant_id = 'tenant_id'
2. RLS policies filter rows where tenant_id = current_setting('app.tenant_id')
3. This prevents any accidental cross-tenant data access

Usage:
    python -m migrations.rls_tenant_policies apply
    python -m migrations.rls_tenant_policies verify
    python -m migrations.rls_tenant_policies rollback
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def discover_tenant_scoped_tables(conn):
    """
    Dynamically discover all tables with tenant_id column from database.
    This ensures RLS policies are created for ALL tenant-scoped tables.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'tenant_id' 
        AND table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    logger.info(f"Discovered {len(tables)} tenant-scoped tables from database")
    return tables


def get_db_connection():
    """Get database connection using environment variable."""
    import psycopg2
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    return psycopg2.connect(database_url)


def create_rls_policy_sql(table_name: str) -> str:
    """Generate SQL to create RLS policy for a table."""
    return f"""
-- Enable RLS on {table_name}
ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY;

-- Force RLS for table owners too (important for superuser bypass prevention)
ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS tenant_isolation_select ON "{table_name}";
DROP POLICY IF EXISTS tenant_isolation_insert ON "{table_name}";
DROP POLICY IF EXISTS tenant_isolation_update ON "{table_name}";
DROP POLICY IF EXISTS tenant_isolation_delete ON "{table_name}";

-- SELECT policy: Only see rows for current tenant
CREATE POLICY tenant_isolation_select ON "{table_name}"
    FOR SELECT
    USING (
        tenant_id = COALESCE(
            NULLIF(current_setting('app.tenant_id', true), ''),
            'live'
        )
    );

-- INSERT policy: Can only insert rows for current tenant
CREATE POLICY tenant_isolation_insert ON "{table_name}"
    FOR INSERT
    WITH CHECK (
        tenant_id = COALESCE(
            NULLIF(current_setting('app.tenant_id', true), ''),
            'live'
        )
    );

-- UPDATE policy: Can only update own tenant's rows
CREATE POLICY tenant_isolation_update ON "{table_name}"
    FOR UPDATE
    USING (
        tenant_id = COALESCE(
            NULLIF(current_setting('app.tenant_id', true), ''),
            'live'
        )
    )
    WITH CHECK (
        tenant_id = COALESCE(
            NULLIF(current_setting('app.tenant_id', true), ''),
            'live'
        )
    );

-- DELETE policy: Can only delete own tenant's rows
CREATE POLICY tenant_isolation_delete ON "{table_name}"
    FOR DELETE
    USING (
        tenant_id = COALESCE(
            NULLIF(current_setting('app.tenant_id', true), ''),
            'live'
        )
    );
"""


def create_bypass_role_sql() -> str:
    """Create a role that can bypass RLS for admin operations."""
    return """
-- Create admin role that bypasses RLS (for migrations, admin tools)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'tenant_admin') THEN
        CREATE ROLE tenant_admin;
    END IF;
END
$$;

-- Grant bypass to admin role
ALTER ROLE tenant_admin BYPASSRLS;
"""


def rollback_rls_policy_sql(table_name: str) -> str:
    """Generate SQL to remove RLS policy from a table."""
    return f"""
-- Disable RLS on {table_name}
ALTER TABLE "{table_name}" DISABLE ROW LEVEL SECURITY;

-- Drop policies
DROP POLICY IF EXISTS tenant_isolation_select ON "{table_name}";
DROP POLICY IF EXISTS tenant_isolation_insert ON "{table_name}";
DROP POLICY IF EXISTS tenant_isolation_update ON "{table_name}";
DROP POLICY IF EXISTS tenant_isolation_delete ON "{table_name}";
"""


def apply_rls_policies():
    """Apply RLS policies to all tenant-scoped tables (dynamically discovered)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        tenant_tables = discover_tenant_scoped_tables(conn)
        
        logger.info(f"Found {len(tenant_tables)} tenant-scoped tables to protect")
        
        logger.info("Creating admin bypass role...")
        cursor.execute(create_bypass_role_sql())
        
        success_count = 0
        error_count = 0
        
        for table_name in tenant_tables:
            try:
                logger.info(f"Applying RLS to '{table_name}'...")
                sql = create_rls_policy_sql(table_name)
                cursor.execute(sql)
                success_count += 1
                logger.info(f"✅ RLS applied to '{table_name}'")
            except Exception as e:
                logger.error(f"❌ Failed to apply RLS to '{table_name}': {e}")
                error_count += 1
        
        conn.commit()
        
        logger.info(f"\n{'='*50}")
        logger.info(f"RLS Policy Application Complete")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Success: {success_count} tables")
        logger.info(f"❌ Errors: {error_count} tables")
        
        return success_count, 0, error_count
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to apply RLS policies: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def verify_rls_policies():
    """Verify RLS policies are correctly applied (using dynamic discovery)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        tenant_tables = discover_tenant_scoped_tables(conn)
        
        cursor.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        table_security = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT tablename, policyname, cmd, qual, with_check
            FROM pg_policies
            WHERE schemaname = 'public'
        """)
        policies = {}
        for row in cursor.fetchall():
            table, policy, cmd, qual, check = row
            if table not in policies:
                policies[table] = []
            policies[table].append({'name': policy, 'cmd': cmd})
        
        logger.info(f"\n{'='*60}")
        logger.info("RLS Policy Verification Report")
        logger.info(f"{'='*60}")
        
        protected_count = 0
        unprotected_count = 0
        
        for table_name in tenant_tables:
            if table_name not in table_security:
                continue
            
            rls_enabled = table_security.get(table_name, False)
            table_policies = policies.get(table_name, [])
            
            if rls_enabled and len(table_policies) >= 4:
                logger.info(f"✅ {table_name}: RLS enabled, {len(table_policies)} policies")
                protected_count += 1
            elif rls_enabled:
                logger.warning(f"⚠️  {table_name}: RLS enabled but only {len(table_policies)} policies")
                unprotected_count += 1
            else:
                logger.error(f"❌ {table_name}: RLS NOT enabled")
                unprotected_count += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Summary: {protected_count} protected, {unprotected_count} need attention")
        logger.info(f"{'='*60}")
        
        return protected_count, unprotected_count
        
    finally:
        cursor.close()
        conn.close()


def rollback_rls_policies():
    """Remove RLS policies from all tables (using dynamic discovery)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        tenant_tables = discover_tenant_scoped_tables(conn)
        
        for table_name in tenant_tables:
            try:
                logger.info(f"Removing RLS from '{table_name}'...")
                sql = rollback_rls_policy_sql(table_name)
                cursor.execute(sql)
                logger.info(f"✅ RLS removed from '{table_name}'")
            except Exception as e:
                logger.warning(f"⚠️  Could not remove RLS from '{table_name}': {e}")
        
        conn.commit()
        logger.info("RLS rollback complete")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to rollback RLS policies: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def test_rls_isolation():
    """Test that RLS properly isolates tenant data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        logger.info("Testing RLS tenant isolation...")
        
        cursor.execute("SET LOCAL app.tenant_id = 'live'")
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        live_count = cursor.fetchone()[0]
        logger.info(f"Tenant 'live': {live_count} users visible")
        
        cursor.execute("SET LOCAL app.tenant_id = 'test_tenant_xyz'")
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        test_count = cursor.fetchone()[0]
        logger.info(f"Tenant 'test_tenant_xyz': {test_count} users visible")
        
        if test_count == 0 and live_count > 0:
            logger.info("✅ RLS isolation test PASSED - tenants are isolated")
            return True
        elif test_count > 0:
            logger.error("❌ RLS isolation test FAILED - cross-tenant data visible")
            return False
        else:
            logger.warning("⚠️  No data to test with")
            return None
            
    except Exception as e:
        logger.error(f"RLS test failed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m migrations.rls_tenant_policies <command>")
        print("Commands: apply, verify, rollback, test")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'apply':
        apply_rls_policies()
    elif command == 'verify':
        verify_rls_policies()
    elif command == 'rollback':
        rollback_rls_policies()
    elif command == 'test':
        test_rls_isolation()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
