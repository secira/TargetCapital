#!/bin/bash
set -e

echo "======================================"
echo "Target Capital — Deployment Startup"
echo "======================================"

# Step 1: Run database migrations (creates tables, tenant, etc.)
echo ""
echo "[1/5] Running database migrations..."
python railway_migrate.py
echo "Migrations done."

# Step 2: Seed research list stocks (501 stocks)
echo ""
echo "[2/5] Seeding research list..."
python seed_research_list.py
echo "Research list seed done."

# Step 3: Seed pre-computed I-Score data
echo ""
echo "[3/5] Seeding I-Score data..."
python seed_iscore_data.py
echo "I-Score seed done."

# Step 4: Seed blog posts (5 articles)
echo ""
echo "[4/5] Seeding blog posts..."
python seed_blog_posts.py
echo "Blog posts seed done."

# Step 5: Start the app
echo ""
echo "[5/5] Starting gunicorn..."
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --timeout 120 \
    --preload \
    main:app
