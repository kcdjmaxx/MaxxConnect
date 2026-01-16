---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# QRCodeGenerator
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- base_url: Application base URL for QR links
- token_hash_length: Length of secure random hash (default: 16 bytes)

### Does
- generate_token(campaign_id, customer_id): Create unique secure token
- generate_qr_image(url): Render QR code as PNG bytes
- encode_base64(qr_image): Convert image bytes to base64 string
- create_qr_code(db, campaign, customer, base_url): Generate and persist QR code entity
- get_existing_qr_code(db, campaign_id, customer_id): Check if QR already exists
- regenerate_base64(qr_code, base_url): Regenerate base64 from existing token
- regenerate_bytes(qr_code, base_url): Regenerate PNG bytes for CID attachment
- generate_content_id(campaign_id, customer_id): Create unique CID for email reference
- generate_batch(campaign, customers): Bulk generate QR codes efficiently (planned)
- generate_short_url(token): Create shortened URL for SMS (planned)
- calculate_expiration(campaign): Compute expires_at from campaign settings

## Collaborators
- QRCode: Creates QR code entities
- Campaign: Reads expiration settings
- Customer: Associates QR codes with customers
- secrets: Python module for cryptographic randomness

## Sequences
- seq-qr-generate.md: Generate QR codes for campaign customers
- seq-campaign-send.md: QR generation during campaign send
