---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - type/moc
  - status/active
---

# MailChimp Clone MOC

Map of Content for the email/SMS marketing platform - a production-ready system for small business marketing campaigns with QR code redemption tracking.

## Project Overview

Custom email and SMS marketing platform deployed on Railway.app. Supports CSV contact imports, campaign management, and QR code-based deal redemption tracking.

**Status:** Phase 1 Complete, Deployed to Production

## Core Documentation

- [[mailChimpClone/CLAUDE]] - Comprehensive technical guide for AI assistants
- [[mailChimpClone/intitalPromtReply01]] - Initial project planning and architecture
- [[mailChimpClone/phase01]] - Phase 1 implementation details

## Implementation Guides

- [[mailChimpClone/phase01Checklist]] - Setup and testing checklist
- [[mailChimpClone/SMS_INTEGRATION_SUMMARY]] - SMS/Twilio integration documentation
- [[mailChimpClone/RAILWAY_DEPLOYMENT_GUIDE]] - Cloud deployment instructions

## Technology Stack

**Backend:**
- Python 3.11 + Flask 3.0.0
- SQLAlchemy 2.0.23 (ORM)
- SQLite (dev) / PostgreSQL (production)

**APIs:**
- SendGrid (email delivery)
- Twilio (SMS delivery)

**Security:**
- Fernet AES-128 encryption for all PII (emails, phone numbers)

**Deployment:**
- Railway.app (cloud hosting)
- Gunicorn (WSGI server)

## Key Features (Phase 1 - COMPLETE)

### Dashboard
- 5 stat cards: Total Contacts, Email Subscribed/Unsubscribed, SMS Subscribed/Unsubscribed

### Contact Management
- CSV import with automatic deduplication
- Phone number auto-formatting (E.164)
- Email validation
- Segment/tag support

### Email System
- SendGrid API integration
- HTML email templates (Jinja2)
- Preview interface
- Test email sending
- Secure unsubscribe links
- CAN-SPAM compliant

### SMS System
- Twilio API integration
- 160 character limit enforcement
- Automatic opt-out footer
- SMS preview interface
- Webhook for STOP replies (`/sms-optout`)
- TCPA compliant

## Database Schema

**Customer Model:**
- Email (encrypted), phone (encrypted), name
- Email subscription tracking (opted_in_date, unsubscribed_date)
- SMS subscription tracking (sms_opted_in_date, sms_unsubscribed_date)
- Segments/tags

**Campaign Model:**
- Name, subject, html_content
- Status (draft/sent/sending)
- Sent date, created date

## Development Commands

```bash
# Setup
cd mailChimpClone
pip install -r requirements.txt
python -c "from backend.database import init_db; init_db()"

# Development
python app.py  # http://localhost:5001

# Production
gunicorn app:app
```

## Legal Compliance

**CAN-SPAM (Email):**
- Unsubscribe link in every email
- Physical mailing address in footer
- Opt-in timestamps stored
- Immediate unsubscribe processing

**TCPA (SMS):**
- Explicit opt-in required
- STOP reply handling
- Opt-out instructions in every message
- SMS opt-in timestamps stored
- Quiet hours respected (9 AM - 8 PM recommended)

## Project Phases

### Phase 1 (COMPLETE)
- Email/SMS API integration
- CSV import with deduplication
- Email/SMS preview and testing
- Unsubscribe/opt-out management
- Railway.app deployment

### Phase 2 (PLANNED)
- QR code generation with unique tokens
- Customer segmentation/tagging
- Email queue with rate limiting
- Campaign tracking

### Phase 3 (PLANNED)
- iOS QR scanner app
- Redemption validation API
- Usage tracking (prevent multi-redemption)
- Analytics dashboard

### Phase 4 (PLANNED)
- Bounce handling automation
- Redemption report exports
- A/B testing infrastructure
- Performance optimization

## Code Structure

```
mailChimpClone/
├── app.py (327 LOC)
├── backend/
│   ├── database.py
│   ├── models.py
│   ├── email_service.py
│   ├── sms_service.py
│   ├── csv_importer.py
│   └── encryption.py
├── templates/ (Jinja2)
└── static/style.css
```

## Configuration

Required `.env` variables:
- `SENDGRID_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `BUSINESS_NAME`
- `BUSINESS_ADDRESS`
- `ENCRYPTION_KEY`

## Testing Data

- [[mailChimpClone/test_contacts.csv]] - Sample CSV with phone numbers for testing

## Cross-References

**Related Projects:**
- [[Fric & Frac Marketing MOC]] - Primary customer for this platform

**Key Concepts:**
- Email deliverability
- SMS compliance
- PII encryption
- Marketing automation
- QR code redemption systems

## Production Deployment

**Live Environment:** Railway.app
- Auto-deploy from GitHub
- PostgreSQL database (500MB free tier)
- HTTPS included
- Environment variable management
- Automatic restart policies

## Next Steps

1. Implement Phase 2: QR code generation
2. Build customer segmentation UI
3. Create email queue system with rate limiting
4. Design iOS scanner app (Phase 3)
