---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# Sequence: Campaign Send with QR Code Generation
**Source Spec:** phase-2-campaign-management.md

## Participants
- Admin: Business user sending campaign
- SendConfirmForm: campaign_send_confirm.html template
- FlaskRoute: campaign_send() in app.py
- Campaign: SQLAlchemy model
- Customer: SQLAlchemy model for audience
- QRCodeGenerator: Service for QR code generation
- QRCode: Domain model entity
- EmailService: send_email() function
- Database: SQLite/PostgreSQL persistence

## Precondition
- Campaign.has_qr_code = True

## Sequence
```
     Admin          SendConfirmForm         FlaskRoute           Campaign        QRCodeGenerator         Customer           EmailService          Database
       |                  |                    |                    |                    |                    |                    |                    |
       | confirm send     |                    |                    |                    |                    |                    |                    |
       |----------------->|                    |                    |                    |                    |                    |                    |
       |                  | POST /campaign/send/<id>                |                    |                    |                    |                    |
       |                  |------------------->|                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    | query Campaign     |                    |                    |                    |                    |
       |                  |                    |------------------->|                    |                    |                    |                    |
       |                  |                    |                    |--------------------------------------------------->          |
       |                  |                    |<-------------------|                    |                    |<-------------------------------------------------|
       |                  |                    | campaign           |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    | check has_qr_code  |                    |                    |                    |                    |
       |                  |                    |------------------->|                    |                    |                    |                    |
       |                  |                    |<-------------------|                    |                    |                    |                    |
       |                  |                    | True               |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    | query subscribers by segment           |                    |                    |                    |
       |                  |                    |------------------------------------------------------------>|                    |                    |
       |                  |                    |                    |                    |                    |----------------------------------->          |
       |                  |                    |                    |                    |                    |<-----------------------------------|         |
       |                  |                    |<------------------------------------------------------------|                    |                    |
       |                  |                    | subscribers[]      |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    |======= LOOP for each subscriber ====================================================                  |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    | generate_token()   |                    |                    |                    |                    |
       |                  |                    |----------------------------------->     |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    | create_qr_code(campaign, customer)     |                    |                    |
       |                  |                    |                    |------------------->|                    |                    |                    |
       |                  |                    |                    |                    | secrets.token_hex  |                    |                    |
       |                  |                    |                    |                    |----+               |                    |                    |
       |                  |                    |                    |                    |<---+               |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    | generate_qr_image  |                    |                    |
       |                  |                    |                    |                    |----+               |                    |                    |
       |                  |                    |                    |                    |<---+               |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    | encode_base64      |                    |                    |
       |                  |                    |                    |                    |----+               |                    |                    |
       |                  |                    |                    |                    |<---+               |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    | INSERT QRCode      |                    |                    |
       |                  |                    |                    |                    |-------------------------------------------------------------->|
       |                  |                    |                    |                    |<--------------------------------------------------------------|
       |                  |                    |<-----------------------------------|    |                    |                    |                    |
       |                  |                    | qr_code (with token, base64)       |    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    | render_template_string(html, customer, qr_code_base64)       |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |
       |                  |                    | personalized_html with QR code        |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    | send_email(customer.email, html_with_qr)                    |                    |                    |
       |                  |                    |--------------------------------------------------------------------------->         |                    |
       |                  |                    |                    |                    |                    | SendGrid API       |                    |
       |                  |                    |                    |                    |                    |----+               |                    |
       |                  |                    |                    |                    |                    |<---+               |                    |
       |                  |                    |<---------------------------------------------------------------------------|        |                    |
       |                  |                    | track sent/failed  |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    |======= END LOOP ============================================================================             |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |                    | update campaign status='sent'          |                    |                    |                    |
       |                  |                    |------------------->|                    |                    |                    |                    |
       |                  |                    |                    |--------------------------------------------------------------------->            |
       |                  |                    |                    |<---------------------------------------------------------------------|           |
       |                  |                    |<-------------------|                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |                    |
       | flash "X sent with QR codes"          |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |
```

## QR Code Generation Details
- Token format: `{campaign_id}-{customer_id}-{16-byte-hex-hash}`
- Uses `secrets.token_hex(16)` for cryptographic randomness
- QR image rendered as PNG bytes using python-qrcode library
- Each customer gets exactly one unique QR code per campaign

## CID Embedding (Gmail Compatible)
Base64 data URIs are **blocked by Gmail** for security. The CID approach:

1. **HTML placeholder**: Campaign stores `[[QR_CODE_DATA_URI]]` in html_content
2. **At send time**: Placeholder replaced with `cid:qr-{campaign_id}-{customer_id}`
3. **Attachment**: QR image attached as inline MIME attachment with matching Content-ID
4. **Result**: `<img src="cid:qr-1-2">` displays correctly in Gmail, Apple Mail, Outlook

Content-ID format: `qr-{campaign_id}-{customer_id}` (e.g., `qr-5-123`)

## Template System
- Templates use `<!-- QR_CODE_SECTION -->` comment placeholder
- Campaign creation (if has_qr_code=True): Injects QR HTML with `[[QR_CODE_DATA_URI]]`
- Send time: Replaces `[[QR_CODE_DATA_URI]]` with `cid:{content_id}`
- Same template works for both QR and non-QR campaigns

## Notes
- QR codes generated at send time (not pre-generated)
- Each QR code persisted to database before email send
- Failure to generate QR code logs error but continues (email sent without QR)
- Existing QR codes reused if customer/campaign pair already exists
- Test mode: Generates QR with token `TEST-{campaign_id}-{customer_id}`
