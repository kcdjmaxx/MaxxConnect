---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - tool/flask
  - status/active
  - type/project-planning
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is MaxxConnect, a custom email and SMS marketing platform designed for small business use, deployed on Railway.app. The system sends promotional emails and SMS messages with unique QR codes for deal redemption tracking.

**Environment-Aware Configuration:**
- **Development**: Base64 images, SQLite database, localhost URLs
- **Production**: External image URLs, PostgreSQL, Railway URLs
- See `CONFIGURATION.md` for complete setup guide

## Architecture

The system consists of three main components:

1. **Flask Web Application** - Single unified app with HTML/CSS interface for campaign creation, CSV contact imports, analytics, email/SMS preview
2. **Flask REST API** - API endpoints for iOS redemption app, unsubscribe/opt-out handling
3. **iOS Scanner App** - QR code scanning for deal redemption validation

### Data Flow
```
Flask Web UI → Database → Email/SMS Services (SendGrid/Twilio)
                   ↓
              QR Codes → iOS Scanner → API Validation → Redemption Tracking
```

### Railway Deployment (Production)

Two services from the same repo:

**Web Service:**
- Start command: `gunicorn app:app` (from Procfile)
- Connects to: PostgreSQL, Redis

**Worker Service:**
- Start command: `celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=2`
- Required env vars (copy from web): `DATABASE_URL`, `REDIS_URL`, `ENCRYPTION_KEY`, `SENDGRID_API_KEY`, `SENDER_EMAIL`, `BUSINESS_NAME`

**Railway Volume (for uploaded images):**
- Mount path: `/app/uploads/images`
- Purpose: Persist user-uploaded template images across deploys
- Setup: Railway Dashboard → Web Service → Settings → Volumes → Add Volume

## Database Schema

Core entities to track:
- **Customers**:
  - email, phone (E.164 format), name
  - Email: subscription_status, opted_in_timestamp
  - SMS: sms_subscribed, sms_opted_in_date, sms_unsubscribed_date
  - segments/tags (comma-separated)
- **Campaigns**: subject, content, sent_date, a_b_test_variant, status
- **QR Codes**: unique_token (format: `{campaign_id}-{customer_id}-{hash}`), usage_count, expiration_date
- **Redemptions**: timestamp, qr_code_id, customer_id

Start with SQLite for development, PostgreSQL for production.

## Tech Stack

**Backend:**
- Flask (unified web app + REST API)
- SQLAlchemy (ORM)
- Jinja2 (HTML templates)
- Celery + Redis (async email/SMS queue with rate limiting)

**Email:**
- SendGrid (email delivery API)
- python-qrcode (QR code generation)
- Jinja2 (HTML email templates)

**SMS:**
- Twilio (SMS delivery API)
- Automatic STOP/opt-out handling
- 160-character limit enforcement

**iOS:**
- Swift + AVFoundation (QR scanning)
- URLSession (API communication)

**Database:**
- SQLite (development)
- PostgreSQL (production)

## Email Template System

HTML email templates use Jinja2 with these required placeholders:
- `{{ customer_name }}` - Personalization
- `{{ qr_code_base64 }}` - Base64-encoded QR image
- `{{ unsubscribe_link }}` - Legal requirement (CAN-SPAM)
- Physical mailing address in footer (legal requirement)

QR code tokens must be cryptographically secure with format: `{campaign_id}-{customer_id}-{random_hash}`

## SMS System

SMS messages via Twilio with these requirements:
- 160 character limit for single SMS
- Automatic opt-out footer: "Reply STOP to unsubscribe. - {Business Name}"
- Phone numbers stored in E.164 format (+1234567890)
- Format validation and normalization on import
- Webhook endpoint `/sms-optout` for Twilio STOP replies

## Campaign Management System

**Overview:**
Complete CRUD system for email campaigns with template selection, audience targeting, and test mode.

**Campaign Workflow:**
1. **Create Campaign** (`/campaign/new`)
   - Select from available email templates in `templates/email/`
   - Templates automatically discovered and listed
   - Enter campaign name and subject line
   - Preview or save as draft

2. **Edit Campaign** (`/campaign/edit/<id>`)
   - Click campaign name in campaigns list
   - Update name, subject, or template
   - Re-renders HTML if template changed
   - Preview changes before saving

