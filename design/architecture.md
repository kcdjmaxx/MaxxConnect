# Architecture
**Source Spec:** phase-2-campaign-management.md

## Systems

### Campaign Management (IMPLEMENTED)
**Purpose:** Create, configure, and send marketing campaigns with template selection and audience targeting
**Status:** Phase 1 Complete, QR Toggle designed
**Design Elements:** crc-Campaign.md, crc-CampaignManager.md, crc-ImageHandler.md, crc-Config.md, seq-campaign-create.md, seq-campaign-preview.md, seq-campaign-send.md, seq-campaign-send-qr.md, ui-campaign-list.md, ui-campaign-create.md, ui-campaign-send-confirm.md

### Image Handling (IMPLEMENTED)
**Purpose:** Environment-aware image processing for email templates
**Status:** Complete
**Design Elements:** crc-ImageHandler.md, crc-Config.md
- Development: Base64 encoded images inline
- Production: External URLs via Railway.app

### QR Code System (PLANNED)
**Purpose:** Generate and manage unique QR codes for redemption tracking
**Status:** Phase 2
**Design Elements:** crc-QRCode.md, crc-QRCodeGenerator.md, seq-qr-generate.md, ui-qr-display.md

### Async Queue System (PLANNED)
**Purpose:** Background processing of email/SMS with rate limiting
**Status:** Phase 2
**Design Elements:** crc-CeleryApp.md, crc-EmailQueueTask.md, crc-SMSQueueTask.md, crc-RateLimiter.md, seq-email-process.md, seq-sms-process.md, seq-email-retry.md, seq-sms-retry.md

### Customer Segmentation (PARTIAL)
**Purpose:** Organize customers into targetable groups
**Status:** Basic audience selection implemented, tag-based segments planned
**Design Elements:** crc-Customer.md, crc-SegmentManager.md, seq-segment-filter.md, seq-segment-manage.md, ui-segment-list.md

### Analytics (PLANNED)
**Purpose:** Track and report campaign performance metrics
**Status:** Phase 3
**Design Elements:** crc-CampaignAnalytics.md, seq-campaign-analytics.md, ui-campaign-analytics.md

## Cross-Cutting Concerns
**Design Elements:** manifest-ui.md

## Source File Mapping

### Models (backend/models.py) - IMPLEMENTED
- Campaign: id, name, subject, template_name, html_content, status, sent_date, created_at, has_qr_code
- Customer: Encrypted email/phone, subscription flags, segments

### Configuration (backend/) - IMPLEMENTED
- config.py: Environment detection, image strategy, URL configuration
- image_handler.py: Base64/external URL image processing

### Routes (app.py) - IMPLEMENTED
- GET /campaigns - List all campaigns
- GET/POST /campaign/new - Create campaign
- GET/POST /campaign/edit/<id> - Edit campaign
- GET /campaign/preview/<id> - Preview campaign HTML
- GET /campaign/send-confirm/<id> - Send confirmation page
- POST /campaign/send/<id> - Execute send
- POST /campaign/delete/<id> - Delete campaign

### Templates (templates/) - IMPLEMENTED
- campaigns.html - Campaign list view
- campaign_create.html - Create campaign form
- campaign_edit.html - Edit campaign form
- campaign_send_confirm.html - Send confirmation with audience selection
- email/monday_special.html - Sample email template

### Services (backend/services/) - PLANNED
- campaign_manager.py (extracted from routes)
- qr_generator.py
- segment_manager.py
- campaign_analytics.py
- rate_limiter.py

### Tasks (backend/tasks/) - PLANNED
- celery_app.py
- email_task.py
- sms_task.py
