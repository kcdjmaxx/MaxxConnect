# MaxxConnect

A custom email and SMS marketing platform designed for small businesses, featuring campaign management, contact segmentation, and legal-compliant unsubscribe handling.

## Features

### Phase 1 (Complete)
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

### Upcoming Phases
- **Phase 2**: QR code generation, customer segmentation, campaign analytics
- **Phase 3**: iOS redemption app, redemption tracking
- **Phase 4**: Bounce handling, A/B testing, advanced analytics

## Tech Stack

**Backend:**
- Flask 3.0.0 (Python 3.11)
- SQLAlchemy (ORM)
- SQLite (development) / PostgreSQL (production)
- Cryptography (Fernet encryption)

**APIs:**
- SendGrid (email delivery)
- Twilio (SMS delivery)

**Deployment:**
- Railway.app (production hosting)
- Gunicorn (WSGI server)

## Prerequisites

- Python 3.11+
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
SENDGRID_FROM_EMAIL=your-verified-email@domain.com

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

# Database (optional for local development)
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

### 6. Run the Application
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
5. Save as draft or send immediately

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

### Managing Unsubscribes

**Email:**
- Unsubscribe links are automatically included in all emails
- Contacts are immediately unsubscribed when they click the link

**SMS:**
- Reply STOP to any SMS to opt-out
- Twilio webhook automatically processes opt-out requests
- Webhook URL: `https://your-domain.com/sms-optout`

## Deployment to Railway

### 1. Sign Up
Create an account at [railway.app](https://railway.app)

### 2. Create New Project
- Connect your GitHub repository
- Railway auto-detects Flask application

### 3. Add PostgreSQL Database
- Click "+ New" → "Database" → "PostgreSQL"
- Railway automatically sets `DATABASE_URL` environment variable

### 4. Configure Environment Variables
Add all variables from your `.env` file in Railway dashboard → Variables tab

### 5. Deploy
- Push to GitHub: `git push origin main`
- Railway auto-deploys on every push
- Monitor deployment in Deployments tab

### 6. Configure Twilio Webhook
- Go to Twilio Console → Phone Numbers → Active Numbers
- Click your phone number
- Under "Messaging", set webhook URL: `https://your-app.up.railway.app/sms-optout`
- Method: POST
- Save

## Project Structure

```
MaxxConnect/
├── app.py                    # Main Flask application
├── backend/
│   ├── api/                  # API endpoints
│   ├── csv_importer.py       # CSV import logic
│   ├── database.py           # Database models
│   ├── email_service.py      # SendGrid integration
│   ├── sms_service.py        # Twilio integration
│   └── image_handler.py      # Image processing
├── templates/
│   ├── email/                # Email campaign templates
│   └── *.html                # Web UI templates
├── static/                   # CSS, JS, images
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version (Railway)
└── Procfile                  # Railway deployment config
```

## Legal Compliance

### CAN-SPAM (Email)
- ✅ Unsubscribe link in every email
- ✅ Physical mailing address in footer
- ✅ Opt-in timestamps stored
- ✅ Immediate unsubscribe processing

### TCPA (SMS)
- ✅ Explicit opt-in required before sending
- ✅ STOP reply handling via webhook
- ✅ Opt-out instructions in every message
- ✅ SMS opt-in/opt-out timestamps stored

### Data Security
- ✅ Email addresses encrypted (Fernet/AES-128)
- ✅ Phone numbers encrypted
- ✅ Environment variables for sensitive data
- ✅ No credentials in source code

## Development

### Running Tests
```bash
# Test SendGrid email
python test_sendgrid.py your-email@example.com

# Test Twilio SMS
python test_twilio.py +11234567890
```

### Local Development
```bash
source venv/bin/activate
python app.py
# App runs on http://localhost:5001
```

## Environment-Aware Configuration

The application automatically adapts based on environment:

**Development (localhost):**
- Base64-encoded images in emails
- SQLite database
- Localhost URLs

**Production (Railway):**
- External image URLs
- PostgreSQL database
- Railway domain URLs

## Contributing

This is a private project for small business use. For issues or feature requests, please contact the repository owner.

## License

Proprietary - All rights reserved.

## Support

For questions or issues:
- Check `CONFIGURATION.md` for detailed setup guide
- Check `phase01Checklist.md` for deployment checklist
- Review `CLAUDE.md` for technical documentation

## Project Status

**Current Phase**: Phase 1 Complete ✅
- Email campaigns: ✅
- SMS campaigns: ✅
- Contact management: ✅
- Campaign CRUD: ✅
- Legal compliance: ✅

**Next Steps**:
- Deploy to Railway production
- Phase 2: QR codes and analytics
- Phase 3: iOS redemption app

---

**Built for small businesses who need powerful marketing tools without the enterprise price tag.**
