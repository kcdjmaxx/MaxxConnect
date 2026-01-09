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

### Environment Configuration
- FLASK_ENV: Controls dev vs production mode
- Development: Base64 images, SQLite
- Production: External URLs, PostgreSQL
- See crc-Config.md, crc-ImageHandler.md

### Routing
- See manifest-ui.md for all routes

### Error Handling
- Flash messages for user feedback
- SMS opt-out webhook for STOP replies

## Artifacts

### CRC Cards
- crc-Campaign.md
  - [x] backend/models.py (Campaign class)
- crc-CampaignManager.md
  - [x] app.py (campaign routes)
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
  - [ ] backend/tasks/celery_app.py - Phase 2
- crc-EmailQueueTask.md
  - [ ] backend/tasks/email_task.py - Phase 2
- crc-SMSQueueTask.md
  - [ ] backend/tasks/sms_task.py - Phase 2
- crc-RateLimiter.md
  - [ ] backend/services/rate_limiter.py - Phase 2
- crc-CampaignAnalytics.md
  - [ ] backend/services/campaign_analytics.py - Phase 3

### Sequences
- seq-campaign-create.md
  - [x] app.py (campaign_new)
- seq-campaign-preview.md
  - [x] app.py (campaign_preview)
- seq-campaign-send.md
  - [x] app.py (campaign_send)
- seq-campaign-send-qr.md
  - [ ] Phase 2 (QR toggle feature)
- seq-email-process.md
  - [ ] Phase 2
- seq-sms-process.md
  - [ ] Phase 2
- seq-email-retry.md
  - [ ] Phase 2
- seq-sms-retry.md
  - [ ] Phase 2
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

**Status:** Phase 1 Complete, Phase 2 Ready
- CRC Cards: 13 (5 implemented, 8 planned)
- Sequences: 12 (4 implemented, 8 planned)
- UI Specs: 7 (4 implemented, 3 planned)
- Test Designs: 6 (complete)
