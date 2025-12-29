# Sequence: Email Retry
**Source Spec:** phase-2-campaign-management.md

## Participants
- CeleryWorker: Background task processor
- EmailQueueTask: Celery task for email
- EmailService: SendGrid integration
- CampaignAnalytics: Metrics tracking
- Database: Persistence layer

## Sequence
```
  CeleryWorker       EmailQueueTask        EmailService      CampaignAnalytics        Database
       |                   |                    |                    |                    |
       |  execute()        |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |                   | send_email()       |                    |                    |
       |                   |------------------->|                    |                    |
       |                   |                    |                    |                    |
       |                   |                    | SendGrid API error |                    |
       |                   |                    |----+               |                    |
       |                   |                    |    |               |                    |
       |                   |                    |<---+               |                    |
       |                   |                    |                    |                    |
       |                   |<-------------------|                    |                    |
       |                   |  error (429/500)   |                    |                    |
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
       |                   | send_email()       |                    |                    |
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
       |                   |                    |                    | UPDATE emails_failed
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
- Campaign continues even with individual failures
