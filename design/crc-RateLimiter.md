# RateLimiter
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- redis_client: Redis connection for rate state
- email_rate_limit: Emails per minute (default: 100)
- sms_rate_limit: SMS per minute (default: 10)
- window_size: Rate limit window in seconds (60)

### Does
- check_email_rate(campaign_id): Check if email can be sent
- check_sms_rate(campaign_id): Check if SMS can be sent
- increment_email_count(campaign_id): Record email sent
- increment_sms_count(campaign_id): Record SMS sent
- get_current_rate(campaign_id, type): Return current send velocity
- wait_if_needed(campaign_id, type): Block until rate allows send
- reset_counters(campaign_id): Clear rate counters (on campaign complete)

## Collaborators
- EmailQueueTask: Rate check before email send
- SMSQueueTask: Rate check before SMS send
- Campaign: Source rate limit configuration

## Sequences
- seq-campaign-send.md: Rate limiting during send
