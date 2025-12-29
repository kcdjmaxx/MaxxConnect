# Test Design: Analytics

**Source Specs**: specs/phase-2-campaign-management.md
**CRC Cards**: crc-CampaignAnalytics.md
**Sequences**: seq-campaign-analytics.md

## Overview

Tests for campaign analytics, metrics calculation, reporting, and data export.

## Test Cases

### Test: Get campaign summary

**Purpose**: Verify summary returns all key metrics

**Input**:
- Completed campaign with known metrics

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: get_campaign_summary()"
- Sequence: seq-campaign-analytics.md

**Expected Results**:
- Returns total_targeted, emails_sent, emails_failed
- Returns sms_sent, sms_failed
- Returns status, sent_at, completed_at

---

### Test: Calculate send rate

**Purpose**: Verify send velocity calculation

**Input**:
- Campaign: 5000 emails sent in 50 minutes

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: calculate_send_rate()"

**Expected Results**:
- Returns 100 emails/minute
- Calculated from sent_at to completed_at
- Handles edge cases (0 duration)

---

### Test: Calculate completion time

**Purpose**: Verify duration calculation

**Input**:
- sent_at: 2024-01-15 12:00
- completed_at: 2024-01-15 12:50

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: calculate_completion_time()"

**Expected Results**:
- Returns 50 minutes
- Formatted appropriately for UI
- Handles in-progress campaigns

---

### Test: Get segment breakdown

**Purpose**: Verify metrics per segment

**Input**:
- Campaign targeting vip (150), pizza-lover (2300)
- Various success/failure counts per segment

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: get_segment_breakdown()"

**Expected Results**:
- Returns per-segment metrics
- Handles overlapping customers correctly
- Accurate failure attribution

---

### Test: Get failure reasons

**Purpose**: Verify failure aggregation

**Input**:
- Campaign with 10 failed emails
- 6 "invalid address", 3 "mailbox full", 1 "server error"

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: get_failure_reasons()"

**Expected Results**:
- Returns aggregated counts per reason
- Sorted by count descending
- Includes all unique reasons

---

### Test: Export report CSV

**Purpose**: Verify CSV export functionality

**Input**:
- Completed campaign with full metrics

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: export_report_csv()"

**Expected Results**:
- Valid CSV file generated
- Contains all summary metrics
- Contains segment breakdown
- Contains failure reasons
- Proper headers and formatting

---

### Test: Update metrics atomically

**Purpose**: Verify concurrent metric updates

**Input**:
- Multiple workers updating emails_sent simultaneously

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: update_metrics()"

**Expected Results**:
- Atomic increment (no lost updates)
- Thread-safe operation
- Database transaction handles concurrency

---

### Test: Analytics for in-progress campaign

**Purpose**: Verify partial metrics during send

**Input**:
- Campaign in "sending" status
- 2500/5000 emails sent

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: get_campaign_summary()"

**Expected Results**:
- Returns current progress
- completed_at is null
- Progress percentage accurate

---

### Test: Analytics for failed campaign

**Purpose**: Verify metrics for fully failed campaign

**Input**:
- Campaign where all sends failed

**References**:
- CRC: crc-CampaignAnalytics.md - "Does: get_campaign_summary()"

**Expected Results**:
- emails_sent = 0
- emails_failed = total_targeted
- Status shows "failed"
- Failure reasons available

---

### Test: QR code count

**Purpose**: Verify QR codes counted for campaign

**Input**:
- Campaign with 5000 QR codes generated

**References**:
- Sequence: seq-campaign-analytics.md

**Expected Results**:
- Returns accurate QR code count
- Matches targeted customer count

## Coverage Summary

**Responsibilities Covered**:
- Summary metrics retrieval
- Send rate calculation
- Duration calculation
- Segment breakdown
- Failure aggregation
- CSV export
- Atomic updates
- In-progress metrics

**Scenarios Covered**:
- seq-campaign-analytics.md: Full flow

**Gaps**:
- Redemption analytics (Phase 3)
- Open rate tracking (Phase 4)
- Revenue attribution
