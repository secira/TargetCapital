#!/bin/bash
# TargetCapital - Quick Start Script

echo "🚀 TargetCapital Quick Start"
echo "================================"
echo ""

# Check if services are running
echo "📊 Service Status:"
echo "-------------------"
sudo supervisorctl status targetcapital
sudo service postgresql status | grep "Active:"
echo ""

# Application info
echo "🌐 Application Access:"
echo "----------------------"
echo "Main App: http://localhost:5000"
echo "Health Check: http://localhost:5000/health"
echo "Admin Login: http://localhost:5000/login"
echo ""

# Credentials
echo "🔑 Admin Credentials:"
echo "---------------------"
echo "Username: admin"
echo "Password: admin123"
echo "Email: admin@targetcapital.ai"
echo ""

# Database info
echo "💾 Database:"
echo "------------"
echo "Type: PostgreSQL 15"
echo "Database: targetcapital"
echo "User: tcuser"
echo ""

# Quick actions
echo "⚡ Quick Actions:"
echo "-----------------"
echo "1. Restart App: sudo supervisorctl restart targetcapital"
echo "2. View Logs: tail -f /var/log/supervisor/targetcapital.out.log"
echo "3. Check Health: curl http://localhost:5000/health"
echo "4. Connect to DB: sudo -u postgres psql -d targetcapital"
echo ""

# Test health
echo "🔍 Testing Application..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Application is healthy (HTTP $HTTP_CODE)"
else
    echo "⚠️  Application returned HTTP $HTTP_CODE"
fi

echo ""
echo "✨ Setup complete! Open http://localhost:5000 in your browser"
