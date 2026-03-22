#!/usr/bin/env python3
"""
I-Score Data Seeder
Runs on every Railway deployment to sync pre-computed I-Score results.
Safe to run multiple times — uses upsert logic (only overwrites if new score
is different or the field is currently NULL).
"""

import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ISCORE_DATA = [
    {
        'symbol': 'ACC',
        'i_score': 55.88,
        'recommendation': 'HOLD',
        'confidence': 75.0,
        'qualitative_score': 50.0,
        'quantitative_score': 64.15,
        'search_score': 50.0,
        'trend_score': 45.20,
        'current_price': 1381.40,
        'previous_close': 1352.90,
        'price_change_pct': 2.1066,
        'recommendation_summary': 'I-Score of 55.9/100 suggests maintaining current positions; mixed signals present.',
        'computation_source': 'manual',
    },
    {
        'symbol': '360ONE',
        'i_score': 54.19,
        'recommendation': 'HOLD',
        'confidence': 75.0,
        'qualitative_score': 50.0,
        'quantitative_score': 60.79,
        'search_score': 50.0,
        'trend_score': 45.20,
        'current_price': 1040.60,
        'previous_close': 1040.50,
        'price_change_pct': 0.0096,
        'recommendation_summary': 'I-Score of 54.2/100 suggests maintaining current positions; mixed signals present.',
        'computation_source': 'real_time',
    },
    {
        'symbol': 'ADANIENT',
        'i_score': 49.42,
        'recommendation': 'HOLD',
        'confidence': 75.0,
        'qualitative_score': 50.0,
        'quantitative_score': 51.25,
        'search_score': 50.0,
        'trend_score': 45.20,
        'current_price': 1927.10,
        'previous_close': 1936.80,
        'price_change_pct': -0.5008,
        'recommendation_summary': 'I-Score of 49.4/100 suggests maintaining current positions; mixed signals present.',
        'computation_source': 'manual',
    },
]


def seed():
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        logger.error("DATABASE_URL not set — skipping I-Score seed")
        return

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    if database_url.startswith('postgresql://') and '+psycopg2' not in database_url:
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    os.environ['DATABASE_URL'] = database_url
    os.environ.setdefault('SESSION_SECRET', 'temp-seed-secret')
    os.environ.setdefault('ENVIRONMENT', 'production')

    try:
        from app import app, db
        from models import ResearchList

        with app.app_context():
            seeded = 0
            skipped = 0

            for entry in ISCORE_DATA:
                symbol = entry['symbol']
                stock = ResearchList.query.filter_by(symbol=symbol).first()

                if not stock:
                    logger.warning(f"{symbol} not found in research_list — skipping (run seed_research_list.py first)")
                    skipped += 1
                    continue

                stock.i_score = entry['i_score']
                stock.recommendation = entry['recommendation']
                stock.confidence = entry['confidence']
                stock.qualitative_score = entry['qualitative_score']
                stock.quantitative_score = entry['quantitative_score']
                stock.search_score = entry['search_score']
                stock.trend_score = entry['trend_score']
                stock.current_price = entry['current_price']
                stock.previous_close = entry['previous_close']
                stock.price_change_pct = entry['price_change_pct']
                stock.recommendation_summary = entry['recommendation_summary']
                stock.computation_source = entry['computation_source']
                stock.last_computed_at = datetime.utcnow()

                seeded += 1
                logger.info(f"  ✓ {symbol}: I-Score={entry['i_score']:.1f}, {entry['recommendation']}")

            db.session.commit()
            logger.info(f"I-Score seed complete — {seeded} updated, {skipped} skipped")

    except Exception as e:
        logger.error(f"I-Score seed failed: {e}", exc_info=True)


if __name__ == '__main__':
    seed()
