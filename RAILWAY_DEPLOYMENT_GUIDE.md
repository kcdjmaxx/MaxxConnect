---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - subject/deployment
  - tool/flask
  - tool/railway
  - status/active
  - type/implementation-guide
---

# Railway.app Deployment Guide

## Why Railway?

✅ **FREE tier** - Perfect for small business
✅ **HTTPS included** - Automatic SSL certificate
✅ **PostgreSQL included** - Free 500MB database
✅ **Environment variables** - Encrypted and secure
✅ **Auto-deploy from GitHub** - Push code, automatically deploys
✅ **Built-in security** - Firewall, DDoS protection
✅ **No server management** - Railway handles everything

## What's Been Added for Deployment

### ✅ Encryption (PII Protection)
- **Emails and phone numbers encrypted** in database
- Uses industry-standard Fernet (AES-128) encryption
- Encryption key stored in environment variable
- Automatic encryption/decryption (transparent to app)

### ✅ Production Server
- **Gunicorn** WSGI server (not Flask dev server)
- Handles multiple requests efficiently
- Auto-restart on crashes

### ✅ PostgreSQL Support
- Switched from SQLite to PostgreSQL
- Better for production
- Railway provides free tier

### ✅ Railway Configuration
- `Procfile` - Tells Railway how to run app
- `railway.toml` - Railway-specific config
- `runtime.txt` - Python version

---

## Step-by-Step Deployment

### Part 1: Prepare Your Code

#### 1. Generate Encryption Key
```bash
cd MaxxConnect
source venv/bin/activate
python backend/encryption.py
```

Copy the `ENCRYPTION_KEY=...` output. You'll need this later.

#### 2. Push to GitHub (if not already)
```bash
# Initialize git if needed
git init
git add .
git commit -m "Initial commit - email/SMS marketing platform"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/MaxxConnect.git
git push -u origin main
```

### Part 2: Set Up Railway

#### 1. Create Railway Account
- Go to https://railway.app
- Click "Login with GitHub"
- Authorize Railway

#### 2. Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your `MaxxConnect` repository
- Railway will start deploying automatically

#### 3. Add PostgreSQL Database
- In your project, click "+ New"
- Select "Database" → "PostgreSQL"
- Railway creates database and provides connection string

#### 4. Configure Environment Variables
- Click on your web service (not database)
- Go to "Variables" tab
- Click "+ New Variable" and add each:

```
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your-verified-email@example.com
SENDER_NAME=Your Business Name

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+11234567890

BUSINESS_ADDRESS=123 Main St, City, State 12345

SECRET_KEY=generate-a-random-long-string-here
ENCRYPTION_KEY=paste-the-key-from-step-1-here

DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**Important**: The `DATABASE_URL` line uses Railway's magic variable - it automatically connects to your PostgreSQL database.

#### 5. Deploy!
- Railway automatically deploys when you add variables
- Watch the deployment logs
- Look for "Build successful" and "Deployment live"

#### 6. Get Your URL
- In Railway dashboard, you'll see your app URL
- It looks like: `https://your-app-name.up.railway.app`
- Click to open - your app is live!

---

## Part 3: Configure Twilio Webhook

Your app is now publicly accessible, so Twilio can send webhooks!

#### 1. Copy Your Railway URL
- From Railway dashboard: `https://your-app-name.up.railway.app`

#### 2. Set Twilio Webhook
- Go to Twilio Console
- Phone Numbers → Manage → Active Numbers
- Click your phone number
- Scroll to "Messaging"
- Set webhook URL to: `https://your-app-name.up.railway.app/sms-optout`
- Method: POST
- Click Save

#### 3. Test STOP Replies
- Send an SMS from your app
- Reply "STOP"
- Check your app - contact should be unsubscribed!

---

## Part 4: Initialize Database

Your database is empty! Add initial data:

#### Option A: Via Railway Terminal
1. In Railway dashboard, click your service
2. Click "Terminal" tab at bottom
3. Run:
```bash
python -c "from backend.database import init_db; init_db()"
```

#### Option B: Import CSV
1. Open your app URL
2. Go to "Import CSV"
3. Upload your contacts CSV
4. Database is now populated!

---

## Testing Your Deployment

### 1. Visit Your App
```
https://your-app-name.up.railway.app
```

### 2. Check Dashboard
- Should show 5 stat cards
- All zeros initially

### 3. Import Contacts
- Go to Import CSV
- Upload test_contacts.csv
- Verify import succeeds

### 4. Send Test Email
- Go to Email Preview
- Send test email to yourself
- Check inbox (and spam)

### 5. Send Test SMS
- Go to SMS Preview
- Send test SMS to yourself
- Verify received

