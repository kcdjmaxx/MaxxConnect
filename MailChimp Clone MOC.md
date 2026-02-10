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

**Status:** Phase 3 Complete + Visual Template Designer, Deployed to Production

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

### Phase 2: QR Code & Queue System (COMPLETE)
- [[MaxxConnect/specs/phase-2-campaign-management]] - QR codes, segmentation, queue system

### Phase 3: Redemption System (COMPLETE)
- [[MaxxConnect/specs/phase-3-public-signup]] - Customer acquisition features

### Visual Template Designer (COMPLETE)
- [[MaxxConnect/specs/spec-template-designer]] - GrapesJS drag-and-drop editor
- [[MaxxConnect/TEMPLATE-DESIGNER-DEBUG]] - Debug log and fix history (9 fixes)

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
- [[MaxxConnect/design/crc-EmailDelivery]] - Individual email delivery tracking
- [[MaxxConnect/design/crc-Redemption]] - Redemption event tracking

**Managers & Services:**
- [[MaxxConnect/design/crc-CampaignManager]] - Campaign CRUD routes
- [[MaxxConnect/design/crc-CampaignAnalytics]] - Analytics service
- [[MaxxConnect/design/crc-SegmentManager]] - Customer segmentation
- [[MaxxConnect/design/crc-QRCodeGenerator]] - QR code generation service
- [[MaxxConnect/design/crc-RedemptionService]] - QR validation and redemption
- [[MaxxConnect/design/crc-EmailService]] - Email delivery with CID attachments
- [[MaxxConnect/design/crc-TemplateProcessor]] - Template validation and auto-injection

**Queue System:**
- [[MaxxConnect/design/crc-EmailQueueTask]] - Email queue tasks
- [[MaxxConnect/design/crc-SMSQueueTask]] - SMS queue tasks
- [[MaxxConnect/design/crc-CeleryApp]] - Celery task manager
- [[MaxxConnect/design/crc-RateLimiter]] - Rate limiting service

**Visual Template Designer:**
- [[MaxxConnect/design/crc-GrapesDesigner]] - GrapesJS editor page
- [[MaxxConnect/design/crc-DesignerAPI]] - Designer save/load API routes
- [[MaxxConnect/design/crc-CustomBlocks]] - Custom MaxxConnect blocks

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
- [[MaxxConnect/design/seq-qr-redemption]] - QR redemption flow

**Template System:**
- [[MaxxConnect/design/seq-template-import]] - Template import flow
- [[MaxxConnect/design/seq-designer-save]] - Designer save flow
- [[MaxxConnect/design/seq-designer-load]] - Designer load flow

### UI Specifications
- [[MaxxConnect/design/ui-campaign-list]] - Campaign list page
- [[MaxxConnect/design/ui-campaign-create]] - Campaign creation form
- [[MaxxConnect/design/ui-campaign-preview]] - Campaign preview page
- [[MaxxConnect/design/ui-campaign-send-confirm]] - Send confirmation page
- [[MaxxConnect/design/ui-campaign-analytics]] - Analytics dashboard
- [[MaxxConnect/design/ui-staff-scanner]] - Staff QR scanner PWA
- [[MaxxConnect/design/ui-redeem-result]] - Redemption result page
- [[MaxxConnect/design/ui-template-list]] - Template list page
- [[MaxxConnect/design/ui-template-import]] - Template import wizard
- [[MaxxConnect/design/ui-template-edit]] - Template code editor
- [[MaxxConnect/design/ui-template-designer]] - GrapesJS visual designer
- [[MaxxConnect/design/ui-template-create-choice]] - Template create (visual/code choice)
- [[MaxxConnect/design/ui-segment-list]] - Segment list page (planned)
- [[MaxxConnect/design/ui-qr-display]] - QR code display (planned)

### Test Designs
- [[MaxxConnect/design/test-Campaign]] - Campaign functionality tests
- [[MaxxConnect/design/test-Analytics]] - Analytics tests
- [[MaxxConnect/design/test-Segmentation]] - Segmentation tests
- [[MaxxConnect/design/test-QRCode]] - QR code generation tests
- [[MaxxConnect/design/test-Queue]] - Queue system tests
- [[MaxxConnect/design/test-UI]] - UI component tests
- [[MaxxConnect/design/test-Designer]] - Visual template designer tests

