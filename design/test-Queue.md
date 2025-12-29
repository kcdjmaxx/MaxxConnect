# Test Design: Queue System

**Source Specs**: specs/phase-2-campaign-management.md
**CRC Cards**: crc-CeleryApp.md, crc-EmailQueueTask.md, crc-SMSQueueTask.md, crc-RateLimiter.md
**Sequences**: seq-email-process.md, seq-sms-process.md, seq-email-retry.md

## Overview

Tests for Celery task queue, email/SMS processing, rate limiting, and retry logic.

## Test Cases

### Test: Celery app configuration

**Purpose**: Verify Celery connects to Redis broker

**Input**:
- Redis connection URL
- Task queue configuration

**References**:
- CRC: crc-CeleryApp.md - "Does: configure()"

**Expected Results**:
- Connection to Redis established
- Named queues created (email_queue, sms_queue)
- Workers can register

---

### Test: Email task execution success

**Purpose**: Verify email task sends successfully

**Input**:
- Valid campaign_id, customer_id, qr_code_id
- Customer with valid email address

**References**:
- CRC: crc-EmailQueueTask.md - "Does: execute()"
- Sequence: seq-email-process.md

**Expected Results**:
- Email rendered with QR code embedded
- SendGrid API called
- Task marked complete
- Campaign emails_sent incremented

---

### Test: SMS task execution success

**Purpose**: Verify SMS task sends successfully

**Input**:
- Valid campaign_id, customer_id, qr_code_id
- Customer with valid phone number

**References**:
- CRC: crc-SMSQueueTask.md - "Does: execute()"
- Sequence: seq-sms-process.md

**Expected Results**:
- SMS rendered with short URL
- Opt-out footer appended
- Twilio API called
- Task marked complete
- Campaign sms_sent incremented

---

### Test: SMS length validation

**Purpose**: Verify SMS enforces 160 character limit

**Input**:
- Message content + opt-out footer > 160 chars

**References**:
- CRC: crc-SMSQueueTask.md - "Does: validate_length()"
- CRC: crc-SMSQueueTask.md - "Does: append_optout_footer()"

**Expected Results**:
- Validation error if over limit
- Message truncated or error raised
- Task fails gracefully

---

### Test: Rate limiter blocks when exceeded

**Purpose**: Verify rate limiting prevents burst sending

**Input**:
- Email rate limit: 100/minute
- 150 emails attempted in 1 minute

**References**:
- CRC: crc-RateLimiter.md - "Does: check_email_rate()"
- CRC: crc-RateLimiter.md - "Does: wait_if_needed()"

**Expected Results**:
- First 100 emails send immediately
- Remaining 50 blocked until next window
- Redis counter tracks sends

---

### Test: Rate limiter resets after window

**Purpose**: Verify rate counter resets

**Input**:
- Rate window: 60 seconds
- Wait 60 seconds after hitting limit

**References**:
- CRC: crc-RateLimiter.md - "Knows: window_size"

**Expected Results**:
- Counter resets after window
- New sends allowed
- Redis TTL handles expiration

---

### Test: Email retry on temporary failure

**Purpose**: Verify retry logic for failed sends

**Input**:
- SendGrid returns 429 (rate limit) or 500 (server error)
- retry_count < 3

**References**:
- CRC: crc-EmailQueueTask.md - "Does: handle_failure()"
- CRC: crc-EmailQueueTask.md - "Does: should_retry()"
- Sequence: seq-email-retry.md

**Expected Results**:
- Task re-queued with exponential backoff
- retry_count incremented
- Delay: 2^retry seconds

---

### Test: Email permanent failure after max retries

**Purpose**: Verify task fails permanently after 3 attempts

**Input**:
- retry_count = 3
- Next send attempt fails

**References**:
- CRC: crc-EmailQueueTask.md - "Does: should_retry()"
- Sequence: seq-email-retry.md

**Expected Results**:
- Task marked as permanently failed
- Campaign emails_failed incremented
- Error logged with reason
- No more retries

---

### Test: SMS retry on temporary failure

**Purpose**: Verify SMS retry similar to email

**Input**:
- Twilio returns temporary error
- retry_count < 3

**References**:
- CRC: crc-SMSQueueTask.md - "Does: handle_failure()"

**Expected Results**:
- Task re-queued with backoff
- Same retry logic as email

---

### Test: Email rendering with QR code

**Purpose**: Verify email includes embedded QR image

**Input**:
- Campaign with email_content containing {{ qr_code_base64 }}
- Valid QR code for customer

**References**:
- CRC: crc-EmailQueueTask.md - "Does: render_email()"

**Expected Results**:
- QR code base64 inserted in template
- Customer name personalized
- Unsubscribe link generated

---

### Test: SMS rendering with short URL

**Purpose**: Verify SMS includes QR display URL

**Input**:
- Campaign with sms_content
- Valid QR code for customer

**References**:
- CRC: crc-SMSQueueTask.md - "Does: render_sms()"

**Expected Results**:
- Short URL inserted
- Customer name personalized (if placeholder)
- Opt-out footer appended

---

### Test: Queue length monitoring

**Purpose**: Verify queue status can be queried

**Input**:
- Campaign with 1000 tasks queued

**References**:
- CRC: crc-CeleryApp.md - "Does: get_queue_length()"

**Expected Results**:
- Correct count returned
- Can distinguish email vs SMS queues

---

### Test: Task revocation

**Purpose**: Verify pending tasks can be cancelled

**Input**:
- Campaign paused mid-send
- Tasks still in queue

**References**:
- CRC: crc-CeleryApp.md - "Does: revoke_task()"

**Expected Results**:
- Pending tasks cancelled
- Already-processing tasks complete
- Campaign status updated

---

### Test: Worker crash recovery

**Purpose**: Verify tasks survive worker restart

**Input**:
- Worker processing task
- Worker process killed

**References**:
- CRC: crc-CeleryApp.md - "Knows: broker_url"

**Expected Results**:
- Task remains in queue
- New worker picks up task
- No duplicate sends

## Coverage Summary

**Responsibilities Covered**:
- Celery configuration
- Email task processing
- SMS task processing
- Rate limiting
- Retry logic
- Rendering
- Queue monitoring
- Task cancellation
- Crash recovery

**Scenarios Covered**:
- seq-email-process.md: Full flow
- seq-sms-process.md: Full flow
- seq-email-retry.md: Full flow

**Gaps**:
- Redis cluster failover
- Dead letter queue handling
