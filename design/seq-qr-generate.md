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
- Bulk insert for performance with large campaigns
- Each customer gets exactly one QR code per campaign
- Expiration calculated from campaign start + qr_expiration_days
