# Sequence: SMS Retry
**Source Spec:** phase-2-campaign-management.md

## Participants
- CeleryWorker: Background task processor
- SMSQueueTask: Celery task for SMS
- SMSService: Twilio integration
- CampaignAnalytics: Metrics tracking
- Database: Persistence layer

## Sequence
```
  CeleryWorker        SMSQueueTask         SMSService       CampaignAnalytics        Database
       |                   |                    |                    |                    |
       |  execute()        |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |                   | send_sms()         |                    |                    |
       |                   |------------------->|                    |                    |
       |                   |                    |                    |                    |
       |                   |                    | Twilio API error   |                    |
       |                   |                    |----+               |                    |
       |                   |                    |    |               |                    |
       |                   |                    |<---+               |                    |
       |                   |                    |                    |                    |
       |                   |<-------------------|                    |                    |
       |                   |  error (rate/temp) |                    |                    |
       |                   |                    |                    |                    |
       |                   | handle_failure()   |                    |                    |
       |                   |----+               |                    |                    |
       |                   |    |               |                    |                    |
       |                   |<---+               |                    |                    |
       |                   |                    |                    |                    |
       |                   | should_retry()     |                    |                    |
       |                   |----+               |                    |                    |
       |                   |    | retry < 3     |                    |                    |
       |                   |<---+               |                    |                    |
       |                   |                    |                    |                    |
       |                   | log retry          |                    |                    |
       |                   |---------------------------------------------------------------------------->
       |                   |                    |                    |                    |
       |<------------------|                    |                    |                    |
       |  raise Retry()    |                    |                    |                    |
       |                   |                    |                    |                    |
       |                   |                    |                    |                    |
       | ====== AFTER BACKOFF (2^retry seconds) ======                                    |
       |                   |                    |                    |                    |
       |  execute() again  |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |                   | send_sms()         |                    |                    |
       |                   |------------------->|                    |                    |
       |                   |                    |                    |                    |
       |                   |<-------------------|                    |                    |
       |                   |  success           |                    |                    |
       |                   |                    |                    |                    |
       |                   | update_metrics()   |                    |                    |
       |                   |----------------------------------->     |                    |
       |                   |                    |                    |                    |
       |<------------------|                    |                    |                    |
       |  task complete    |                    |                    |                    |
       |                   |                    |                    |                    |
       |                   |                    |                    |                    |
       | ====== ALTERNATE: MAX RETRIES EXCEEDED ======                                    |
       |                   |                    |                    |                    |
       |                   | should_retry()     |                    |                    |
       |                   |----+               |                    |                    |
       |                   |    | retry >= 3    |                    |                    |
       |                   |<---+               |                    |                    |
       |                   |                    |                    |                    |
       |                   | update_metrics(failed)                  |                    |
       |                   |----------------------------------->     |                    |
       |                   |                    |                    |                    |
       |                   |                    |                    | UPDATE sms_failed  |
       |                   |                    |                    |------------------->|
       |                   |                    |                    |                    |
       |<------------------|                    |                    |                    |
       |  task failed      |                    |                    |                    |
       |                   |                    |                    |                    |
```

## Notes
- Exponential backoff: 2^retry seconds (2s, 4s, 8s)
- After 3 retries, task permanently fails
- Failure reasons logged for analytics
- SMS-specific errors: invalid number, carrier rejection, rate limit
- Campaign continues even with individual failures
