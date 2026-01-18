---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - type/documentation
  - status/active
  - tool/flask
  - tool/sendgrid
  - tool/twilio
---

# MaxxConnect

A custom email and SMS marketing platform designed for small businesses, featuring campaign management, QR code generation, deal redemption tracking, and legal-compliant messaging.

## Features

### Phase 1: Foundation (Complete)
- **Email Campaigns**: Send HTML email campaigns via SendGrid with custom templates
- **SMS Campaigns**: Send SMS messages via Twilio with automatic opt-out handling
- **Contact Management**: CSV import with automatic deduplication and phone number normalization
- **Campaign System**: Full CRUD operations for campaigns with template selection
- **Preview & Testing**: Preview emails/SMS before sending, test mode for safe testing
- **Legal Compliance**:
  - CAN-SPAM compliant (unsubscribe links, physical address)
  - TCPA compliant (SMS opt-in tracking, STOP reply handling)
  - Data encryption for email addresses and phone numbers
- **Multi-format CSV Import**: Supports both simple CSV and Square POS export formats

### Phase 2: QR Code Generation (Complete)
- **Async Queue**: Celery + Redis for background email/SMS processing
- **Rate Limiting**: 100 emails/min, 10 SMS/min to avoid spam flags
- **Progress Tracking**: Live UI updates during campaign sends
- **QR Code Generation**: Unique codes per customer with expiration dates
- **Gmail Compatibility**: CID-embedded QR images for reliable display

### Phase 3: Redemption System (Complete)
- **Staff Scanner PWA**: Mobile-friendly QR scanner that works on iOS home screen
  - Camera-based scanning with jsQR
  - Manual token entry fallback
  - Audio feedback (success/error tones)
  - Voice announcements
  - Full-page color feedback (green=valid, red=invalid)
- **Deal Descriptions**: Staff see what deal to honor when scanning
- **Redemption Tracking**: Prevent multi-use, track who redeemed when
- **Analytics Dashboard**: Redemption rates, hourly distribution, per-campaign stats

### Phase 4: Advanced Features (Planned)
- Bounce handling automation
- Redemption report exports
- A/B testing infrastructure

## Tech Stack

**Backend:**
- Flask 3.0.0 (Python 3.11)
- SQLAlchemy (ORM)
- Celery + Redis (async task queue)
- SQLite (development) / PostgreSQL (production)
- Cryptography (Fernet encryption)

**APIs:**
- SendGrid (email delivery)
- Twilio (SMS delivery)

**Frontend:**
- Jinja2 templates
- Vanilla JavaScript
- PWA support for staff scanner

**Deployment:**
- Railway.app (production hosting)
- Gunicorn (WSGI server)

## Prerequisites

- Python 3.11+
- Redis (for Celery task queue)
- SendGrid account with verified domain
- Twilio account with A2P 10DLC registration
- PostgreSQL (production) or SQLite (development)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kcdjmaxx/MaxxConnect.git
cd MaxxConnect
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=your-verified-email@domain.com

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Business Information
BUSINESS_NAME=Your Business Name
BUSINESS_ADDRESS=123 Main St, City, State 12345

# Security
ENCRYPTION_KEY=your_fernet_encryption_key
SECRET_KEY=your_flask_secret_key

# Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_admin_password
STAFF_USERNAME=staff
STAFF_PASSWORD=your_secure_staff_password

# Redis (required for async queue)
REDIS_URL=redis://localhost:6379/0

# Database (optional for local development - defaults to SQLite)
# DATABASE_URL=postgresql://user:pass@localhost/dbname
```

**Generate Encryption Key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 5. Initialize Database
```bash
python -c "from backend.database import init_db; init_db()"
```

### 6. Start Redis (for async queue)
```bash
redis-server
```

### 7. Start Celery Worker (separate terminal)
```bash
celery -A backend.tasks.celery_app worker --loglevel=info
```

### 8. Run the Application
```bash
python app.py
```

Visit `http://localhost:5001` in your browser.

## Usage

### Importing Contacts

1. Navigate to **Import CSV** page
2. Upload a CSV file with columns: `email`, `name`, `phone` (optional)
3. System automatically:
   - Validates email addresses
   - Normalizes phone numbers to E.164 format
   - Deduplicates existing contacts
   - Tracks opt-in status

**Supported CSV Formats:**
- Simple: `email,name,phone`
- Square POS: `Email Address,First Name,Last Name,Phone Number`

### Creating Campaigns

1. Go to **Campaigns** page
2. Click **Create New Campaign**
3. Enter campaign name and subject
4. Select an email template from `templates/email/`
5. **Enable QR Code** (optional):
   - Check "Include QR Code for redemption"
   - Enter a **Deal Description** (e.g., "Buy one burger, get one FREE")
   - Staff will see this when scanning
6. Save as draft or send immediately

### Sending Campaigns

1. Click **Send** button on any draft campaign
2. Select target audience:
   - All Subscribers
   - Email Only
   - SMS Only
   - Email + SMS
