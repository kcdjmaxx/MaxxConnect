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
