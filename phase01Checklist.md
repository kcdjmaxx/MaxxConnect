---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - tool/flask
  - tool/railway
  - status/active
  - type/checklist
---

# Phase 1 Completion Checklist (Railway Deployment)

## 🎯 CURRENT STATUS (Last Updated: Jan 16, 2026)

✅ **Phase 1 - COMPLETE!**
✅ **Phase 2 - QR Codes & Async Queue COMPLETE!**

### Production Status
- **Railway Deployment:** Live at maxxconnect.up.railway.app
- **SendGrid:** ⏳ AWAITING REGULATORY APPROVAL (Ticket #24741818)
  - Free trial hit 100 email/day limit during first campaign
  - Upgrade submitted, requires regulatory approval
  - Privacy policy added to email templates
- **Twilio SMS:** ⏳ Awaiting A2P 10DLC approval

### Recently Completed (Jan 2026)
- ✅ QR Code CID implementation (Gmail-compatible)
- ✅ Async email queue with Celery + Redis
- ✅ Campaign resume feature (send to unsent recipients only)
- ✅ Customer name personalization (`[[CUSTOMER_NAME]]` placeholder)
- ✅ Email delivery tracking (`email_deliveries` table)
- ✅ Privacy policy link added to email templates
- ✅ Progress tracking UI with live polling

### Blocking Issues
1. **SendGrid limit:** Trial allows only 100 emails/day. Upgrade pending regulatory approval.
2. **A2P 10DLC:** SMS blocked until Twilio approves campaign registration.

---

## Setup Tasks

### 1. SendGrid Account Setup ✅ COMPLETE
- [x] Sign up for SendGrid account at https://sendgrid.com
- [x] Generate API key from SendGrid dashboard
- [x] **Domain Authentication Complete** - deals@fricandfrac.net verified
- [x] Verify your sender email address in SendGrid
- [x] Copy API key for local .env file
- [x] **Test email sent successfully** to kcdjmaxx@gmail.com
- [ ] Copy API key for Railway environment variables (when deploying)

### 2. Twilio Account Setup (for SMS) ✅ SETUP COMPLETE / ⏳ A2P PENDING
- [x] Sign up for Twilio account at https://twilio.com
- [x] Get $15 free trial credit
- [x] Copy Account SID from dashboard: `[CONFIGURED]`
- [x] Copy Auth Token from dashboard
- [x] Get phone number: **+18168399958** (local KC number)
- [x] Verify caller ID: +18168383050
- [x] Copy credentials to local .env file
- [x] **A2P 10DLC Registration Submitted** - Status: IN PROGRESS
- [ ] **Wait for A2P approval** (check Twilio Console → Messaging → Regulatory Compliance)
- [ ] Test SMS once A2P approved

### 3. Local Environment Setup ✅ COMPLETE
- [x] Database schema updated (recreated database.db with SMS fields)
- [x] .env file configured with all credentials:
  - SendGrid API Key: Configured
  - Sender Email: deals@fricandfrac.net
  - Twilio Account SID: Configured
  - Twilio Auth Token: Configured
  - Twilio Phone: +18168399958
  - Business Name: Fric & Frac
  - Business Address: 1700 W39th St. Kansas City, MO 64111
  - Encryption Key: Generated
  - Secret Key: Generated
- [x] Dependencies installed in venv
- [x] Flask app tested locally (fixed database schema issue)

### 4. Railway Project Setup - NOT STARTED
- [x] Sign up for Railway account at https://railway.app
- [x] Create new project
- [x] Connect your GitHub repository (or create one)
- [x] Railway will auto-detect Flask app

### 5. Configure Railway Environment Variables - NOT STARTED
- [x] Go to Railway project → Variables tab
- [x] Add the following environment variables:
  - [x] `SENDGRID_API_KEY` = your SendGrid API key
  - [x] `SENDGRID_FROM_EMAIL` = your-verified-email@domain.com
  - [x] `TWILIO_ACCOUNT_SID` = your Twilio Account SID
  - [x] `TWILIO_AUTH_TOKEN` = your Twilio Auth Token
  - [ ] `TWILIO_PHONE_NUMBER` = +1234567890
  - [ ] `BUSINESS_NAME` = Your Business Name
  - [ ] `BUSINESS_ADDRESS` = 123 Main St, City, State 12345
  - [ ] `ENCRYPTION_KEY` = (generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
  - [ ] `DATABASE_URL` = (Railway PostgreSQL automatically provides this)

### 6. Add PostgreSQL Database - NOT STARTED
- [ ] In Railway project, click "+ New"
- [ ] Select "Database" → "PostgreSQL"
- [ ] Railway automatically sets `DATABASE_URL` environment variable
- [ ] Note: Database will auto-initialize on first deployment

### 7. Deploy to Railway - NOT STARTED
- [ ] Push code to GitHub (Railway auto-deploys on push)
- [ ] Or click "Deploy" in Railway dashboard
- [ ] Wait for build to complete (check Deployments tab)
- [ ] Verify deployment succeeded (green checkmark)
- [ ] Copy your Railway app URL: `https://your-app-name.up.railway.app`

### 8. Initialize Production Database - NOT STARTED
- [ ] Railway will run database initialization automatically on first start
- [ ] Verify in Railway logs: Look for "Database initialized" message
- [ ] If needed, manually trigger: Railway → Settings → Redeploy

### 9. Configure Twilio Webhook (for SMS opt-out) - PENDING A2P APPROVAL
- [ ] **First: Wait for A2P 10DLC approval** (check status in Twilio Console)
- [ ] Go to Twilio console: Phone Numbers → Manage → Active Numbers
- [ ] Click on +18168399958
- [ ] Under "Messaging", find "A MESSAGE COMES IN"
- [ ] Set Webhook URL: `https://your-app-name.up.railway.app/sms-optout`
- [ ] Set method to: POST
- [ ] Click "Save"

## Local Testing (Completed)

### 10. Test Email Locally ✅ COMPLETE
- [x] Created test_sendgrid.py script
- [x] Sent test email to kcdjmaxx@gmail.com
- [x] Email delivered successfully with:
  - Correct sender: Fric & Frac <deals@fricandfrac.net>
  - Business address in footer
  - Professional formatting

### 11. Test SMS Locally ⏳ PENDING A2P APPROVAL
- [x] Created test_twilio.py script
- [x] Verified caller ID: +18168383050
- [x] Attempted SMS test - blocked due to A2P registration pending
- [ ] **Retry after A2P approval** (Status: IN PROGRESS in Twilio Console)
- [ ] Verify SMS received with trial prefix
- [ ] Test STOP reply handling

---

## Production Testing (Railway) - NOT STARTED

### 12. Test Production Dashboard
- [ ] Navigate to your Railway URL: `https://your-app-name.up.railway.app`
- [ ] Verify stats show 5 cards: Total Contacts, Email Subscribed, Email Unsubscribed, SMS Subscribed, SMS Unsubscribed
- [ ] All stats should show 0
- [ ] Click all navigation links to verify pages load (Dashboard, Contacts, Import CSV, Email Preview, SMS Preview)

### 13. Test CSV Import
- [ ] Click "Import CSV" in navigation
- [ ] Upload `test_contacts.csv` file (includes phone number)
- [ ] Verify import success message appears
- [ ] Check that stats show: Added: 1, Updated: 0
- [ ] Go to "Contacts" page
- [ ] Verify kcdjmaxx@gmail.com appears with phone number +11234567890
- [ ] Verify "✓ SMS On" status shows

### 14. Test Email Preview
- [ ] Click "Email Preview" in navigation
- [ ] Enter email subject: "Test Email"
- [ ] Enter email body (HTML):
  ```html
  <h2>Hello!</h2>
  <p>This is a test email from Railway deployment.</p>
  ```
- [ ] Click "Preview Email" button
- [ ] Verify preview shows below with your business info and unsubscribe link

### 12. Test Sending Email (Production)
- [ ] In "Email Preview" page, enter your email in "Test Email Address" field
- [ ] Click "Send Test Email" button
- [ ] Verify success message appears
- [ ] Check your email inbox (and spam folder)
- [ ] Verify email received with:
  - [ ] Correct subject
  - [ ] Your HTML content
  - [ ] Business name in footer
  - [ ] Business address in footer
  - [ ] Unsubscribe link in footer (should point to Railway URL)

### 13. Test Email Unsubscribe
- [ ] Open the test email you received
- [ ] Click the "Unsubscribe" link
- [ ] Verify unsubscribe confirmation page appears (on Railway URL)
- [ ] Go back to app dashboard
- [ ] Verify Email Unsubscribed stat increased
- [ ] Go to "Contacts" page
- [ ] Verify kcdjmaxx@gmail.com shows "✗ Unsubscribed" for email

### 14. Test SMS Preview
- [ ] Click "SMS Preview" in navigation
- [ ] Enter SMS message: "Test SMS from Railway - Special offer today only!"
- [ ] Click "Preview SMS" button
- [ ] Verify character count shows (message + opt-out footer)
- [ ] Verify preview shows message in chat bubble format

### 15. Test Sending SMS (Production)
- [ ] In "SMS Preview" page, enter your phone number in E.164 format (+11234567890)
- [ ] Click "Send Test SMS" button
- [ ] Verify success message appears
- [ ] Check your phone for SMS
- [ ] Verify SMS received with:
  - [ ] Your message text
  - [ ] Opt-out footer: "Reply STOP to unsubscribe. - Your Business Name"

### 16. Test SMS Opt-Out (Webhook)
- [ ] Reply "STOP" to the SMS you received
- [ ] Wait 5-10 seconds for Twilio webhook to trigger
- [ ] Go to Railway → Deployments → Logs
- [ ] Verify you see: "SMS opt-out processed for +11234567890"
- [ ] Go to app dashboard
- [ ] Verify SMS Unsubscribed stat increased
- [ ] Go to "Contacts" page
- [ ] Verify contact shows "✗ SMS Off"

### 17. Test Re-importing Contacts
- [ ] Go to "Import CSV" page
- [ ] Upload `test_contacts.csv` again
- [ ] Verify it shows: Updated: 1, Added: 0 (deduplication working)

### 18. Test Campaign Management (NEW - Dec 2024)
- [x] Navigate to "Campaigns" page
- [x] Click "Create New Campaign"
- [x] Fill in campaign details:
  - [x] Campaign Name: "Test Monday Special"
  - [x] Subject: "Test - Monday Burgers"
  - [x] Template: Select "Monday Special"
- [x] Click "Save as Draft" - verify success
- [x] Campaign appears in campaigns list

### 19. Test Campaign Edit
- [x] Click on campaign name in list
- [x] Update subject line
- [x] Click "Save Changes"
- [x] Verify changes reflected in list

### 20. Test Campaign Preview
- [x] Click Preview (👁️) icon
- [x] Verify email renders correctly
- [x] Check images display (base64 embedded in dev)
- [x] Verify unsubscribe link present

### 21. Test Campaign Send - Test Mode
- [x] Click Send (📧) icon on draft campaign
- [x] Send confirmation page opens
- [x] Check "Test Mode" checkbox
- [x] Enter test email address
- [x] Button changes to orange "📧 Send Test Email Only"
- [x] Click send button
- [x] Confirm dialog appears
- [x] Test email received with:
  - [x] Correct subject
  - [x] Images displaying
  - [x] Personalization working
  - [x] Unsubscribe link present

### 22. Test Campaign Send - Live Mode (Optional)
- [ ] Click Send (📧) on draft campaign
- [ ] Select target audience (All Subscribers)
- [ ] Ensure test mode is OFF
- [ ] Click green "📧 Send Campaign" button
- [ ] Warning confirmation appears
- [ ] Campaign sent to subscribers
- [ ] Status changes to "sent"
- [ ] Cannot edit sent campaign

### 23. Test Campaign Delete
- [x] Click trash icon (🗑️) on a campaign
- [x] Confirmation dialog appears
- [x] Confirm deletion
- [x] Campaign removed from list

## Validation Checklist

### Core Features
- [ ] ✓ Application runs on Railway without errors
- [ ] ✓ PostgreSQL database connected and initialized
- [ ] ✓ Dashboard displays email AND SMS statistics
- [ ] ✓ CSV import works correctly (email + phone)
- [ ] ✓ Duplicate emails/phones are deduplicated
- [ ] ✓ Invalid emails are rejected
- [ ] ✓ Phone numbers are formatted correctly
- [ ] ✓ Email preview renders correctly
- [ ] ✓ SMS preview shows character count
- [ ] ✓ Test email sends successfully via SendGrid
- [ ] ✓ Test SMS sends successfully via Twilio
- [ ] ✓ Email includes unsubscribe link (points to Railway URL)
- [ ] ✓ Email includes business address
- [ ] ✓ SMS includes opt-out instructions
- [ ] ✓ Email unsubscribe functionality works
- [ ] ✓ SMS opt-out (STOP reply) works via webhook
- [ ] ✓ Contact status updates after unsubscribe
- [ ] ✓ All environment variables configured on Railway
- [ ] ✓ Encryption key configured and working

### Campaign Management Features (NEW)
- [x] ✓ Campaign CRUD operations (Create, Read, Update, Delete)
- [x] ✓ Template selection from templates/email/ directory
- [x] ✓ Campaign list displays all campaigns
- [x] ✓ Click campaign name to edit
- [x] ✓ Preview campaign before sending
- [x] ✓ Send confirmation page with audience selection
- [x] ✓ Test mode sends only to test email
- [x] ✓ Live mode sends to selected audience
- [x] ✓ Safety confirmations (different for test vs live)
- [x] ✓ Visual indicators (orange for test, green for live)
- [x] ✓ Delete campaign with confirmation
- [x] ✓ Campaign status tracking (draft, sent)
- [x] ✓ Cannot edit sent campaigns
- [x] ✓ Image handling (base64 in dev, URLs in prod)
- [x] ✓ Personalization (customer names, unsubscribe links)
- [x] ✓ Audience targeting (All, Email Only, SMS Only, Both)

## Troubleshooting

### If Railway deployment fails:
1. Check Railway → Deployments → Build Logs for errors
2. Verify `requirements.txt` includes all dependencies
3. Verify `runtime.txt` specifies Python version (e.g., `python-3.11.0`)
4. Check that `Procfile` or Railway start command is correct: `gunicorn app:app`
5. Verify environment variables are set correctly (no quotes needed in Railway)

### If SendGrid email fails:
1. Check Railway environment variables: `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL`
2. Verify sender email is verified in SendGrid dashboard
3. Check SendGrid Activity dashboard for error details
4. Look in spam folder
5. Check Railway logs for SendGrid API errors

### If Twilio SMS fails:
1. Check Railway environment variables: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
2. Verify phone number format: +11234567890 (must include +1)
3. Confirm you have trial credit or paid balance in Twilio
4. Check Twilio console logs for error details
5. Check Railway logs for Twilio API errors

### If database errors occur:
1. Verify PostgreSQL is provisioned in Railway project
2. Check Railway logs for database connection errors
3. Verify `DATABASE_URL` environment variable is set (automatic)
4. In Railway → PostgreSQL → Data tab, verify tables exist
5. Redeploy to trigger database initialization

### If CSV import fails:
1. Verify CSV has `email` column (case-sensitive)
2. Phone column is optional but must be formatted correctly
3. Check CSV is properly formatted (comma-separated)
4. Check Railway logs for specific error message
5. Test with `test_contacts.csv` first

### If SMS opt-out webhook doesn't work:
1. Verify Twilio webhook URL is set correctly: `https://your-app-name.up.railway.app/sms-optout`
2. Verify webhook method is POST
3. Check Railway logs when you send STOP - should see webhook hit
4. Verify contact phone number matches in database
5. Test webhook manually: `curl -X POST https://your-app-name.up.railway.app/sms-optout -d "From=+11234567890&Body=STOP"`

### Viewing Railway Logs:
1. Railway dashboard → Your project
2. Click on "Deployments" tab
3. Click on latest deployment
4. View "Deploy Logs" (build time) or "View Logs" (runtime)
5. Use logs to debug API errors, database issues, etc.

### Checking Database Contents:
**Option 1: Railway PostgreSQL Data Tab**
1. Railway → PostgreSQL service → Data tab
2. Run SQL queries directly: `SELECT * FROM customers;`

**Option 2: Connect via psql**
1. Railway → PostgreSQL → Connect
2. Copy connection command
3. Run in terminal to access database

## Phase 1 Complete! 🎉

Once all items are checked, you have:
- ✓ Working email AND SMS marketing platform
- ✓ **Production deployment on Railway.app**
- ✓ **PostgreSQL database in production**
- ✓ CSV import with deduplication (email + phone)
- ✓ Email preview and testing
- ✓ SMS preview and testing
- ✓ Legal-compliant unsubscribe system (email + SMS)
- ✓ Automatic STOP reply handling for SMS via webhook
- ✓ Clean web interface with 6 pages (+ Campaigns!)
- ✓ Dual-channel marketing capabilities
- ✓ **Secure environment variable management**
- ✓ **Auto-deploy on git push**
- ✓ **Complete Campaign Management System:**
  - ✓ Create campaigns with template selection
  - ✓ Edit and delete campaigns
  - ✓ Preview campaigns before sending
  - ✓ Send confirmation with audience targeting
  - ✓ Test mode for safe testing
  - ✓ Live mode for real sends
  - ✓ Image handling (base64 for dev, URLs for prod)
  - ✓ Personalization and unsubscribe links

**Ready for Phase 2:** QR code generation and redemption tracking!

---

## Quick Reference Commands

**View Railway app:**
```
https://your-app-name.up.railway.app
```

**Deploy new version:**
```bash
git add .
git commit -m "Your changes"
git push origin main
# Railway auto-deploys
```

**View logs:**
```bash
# Install Railway CLI: npm install -g @railway/cli
railway login
railway logs
```

**Connect to production database:**
```bash
# From Railway dashboard → PostgreSQL → Connect
# Copy the connection string and run:
psql <connection-string>
SELECT * FROM customers;
\q
```

**Local development (optional):**
```bash
cd "/Users/maxross/Library/Mobile Documents/iCloud~md~obsidian/Documents/Kcdjmaxx Main Vault/MaxxConnect"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from backend.database import init_db; init_db()"
python app.py  # Runs on http://localhost:5001
```

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🚀 QUICK START - When You Return

### Step 1: Check A2P 10DLC Status
1. Go to **Twilio Console** → **Messaging** → **Regulatory Compliance**
2. Look for your A2P campaign status
3. If status = **"Active"** or **"Verified"** → SMS is ready!
4. If still "In Progress" → keep waiting

### Step 2: Test SMS (Once A2P Approved)
```bash
cd "/Users/maxross/Library/Mobile Documents/iCloud~md~obsidian/Documents/Kcdjmaxx Main Vault/MaxxConnect"
source venv/bin/activate
python test_twilio.py +18168383050
```
Check your phone for the test SMS!

### Step 3: Test Email (Already Working)
```bash
cd "/Users/maxross/Library/Mobile Documents/iCloud~md~obsidian/Documents/Kcdjmaxx Main Vault/MaxxConnect"
source venv/bin/activate
python test_sendgrid.py kcdjmaxx@gmail.com
```

### Step 4: Deploy to Railway
Once SMS is working (or skip SMS for now):
1. Sign up at https://railway.app
2. Create new project
3. Connect GitHub repo or deploy directly
4. Add environment variables from your `.env` file
5. Deploy!

---

## 📝 Important Configuration Details

**SendGrid (Email):**
- Sender: deals@fricandfrac.net ✅ Domain Authenticated
- API Key: Configured in `.env`
- Test: SUCCESSFUL ✅

**Twilio (SMS):**
- Phone Number: +18168399958 (Local KC)
- Account SID: [CONFIGURED]
- Verified Caller ID: +18168383050
- A2P Status: ⏳ IN PROGRESS (check Twilio Console)

**Database:**
- Local: SQLite (database.db) - recreated with SMS fields ✅
- Production: PostgreSQL (via Railway) - not deployed yet

**Business Info:**
- Name: Fric & Frac
- Address: 1700 W39th St. Kansas City, MO 64111
