# Phase 2: Campaign Management System

**Status:** Level 1 Specification
**Date:** 2025-12-18
**Dependencies:** Phase 1 (Email/SMS integration, CSV import, unsubscribe management)

## Overview

Phase 2 extends the basic email/SMS functionality into a full campaign management system with personalized QR code generation, customer segmentation, asynchronous sending with rate limiting, and comprehensive tracking. This transforms the platform from a simple broadcast tool into a sophisticated marketing system.

## Business Requirements

### 1. QR Code Generation & Personalization

**Requirement:** Each customer receives a unique QR code with their email/SMS that can be scanned for deal redemption.

**Rationale:**
- Enables tracking of individual redemptions (which customers actually used the deal)
- Prevents coupon sharing/fraud (one QR code per customer)
- Provides analytics on conversion rates (emails sent vs. deals redeemed)
- Links digital marketing to physical store visits

**Specifications:**
- QR codes must be cryptographically unique per customer per campaign
- Token format: `{campaign_id}-{customer_id}-{secure_random_hash}`
- QR codes must be embedded in email templates as base64-encoded images
- SMS messages must include a short URL that displays the QR code on mobile
- QR codes must have expiration dates (configurable per campaign)
- System must prevent duplicate redemptions (track usage count per QR code)

**Security Requirements:**
- Random hash must be cryptographically secure (not predictable)
- QR validation must occur server-side only (iOS app cannot validate locally)
- Tokens must be stored in database for validation during redemption
- Expired QR codes must be rejected during redemption

**Example Use Case:**
> Business creates "20% off pizza" campaign. Customer Alice receives email with embedded QR code. She visits restaurant, shows QR code, staff scans with iOS app, system validates token and marks as redeemed. If Alice tries to use the same QR code again, system rejects it.

---

### 2. Customer Segmentation & Targeting

**Requirement:** Business can organize customers into segments (tags) and target specific groups with campaigns.

**Rationale:**
- Not all customers want all promotions (pizza lovers vs. salad lovers)
- Reduces unsubscribe rates by sending relevant offers only
- Enables targeted marketing (VIP customers, new customers, lapsed customers)
- Improves campaign effectiveness (higher redemption rates from relevant audiences)

**Specifications:**
- Customers can have multiple tags (comma-separated list)
- Tags are assigned during CSV import or manually added per customer
- Campaign creation UI allows selecting target segments (e.g., "Send only to customers tagged: VIP, pizza-lovers")
- Special "ALL" segment sends to entire customer list
- Tags must be case-insensitive (normalize to lowercase during storage)
- System must show customer count per segment before campaign send

**Example Tags:**
- `vip`, `new-customer`, `inactive-6months`, `pizza-lover`, `salad-enthusiast`, `frequent-visitor`

**Example Use Case:**
> Business wants to re-engage customers who haven't visited in 6 months. They create campaign targeting segment `inactive-6months` with special "We miss you! 30% off your next visit" offer. Only 150 customers with that tag receive the email, not the entire 5,000-customer list.

---

### 3. Asynchronous Campaign Queue with Rate Limiting

**Requirement:** Emails and SMS must be sent through a background queue system that respects rate limits to avoid spam filters and service provider throttling.

**Rationale:**
- SendGrid/Twilio have rate limits (e.g., 100 emails/second for free tier)
- Sending 5,000 emails instantly triggers spam filters and blacklisting
- Gradual sending (e.g., 500 emails/hour) appears more legitimate to email providers
- Background queue prevents Flask app from blocking during large campaign sends
- Queue system enables retry logic for failed sends

**Specifications:**

**Queue Technology:**
- Use Celery (Python task queue) with Redis as message broker
- Flask app creates campaign and enqueues tasks
- Celery workers process email/SMS sending asynchronously

**Rate Limiting:**
- Configurable send rate per campaign (default: 100 emails/minute, 10 SMS/minute)
- System must track sending velocity and throttle if exceeding limits
- Must respect SendGrid/Twilio API rate limits (avoid 429 errors)
- Email batch sending: process in chunks of 50-100 emails at a time

**Retry Logic:**
- Failed sends (network errors, API errors) must retry up to 3 times with exponential backoff
- After 3 failures, mark send as "permanently failed" and log error
- Track failed sends per campaign for analytics

**Campaign Status Tracking:**
- Campaign states: `draft`, `queued`, `sending`, `completed`, `failed`
- Track progress: `emails_sent`, `emails_failed`, `sms_sent`, `sms_failed`
- Real-time progress updates in admin UI (e.g., "Sending: 1,243 / 5,000 emails sent")

**Example Use Case:**
> Business creates campaign for 5,000 customers. Flask app creates campaign record, enqueues 5,000 email tasks to Celery, and returns immediately. Over the next hour, Celery workers send emails at 100/minute rate. Admin dashboard shows live progress. If SendGrid returns error for 10 emails, system retries those 3 times before marking as failed. After 50 minutes, campaign completes with 4,990 successful sends and 10 permanent failures.

---

### 4. Campaign Analytics & Tracking

**Requirement:** Business can view detailed analytics for each campaign including send metrics and (future) redemption rates.

