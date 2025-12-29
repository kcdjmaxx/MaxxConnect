# QRCodeGenerator
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- base_url: Application base URL for QR links
- token_hash_length: Length of secure random hash (default: 16 bytes)

### Does
- generate_token(campaign_id, customer_id): Create unique secure token
- generate_qr_image(token): Render QR code as image
- encode_base64(qr_image): Convert image to base64 for email embedding
- create_qr_code(campaign, customer): Generate and persist QR code entity
- generate_batch(campaign, customers): Bulk generate QR codes efficiently
- generate_short_url(token): Create shortened URL for SMS
- calculate_expiration(campaign): Compute expires_at from campaign settings

## Collaborators
- QRCode: Creates QR code entities
- Campaign: Reads expiration settings
- Customer: Associates QR codes with customers
- secrets: Python module for cryptographic randomness

## Sequences
- seq-qr-generate.md: Generate QR codes for campaign customers
- seq-campaign-send.md: QR generation during campaign send
