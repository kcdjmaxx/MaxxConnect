# QRCode
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- id: Unique QR code identifier (primary key)
- campaign_id: Foreign key to Campaign
- customer_id: Foreign key to Customer
- token: Unique cryptographic token (format: {campaign_id}-{customer_id}-{hash})
- created_at: Generation timestamp
- expires_at: Expiration timestamp
- usage_count: Number of times redeemed (default: 0)
- max_usage: Maximum allowed redemptions (default: 1)
- redeemed_at: Timestamp of first redemption

### Does
- is_valid(): Check if not expired and under max usage
- is_expired(): Check if current time > expires_at
- can_redeem(): Check usage_count < max_usage
- increment_usage(): Mark as used, increment counter
- get_short_url(): Generate shortened URL for SMS display

## Collaborators
- Campaign: Parent campaign this QR code belongs to
- Customer: Customer this QR code is assigned to
- QRCodeGenerator: Creates new QR code instances

## Sequences
- seq-qr-generate.md: Generate QR codes for campaign
- seq-qr-validate.md: Validate QR code during redemption (Phase 3)