**Rationale:**
- Understand campaign effectiveness (open rates, redemption rates)
- Identify which customer segments respond best
- Optimize future campaigns based on data
- Justify marketing ROI to business stakeholders

**Phase 2 Metrics (Send Tracking):**
- Total emails sent / failed (with failure reasons)
- Total SMS sent / failed
- Customers targeted (total count, breakdown by segment)
- Send date/time and completion time
- Average send rate (emails per minute)

**Phase 3 Metrics (Redemption Tracking - Future):**
- QR codes scanned (redemption count)
- Redemption rate (% of customers who redeemed)
- Redemption timeline (when customers redeemed after receiving email)
- Revenue impact (if deal value tracked)

**UI Requirements:**
- Campaign list view: shows all campaigns with status, date, send counts
- Campaign detail view: shows full analytics for single campaign
- Export functionality: download campaign report as CSV

**Example Use Case:**
> Business views analytics for "20% off pizza" campaign sent last week. Report shows: 5,000 emails sent, 4,990 successful, 10 failed (bounce), 2 opt-outs. In Phase 3, report will also show: 1,200 QR codes scanned (24% redemption rate), average redemption occurred 2.3 days after email sent.

---

## Non-Functional Requirements

### Performance
- Campaign creation must complete in under 5 seconds (queuing tasks, not sending)
- Queue must handle bursts of 10,000+ tasks without memory issues
- Admin dashboard must load campaign status within 2 seconds

### Scalability
- System must support campaigns up to 50,000 customers
- Queue workers must be horizontally scalable (add more workers = faster sending)
- Redis must persist queue state (survive server restarts without losing tasks)

### Reliability
- Failed sends must not crash the queue worker
- Queue must survive Redis restarts (persistent storage)
- Campaign state must be recoverable after system crash

### Security
- QR token generation must use `secrets` module (cryptographically secure)
- QR validation must prevent timing attacks (constant-time comparison)
- Campaign creation must validate segment names (prevent injection attacks)

---

## Database Schema Changes

**New Table: `campaigns`**
- `id` (primary key)
- `name` (campaign title)
- `subject` (email subject line)
- `email_content` (HTML email body with Jinja2 placeholders)
- `sms_content` (SMS message text)
- `target_segments` (comma-separated tags, or "ALL")
- `qr_expiration_days` (days until QR codes expire)
- `send_rate_limit_emails` (emails per minute)
- `send_rate_limit_sms` (SMS per minute)
- `status` (draft/queued/sending/completed/failed)
- `created_at`, `sent_at`, `completed_at`
- `total_targeted`, `emails_sent`, `emails_failed`, `sms_sent`, `sms_failed`

**New Table: `qr_codes`**
- `id` (primary key)
- `campaign_id` (foreign key to campaigns)
- `customer_id` (foreign key to customers)
- `token` (unique cryptographic token)
- `created_at`, `expires_at`
- `usage_count` (default 0, increment on redemption)
- `max_usage` (default 1, configurable per campaign)
- `redeemed_at` (timestamp of first redemption)

**Modified Table: `customers`**
- Add `segments` field (comma-separated tags)

---

## Phase 2 Workflow

1. **Business creates campaign:**
   - Enters campaign name, subject, email/SMS content
   - Selects target segments (or "ALL")
   - Configures QR expiration (default: 30 days)
   - Sets send rate limits (default: 100 emails/min, 10 SMS/min)
   - Saves as `draft`

2. **Business previews campaign:**
   - System shows sample email with QR code embedded
   - System shows sample SMS with short URL
   - System displays customer count for selected segments

3. **Business sends campaign:**
   - System generates QR codes for all targeted customers
   - System creates Celery tasks for each customer
   - System marks campaign as `queued`
   - Returns immediately (does not block)

4. **Background queue processes sends:**
   - Celery workers pick up tasks from Redis queue
   - Send emails via SendGrid, SMS via Twilio
   - Respect rate limits (throttle sending)
   - Retry failures up to 3 times
   - Update campaign progress in database

5. **Campaign completes:**
   - All tasks processed
   - System marks campaign as `completed`
   - Business views analytics in admin dashboard

---

## Success Criteria

Phase 2 is complete when:
- [x] Businesses can create campaigns with segment targeting
- [x] System generates unique QR codes per customer per campaign
- [x] Emails include embedded QR codes as base64 images
- [x] SMS includes short URLs to QR code display page
- [x] Celery queue sends emails/SMS asynchronously with rate limiting
- [x] Admin dashboard shows real-time campaign progress
- [x] Campaign analytics display send metrics (sent/failed counts)
- [x] System prevents duplicate redemptions (Phase 3 validation)
- [x] Failed sends retry automatically up to 3 times
- [x] QR codes have expiration dates enforced during validation

---

## Out of Scope (Phase 3+)

- iOS QR scanner app (Phase 3)
- Redemption validation API (Phase 3)
- A/B testing for subject lines (Phase 4)
- Email open rate tracking (Phase 4)
- Bounce handling automation (Phase 4)
- Customer import via API (Phase 4)
