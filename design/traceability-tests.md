# Test Traceability Map

## specs/phase-2-campaign-management.md

### Requirement 1: QR Code Generation
**CRC Cards**: crc-QRCode.md, crc-QRCodeGenerator.md
**Sequences**: seq-qr-generate.md
**Test Designs**: test-QRCode.md

### Requirement 2: Customer Segmentation
**CRC Cards**: crc-Customer.md, crc-SegmentManager.md
**Sequences**: seq-segment-filter.md
**Test Designs**: test-Segmentation.md

### Requirement 3: Async Queue
**CRC Cards**: crc-CeleryApp.md, crc-EmailQueueTask.md, crc-SMSQueueTask.md, crc-RateLimiter.md
**Sequences**: seq-email-process.md, seq-sms-process.md, seq-email-retry.md
**Test Designs**: test-Queue.md

### Requirement 4: Analytics
**CRC Cards**: crc-CampaignAnalytics.md
**Sequences**: seq-campaign-analytics.md
**Test Designs**: test-Analytics.md

### Campaign Management
**CRC Cards**: crc-Campaign.md, crc-CampaignManager.md
**Sequences**: seq-campaign-create.md, seq-campaign-preview.md, seq-campaign-send.md
**Test Designs**: test-Campaign.md

### UI Components
**UI Specs**: ui-campaign-list.md, ui-campaign-create.md, ui-campaign-preview.md, ui-campaign-analytics.md, ui-segment-list.md, ui-qr-display.md
**Test Designs**: test-UI.md

---

## Test Design to Implementation Mapping

### test-Campaign.md -> tests/test_campaign.py
- [ ] "Test: Create campaign with valid data"
- [ ] "Test: Validate campaign before send"
- [ ] "Test: Status transitions follow valid flow"
- [ ] "Test: Calculate target customer count"
- [ ] "Test: Estimate send duration"
- [ ] "Test: Campaign preview generation"
- [ ] "Test: Send campaign queues tasks"
- [ ] "Test: Update campaign metrics"
- [ ] "Test: Progress percentage calculation"

### test-QRCode.md -> tests/test_qr_code.py
- [ ] "Test: Generate unique token"
- [ ] "Test: Token cryptographic security"
- [ ] "Test: Generate QR image"
- [ ] "Test: Batch QR generation performance"
- [ ] "Test: QR code expiration calculation"
- [ ] "Test: QR validity check (not expired)"
- [ ] "Test: QR validity check (expired)"
- [ ] "Test: QR validity check (max usage exceeded)"
- [ ] "Test: Increment usage count"
- [ ] "Test: Generate short URL"
- [ ] "Test: Duplicate prevention"

### test-Queue.md -> tests/test_queue.py
- [ ] "Test: Celery app configuration"
- [ ] "Test: Email task execution success"
- [ ] "Test: SMS task execution success"
- [ ] "Test: SMS length validation"
- [ ] "Test: Rate limiter blocks when exceeded"
- [ ] "Test: Rate limiter resets after window"
- [ ] "Test: Email retry on temporary failure"
- [ ] "Test: Email permanent failure after max retries"
- [ ] "Test: SMS retry on temporary failure"
- [ ] "Test: Email rendering with QR code"
- [ ] "Test: SMS rendering with short URL"
- [ ] "Test: Queue length monitoring"
- [ ] "Test: Task revocation"
- [ ] "Test: Worker crash recovery"

### test-Segmentation.md -> tests/test_segmentation.py
- [ ] "Test: Parse customer segments"
- [ ] "Test: Add segment to customer"
- [ ] "Test: Remove segment from customer"
- [ ] "Test: Check customer has segment"
- [ ] "Test: Segment normalization"
- [ ] "Test: Segment validation"
- [ ] "Test: Get all unique segments"
- [ ] "Test: Get segment counts"
- [ ] "Test: Filter customers by single segment"
- [ ] "Test: Filter customers by multiple segments"
- [ ] "Test: Filter customers with ALL segment"
- [ ] "Test: Customer matches segments check"
- [ ] "Test: Bulk segment assignment"
- [ ] "Test: Subscription filter during segment query"

