#!/bin/bash
set -e

echo "======================================"
echo "Target Capital — Deployment Startup"
echo "======================================"

# Step 1: Run database migrations (creates tables, tenant, etc.)
echo ""
echo "[1/4] Running database migrations..."
python railway_migrate.py
echo "Migrations done."

# Step 2: Seed research list stocks (501 stocks)
echo ""
echo "[2/4] Seeding research list..."
python seed_research_list.py
echo "Research list seed done."

# Step 3: Seed blog posts (5 articles)
echo ""
echo "[3/4] Seeding blog posts..."
python seed_blog_posts.py
echo "Blog posts seed done."

# Step 4: Start the app
echo ""
echo "[4/4] Starting gunicorn..."
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --timeout 120 \
    --preload \
    main:app
