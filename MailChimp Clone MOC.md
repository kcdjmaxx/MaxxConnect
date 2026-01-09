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

- [[MaxxConnect/CLAUDE]] - Comprehensive technical guide for AI assistants
- [[MaxxConnect/intitalPromtReply01]] - Initial project planning and architecture
- [[MaxxConnect/phase01]] - Phase 1 implementation details

## Implementation Guides

- [[MaxxConnect/README]] - Project overview and quick start guide
- [[MaxxConnect/CONFIGURATION]] - Environment configuration (dev/prod)
- [[MaxxConnect/phase01Checklist]] - Setup and testing checklist
- [[MaxxConnect/SMS_INTEGRATION_SUMMARY]] - SMS/Twilio integration documentation
- [[MaxxConnect/RAILWAY_DEPLOYMENT_GUIDE]] - Cloud deployment instructions
- [[MaxxConnect/CAMPAIGN_MANAGEMENT_GUIDE]] - Complete campaign management guide
- [[MaxxConnect/SESSION-SUMMARY]] - Recent development session notes
- [[MaxxConnect/TODO-UNSUBSCRIBE]] - Known issues and fixes

## Phase Specifications

### Phase 2: Campaign Management (Planned)
- [[MaxxConnect/specs/phase-2-campaign-management]] - QR codes, segmentation, queue system

### Phase 3: Public Signup (Planned)
- [[MaxxConnect/specs/phase-3-public-signup]] - Customer acquisition features

## Design Documentation

### Architecture & Overview
- [[MaxxConnect/design/architecture]] - System architecture and component organization
- [[MaxxConnect/design/gaps]] - Design coverage gaps
- [[MaxxConnect/design/traceability]] - Code-to-design traceability map
- [[MaxxConnect/design/traceability-tests]] - Test coverage traceability
- [[MaxxConnect/design/manifest-ui]] - UI component manifest

### CRC Cards (Class Responsibility Collaborator)
**Core Models:**
- [[MaxxConnect/design/crc-Customer]] - Customer data model
- [[MaxxConnect/design/crc-Campaign]] - Campaign model
- [[MaxxConnect/design/crc-QRCode]] - QR code model

**Managers & Services:**
- [[MaxxConnect/design/crc-CampaignManager]] - Campaign CRUD routes
- [[MaxxConnect/design/crc-CampaignAnalytics]] - Analytics service
- [[MaxxConnect/design/crc-SegmentManager]] - Customer segmentation
- [[MaxxConnect/design/crc-QRCodeGenerator]] - QR code generation service

**Queue System:**
- [[MaxxConnect/design/crc-EmailQueueTask]] - Email queue tasks
- [[MaxxConnect/design/crc-SMSQueueTask]] - SMS queue tasks
- [[MaxxConnect/design/crc-CeleryApp]] - Celery task manager
- [[MaxxConnect/design/crc-RateLimiter]] - Rate limiting service

**Utilities:**
- [[MaxxConnect/design/crc-Config]] - Configuration management
- [[MaxxConnect/design/crc-ImageHandler]] - Image processing (base64/external URLs)

### Sequence Diagrams
**Campaign Workflows:**
- [[MaxxConnect/design/seq-campaign-create]] - Campaign creation flow
- [[MaxxConnect/design/seq-campaign-send]] - Campaign sending flow
- [[MaxxConnect/design/seq-campaign-send-qr]] - Campaign with QR codes
- [[MaxxConnect/design/seq-campaign-preview]] - Campaign preview
- [[MaxxConnect/design/seq-campaign-analytics]] - Analytics generation

**Email/SMS Processing:**
- [[MaxxConnect/design/seq-email-process]] - Email sending process
- [[MaxxConnect/design/seq-email-retry]] - Email retry logic
- [[MaxxConnect/design/seq-sms-process]] - SMS sending process
- [[MaxxConnect/design/seq-sms-retry]] - SMS retry logic

**Segmentation & QR:**
- [[MaxxConnect/design/seq-segment-manage]] - Segment management
- [[MaxxConnect/design/seq-segment-filter]] - Segment filtering
- [[MaxxConnect/design/seq-qr-generate]] - QR code generation

### UI Specifications
- [[MaxxConnect/design/ui-campaign-list]] - Campaign list page
- [[MaxxConnect/design/ui-campaign-create]] - Campaign creation form
- [[MaxxConnect/design/ui-campaign-preview]] - Campaign preview page
- [[MaxxConnect/design/ui-campaign-send-confirm]] - Send confirmation page
- [[MaxxConnect/design/ui-campaign-analytics]] - Analytics dashboard
- [[MaxxConnect/design/ui-segment-list]] - Segment list page
- [[MaxxConnect/design/ui-qr-display]] - QR code display

### Test Designs
- [[MaxxConnect/design/test-Campaign]] - Campaign functionality tests
- [[MaxxConnect/design/test-Analytics]] - Analytics tests
- [[MaxxConnect/design/test-Segmentation]] - Segmentation tests
- [[MaxxConnect/design/test-QRCode]] - QR code generation tests
- [[MaxxConnect/design/test-Queue]] - Queue system tests
- [[MaxxConnect/design/test-UI]] - UI component tests

### Implementation Notes
- [[MaxxConnect/design/notes-qr-toggle-implementation]] - QR toggle feature notes

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
cd MaxxConnect
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
MaxxConnect/
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

- [[MaxxConnect/test_contacts.csv]] - Sample CSV with phone numbers for testing

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
