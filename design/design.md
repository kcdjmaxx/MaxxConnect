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

### QR Code System (PLANNED - Phase 2)
**Purpose:** Generate unique QR codes for redemption tracking
**Design Elements:** crc-QRCode.md, crc-QRCodeGenerator.md

### Async Queue System (PLANNED - Phase 2)
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
  - [ ] backend/models.py (QRCode class) - Phase 2
- crc-QRCodeGenerator.md
  - [ ] backend/services/qr_generator.py - Phase 2
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
  - [ ] Phase 2 (QR toggle feature)
- seq-email-process.md
  - [x] backend/tasks/email_task.py
- seq-sms-process.md
  - [x] backend/tasks/sms_task.py
- seq-email-retry.md
  - [x] backend/tasks/email_task.py (retry logic)
- seq-sms-retry.md
  - [x] backend/tasks/sms_task.py (retry logic)
- seq-qr-generate.md
  - [ ] Phase 2
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
- B1: Campaign model needs Phase 2 fields (qr_expiration_days, rate limits, etc.)
- B2: QRCode model not yet created
- B3: Customer.segments helpers missing (get_segments_list, add_segment, etc.)
- B4: No backend/services/ directory yet
- B5: No Celery infrastructure yet

### Code to Design
- All implemented code has corresponding design artifacts

### Deferred
- seq-qr-validate.md: Deferred to Phase 3
- Webhook handling for bounces: Phase 4

## Summary

**Status:** Phase 2 In Progress (Async Queue Complete)
- CRC Cards: 14 (10 implemented, 4 planned)
- Sequences: 13 (9 implemented, 4 planned)
- UI Specs: 7 (4 implemented, 3 planned)
- Test Designs: 6 (complete)

**Recent Updates:**
- Implemented Celery + Redis async queue system
- Added CampaignSend model for progress tracking
- Added email_task.py and sms_task.py background tasks
- Added rate_limiter.py service
- Updated campaign_send route for non-blocking sends
- Added progress API endpoints and UI polling
- Updated Procfile for Railway worker deployment
