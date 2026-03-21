#!/usr/bin/env python3
"""
Research List Seeder
Runs on every Railway deployment to ensure all 501 stocks are present.
Safe to run multiple times — uses INSERT ... ON CONFLICT DO NOTHING logic.
"""

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def seed():
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        logger.error("DATABASE_URL not set — skipping seed")
        return

    # Normalize Railway's postgres:// prefix
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    if database_url.startswith('postgresql://') and '+psycopg2' not in database_url:
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    os.environ['DATABASE_URL'] = database_url
    os.environ.setdefault('SESSION_SECRET', 'temp-seed-secret')
    os.environ.setdefault('ENVIRONMENT', 'production')

    try:
        from seed_data import RESEARCH_LIST_STOCKS
    except ImportError:
        logger.error("seed_data.py not found — cannot seed")
        return

    logger.info(f"Seed file contains {len(RESEARCH_LIST_STOCKS)} stocks")

    try:
        from app import app, db
        from models import ResearchList

        with app.app_context():
            current_count = ResearchList.query.filter_by(is_active=True).count()
            logger.info(f"Current research_list active count: {current_count}")

            if current_count >= len(RESEARCH_LIST_STOCKS):
                logger.info("Research list already fully seeded — nothing to do")
                return

            inserted = 0
            updated = 0
            for stock in RESEARCH_LIST_STOCKS:
                symbol = stock['symbol']
                existing = ResearchList.query.filter_by(symbol=symbol).first()
                if existing:
                    # Update metadata only — never touch i_score
                    existing.company_name = stock['company_name']
                    existing.asset_type = stock['asset_type']
                    existing.sector = stock['sector']
                    existing.is_active = True
                    if not existing.tenant_id:
                        existing.tenant_id = 'live'
                    updated += 1
                else:
                    new_stock = ResearchList(
                        symbol=symbol,
                        company_name=stock['company_name'],
                        asset_type=stock['asset_type'],
                        sector=stock['sector'],
                        is_active=True,
                        tenant_id='live',
                    )
                    db.session.add(new_stock)
                    inserted += 1

                # Commit in batches of 50
                if (inserted + updated) % 50 == 0:
                    db.session.commit()
                    logger.info(f"  Progress: {inserted} inserted, {updated} updated so far...")

            db.session.commit()
            final_count = ResearchList.query.filter_by(is_active=True).count()
            logger.info(f"Seed complete — {inserted} inserted, {updated} updated. Total active: {final_count}")

    except Exception as e:
        logger.error(f"Seed failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Research List Seeder Starting")
    logger.info("=" * 50)
    seed()
    logger.info("=" * 50)
    logger.info("Seeder finished")
    logger.info("=" * 50)
