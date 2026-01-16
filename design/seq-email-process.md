---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# Sequence: Email Process (Worker)
**Source Spec:** phase-2-campaign-management.md

## Participants
- CeleryWorker: Background task processor
- EmailQueueTask: Celery task for email
- RateLimiter: Rate limiting service
- Campaign: Domain model entity
- Customer: Target recipient
- QRCode: Customer's QR code
- EmailService: SendGrid integration
- CampaignAnalytics: Metrics tracking
- Database: Persistence layer

## Sequence
```
  CeleryWorker       EmailQueueTask        RateLimiter          Campaign           EmailService          Database
       |                   |                    |                    |                    |                    |
       |  pick task        |                    |                    |                    |                    |
       |------------------>|                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | check_email_rate() |                    |                    |                    |
       |                   |------------------->|                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    | check Redis counter|                    |                    |
       |                   |                    |----+               |                    |                    |
       |                   |                    |    |               |                    |                    |
       |                   |                    |<---+               |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |<-------------------|                    |                    |                    |
       |                   |  rate_ok           |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | load campaign      |                    |                    |                    |
       |                   |---------------------------------------------------------------------------->      |
       |                   |                    |                    |                    |                    |
       |                   |<----------------------------------------------------------------------------|
       |                   |                    |                    |                    |                    |
       |                   | load customer, qr  |                    |                    |                    |
       |                   |---------------------------------------------------------------------------->      |
       |                   |                    |                    |                    |                    |
       |                   |<----------------------------------------------------------------------------|
       |                   |                    |                    |                    |                    |
       |                   | render_email()     |                    |                    |                    |
       |                   |----+               |                    |                    |                    |
       |                   |    |               |                    |                    |                    |
       |                   |<---+               |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | send_email()       |                    |                    |                    |
       |                   |------------------------------------------------------>       |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    |                    |                    | SendGrid API       |
       |                   |                    |                    |                    |----+               |
       |                   |                    |                    |                    |    |               |
       |                   |                    |                    |                    |<---+               |
       |                   |                    |                    |                    |                    |
       |                   |<------------------------------------------------------|      |                    |
       |                   |  success           |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | increment_email_count()                 |                    |                    |
       |                   |------------------->|                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | update_metrics()   |                    |                    |                    |
       |                   |----------------------------------->     |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    |                    | UPDATE emails_sent |                    |
       |                   |                    |                    |----------------------------------->     |
       |                   |                    |                    |                    |                    |
       |<------------------|                    |                    |                    |                    |
       |  task complete    |                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
```

## Notes
- Worker blocks if rate limit exceeded (wait_if_needed)
- Failed sends trigger retry with exponential backoff
- After 3 failures, task marked permanently failed
- Campaign status updated to 'completed' when all tasks done

## QR Code CID Flow
When campaign.has_qr_code=True:

1. **build_template_vars()** returns:
   - `vars`: Template variables for Jinja2
   - `qr_attachment`: `{'content_id': 'qr-X-Y', 'image_bytes': bytes}`

2. **HTML Processing**:
   - Replace `[[QR_CODE_DATA_URI]]` with `cid:qr-{campaign_id}-{customer_id}`
   - Render with Jinja2 (CID reference survives rendering)

3. **send_email()** called with:
   - `inline_attachments=[qr_attachment]`
   - SendGrid attaches image with `Disposition('inline')` and matching `ContentId`

4. **Gmail Compatibility**:
   - CID images display correctly (unlike base64 data URIs which Gmail strips)
   - Image embedded in email (works offline, no external dependency)
