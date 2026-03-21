#!/usr/bin/env python3
"""
Blog Posts Seeder
Runs on every Railway deployment to ensure all blog posts are present.
Safe to run multiple times — matches on slug, never overwrites existing content/view counts.
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def seed():
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        logger.error("DATABASE_URL not set — skipping blog seed")
        return

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    if database_url.startswith('postgresql://') and '+psycopg2' not in database_url:
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    os.environ['DATABASE_URL'] = database_url
    os.environ.setdefault('SESSION_SECRET', 'temp-seed-secret')
    os.environ.setdefault('ENVIRONMENT', 'production')

    try:
        from seed_blog import BLOG_POSTS
    except ImportError:
        logger.error("seed_blog.py not found — cannot seed blog posts")
        return

    logger.info(f"Seed file contains {len(BLOG_POSTS)} blog posts")

    try:
        from app import app, db
        from models import BlogPost

        with app.app_context():
            current_count = BlogPost.query.filter_by(status='published').count()
            logger.info(f"Current published blog post count: {current_count}")

            if current_count >= len(BLOG_POSTS):
                logger.info("Blog posts already fully seeded — nothing to do")
                return

            inserted = 0
            updated = 0
            for post_data in BLOG_POSTS:
                existing = BlogPost.query.filter_by(slug=post_data['slug']).first()
                if existing:
                    existing.title = post_data['title']
                    existing.excerpt = post_data['excerpt']
                    existing.author_name = post_data['author_name']
                    existing.featured_image = post_data['featured_image']
                    existing.category = post_data['category']
                    existing.tags = post_data['tags']
                    existing.status = post_data['status']
                    existing.meta_description = post_data['meta_description']
                    existing.is_featured = post_data['is_featured']
                    updated += 1
                else:
                    published_at = None
                    if post_data.get('published_at'):
                        try:
                            published_at = datetime.fromisoformat(post_data['published_at'])
                        except Exception:
                            published_at = datetime.utcnow()

                    new_post = BlogPost(
                        title=post_data['title'],
                        slug=post_data['slug'],
                        content=post_data['content'],
                        excerpt=post_data['excerpt'],
                        author_name=post_data['author_name'],
                        featured_image=post_data['featured_image'],
                        category=post_data['category'],
                        tags=post_data['tags'],
                        status=post_data['status'],
                        meta_description=post_data['meta_description'],
                        published_at=published_at or datetime.utcnow(),
                        is_featured=post_data['is_featured'],
                        view_count=0,
                    )
                    db.session.add(new_post)
                    inserted += 1

            db.session.commit()
            final_count = BlogPost.query.filter_by(status='published').count()
            logger.info(f"Blog seed complete — {inserted} inserted, {updated} updated. Total published: {final_count}")

    except Exception as e:
        logger.error(f"Blog seed failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Blog Posts Seeder Starting")
    logger.info("=" * 50)
    seed()
    logger.info("=" * 50)
    logger.info("Blog seeder finished")
    logger.info("=" * 50)
