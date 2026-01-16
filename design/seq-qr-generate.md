---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# Sequence: QR Code Generate
**Source Spec:** phase-2-campaign-management.md

## Participants
- CampaignManager: Service orchestrating campaign lifecycle
- QRCodeGenerator: Service generating QR codes
- QRCode: Domain model entity
- Campaign: Source campaign
- Customer: Target customer
- Database: Persistence layer
- secrets: Python cryptographic module

## Sequence
```
  CampaignManager     QRCodeGenerator         QRCode             Campaign            secrets            Database
       |                   |                    |                    |                    |                    |
       |  generate_batch() |                    |                    |                    |                    |
       |------------------>|                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | get expiration_days|                    |                    |                    |
       |                   |----------------------------------->     |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |<-----------------------------------|    |                    |                    |
       |                   |  qr_expiration_days|                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | calculate_expiration()                  |                    |                    |
       |                   |----+               |                    |                    |                    |
       |                   |    |               |                    |                    |                    |
       |                   |<---+               |                    |                    |                    |
       |                   |  expires_at        |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |======= LOOP for each customer ==========================================          |
       |                   |                    |                    |                    |                    |
       |                   | token_bytes()      |                    |                    |                    |
       |                   |------------------------------------------------------>       |                    |
       |                   |                    |                    |                    |                    |
       |                   |<------------------------------------------------------|      |                    |
       |                   |  random_hash       |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | generate_token()   |                    |                    |                    |
       |                   |----+               |                    |                    |                    |
       |                   |    | format: campaign_id-customer_id-hash                    |                    |
       |                   |<---+               |                    |                    |                    |
       |                   |  token             |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   | new QRCode()       |                    |                    |                    |
       |                   |------------------->|                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |                   |======= END LOOP ================================================                  |
       |                   |                    |                    |                    |                    |
       |                   | bulk INSERT        |                    |                    |                    |
       |                   |---------------------------------------------------------------------------->      |
       |                   |                    |                    |                    |                    |
       |                   |<----------------------------------------------------------------------------|
       |                   |  qr_code_ids       |                    |                    |                    |
       |                   |                    |                    |                    |                    |
       |<------------------|                    |                    |                    |                    |
       |  qr_codes[]       |                    |                    |                    |                    |
       |                   |                    |                    |                    |                    |
```

## Notes
- Token format: `{campaign_id}-{customer_id}-{16-byte-hex-hash}`
- Uses `secrets.token_hex(16)` for cryptographic randomness
- Each customer gets exactly one QR code per campaign
- Expiration: 30 days from creation (DEFAULT_EXPIRATION_DAYS)

## Current Implementation (Jan 2026)
QR codes are generated **on-demand during email sends** rather than batch pre-generation:

1. `build_template_vars()` in email_task.py checks campaign.has_qr_code
2. Calls `get_existing_qr_code()` to check if QR already exists
3. If not, calls `create_qr_code()` to generate and persist
4. Returns QR bytes for CID attachment

**Functions in qr_generator.py:**
- `generate_token(campaign_id, customer_id)` - Create unique token
- `generate_qr_image(url)` - Render QR as PNG bytes
- `create_qr_code(db, campaign, customer, base_url)` - Generate and persist
- `get_existing_qr_code(db, campaign_id, customer_id)` - Check existence
- `regenerate_bytes(qr_code, base_url)` - Regenerate PNG for existing QR
- `generate_content_id(campaign_id, customer_id)` - Create CID for email

**Future:** Bulk pre-generation may be added for very large campaigns.
