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

### Customer Segmentation (PARTIAL)
**Purpose:** Organize customers into targetable groups
**Design Elements:** crc-Customer.md, crc-SegmentManager.md

### Analytics (PLANNED - Phase 3)
**Purpose:** Track campaign performance metrics
**Design Elements:** crc-CampaignAnalytics.md

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
  - [ ] backend/services/campaign_analytics.py - Phase 3

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
  - [ ] Phase 3

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
  - [ ] Phase 3
- ui-segment-list.md
  - [ ] Phase 2
- ui-qr-display.md
  - [ ] Phase 2

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
- seq-qr-validate.md: Deferred to Phase 3 (redemption scanning)
- Webhook handling for bounces: Phase 4
- ui-qr-display.md: QR display in iOS scanner app (Phase 3)

## Summary

**Status:** Phase 2 Complete (QR Codes + Async Queue Deployed)
- CRC Cards: 15 (13 implemented, 2 planned)
- Sequences: 13 (11 implemented, 2 planned)
- UI Specs: 7 (4 implemented, 3 planned)
- Test Designs: 6 (complete)

**Recent Updates:**
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
