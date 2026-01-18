---
tags:
  - project/mailchimp-clone
  - subject/software-architecture
  - type/sequence-diagram
  - status/implemented
---

# Sequence: QR Code Redemption

**Source Spec:** phase-3-redemption.md
**CRC Cards:** crc-Redemption.md, crc-RedemptionService.md, crc-QRCode.md

## Actors

- Staff: Employee using scanner interface
- StaffScanner: templates/staff_redeem.html (PWA)
- API: app.py routes
- RedemptionService: backend/services/redemption_service.py
- DB: Database (QRCode, Redemption, Customer, Campaign tables)

## Flow: Scan and Validate

```
Staff              StaffScanner           API                    RedemptionService      DB
  |                     |                   |                          |                 |
  |--[scan QR code]---->|                   |                          |                 |
  |                     |                   |                          |                 |
  |                     |--[extract token]->|                          |                 |
  |                     |                   |                          |                 |
  |                     |----GET /api/validate/{token}---------------->|                 |
  |                     |                   |                          |                 |
  |                     |                   |-------validate(token)--->|                 |
  |                     |                   |                          |--[query QRCode]-|
  |                     |                   |                          |<-[QRCode row]---|
  |                     |                   |                          |                 |
  |                     |                   |                          |--[check expiry] |
  |                     |                   |                          |--[check usage]  |
  |                     |                   |                          |                 |
  |                     |                   |                          |--[query Customer]
  |                     |                   |                          |<-[Customer row]-|
  |                     |                   |                          |                 |
  |                     |                   |<--RedemptionResult-------|                 |
  |                     |                   |                          |                 |
  |                     |<--JSON {success, status, data}---------------|                 |
  |                     |                   |                          |                 |
  |<--[show result]----|                   |                          |                 |
  |   (green=valid)    |                   |                          |                 |
  |   (red=invalid)    |                   |                          |                 |
  |   [play sound]     |                   |                          |                 |
  |   [speak result]   |                   |                          |                 |
```

## Flow: Confirm Redemption

```
Staff              StaffScanner           API                    RedemptionService      DB
  |                     |                   |                          |                 |
  |--[tap REDEEM btn]-->|                   |                          |                 |
  |                     |                   |                          |                 |
  |                     |----POST /api/redeem/{token}----------------->|                 |
  |                     |     {method:'scan'}                          |                 |
  |                     |                   |                          |                 |
  |                     |                   |-------redeem(token,...)-->|                 |
  |                     |                   |                          |                 |
  |                     |                   |                          |--[validate()]---|
  |                     |                   |                          |                 |
  |                     |                   |                          |--[increment]----|
  |                     |                   |                          |   usage_count   |
  |                     |                   |                          |                 |
  |                     |                   |                          |--[create]-------|
  |                     |                   |                          |   Redemption    |
  |                     |                   |                          |   record        |
  |                     |                   |                          |                 |
  |                     |                   |                          |--[commit]-------|
  |                     |                   |                          |                 |
  |                     |                   |<--RedemptionResult-------|                 |
  |                     |                   |   {status:'redeemed'}    |                 |
  |                     |                   |                          |                 |
  |                     |<--JSON {success:true}------------------------|                 |
  |                     |                   |                          |                 |
  |<--[show REDEEMED]---|                   |                          |                 |
  |   [play success]   |                   |                          |                 |
  |   [speak "Success"]|                   |                          |                 |
```

## Flow: Customer Views QR Landing Page

```
Customer           Browser                 API                    RedemptionService      DB
  |                   |                      |                          |                 |
  |--[scan QR code]-->|                      |                          |                 |
  |                   |                      |                          |                 |
  |                   |----GET /redeem/{token}------------------------>|                 |
  |                   |                      |                          |                 |
  |                   |                      |-------validate(token)--->|                 |
  |                   |                      |<--RedemptionResult-------|                 |
  |                   |                      |                          |                 |
  |                   |<--render redeem_result.html--------------------|                 |
  |                   |   (shows validity, customer name, campaign)    |                 |
  |                   |                      |                          |                 |
  |<--[see result]----|                      |                          |                 |
  |   "Show this to staff to redeem"         |                          |                 |
```

## Validation States

| State | Condition | UI Display | Sound |
|-------|-----------|------------|-------|
| valid | Code exists, not expired, not used | Green, customer info | Ascending tones |
| not_found | Token not in DB | Red "INVALID" | Descending tones |
| expired | expires_at < now | Red "EXPIRED" | Descending tones |
| already_used | usage_count >= max_usage | Red "ALREADY USED" | Descending tones |

## Implementation Files

- `app.py`: Routes (lines 1680-1800)
- `backend/services/redemption_service.py`: Business logic
- `templates/staff_redeem.html`: PWA scanner interface
- `templates/redeem_result.html`: Public landing page
