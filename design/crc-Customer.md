---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# Customer
**Source Spec:** phase-2-campaign-management.md (extends Phase 1)

## Responsibilities
### Knows
- id: Unique customer identifier (primary key)
- email: Encrypted email address (Fernet AES-128)
- email_hash: SHA-256 hash of email for deterministic lookups
- phone: Encrypted phone number in E.164 format
- phone_hash: SHA-256 hash of phone for deterministic lookups
- name: Customer display name
- subscribed: Email subscription status
- opted_in_date: Email opt-in timestamp
- unsubscribed_date: Email opt-out timestamp
- sms_subscribed: SMS subscription status
- sms_opted_in_date: SMS opt-in timestamp
- sms_unsubscribed_date: SMS opt-out timestamp
- segments: Comma-separated tags (Phase 2 addition)
- created_at: Record creation timestamp
- updated_at: Last modification timestamp

### Does
- find_by_email(db, email): Class method - find customer by email using hash lookup
- find_by_phone(db, phone): Class method - find customer by phone using hash lookup
- get_unsubscribe_token(): Generate secure unsubscribe token
- get_sms_optout_token(): Generate secure SMS opt-out token
- get_segments_list(): Parse segments into list
- add_segment(tag): Add new segment tag
- remove_segment(tag): Remove segment tag
- has_segment(tag): Check if customer has specific tag
- matches_segments(target_segments): Check if customer matches any target segments

## Collaborators
- Campaign: Receives campaigns based on segment membership
- QRCode: Has unique QR codes per campaign
- SegmentManager: Manages segment operations

## Sequences
- seq-segment-filter.md: Filter customers by segment
- seq-campaign-send.md: Receive campaign messages
