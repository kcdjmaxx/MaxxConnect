---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/documentation
  - status/active
  - tool/flask
---

# MaxxConnect Design

**Source Spec:** phase-2-campaign-management.md

## Intent

Email/SMS marketing platform with:
- Campaign management (create, preview, send)
- Customer segmentation and targeting
- QR code generation for redemption tracking
- Async queue for rate-limited delivery
- Analytics and reporting

## Systems

### Campaign Management (IMPLEMENTED)
**Purpose:** Create, configure, and send marketing campaigns
**Design Elements:** crc-Campaign.md, crc-CampaignManager.md, crc-ImageHandler.md, crc-Config.md

### QR Code System (IMPLEMENTED)
**Purpose:** Generate unique QR codes for redemption tracking
**Design Elements:** crc-QRCode.md, crc-QRCodeGenerator.md, crc-EmailService.md
**Implementation:** CID (Content-ID) embedding for Gmail compatibility

### Async Queue System (IMPLEMENTED)
**Purpose:** Background processing with rate limiting
**Design Elements:** crc-CeleryApp.md, crc-EmailQueueTask.md, crc-SMSQueueTask.md, crc-RateLimiter.md

### Template Management (IMPLEMENTED)
**Purpose:** Import, validate, and edit email templates
**Design Elements:** crc-TemplateProcessor.md, ui-template-list.md, ui-template-import.md, seq-template-import.md
**Features:**
- Template import wizard (upload HTML, auto-inject placeholders)
- Template validation (check required elements)
- Template editor (simple textarea with live preview)
- Template list with validation status badges

### Customer Segmentation (PARTIAL)
**Purpose:** Organize customers into targetable groups
**Design Elements:** crc-Customer.md, crc-SegmentManager.md

### QR Redemption System (IMPLEMENTED)
**Purpose:** Staff-facing QR code validation and redemption
**Design Elements:** crc-Redemption.md, crc-RedemptionService.md, seq-qr-redemption.md
**Features:**
- Staff scanner PWA with camera QR scanning
- Manual token entry fallback
- Audio/voice feedback on scan
- Redemption analytics dashboard
- Fraud detection (device info, IP tracking)
- iOS home screen support

### Analytics (IMPLEMENTED)
**Purpose:** Track campaign and redemption performance metrics
**Design Elements:** crc-CampaignAnalytics.md, crc-RedemptionService.md
**Features:**
- Redemption rates by campaign
- Hourly redemption distribution
- Recent redemptions table

### List Hygiene (PLANNED - Phase 4)
**Purpose:** Maintain clean subscriber list
**Features:**
- Bounce cleanup via SendGrid Suppressions API
- Auto-unsubscribe hard bounces
- Bounce rate dashboard
- Manual list cleaning tools

## Cross-Cutting Concerns

### Authentication
- HTTP Basic Auth protects all admin routes
- Credentials via ADMIN_USERNAME / ADMIN_PASSWORD env vars
- Development: Auth disabled if credentials not set
- Production: Auth required (denies access if not configured)
- Public routes (no auth): /unsubscribe, /sms-optout, /signup
- Implementation: flask-httpauth with @auth.login_required decorator

### Environment Configuration
- FLASK_ENV: Controls dev vs production mode
- Development: Base64 images, SQLite
- Production: External URLs, PostgreSQL
- See crc-Config.md, crc-ImageHandler.md

### Routing
- See manifest-ui.md for all routes (includes auth requirements)

### Error Handling
- Flash messages for user feedback
- SMS opt-out webhook for STOP replies

### Dashboard Stats
- Email Unsubscribed: Counts customers with subscribed=False
- SMS Subscribed: Counts customers with sms_subscribed=True
- SMS Unsubscribed: Counts only active opt-outs (customers with sms_unsubscribed_date set)
  - Note: Does NOT count customers who simply have sms_subscribed=False
  - This allows tracking actual STOP/opt-out events vs never-subscribed contacts

### TCPA/CAN-SPAM Compliance
- Email: Unsubscribe link required, physical address in footer
- SMS: Explicit opt-in required, STOP handling via webhook
- CSV Import: Separate consent flags for email vs SMS (sms_consent defaults false)

## Artifacts

### CRC Cards
- crc-Campaign.md
  - [x] backend/models.py (Campaign class)
- crc-CampaignManager.md
  - [x] app.py (campaign routes)
- crc-CSVImporter.md
  - [x] backend/csv_importer.py
  - [x] app.py (import_contacts route)
  - [x] templates/import.html (consent checkboxes)