### test-Analytics.md -> tests/test_analytics.py
- [ ] "Test: Get campaign summary"
- [ ] "Test: Calculate send rate"
- [ ] "Test: Calculate completion time"
- [ ] "Test: Get segment breakdown"
- [ ] "Test: Get failure reasons"
- [ ] "Test: Export report CSV"
- [ ] "Test: Update metrics atomically"
- [ ] "Test: Analytics for in-progress campaign"
- [ ] "Test: Analytics for failed campaign"
- [ ] "Test: QR code count"

### test-UI.md -> tests/test_ui.py (or integration tests)
- [ ] "Test: Campaign list displays all campaigns"
- [ ] "Test: Campaign list status filtering"
- [ ] "Test: Campaign create form validation"
- [ ] "Test: Segment selection updates count"
- [ ] "Test: SMS character counter"
- [ ] "Test: Campaign preview renders email"
- [ ] "Test: Campaign preview renders SMS"
- [ ] "Test: Send confirmation dialog"
- [ ] "Test: Analytics dashboard progress bar"
- [ ] "Test: Analytics auto-refresh"
- [ ] "Test: Segment list displays counts"
- [ ] "Test: QR display page renders"
- [ ] "Test: QR display expired state"
- [ ] "Test: QR display invalid token"
- [ ] "Test: CSV export download"
- [ ] "Test: Navigation links work"

---

## Coverage Summary

### CRC Responsibilities Coverage
| CRC Card | Test Design | Tests Defined |
|----------|-------------|---------------|
| crc-Campaign.md | test-Campaign.md | 9 |
| crc-CampaignManager.md | test-Campaign.md | 5 |
| crc-QRCode.md | test-QRCode.md | 11 |
| crc-QRCodeGenerator.md | test-QRCode.md | 5 |
| crc-CeleryApp.md | test-Queue.md | 4 |
| crc-EmailQueueTask.md | test-Queue.md | 5 |
| crc-SMSQueueTask.md | test-Queue.md | 4 |
| crc-RateLimiter.md | test-Queue.md | 2 |
| crc-Customer.md | test-Segmentation.md | 5 |
| crc-SegmentManager.md | test-Segmentation.md | 9 |
| crc-CampaignAnalytics.md | test-Analytics.md | 10 |

**Total CRC Cards**: 11
**Total Test Cases**: 68

### Sequence Coverage
| Sequence | Test Design | Covered |
|----------|-------------|---------|
| seq-campaign-create.md | test-Campaign.md | Yes |
| seq-campaign-preview.md | test-Campaign.md | Yes |
| seq-campaign-send.md | test-Campaign.md, test-Queue.md | Yes |
| seq-email-process.md | test-Queue.md | Yes |
| seq-sms-process.md | test-Queue.md | Yes |
| seq-email-retry.md | test-Queue.md | Yes |
| seq-qr-generate.md | test-QRCode.md | Yes |
| seq-segment-filter.md | test-Segmentation.md | Yes |
| seq-campaign-analytics.md | test-Analytics.md | Yes |

**Total Sequences**: 9
**Coverage**: 100%

### UI Spec Coverage
| UI Spec | Test Design | Tests |
|---------|-------------|-------|
| ui-campaign-list.md | test-UI.md | 2 |
| ui-campaign-create.md | test-UI.md | 3 |
| ui-campaign-preview.md | test-UI.md | 3 |
| ui-campaign-analytics.md | test-UI.md | 3 |
| ui-segment-list.md | test-UI.md | 1 |
| ui-qr-display.md | test-UI.md | 3 |

**Total UI Specs**: 6
**Total UI Tests**: 15

### Gaps
- Accessibility testing not covered
- Browser compatibility testing not covered
- Mobile responsiveness testing not covered
- Performance/load testing not covered
- Security penetration testing not covered
- Integration with external APIs (SendGrid, Twilio) mocked