### Implementation Notes
- [[MaxxConnect/design/notes-qr-toggle-implementation]] - QR toggle feature notes

## Issue Tracking & Development Notes

- [[MaxxConnect/QRcodeIssues]] - QR code implementation log: Base64 → CID approach, Gmail compatibility, SendGrid upgrade
- [[MaxxConnect/CampaignDeleteIssues]] - Foreign key constraint bug when deleting campaigns with QR codes
- [[MaxxConnect/templateEditorProcess]] - Template Management System (Phase 2.5) documentation

## Technology Stack

**Backend:**
- Python 3.11 + Flask 3.0.0
- SQLAlchemy 2.0.23 (ORM)
- Celery + Redis (async queue with rate limiting)
- SQLite (dev) / PostgreSQL (production)

**Frontend:**
- GrapesJS v0.21.13 (visual email template editor)
- jsQR (QR code scanning for staff PWA)
- Jinja2 (HTML templates)

**APIs:**
- SendGrid (email delivery, Essentials plan: 50,000/month)
- Twilio (SMS delivery)

**Security:**
- Fernet AES-128 encryption for all PII (emails, phone numbers)
- HTTP Basic Auth (admin) + cookie auth (staff scanner, 90-day expiry)

**Deployment:**
- Railway.app (Web + Worker services)
- Gunicorn (WSGI server)
- Railway Volume for persistent uploads

## Key Features

### Dashboard (Phase 1)
- 5 stat cards: Total Contacts, Email Subscribed/Unsubscribed, SMS Subscribed/Unsubscribed

### Contact Management (Phase 1)
- CSV import with automatic deduplication (Simple + Square POS formats)
- Phone number auto-formatting (E.164)
- Email validation
- Segment/tag support

### Email System (Phase 1)
- SendGrid API integration (Essentials plan: 50,000 emails/month)
- HTML email templates (Jinja2)
- Preview interface
- Test email sending
- Secure unsubscribe links
- CAN-SPAM compliant

### SMS System (Phase 1)
- Twilio API integration
- 160 character limit enforcement
- Automatic opt-out footer
- SMS preview interface
- Webhook for STOP replies (`/sms-optout`)
- TCPA compliant

### Async Queue System (Phase 2)
- Celery + Redis background processing
- Rate limiting (100 email/min, 10 SMS/min configurable)
- Progress tracking UI with live polling
- Campaign resume (sends only to unsent customers)
- Individual email delivery tracking

### QR Code System (Phase 2)
- Unique token generation per customer/campaign
- CID (Content-ID) embedding for Gmail compatibility
- QR code display in email templates

### QR Redemption System (Phase 3)
- Staff scanner PWA at `/staff/redeem`
- Camera-based QR scanning (jsQR library)
- Manual token entry fallback
- Audio feedback (Web Audio API tones)
- Voice feedback (Web Speech API)
- iOS home screen support (PWA meta tags, 90-day auth)
- Redemption analytics dashboard

### Template Management System
- Template import wizard (upload HTML, auto-inject placeholders)
- Template validation (required CAN-SPAM elements)
- Template editor (code view with live preview)
- Template list with validation status badges

### Visual Template Designer (GrapesJS)
- Drag-and-drop editor with newsletter preset
- Custom MaxxConnect blocks (Compliance Footer, QR Section, Greeting)
- Image upload via asset manager to Railway volume
- Save/load as JSON sidecar + inlined HTML
- Compliance validation on save
- Desktop/Tablet/Mobile preview toggle
- Template duplication
- Campaign dropdown includes user-created templates

## Database Schema

**Customer Model:**
- Email (encrypted), phone (encrypted), name
- Email subscription tracking (opted_in_date, unsubscribed_date)
- SMS subscription tracking (sms_opted_in_date, sms_unsubscribed_date)
- Segments/tags

**Campaign Model:**
- Name, subject, html_content
- Status (draft/sent/sending), has_qr_code flag
- Sent date, created date

