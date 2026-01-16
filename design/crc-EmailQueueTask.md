---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# EmailQueueTask
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- campaign_id: Campaign being sent
- customer_id: Target customer
- qr_code_id: Associated QR code
- retry_count: Number of retry attempts (max: 3)
- created_at: Task creation timestamp
- status: Task status (pending/processing/completed/failed)

### Does
- send_campaign_email(campaign_id, customer_id, campaign_send_id): Celery task entry point
- build_template_vars(db, customer, campaign, base_url): Build personalization vars + QR attachment
  - Returns: `{'vars': template_vars, 'qr_attachment': attachment_data}`
  - qr_attachment: `{'content_id': str, 'image_bytes': bytes}` for CID embedding
- update_send_progress(db, campaign_send_id, success, error): Track batch progress
- handle_success(): Mark task complete, update campaign metrics
- handle_failure(error): Log error, schedule retry or mark failed

## Collaborators
- Campaign: Source content and settings (has_qr_code flag)
- Customer: Email recipient data and personalization
- QRCodeGenerator: Generate QR bytes and content IDs for CID attachment
- EmailService: SendGrid API with inline_attachments support
- CampaignSend: Progress tracking for batch sends
- RateLimiter: Email rate limiting (100/min default)

## Sequences
- seq-campaign-send.md: Process email queue
- seq-email-retry.md: Handle failed email retry