3. Choose mode:
   - **Test Mode**: Send to a single test email (safe)
   - **Live Mode**: Send to all selected subscribers
4. Confirm and send
5. Monitor progress with live updates

### Staff QR Scanner

**Setup (one-time):**
1. Open `/staff/redeem` on staff member's phone (Safari on iOS)
2. Login with staff credentials
3. Tap Share → "Add to Home Screen"
4. App stays logged in for 90 days

**Using the Scanner:**
1. Open scanner from home screen
2. Tap "Start Scanner" to activate camera
3. Point at customer's QR code
4. Screen turns **green** = valid, **red** = invalid
5. View deal description and customer info
6. Tap "REDEEM NOW" to complete

### Redemption Analytics

View at `/analytics/redemptions`:
- Overall redemption rates
- Per-campaign breakdown
- Hourly distribution (when do customers redeem?)
- Recent redemptions table

### Managing Unsubscribes

**Email:**
- Unsubscribe links are automatically included in all emails
- Contacts are immediately unsubscribed when they click the link

**SMS:**
- Reply STOP to any SMS to opt-out
- Twilio webhook automatically processes opt-out requests
- Webhook URL: `https://your-domain.com/sms-optout`

## Deployment to Railway

### 1. Create Project
- Sign up at [railway.app](https://railway.app)
- Connect your GitHub repository

### 2. Add PostgreSQL Database
- Click "+ New" → "Database" → "PostgreSQL"
- `DATABASE_URL` is automatically set

### 3. Add Redis
- Click "+ New" → "Database" → "Redis"
- `REDIS_URL` is automatically set

### 4. Configure Web Service
Environment variables needed:
```
SENDGRID_API_KEY=...
SENDER_EMAIL=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
BUSINESS_NAME=...
BUSINESS_ADDRESS=...
ENCRYPTION_KEY=...
SECRET_KEY=...
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
STAFF_USERNAME=...
STAFF_PASSWORD=...
```

### 5. Add Celery Worker Service
- Click "+ New" → "Empty Service"
- Connect same GitHub repo
- Set start command: `celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=2`
- Copy these env vars from web service:
  - `DATABASE_URL`
  - `REDIS_URL`
  - `ENCRYPTION_KEY`
  - `SENDGRID_API_KEY`
  - `SENDER_EMAIL`
  - `BUSINESS_NAME`

### 6. Configure Twilio Webhook
- Go to Twilio Console → Phone Numbers → Your Number
- Under "Messaging", set webhook URL: `https://your-app.up.railway.app/sms-optout`
- Method: POST

### 7. Deploy
- Push to GitHub: `git push origin main`
- Railway auto-deploys on every push

## Project Structure

```
MaxxConnect/
├── app.py                    # Main Flask application
├── backend/
│   ├── config.py             # Environment configuration
│   ├── csv_importer.py       # CSV import logic
│   ├── database.py           # Database connection
│   ├── email_service.py      # SendGrid integration
│   ├── encryption.py         # Fernet encryption
│   ├── image_handler.py      # Image processing
│   ├── models.py             # SQLAlchemy models
│   ├── qr_generator.py       # QR code generation
│   ├── sms_service.py        # Twilio integration
│   ├── tasks.py              # Celery async tasks
│   └── services/
│       └── redemption_service.py  # QR validation/redemption
├── templates/
│   ├── email/                # Email campaign templates
│   ├── staff_redeem.html     # Staff scanner PWA
│   └── *.html                # Web UI templates
├── static/                   # CSS, JS, images
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version
└── Procfile                  # Railway deployment config
```

## Authentication

**Two auth levels:**

| Role | Username Env Var | Access |
|------|------------------|--------|
| Admin | `ADMIN_USERNAME` | Full dashboard + scanner |
| Staff | `STAFF_USERNAME` | Scanner only |

Staff auth uses 90-day sliding cookie (refreshes on each use).

## Legal Compliance

### CAN-SPAM (Email)
- Unsubscribe link in every email
- Physical mailing address in footer
- Opt-in timestamps stored
- Immediate unsubscribe processing

### TCPA (SMS)
- Explicit opt-in required before sending
- STOP reply handling via webhook
- Opt-out instructions in every message
- SMS opt-in/opt-out timestamps stored

### Data Security
- Email addresses encrypted (Fernet/AES-128)
- Phone numbers encrypted
- Environment variables for sensitive data
- No credentials in source code

## Development

### Running Locally
```bash
source venv/bin/activate
redis-server &                    # Start Redis
celery -A backend.tasks.celery_app worker &  # Start worker
python app.py                     # Start web app
```

### Environment Detection
The app automatically adapts:

| Setting | Development | Production |
|---------|-------------|------------|
| Images | Base64 embedded | External URLs |
| Database | SQLite | PostgreSQL |
| URLs | localhost:5001 | Railway domain |

## Support

- `CONFIGURATION.md` - Detailed setup guide
- `CLAUDE.md` - Technical documentation
- Issues: Contact repository owner

## License

Proprietary - All rights reserved.

---

**Built for small businesses who need powerful marketing tools without the enterprise price tag.**