3. **Send Campaign** (`/campaign/send-confirm/<id>`)
   - Click Send button → Opens confirmation page
   - Select target audience:
     - All Subscribers
     - Email Only
     - SMS Only (future)
     - Email + SMS (future)
   - **Test Mode Option:**
     - Checkbox to enable test mode
     - Send to single test email address
     - Orange button: "📧 Send Test Email Only"
     - Does NOT send to real subscribers
   - **Live Mode:**
     - Green button: "📧 Send Campaign"
     - Sends to selected audience
     - Warning confirmation required
   - Personalization:
     - `{{ customer_name }}` replaced with actual names
     - `{{ unsubscribe_link }}` with secure token
   - Images handled based on environment:
     - Development: Base64 embedded
     - Production: External URLs

4. **Delete Campaign** (`/campaign/delete/<id>`)
   - Click trash icon (🗑️)
   - Confirmation dialog required
   - Permanently removes campaign

**Routes:**
- `GET /campaigns` - List all campaigns
- `GET /campaign/new` - Create campaign form
- `POST /campaign/new` - Save new campaign
- `GET /campaign/edit/<id>` - Edit campaign form
- `POST /campaign/edit/<id>` - Update campaign
- `GET /campaign/preview/<id>` - Preview campaign HTML
- `GET /campaign/send-confirm/<id>` - Send confirmation page
- `POST /campaign/send/<id>` - Execute send (with audience/test mode)
- `POST /campaign/delete/<id>` - Delete campaign

**Template System:**
- Email templates stored in `templates/email/`
- Auto-discovered by scanning directory
- Support Jinja2 variables:
  - `{{ customer_name }}` - Personalization
  - `{{ logo_base64 }}` or `{{ logo_url }}` - Logo image
  - `{{ hero_image_base64 }}` or `{{ hero_image_url }}` - Hero banner
  - `{{ qr_code_base64 }}` - QR code (future)
  - `{{ unsubscribe_link }}` - Required unsubscribe link
- Image handling:
  - Development: Images converted to base64 via ImageHandler
  - Production: External URLs to Railway static files

## QR Code Redemption System

**Overview:**
Complete system for staff to validate and redeem customer QR codes via mobile-friendly web interface.

**Staff Scanner Interface** (`/staff/redeem`)
- Mobile-optimized PWA (can be added to iOS home screen)
- Camera-based QR scanning using jsQR library
- Manual token entry fallback
- Audio feedback: ascending tones for success, descending for errors
- Voice feedback via Web Speech API ("Valid code for [name]", "Success!")
- Large VALID (green) / INVALID (red) visual display
- Shows customer name, campaign info before redemption
- "REDEEM NOW" confirmation button

**Adding to iOS Home Screen:**
1. Open `/staff/redeem` in Safari
2. Login with staff credentials (first time only)
3. Tap Share button → "Add to Home Screen"
4. App launches in standalone mode, stays logged in for 90 days

**Staff Authentication:**
- Set `STAFF_USERNAME` and `STAFF_PASSWORD` env vars for scanner-only access
- Or use `ADMIN_USERNAME`/`ADMIN_PASSWORD` for full access
- Cookie-based auth with 90-day sliding expiration (refreshes on each use)

**Redemption Flow:**
```
Customer shows QR → Staff scans → Validate → Show info → Staff confirms → Redeem
```

**Routes:**
- `GET /redeem/<token>` - Public landing page (customer sees validity)
- `GET /staff/redeem` - Staff scanner interface (requires auth)
- `POST /api/redeem/<token>` - Perform redemption (requires auth)
- `GET /api/validate/<token>` - Validate without redeeming (requires auth)
- `GET /analytics/redemptions` - Redemption analytics dashboard (requires auth)

**Database Models:**
- `Redemption` - Tracks each redemption event with:
  - qr_code_id, customer_id, campaign_id (foreign keys)
  - redeemed_at (timestamp)
  - redeemed_by (staff identifier)
  - redemption_method ('scan' or 'manual')
  - device_info, ip_address (fraud detection)

**Analytics Dashboard** (`/analytics/redemptions`)
- Overall stats: total codes, redeemed, redemption rate
- Per-campaign breakdown with rates
- Hourly distribution chart (last 30 days)
- Recent redemptions table

## Critical Legal Requirements