### 6. Test STOP Reply
- Reply "STOP" to the SMS
- Check dashboard - SMS Unsubscribed should increase
- This proves webhooks are working!

---

## Monitoring & Logs

### View Logs
- Railway Dashboard → Your Service → "Logs" tab
- See all app output in real-time
- Useful for debugging

### Monitor Usage
- Railway Dashboard → Project Settings → Usage
- Track:
  - Bandwidth
  - Build minutes
  - Database size
  - Active hours

### Free Tier Limits
- **$5/month free credit**
- 500MB PostgreSQL
- 500 execution hours/month
- Unlimited bandwidth
- Should be plenty for small business!

---

## Updating Your App

### Method 1: Push to GitHub (Automatic)
```bash
# Make changes to code
git add .
git commit -m "Update feature X"
git push

# Railway automatically detects and deploys!
```

### Method 2: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Link to project
railway link

# Deploy manually
railway up
```

---

## Security Best Practices

### ✅ Already Implemented
- HTTPS (Railway provides)
- Encrypted emails/phones in database
- Environment variables (not in code)
- PostgreSQL encryption at rest
- Gunicorn production server

### 🔒 Additional Recommendations

#### 1. Rotate Secrets Regularly
- Change ENCRYPTION_KEY every 6-12 months
- Requires data migration (ask me if needed)

#### 2. Monitor Access
- Check Railway logs for suspicious activity
- Set up log alerts in Railway

#### 3. Backup Database
```bash
# In Railway terminal
pg_dump $DATABASE_URL > backup.sql
```

#### 4. Rate Limiting (Optional)
Add Flask-Limiter if you get lots of traffic:
```python
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])
```

---

## Costs

### Free Tier (First Month)
- **$0** - Covered by free credit
- Includes:
  - Web service
  - PostgreSQL database
  - HTTPS
  - Custom domain (optional)

### After Free Tier (~Month 2+)
- **$5/month** - If you use under 500 hours
- **$10/month** - If you run 24/7
- Plus SMS costs (Twilio)

### Twilio Costs
- **SMS**: ~$0.0079 per message
- **Phone number**: ~$1.15/month
- **Example**: 500 SMS/month = ~$5

**Total monthly cost**: $10-15 (Railway + Twilio)

---

## Troubleshooting

### Deployment Fails
**Error**: `Module not found`
- Check `requirements.txt` has all dependencies
- Railway logs will show which module

**Error**: `Database connection failed`
- Verify `DATABASE_URL=${{Postgres.DATABASE_URL}}` in variables
- Make sure PostgreSQL service is running

### App Won't Start
**Check**:
- Railway logs for errors
- All environment variables are set
- `Procfile` exists and is correct

### Encryption Errors
**Error**: `ENCRYPTION_KEY not found`
- Make sure you added it to Railway environment variables
- Generate one with: `python backend/encryption.py`

### Twilio Webhook Not Working
**Check**:
- Webhook URL is correct: `https://your-app.railway.app/sms-optout`
- Method is POST
- Your app is deployed and running
- Check Railway logs when you send STOP reply

---

## Migrating from SQLite to PostgreSQL

If you were testing locally with SQLite:

### 1. Export SQLite Data
```bash
# On local machine
sqlite3 database.db .dump > export.sql
```

### 2. Import to PostgreSQL
```bash
# In Railway terminal
psql $DATABASE_URL < export.sql
```

**Or** just re-import your CSV files (easier!).

---

## Advanced: Custom Domain

Want `marketing.yourbusiness.com` instead of Railway URL?

### 1. In Railway Dashboard
- Click your service
- "Settings" → "Domains"
- Click "Add Custom Domain"
- Enter: `marketing.yourbusiness.com`

### 2. Update DNS
- Go to your domain registrar
- Add CNAME record:
  - Name: `marketing`
  - Value: (Railway provides this)
- Railway handles SSL automatically!

---

## Success Checklist

- [ ] Railway account created
- [ ] GitHub repo connected
- [ ] PostgreSQL database added
- [ ] All environment variables set (10 total)
- [ ] App deployed successfully
- [ ] App URL accessible
- [ ] Twilio webhook configured
- [ ] Test email sent and received
- [ ] Test SMS sent and received
- [ ] STOP reply works (webhook success!)
- [ ] Contacts imported
- [ ] Dashboard shows stats

---

## You're Live! 🎉

Your email/SMS marketing platform is now:
- ✅ Deployed to production
- ✅ Encrypted (emails & phones)
- ✅ HTTPS enabled
- ✅ Publicly accessible
- ✅ Auto-deploys from GitHub
- ✅ Professional infrastructure
- ✅ Cost: ~$10-15/month

**Next**: Import your real contacts and start your first campaign!

Need help? Check Railway docs: https://docs.railway.app
