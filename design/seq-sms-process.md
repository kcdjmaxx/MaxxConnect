# Sequence: SMS Process (Worker)
**Source Spec:** phase-2-campaign-management.md

## Participants
- CeleryWorker: Background task processor
- SMSQueueTask: Celery task for SMS
- RateLimiter: Rate limiting service
- Campaign: Domain model entity
- Customer: Target recipient
- QRCode: Customer's QR code
- SMSService: Twilio integration
- CampaignAnalytics: Metrics tracking
- Database: Persistence layer

## Sequence
```
  CeleryWorker        SMSQueueTask         RateLimiter          Campaign           SMSService           Database
       |                   |                    |                    |                    |                    |
       |  pick task        |                    |                    |                    |                    |
       |------------------>|                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | check_sms_rate()   |                    |                    |                    |
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
       |                   | render_sms()       |                    |                    |                    |
       |                   |----+               |                    |                    |                    |
       |                   |    | include short URL                  |                    |                    |
       |                   |<---+               |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | append_optout_footer()                  |                    |                    |
       |                   |----+               |                    |                    |                    |
       |                   |    |               |                    |                    |                    |
       |                   |<---+               |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | validate_length()  |                    |                    |                    |
       |                   |----+               |                    |                    |                    |
       |                   |    | <= 160 chars  |                    |                    |                    |
       |                   |<---+               |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | send_sms()         |                    |                    |                    |
       |                   |------------------------------------------------------>       |                    |
       |                   |                    |                    |                    |                    |
       |                   |                    |                    |                    | Twilio API         |
       |                   |                    |                    |                    |----+               |
       |                   |                    |                    |                    |    |               |
       |                   |                    |                    |                    |<---+               |
       |                   |                    |                    |                    |                    |
       |                   |<------------------------------------------------------|      |                    |
       |                   |  success           |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | increment_sms_count()                   |                    |                    |
       |                   |------------------->|                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | update_metrics()   |                    |                    |                    |
       |                   |------------------------------------+    |                    |                    |
       |                   |                    |               |    |                    |                    |
       |                   |<-----------------------------------+    |                    |                    |
       |                   |                    |                    |                    |                    |
       |<------------------|                    |                    |                    |                    |
       |  task complete    |                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
```

## Notes
- SMS rate limit lower than email (default: 10/min vs 100/min)
- Message includes short URL to QR code display page
- Opt-out footer "Reply STOP to unsubscribe" always appended
- Total length must be <= 160 characters
- Customer must have sms_subscribed=True and valid phone