**Email:**
- Unsubscribe link (functional, immediate processing)
- Physical mailing address in footer
- Store opt-in timestamps for all contacts
- Honor unsubscribe requests immediately

**SMS (TCPA Compliance):**
- Explicit opt-in required before sending
- Must honor STOP replies immediately
- Include opt-out instructions in every message
- Respect quiet hours (9 AM - 8 PM local time recommended)
- Store SMS opt-in timestamps

## CSV Import System

The system supports two CSV formats for contact imports:

**Simple Format:**
```csv
email,name,phone
john@example.com,John Doe,+11234567890
jane@example.com,Jane Smith,5551234567
```

**Square Export Format (supported as of Dec 2024):**
```csv
Email Address,First Name,Last Name,Phone Number,...
john@example.com,John,Doe,+11234567890,...
```

**Import Features:**
- Automatic column mapping (Square → simple format)
- Name combining (`First Name` + `Last Name` → `name`)
- Phone number normalization to E.164 format
- Email validation and deduplication
- Empty/invalid email filtering
- Segment tagging during import
- Update existing contacts or create new ones

**Implementation:** `backend/csv_importer.py` handles both formats automatically.

## Core Features (Must Implement)

1. **Unsubscribe Management** - Automatic opt-out processing (email + SMS)
2. **Bounce Handling** - Auto-remove invalid emails
3. **Email/SMS Queue System** - Rate-limited sending to avoid spam flags
4. **Rate Limiting** - Respect service provider limits
5. **Analytics Dashboard** - Redemption rates, campaign performance metrics
6. **Customer Segments** - Tag-based targeting for campaigns
7. **Export Reports** - CSV/Excel export for redemption data
8. **Email/SMS Preview** - Test rendering before campaign send
9. **A/B Testing** - Subject line variants with performance tracking
10. **Contact Deduplication** - Merge duplicate emails/phones during CSV import
11. **SMS Opt-out Handling** - Twilio webhook for STOP replies
12. **Multi-format CSV Import** - Support for Square POS exports and simple CSV format

## Email Deliverability

**Critical**: Do NOT send emails directly from Raspberry Pi (spam filters will block).

Required setup:
- Use SendGrid/SES/Mailgun API for sending
- Configure SPF/DKIM/DMARC DNS records
- Implement rate limiting (avoid sudden volume spikes)
- Track bounce rates and remove bad addresses

## Development Phases

**Phase 1 - Foundation:** ✅ COMPLETE
- Email API integration (SendGrid) ✓
- SMS API integration (Twilio) ✓
- CSV import with deduplication (email + phone) ✓
  - Simple CSV format support ✓
  - Square POS export format support ✓
- Test email functionality ✓
- Email preview system ✓
- Unsubscribe management ✓
- Campaign management (CRUD operations) ✓
  - Create campaigns with template selection ✓
  - Edit campaigns ✓
  - Delete campaigns ✓
  - Preview campaigns ✓
- Send confirmation workflow ✓
  - Audience selection (All, Email Only, SMS Only, Both) ✓
  - Test mode with test email option ✓
  - Safety confirmations ✓
- Image handling (environment-aware) ✓
  - Base64 encoding for development ✓
  - External URLs for production ✓

**Phase 2 - QR Code Generation:** ✅ COMPLETE
- Async email/SMS queue with Celery + Redis ✓
- Rate limiting (100 email/min, 10 SMS/min) ✓
- Progress tracking UI with live polling ✓
- QR code generation with unique tokens ✓
- QR code CID embedding for Gmail compatibility ✓
- Template management system ✓
- Customer segmentation/tagging (partial) ✓

**Phase 3 - Redemption System:** ✅ COMPLETE
- Staff QR scanner web app (PWA) ✓
  - Camera-based QR scanning with jsQR ✓
  - Manual token entry fallback ✓
  - Audio feedback (Web Audio API tones) ✓
  - Voice feedback (Web Speech API) ✓
  - iOS home screen support (PWA meta tags) ✓
- Redemption validation API ✓
- Usage tracking (prevent multi-redemption) ✓
- Redemption analytics dashboard ✓
  - Redemption rates by campaign ✓
  - Hourly distribution chart ✓
  - Recent redemptions table ✓

