# Traceability Matrix
**Source Spec:** phase-2-campaign-management.md

## Level 1 to Level 2 (Specs to Design)

### Requirement 1: QR Code Generation & Personalization
| Spec Section | Design Artifacts |
|--------------|-----------------|
| QR code toggle in campaign creation | crc-Campaign.md (has_qr_code), ui-campaign-create.md |
| Unique QR per customer per campaign | crc-QRCode.md, crc-QRCodeGenerator.md, seq-campaign-send-qr.md |
| Token format (campaign-customer-hash) | crc-QRCode.md, seq-qr-generate.md, seq-campaign-send-qr.md |
| Base64 encoding for email | crc-QRCodeGenerator.md, seq-campaign-send-qr.md |
| Short URL for SMS | crc-QRCode.md, ui-qr-display.md |
| Expiration dates | crc-QRCode.md, crc-Campaign.md |
| Prevent duplicate redemptions | crc-QRCode.md (usage_count, max_usage) |
| Cryptographic security | crc-QRCodeGenerator.md, seq-qr-generate.md |
| Conditional template rendering | crc-CampaignManager.md (render_email_with_qr) |
| QR status display on send confirm | ui-campaign-send-confirm.md |

### Requirement 2: Customer Segmentation & Targeting
| Spec Section | Design Artifacts |
|--------------|-----------------|
| Multiple tags per customer | crc-Customer.md (segments field) |
| Tags during CSV import | crc-Customer.md |
| Target segment selection in UI | ui-campaign-create.md |
| "ALL" segment option | crc-SegmentManager.md, seq-segment-filter.md |
| Case-insensitive tags | crc-SegmentManager.md |
| Customer count per segment | ui-campaign-create.md, ui-segment-list.md |

### Requirement 3: Asynchronous Campaign Queue
| Spec Section | Design Artifacts |
|--------------|-----------------|
| Celery + Redis queue | crc-CeleryApp.md |
| Rate limiting (emails/min) | crc-RateLimiter.md, crc-Campaign.md |
| Retry logic (3 attempts) | crc-EmailQueueTask.md, crc-SMSQueueTask.md, seq-email-retry.md |
| Campaign status tracking | crc-Campaign.md, ui-campaign-list.md |
| Progress updates | crc-CampaignAnalytics.md, ui-campaign-analytics.md |

### Requirement 4: Campaign Analytics & Tracking
| Spec Section | Design Artifacts |
|--------------|-----------------|
| Send metrics | crc-CampaignAnalytics.md, crc-Campaign.md |
| Segment breakdown | crc-CampaignAnalytics.md, seq-campaign-analytics.md |
| Failure reasons | crc-CampaignAnalytics.md, ui-campaign-analytics.md |
| CSV export | crc-CampaignAnalytics.md, ui-campaign-analytics.md |

### UI Requirements
| Spec Section | Design Artifacts |
|--------------|-----------------|
| Campaign list view | ui-campaign-list.md |
| Campaign create form | ui-campaign-create.md |
| Campaign preview | ui-campaign-preview.md, seq-campaign-preview.md |
| Analytics dashboard | ui-campaign-analytics.md |
| Segment management | ui-segment-list.md |

## Level 2 to Level 3 (Design to Implementation)

### Models
| Design | Source File | Status |
|--------|-------------|--------|
| crc-Campaign.md | backend/models.py (Campaign class) | [x] Implemented |
| crc-QRCode.md | backend/models.py (QRCode class) | [ ] Planned Phase 2 |
| crc-Customer.md | backend/models.py (Customer class) | [x] Implemented |

### Configuration
| Design | Source File | Status |
|--------|-------------|--------|
| crc-Config.md | backend/config.py | [x] Implemented |
| crc-ImageHandler.md | backend/image_handler.py | [x] Implemented |

### Routes (Flask - app.py)
| Design | Source File | Status |
|--------|-------------|--------|
| crc-CampaignManager.md | app.py (campaign routes) | [x] Implemented |
| - campaigns() | GET /campaigns | [x] |
| - campaign_new() | GET/POST /campaign/new | [x] |
| - campaign_edit() | GET/POST /campaign/edit/<id> | [x] |
| - campaign_preview() | GET /campaign/preview/<id> | [x] |
| - campaign_send_confirm() | GET /campaign/send-confirm/<id> | [x] |
| - campaign_send() | POST /campaign/send/<id> | [x] |
| - campaign_delete() | POST /campaign/delete/<id> | [x] |
| - get_available_templates() | Helper function | [x] |

### Templates
| Design | Source File | Status |
|--------|-------------|--------|
| ui-campaign-list.md | templates/campaigns.html | [x] Implemented |
| ui-campaign-create.md | templates/campaign_create.html | [x] Implemented |
| ui-campaign-send-confirm.md | templates/campaign_send_confirm.html | [x] Implemented |
| (campaign edit) | templates/campaign_edit.html | [x] Implemented |
| (email template) | templates/email/monday_special.html | [x] Implemented |
| ui-campaign-analytics.md | templates/campaigns/analytics.html | [ ] Planned Phase 3 |
| ui-segment-list.md | templates/segments/list.html | [ ] Planned Phase 2 |
| ui-qr-display.md | templates/qr_display.html | [ ] Planned Phase 2 |

### Services (Planned Extraction)
| Design | Source File | Status |
|--------|-------------|--------|
| crc-CampaignManager.md | backend/services/campaign_manager.py | [ ] Extract from app.py |
| crc-QRCodeGenerator.md | backend/services/qr_generator.py | [ ] Planned Phase 2 |
| crc-SegmentManager.md | backend/services/segment_manager.py | [ ] Planned Phase 2 |
| crc-CampaignAnalytics.md | backend/services/campaign_analytics.py | [ ] Planned Phase 3 |
| crc-RateLimiter.md | backend/services/rate_limiter.py | [ ] Planned Phase 2 |

### Celery Tasks (Planned)
| Design | Source File | Status |
|--------|-------------|--------|
| crc-CeleryApp.md | backend/tasks/celery_app.py | [ ] Planned Phase 2 |
| crc-EmailQueueTask.md | backend/tasks/email_task.py | [ ] Planned Phase 2 |
| crc-SMSQueueTask.md | backend/tasks/sms_task.py | [ ] Planned Phase 2 |

### Sequences (Implementation Reference)
| Design | Implements | Status |
|--------|------------|--------|
| seq-campaign-create.md | Campaign creation workflow | [x] Implemented |
| seq-campaign-preview.md | Preview generation workflow | [x] Implemented |
| seq-campaign-send.md | Campaign send with audience selection | [x] Implemented |
| seq-campaign-send-qr.md | Campaign send with QR code generation | [ ] Planned (QR toggle feature) |
| seq-email-process.md | Worker email processing | [ ] Planned Phase 2 |
| seq-sms-process.md | Worker SMS processing | [ ] Planned Phase 2 |
| seq-email-retry.md | Email retry handling | [ ] Planned Phase 2 |
| seq-sms-retry.md | SMS retry handling | [ ] Planned Phase 2 |
| seq-qr-generate.md | QR batch generation | [ ] Planned Phase 2 |
| seq-segment-filter.md | Customer filtering by segment | [x] Basic (audience selection) |
| seq-segment-manage.md | Segment add/remove operations | [ ] Planned Phase 2 |
| seq-campaign-analytics.md | Analytics retrieval | [ ] Planned Phase 3 |
