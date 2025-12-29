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
- execute(): Send email via SendGrid
- render_email(campaign, customer, qr_code): Generate personalized HTML
- handle_success(): Mark task complete, update campaign metrics
- handle_failure(error): Log error, schedule retry or mark failed
- should_retry(): Check if retry_count < max_retries

## Collaborators
- Campaign: Source content and metrics updates
- Customer: Email recipient data
- QRCode: Embed QR image in email
- EmailService: SendGrid API integration
- CampaignAnalytics: Update send metrics

## Sequences
- seq-campaign-send.md: Process email queue
- seq-email-retry.md: Handle failed email retry