- crc-Config.md
  - [x] backend/config.py
- crc-ImageHandler.md
  - [x] backend/image_handler.py
- crc-Customer.md
  - [x] backend/models.py (Customer class)
  - [x] backend/models.py (email_hash, phone_hash, find_by_email, find_by_phone)
  - [ ] backend/models.py (segment helper methods)
- crc-QRCode.md
  - [x] backend/models.py (QRCode class)
- crc-EmailDelivery.md
  - [x] backend/models.py (EmailDelivery class)
  - [x] backend/tasks/email_task.py (delivery tracking)
  - [x] app.py (resume route, delivery stats)
  - [x] templates/campaign_send_confirm.html (resume UI)
- crc-QRCodeGenerator.md
  - [x] backend/services/qr_generator.py
- crc-EmailService.md
  - [x] backend/email_service.py (CID attachment support)
- crc-SegmentManager.md
  - [ ] backend/services/segment_manager.py - Phase 2
- crc-CeleryApp.md
  - [x] backend/tasks/celery_app.py
- crc-EmailQueueTask.md
  - [x] backend/tasks/email_task.py
- crc-SMSQueueTask.md
  - [x] backend/tasks/sms_task.py
- crc-RateLimiter.md
  - [x] backend/services/rate_limiter.py
- crc-CampaignAnalytics.md
  - [x] app.py (redemption_analytics route)
- crc-TemplateProcessor.md
  - [x] backend/services/template_processor.py
- crc-Redemption.md
  - [x] backend/models.py (Redemption class)
- crc-RedemptionService.md
  - [x] backend/services/redemption_service.py

### Sequences
- seq-csv-import.md
  - [x] backend/csv_importer.py
  - [x] app.py (import_contacts)
- seq-campaign-create.md
  - [x] app.py (campaign_new)
- seq-campaign-preview.md
  - [x] app.py (campaign_preview)
- seq-campaign-send.md
  - [x] app.py (campaign_send)
- seq-campaign-send-qr.md
  - [x] backend/tasks/email_task.py (CID embedding)
  - [x] backend/email_service.py (inline attachments)
- seq-email-process.md
  - [x] backend/tasks/email_task.py
- seq-sms-process.md
  - [x] backend/tasks/sms_task.py
- seq-email-retry.md
  - [x] backend/tasks/email_task.py (retry logic)
- seq-sms-retry.md
  - [x] backend/tasks/sms_task.py (retry logic)
- seq-qr-generate.md
  - [x] backend/services/qr_generator.py
- seq-segment-filter.md
  - [x] app.py (audience selection)
- seq-segment-manage.md
  - [ ] Phase 2
- seq-campaign-analytics.md
  - [x] app.py (redemption_analytics)
- seq-qr-redemption.md
  - [x] app.py (redeem routes)
  - [x] backend/services/redemption_service.py
- seq-template-import.md
  - [x] app.py (template routes)
  - [x] backend/services/template_processor.py

### UI Specs
- ui-campaign-list.md
  - [x] templates/campaigns.html
- ui-campaign-create.md
  - [x] templates/campaign_create.html
- ui-campaign-preview.md
  - [x] templates/campaign_preview_wrapper.html
- ui-campaign-send-confirm.md
  - [x] templates/campaign_send_confirm.html
- ui-campaign-analytics.md
  - [x] templates/redemption_analytics.html
- ui-staff-scanner.md
  - [x] templates/staff_redeem.html
- ui-redeem-result.md
  - [x] templates/redeem_result.html
- ui-segment-list.md
  - [ ] Phase 2
- ui-qr-display.md
  - [ ] Phase 2
- ui-template-list.md
  - [x] templates/template_list.html
- ui-template-import.md
  - [x] templates/template_import.html
- ui-template-edit.md
  - [x] templates/template_edit.html

### Test Designs
- test-Campaign.md
- test-QRCode.md
- test-Queue.md
- test-Segmentation.md
- test-Analytics.md
- test-UI.md
- See traceability-tests.md for test-to-code mapping

## Gaps

### Spec to Design
- All Phase 2 requirements have corresponding CRC cards and sequences
- Phase 3 analytics designed but not implemented

### Design to Code
- [x] ~~B1: Campaign model needs Phase 2 fields~~ (has_qr_code implemented)
- [x] ~~B2: QRCode model not yet created~~ (implemented)
- [ ] B3: Customer.segments helpers missing (get_segments_list, add_segment, etc.)
- [x] ~~B4: No backend/services/ directory yet~~ (qr_generator.py, rate_limiter.py)
- [x] ~~B5: No Celery infrastructure yet~~ (implemented and deployed)

