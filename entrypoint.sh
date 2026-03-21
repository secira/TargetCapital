#!/bin/bash
set -e

echo "======================================"
echo "Target Capital — Deployment Startup"
echo "======================================"

# Step 1: Run database migrations (creates tables, tenant, etc.)
echo ""
echo "[1/3] Running database migrations..."
python railway_migrate.py
echo "Migrations done."

# Step 2: Seed research list stocks
echo ""
echo "[2/3] Seeding research list..."
python seed_research_list.py
echo "Seed done."

# Step 3: Start the app
echo ""
echo "[3/3] Starting gunicorn..."
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --timeout 120 \
    --preload \
    main:app