**Phase 4 - Advanced Features:** (PLANNED)
- Bounce handling automation
- Redemption report exports
- A/B testing infrastructure
- Performance optimization
- **Image Gallery** - User interface to view/reuse previously uploaded images
  - List uploaded images with thumbnails
  - Click to insert into template
  - Delete unused images
  - Storage usage indicator

## Project Structure (Recommended)

```
MaxxConnect/
├── backend/
│   ├── api/          # Flask/FastAPI REST endpoints
│   ├── models/       # SQLAlchemy database models
│   ├── services/     # Email queue, QR generation, etc.
│   └── templates/    # Jinja2 email templates
├── dashboard/        # Streamlit admin UI
├── ios-scanner/      # Swift iOS app
├── migrations/       # Database migrations
└── tests/
```

## Security Considerations

- QR tokens must use cryptographically secure random hashes
- Validate all QR scans server-side (never trust client)
- Store email service API keys in environment variables
- Implement API authentication for iOS scanner
- Track redemption attempts (detect fraud patterns)
- Add expiration dates to all QR codes
# Project Instructions

## Mini-Spec Workflow (v2.1.4)

Use `/mini-spec` for all design and implementation work. This is a 3-level architecture:

```
specs/    # Human specs (language, environment required)
design/   # SOURCE OF TRUTH: requirements.md, crc-*, seq-*, ui-*, test-*, design.md
docs/     # user-manual.md, developer-guide.md
src/      # Code with traceability comments
```

### Phases (in order)

1. **Spec Phase** - Create human-readable specs in `specs/`
2. **Requirements Phase** - Create `design/requirements.md` with numbered requirements (R1, R2, ...)
3. **Design Phase** - Create CRC cards, sequences, UI specs in `design/`
4. **Implementation Phase** - Write code with traceability comments
5. **Simplification Phase** - Run code-simplifier agent on modified code
6. **Gaps Phase** - Validate traceability, document gaps
7. **Documentation Phase** (optional) - Create user/developer guides

### Phase Separation

- **"Design"** = design artifacts only, no code
- **"Implement"** = code only, update Artifacts checkboxes
- **"Code changes"** = uncheck Artifacts, ask user about design updates

### Minispec CLI Tool

Use `~/.claude/bin/minispec` for structural operations:

```bash
# Phase validation (run after each phase)
~/.claude/bin/minispec phase spec|requirements|design|implementation|gaps

# Full validation
~/.claude/bin/minispec validate

# Queries
~/.claude/bin/minispec query artifacts|uncovered|gaps|requirements

# Updates
~/.claude/bin/minispec update check design.md crc-Store.md
~/.claude/bin/minispec update uncheck design.md crc-Store.md
~/.claude/bin/minispec update add-ref crc-Store.md R5
```

### Design Phase Artifacts

Create in `design/`:
- `design.md`: Intent + Artifacts (design files → code file checkboxes) + Cross-cutting Concerns + Gaps
- `requirements.md`: Numbered requirements from specs (R1, R2, ...)
- `crc-*`: CRC cards with **Requirements:** references
- `seq-*`: Sequence diagrams (≤150 chars wide)
- `ui-*`: ASCII layouts, reference CRC cards
- `test-*`: Test designs
- `manifest-ui.md`: routes, theme, global components

### Implementation Phase

Add traceability comments:
```python
# CRC: crc-Store.md | Seq: seq-crud.md
def add(data):
```

Mark implemented using minispec:
```bash
~/.claude/bin/minispec update check design.md crc-Store.md
```

### Traceability

- All CRC cards must reference requirements: `**Requirements:** R1, R3, R7`
- `design.md` Artifacts section: design files with code file checkboxes
- **Code changes:** Uncheck artifact, ask user: "Update design, specs, or defer?"
- **Update design:** Read code, update design file, re-check artifact

### Gap Analysis

`design.md` Gaps section tracks (use S1/R1/D1/C1/O1 numbering):
- **Spec→Requirements (Sn):** Spec items not in requirements.md
- **Requirements→Design (Rn):** Requirements without design artifacts
- **Design→Code (Dn):** Designed features without code
- **Code→Design (Cn):** Code without design artifacts
- **Oversights (On):** Missing tests, tech debt, security concerns

### Optional: Spec Agent

For isolated context work:
```
Task(subagent_type="spec-agent", prompt="validate the design in design/")
```

See `.claude/skills/mini-spec/methodology.md` for CRC background.
