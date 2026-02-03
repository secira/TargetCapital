# 🚂 Railway Deployment Guide for TargetCapital

## ✅ Deployment Issue Fixed

**Problem**: `pip: command not found` error during nixpacks build  
**Solution**: Created custom Dockerfile for reliable deployment

---

## 📋 What Was Fixed

### 1. Created Custom Dockerfile
- Uses official Python 3.11 slim image
- Installs PostgreSQL client and build dependencies
- Properly configures Gunicorn with optimal settings
- Includes health check support

### 2. Updated railway.json
- Changed builder from `NIXPACKS` to `DOCKERFILE`
- Configured health check endpoint (`/health`)
- Set restart policy for reliability

### 3. Optimized Build
- Added `.dockerignore` for faster builds
- Excluded unnecessary files (tests, docs, cache)
- Layered Dockerfile for better caching

---

## 🚀 Deploy to Railway

### **Step 1: Connect Repository**
1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your TargetCapital repository

### **Step 2: Configure Environment Variables**

Add these required variables in Railway dashboard:

#### **Required**:
```bash
DATABASE_URL=<railway_postgresql_url>
SESSION_SECRET=<generate_random_secret>
ENVIRONMENT=production
PORT=8000
```

#### **Optional** (for full features):
```bash
# AI Features
OPENAI_API_KEY=sk-...

# Payment Processing
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...

# Email Notifications
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=...
SENDGRID_API_KEY=...

# SMS/OTP
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Redis (optional)
REDIS_URL=redis://...
```

### **Step 3: Add PostgreSQL Database**
1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL`

### **Step 4: Deploy**
1. Railway will auto-detect the Dockerfile
2. Build will start automatically
3. Wait for deployment (2-5 minutes)
4. Check logs for any issues

---

## 🔧 Configuration Files

### **Dockerfile** ✅
```dockerfile
FROM python:3.11-slim
# Installs all dependencies properly
# Runs migrations automatically
# Starts Gunicorn on Railway's $PORT
```

### **railway.json** ✅
```json
{
  "builder": "DOCKERFILE",
  "healthcheckPath": "/health",
  "restartPolicyType": "ON_FAILURE"
}
```

### **Procfile** (backup)
```
web: python railway_migrate.py && gunicorn ...
```

---

## 📊 Expected Build Output

```
✅ Building from Dockerfile
✅ Installing system dependencies
✅ Installing Python packages (100+ packages)
✅ Copying application code
✅ Build complete
✅ Starting deployment
✅ Running migrations
✅ Gunicorn started
✅ Health check passed
✅ Deployment successful
```

---

## 🔍 Troubleshooting

### **Build Still Fails?**

#### Option 1: Force Dockerfile Build
In Railway settings:
- Go to "Settings" → "Build"
- Ensure "Builder" is set to "Dockerfile"

#### Option 2: Check Requirements
```bash
# Test locally first
docker build -t targetcapital .
docker run -p 8000:8000 -e DATABASE_URL=... targetcapital
```

#### Option 3: View Build Logs
- Railway dashboard → "Deployments" → Latest build
- Check for specific error messages
- Share logs if issue persists

### **Deployment Succeeds but App Crashes?**

Check these:
1. **DATABASE_URL**: Must be valid PostgreSQL URL
2. **SESSION_SECRET**: Must be set
3. **Migrations**: Check if they ran successfully
4. **Logs**: Railway dashboard → "View Logs"

### **Common Errors**:

**Error: `No module named 'psycopg2'`**
```bash
# Already fixed in Dockerfile with libpq-dev
```

**Error: `DATABASE_URL not set`**
```bash
# Add PostgreSQL service in Railway
# Or manually set DATABASE_URL variable
```

**Error: `Port binding failed`**
```bash
# Dockerfile uses $PORT environment variable
# Railway sets this automatically
```

---

## 🎯 Post-Deployment Checklist

### **1. Verify Deployment**
```bash
# Health check
curl https://your-app.railway.app/health

# Should return:
{"status": "healthy", "environment": "production"}
```

### **2. Test Login**
- Go to your Railway URL
- Try logging in with admin/admin123
- Change admin password immediately

### **3. Configure Domain** (optional)
- Railway dashboard → "Settings" → "Domains"
- Add custom domain
- Update DNS records

### **4. Enable Monitoring**
- Railway provides built-in metrics
- Check CPU, Memory, Network usage
- Set up alerts if needed

---

## 📈 Scaling on Railway

### **Horizontal Scaling**:
Railway automatically scales based on:
- Incoming requests
- Resource usage
- Health check status

### **Vertical Scaling**:
Upgrade your Railway plan for:
- More RAM
- More CPU
- Higher request limits

### **Database Scaling**:
- Railway PostgreSQL scales automatically
- Consider upgrading plan for larger databases

---

## 🔐 Security Checklist

✅ **Environment Variables**: All secrets in Railway dashboard  
✅ **SESSION_SECRET**: Use strong random value  
✅ **HTTPS**: Enabled by default on Railway  
✅ **CORS**: Already configured for production  
✅ **CSP**: Flask-Talisman enabled in production  
✅ **Rate Limiting**: Configured with Redis (optional)  

---

## 💰 Cost Estimate

### **Railway Pricing**:
- **Starter**: $5/month (500 hours)
- **Developer**: $20/month (Unlimited)
- **PostgreSQL**: Included in plan

### **External Services** (optional):
- OpenAI API: Pay-as-you-go
- Razorpay: Transaction fees
- SendGrid: Free tier available
- Twilio: Pay-as-you-go

---

## ✅ Summary

**Issue**: Nixpacks couldn't find pip  
**Fix**: Created custom Dockerfile  
**Status**: Ready to deploy to Railway  

**Next Steps**:
1. Push updated files to GitHub
2. Connect repo to Railway
3. Add environment variables
4. Add PostgreSQL database
5. Deploy!

---

**🎊 Your TargetCapital app is now Railway-ready!**

Simply push the changes to GitHub and Railway will build using the new Dockerfile.
