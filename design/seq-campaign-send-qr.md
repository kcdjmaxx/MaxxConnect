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
- QR image rendered as PNG using python-qrcode library
- Image encoded as base64 for inline email embedding
- Each customer gets exactly one unique QR code per campaign

## Template Rendering
- Template uses conditional: `{% if qr_code_base64 %}...{% endif %}`
- QR code displayed in visually distinct section
- Same template works for both QR and non-QR campaigns

## Notes
- QR codes generated inline during send (not pre-generated)
- Each QR code persisted to database before email send
- Failure to generate QR code should skip that recipient (log error)
- Campaign status locked after send (has_qr_code immutable)
- Test mode: Generates QR code for test email address