### Code to Design
- [x] crc-EmailService.md created for CID attachment support

### Deferred
- Webhook handling for bounces: Phase 4
- ui-qr-display.md: iOS native scanner app (web PWA implemented instead)

## Summary

**Status:** Phase 3 Complete (QR Redemption System Implemented)
- CRC Cards: 17 (16 implemented, 1 planned)
- Sequences: 14 (13 implemented, 1 planned)
- UI Specs: 13 (10 implemented, 3 planned)
- Test Designs: 6 (complete)

**Recent Updates:**
- **QR Redemption System (Jan 17, 2026):**
  - Added `Redemption` model for tracking redemption events
  - Added `RedemptionService` for validate/redeem operations
  - Staff scanner PWA at `/staff/redeem`:
    - Camera QR scanning with jsQR library
    - Manual token entry fallback
    - Audio feedback via Web Audio API
    - Voice feedback via Web Speech API
    - iOS home screen support (PWA meta tags)
  - Public landing page at `/redeem/<token>`
  - Redemption analytics dashboard at `/analytics/redemptions`
  - Navigation updated with "Redeem QR" and "Analytics" links
- **Template Management System (Jan 17, 2026):**
  - Added `TemplateProcessor` service for validation and auto-injection
  - New routes: `/templates`, `/template/import`, `/template/edit/<filename>`
  - Template import wizard: upload HTML, auto-inject required placeholders
  - Template validation: checks for unsubscribe link, address, customer name, QR section
  - Template editor with live preview and test email functionality
  - Template list with validation status badges
- **Campaign Resume & Delivery Tracking (Jan 16, 2026):**
  - Added `EmailDelivery` model to track individual customer/campaign sends
  - New `/campaign/resume/<id>` route sends only to unsent customers
  - UI shows delivery stats (Sent/Failed/Remaining) with resume button
  - Prevents duplicate sends when resuming interrupted campaigns
- **Customer Name Personalization Fix (Jan 16, 2026):**
  - Changed from `{{ customer_name }}` (evaluated at creation) to `[[CUSTOMER_NAME]]` placeholder
  - Placeholder survives Jinja2 rendering, replaced at send time with actual name
  - Updated all email templates and send paths
- **Privacy Policy & Compliance (Jan 16, 2026):**
  - Added privacy policy link to WelcomeTemplate footer
  - Link: https://fricandfrac.net/privacy/
  - Required for SendGrid upgrade approval
- **SendGrid Upgrade Complete (Jan 16, 2026):**
  - Upgraded to Essentials plan: 50,000 emails/month
  - Ticket #24741818 - Approved
  - Rate limit configurable via EMAIL_RATE_LIMIT env var (default 100/min)
- **QR Code CID Implementation (Jan 16, 2026):**
  - Implemented Content-ID (CID) approach for Gmail compatibility
  - Gmail blocks base64 data URIs; CID inline attachments work correctly
  - Added regenerate_bytes() and generate_content_id() to qr_generator.py
  - Added inline_attachments parameter to send_email()
  - Updated email_task.py to use CID references instead of data URIs
  - Created crc-EmailService.md design document
  - QR codes now display correctly in Gmail, Apple Mail, Outlook
- **Async Queue (Jan 2026):**
  - Implemented Celery + Redis async queue system
  - Added CampaignSend model for progress tracking
  - Added email_task.py and sms_task.py background tasks
  - Added rate_limiter.py service
  - Updated campaign_send route for non-blocking sends
  - Added progress API endpoints and UI polling
  - Successfully deployed to Railway

## Railway Deployment Notes

The async queue requires **two Railway services** from the same repo:

### Web Service
- Uses default Procfile (`web: gunicorn app:app`)
- Connects to: PostgreSQL, Redis

### Worker Service
- Custom start command: `celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=2`
- Connects to: PostgreSQL, Redis
- **Required environment variables** (copy from web service):
  - `DATABASE_URL` (reference from PostgreSQL)
  - `REDIS_URL` (reference from Redis)
  - `ENCRYPTION_KEY`
  - `SENDGRID_API_KEY`
  - `SENDER_EMAIL`
  - `SENDER_NAME` or `BUSINESS_NAME`

### Configuration
- Removed `startCommand` from `railway.toml` to allow per-service commands
- Rate limits configurable via `EMAIL_RATE_LIMIT` (default 100/min) and `SMS_RATE_LIMIT` (default 10/min)