**QRCode Model:**
- unique_token (format: `{campaign_id}-{customer_id}-{hash}`)
- usage_count, expiration_date
- FK: campaign_id, customer_id

**EmailDelivery Model:**
- Tracks individual email sends per customer/campaign
- Status (pending/sent/failed), error tracking
- FK: campaign_id, customer_id

**CampaignSend Model:**
- Tracks batch send progress
- Total, sent, failed counts
- FK: campaign_id

**Redemption Model:**
- Timestamp, redeemed_by (staff identifier)
- redemption_method (scan/manual)
- device_info, ip_address (fraud detection)
- FK: qr_code_id, customer_id, campaign_id

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

### Phase 1 - Foundation (COMPLETE)
- Email/SMS API integration (SendGrid, Twilio)
- CSV import with deduplication (Simple + Square formats)
- Email/SMS preview and testing
- Unsubscribe/opt-out management
- Campaign CRUD management
- Railway.app deployment

### Phase 2 - QR Code & Queue (COMPLETE)
- Async email/SMS queue with Celery + Redis
- Rate limiting (100 email/min, 10 SMS/min)
- Progress tracking UI with live polling
- QR code generation with unique tokens
- QR code CID embedding for Gmail compatibility
- Template management system
- Customer segmentation/tagging (partial)

### Phase 3 - Redemption System (COMPLETE)
- Staff QR scanner web app (PWA)
- Redemption validation API
- Usage tracking (prevent multi-redemption)
- Redemption analytics dashboard

### Visual Template Designer (COMPLETE)
- GrapesJS drag-and-drop editor
- Custom MaxxConnect blocks
- Template duplication
- Campaign integration with user templates
- Cascade campaign deletion

### Phase 4 - Advanced Features (PLANNED)
- Bounce handling automation
- Redemption report exports
- A/B testing infrastructure
- Performance optimization
- Image gallery for uploaded images

## Code Structure

```
MaxxConnect/
├── app.py                          # Flask routes (campaigns, templates, designer, redemption, analytics)
├── backend/
│   ├── database.py                 # SQLAlchemy setup
│   ├── models.py                   # Customer, Campaign, QRCode, EmailDelivery, CampaignSend, Redemption
│   ├── config.py                   # Environment-aware configuration
│   ├── email_service.py            # SendGrid with CID attachment support
│   ├── sms_service.py              # Twilio SMS
│   ├── csv_importer.py             # CSV import (Simple + Square formats)
│   ├── encryption.py               # Fernet AES-128 for PII
│   ├── image_handler.py            # Base64 (dev) / External URL (prod) images
│   ├── services/
│   │   ├── qr_generator.py         # QR code generation
│   │   ├── rate_limiter.py         # Rate limiting service
│   │   ├── redemption_service.py   # QR validation and redemption
│   │   └── template_processor.py   # Template validation and auto-injection
│   └── tasks/
│       ├── celery_app.py           # Celery configuration
│       ├── email_task.py           # Async email sending with delivery tracking
│       └── sms_task.py             # Async SMS sending
├── templates/                      # Jinja2 templates (pages + email templates)
│   ├── email/                      # Bundled email templates
│   └── template_designer.html      # GrapesJS standalone page
├── uploads/                        # Railway volume mount
│   ├── images/                     # User-uploaded template images
│   └── templates/                  # User-created templates (HTML + .grapes.json sidecars)
├── static/
│   ├── style.css
│   └── test_grapes.html            # Standalone GrapesJS verification page
├── design/                         # Mini-spec design artifacts
├── specs/                          # Human-readable specifications
└── refs/                           # Reference documentation
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
- Auto-deploy on push to `main`
- Two services: Web (gunicorn) + Worker (Celery)
- PostgreSQL database
- Redis for Celery task queue
- Volume mount at `/app/uploads/` (persists images + user templates)
- HTTPS included
- Environment variable management

## Next Steps (Phase 4)

1. Bounce handling automation (SendGrid Suppressions API)
2. Redemption report exports (CSV/Excel)
3. A/B testing infrastructure
4. Image gallery for uploaded images
5. Full customer segmentation UI
6. Automated test coverage
