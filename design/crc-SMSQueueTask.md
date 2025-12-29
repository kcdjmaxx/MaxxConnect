# SMSQueueTask
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
- execute(): Send SMS via Twilio
- render_sms(campaign, customer, qr_code): Generate personalized message with short URL
- validate_length(): Ensure message under 160 chars
- handle_success(): Mark task complete, update campaign metrics
- handle_failure(error): Log error, schedule retry or mark failed
- should_retry(): Check if retry_count < max_retries
- append_optout_footer(): Add "Reply STOP" text

## Collaborators
- Campaign: Source content and metrics updates
- Customer: SMS recipient data
- QRCode: Generate short URL for QR display
- SMSService: Twilio API integration
- CampaignAnalytics: Update send metrics

## Sequences
- seq-campaign-send.md: Process SMS queue
- seq-sms-retry.md: Handle failed SMS retry
