# Test Design: QRCode

**Source Specs**: specs/phase-2-campaign-management.md
**CRC Cards**: crc-QRCode.md, crc-QRCodeGenerator.md
**Sequences**: seq-qr-generate.md

## Overview

Tests for QR code generation, token uniqueness, validation, and expiration handling.

## Test Cases

### Test: Generate unique token

**Purpose**: Verify token format and uniqueness

**Input**:
- campaign_id: 123
- customer_id: 456

**References**:
- CRC: crc-QRCodeGenerator.md - "Does: generate_token()"
- Sequence: seq-qr-generate.md

**Expected Results**:
- Token format: "123-456-{16-byte-hex}"
- Token is cryptographically random
- Same inputs generate different tokens (not deterministic)

---

### Test: Token cryptographic security

**Purpose**: Verify tokens use secure random generation

**Input**:
- Generate 1000 tokens
- Analyze randomness distribution

**References**:
- CRC: crc-QRCodeGenerator.md - "Collaborators: secrets"

**Expected Results**:
- Tokens use secrets.token_hex()
- No predictable patterns
- Hash portion is 32 hex characters (16 bytes)

---

### Test: Generate QR image

**Purpose**: Verify QR code image generation

**Input**:
- Valid token string

**References**:
- CRC: crc-QRCodeGenerator.md - "Does: generate_qr_image()"
- CRC: crc-QRCodeGenerator.md - "Does: encode_base64()"

**Expected Results**:
- PNG image generated
- Image is scannable QR code
- Base64 encoding valid
- Can be embedded in HTML img tag

---

### Test: Batch QR generation performance

**Purpose**: Verify efficient generation for large campaigns

**Input**:
- Campaign with 5000 customers

**References**:
- CRC: crc-QRCodeGenerator.md - "Does: generate_batch()"
- Sequence: seq-qr-generate.md

**Expected Results**:
- All QR codes generated
- Bulk insert to database
- Completes in reasonable time (<5 seconds)

---

### Test: QR code expiration calculation

**Purpose**: Verify expiration dates calculated correctly

**Input**:
- Campaign with qr_expiration_days: 30
- Campaign start time: 2024-01-15 12:00

**References**:
- CRC: crc-QRCodeGenerator.md - "Does: calculate_expiration()"
- CRC: crc-QRCode.md - "Knows: expires_at"

**Expected Results**:
- expires_at = 2024-02-14 12:00
- Expiration stored in database

---

### Test: QR validity check (not expired)

**Purpose**: Verify valid QR passes validation

**Input**:
- QR code with expires_at in future
- usage_count: 0
- max_usage: 1

**References**:
- CRC: crc-QRCode.md - "Does: is_valid()"
- CRC: crc-QRCode.md - "Does: can_redeem()"

**Expected Results**:
- is_valid() returns True
- is_expired() returns False
- can_redeem() returns True

---

### Test: QR validity check (expired)

**Purpose**: Verify expired QR fails validation

**Input**:
- QR code with expires_at in past

**References**:
- CRC: crc-QRCode.md - "Does: is_expired()"
- CRC: crc-QRCode.md - "Does: is_valid()"

**Expected Results**:
- is_expired() returns True
- is_valid() returns False
- Appropriate error message

---

### Test: QR validity check (max usage exceeded)

**Purpose**: Verify over-used QR fails validation

**Input**:
- QR code with usage_count: 1, max_usage: 1

**References**:
- CRC: crc-QRCode.md - "Does: can_redeem()"
- CRC: crc-QRCode.md - "Does: is_valid()"

**Expected Results**:
- can_redeem() returns False
- is_valid() returns False
- Appropriate error message

---

### Test: Increment usage count

**Purpose**: Verify usage tracking on redemption

**Input**:
- Valid QR code with usage_count: 0

**References**:
- CRC: crc-QRCode.md - "Does: increment_usage()"
- CRC: crc-QRCode.md - "Knows: redeemed_at"

**Expected Results**:
- usage_count incremented to 1
- redeemed_at timestamp set
- Database updated

---

### Test: Generate short URL

**Purpose**: Verify short URL generation for SMS

**Input**:
- QR token

**References**:
- CRC: crc-QRCode.md - "Does: get_short_url()"
- CRC: crc-QRCodeGenerator.md - "Does: generate_short_url()"

**Expected Results**:
- URL format: {base_url}/qr/{token}
- URL is valid and accessible
- URL displays QR code image

---

### Test: Duplicate prevention

**Purpose**: Verify one QR per customer per campaign

**Input**:
- Attempt to create second QR for same customer/campaign

**References**:
- CRC: crc-QRCode.md - "Knows: campaign_id, customer_id"

**Expected Results**:
- Database constraint prevents duplicate
- Error raised on duplicate attempt

## Coverage Summary

**Responsibilities Covered**:
- Token generation and format
- Cryptographic security
- Image generation and encoding
- Batch processing
- Expiration handling
- Validity checks
- Usage tracking
- Short URL generation

**Scenarios Covered**:
- seq-qr-generate.md: Full flow

**Gaps**:
- QR validation during redemption (Phase 3)
- Multi-use QR codes (future feature)
