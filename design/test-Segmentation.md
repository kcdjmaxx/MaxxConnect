# Test Design: Segmentation

**Source Specs**: specs/phase-2-campaign-management.md
**CRC Cards**: crc-Customer.md, crc-SegmentManager.md
**Sequences**: seq-segment-filter.md

## Overview

Tests for customer segmentation, tag management, and segment-based filtering.

## Test Cases

### Test: Parse customer segments

**Purpose**: Verify comma-separated segments parsed correctly

**Input**:
- Customer with segments: "vip,pizza-lover,frequent-visitor"

**References**:
- CRC: crc-Customer.md - "Does: get_segments_list()"

**Expected Results**:
- Returns list: ["vip", "pizza-lover", "frequent-visitor"]
- Handles whitespace trimming
- Returns empty list for null segments

---

### Test: Add segment to customer

**Purpose**: Verify segment can be added

**Input**:
- Customer with segments: "vip"
- Add segment: "new-customer"

**References**:
- CRC: crc-Customer.md - "Does: add_segment()"
- CRC: crc-SegmentManager.md - "Does: add_segment_to_customer()"

**Expected Results**:
- segments becomes "vip,new-customer"
- Database updated
- No duplicate tags

---

### Test: Remove segment from customer

**Purpose**: Verify segment can be removed

**Input**:
- Customer with segments: "vip,pizza-lover"
- Remove segment: "vip"

**References**:
- CRC: crc-Customer.md - "Does: remove_segment()"

**Expected Results**:
- segments becomes "pizza-lover"
- Database updated

---

### Test: Check customer has segment

**Purpose**: Verify segment membership check

**Input**:
- Customer with segments: "vip,pizza-lover"
- Check for "vip", "salad", "VIP"

**References**:
- CRC: crc-Customer.md - "Does: has_segment()"

**Expected Results**:
- "vip" returns True
- "salad" returns False
- "VIP" returns True (case-insensitive)

---

### Test: Segment normalization

**Purpose**: Verify tags normalized to lowercase

**Input**:
- Tag: "VIP"
- Tag: " pizza-lover "

**References**:
- CRC: crc-SegmentManager.md - "Does: normalize_segment()"

**Expected Results**:
- "VIP" becomes "vip"
- Whitespace trimmed
- Stored in lowercase

---

### Test: Segment validation

**Purpose**: Verify invalid segments rejected

**Input**:
- Tag: "vip; DROP TABLE customers;"
- Tag: "<script>alert('xss')</script>"
- Tag: "" (empty)

**References**:
- CRC: crc-SegmentManager.md - "Does: validate_segment()"

**Expected Results**:
- SQL injection characters rejected
- HTML/script tags rejected
- Empty strings rejected
- Only alphanumeric and hyphens allowed

---

### Test: Get all unique segments

**Purpose**: Verify unique segment list retrieval

**Input**:
- Database with customers having various segments

**References**:
- CRC: crc-SegmentManager.md - "Does: get_all_segments()"

**Expected Results**:
- Returns deduplicated list
- Sorted alphabetically
- Excludes empty/null

---

### Test: Get segment counts

**Purpose**: Verify customer count per segment

**Input**:
- 150 customers with "vip" segment
- 2300 customers with "pizza-lover" segment

**References**:
- CRC: crc-SegmentManager.md - "Does: get_segment_counts()"

**Expected Results**:
- {"vip": 150, "pizza-lover": 2300}
- Accurate counts
- Updates on customer changes

---

### Test: Filter customers by single segment

**Purpose**: Verify filtering by one segment

**Input**:
- target_segments: "vip"

**References**:
- CRC: crc-SegmentManager.md - "Does: get_customers_by_segments()"
- Sequence: seq-segment-filter.md

**Expected Results**:
- Returns all customers with "vip" segment
- Only subscribed customers included
- Case-insensitive matching

---

### Test: Filter customers by multiple segments

**Purpose**: Verify filtering by multiple segments (OR logic)

**Input**:
- target_segments: "vip,pizza-lover"

**References**:
- CRC: crc-SegmentManager.md - "Does: get_customers_by_segments()"

**Expected Results**:
- Returns customers with vip OR pizza-lover
- Deduplicated (customer in both counted once)
- Only subscribed customers

---

### Test: Filter customers with ALL segment

**Purpose**: Verify ALL returns entire subscribed list

**Input**:
- target_segments: "ALL"

**References**:
- CRC: crc-SegmentManager.md - "Does: get_customers_by_segments()"
- Sequence: seq-segment-filter.md

**Expected Results**:
- Returns all subscribed customers
- Both email and SMS subscribed included
- Unsubscribed excluded

---

### Test: Customer matches segments check

**Purpose**: Verify customer-campaign segment matching

**Input**:
- Customer with segments: "vip,pizza-lover"
- Campaign targeting: "inactive,vip"

**References**:
- CRC: crc-Customer.md - "Does: matches_segments()"

**Expected Results**:
- Returns True (matches "vip")
- Partial match sufficient
- Empty customer segments returns False

---

### Test: Bulk segment assignment

**Purpose**: Verify adding segment to multiple customers

**Input**:
- List of 100 customer IDs
- Tag: "imported-2024-01"

**References**:
- CRC: crc-SegmentManager.md - "Does: bulk_add_segment()"

**Expected Results**:
- All 100 customers updated
- Single database transaction
- Performance acceptable

---

### Test: Subscription filter during segment query

**Purpose**: Verify only subscribed customers returned

**Input**:
- Customer with "vip" segment, subscribed=False

**References**:
- CRC: crc-SegmentManager.md - "Does: get_customers_by_segments()"

**Expected Results**:
- Unsubscribed customer excluded
- SMS-only subscribed included for SMS campaigns
- Email-only subscribed included for email campaigns

## Coverage Summary

**Responsibilities Covered**:
- Segment parsing and formatting
- Add/remove segments
- Segment membership checks
- Normalization and validation
- Segment listing and counting
- Customer filtering by segment
- Bulk operations
- Subscription filtering

**Scenarios Covered**:
- seq-segment-filter.md: Full flow

**Gaps**:
- Segment hierarchy/nesting
- Auto-tagging based on behavior
