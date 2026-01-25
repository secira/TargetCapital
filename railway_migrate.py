#!/usr/bin/env python3
"""
Railway Database Migration Script
Runs database migrations on first deployment and subsequent updates
"""

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations using Alembic"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL environment variable is required")
        sys.exit(1)
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        os.environ['DATABASE_URL'] = database_url
    
    logger.info("Starting database migration...")
    
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.warning(f"Alembic migration failed, attempting direct table creation: {e}")
        create_tables_directly()

def create_tables_directly():
    """Fallback: Create tables directly using SQLAlchemy"""
    logger.info("Creating database tables directly...")
    
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
        
        os.environ['DATABASE_URL'] = database_url
        os.environ.setdefault('SESSION_SECRET', 'temp-migration-secret')
        os.environ.setdefault('ENVIRONMENT', 'production')
        
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30
            } if 'postgresql' in database_url else {}
        )
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            session.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            session.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
            session.commit()
            logger.info("PostgreSQL extensions created")
        except Exception as ext_error:
            logger.warning(f"Could not create extensions (may already exist): {ext_error}")
            session.rollback()
        
        try:
            from app import db, app
            with app.app_context():
                db.create_all()
                logger.info("All database tables created successfully")
                
                from models import Tenant
                Tenant.get_or_create_default()
                logger.info("Default tenant initialized")
                
        except Exception as app_error:
            logger.error(f"Failed to create tables via app context: {app_error}")
            raise
            
        session.close()
        engine.dispose()
        
    except Exception as e:
        logger.error(f"Direct table creation failed: {e}")
        raise

def verify_database_connection():
    """Verify database connection before migration"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL not set")
        return False
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30
            } if 'postgresql' in database_url else {}
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        engine.dispose()
        logger.info("Database connection verified successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Railway Migration Script Starting")
    logger.info("=" * 50)
    
    if not verify_database_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    run_migrations()
    
    logger.info("=" * 50)
    logger.info("Migration script completed")
    logger.info("=" * 50)
