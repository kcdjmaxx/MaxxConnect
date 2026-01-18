---
tags:
  - project/mailchimp-clone
  - subject/software-architecture
  - type/crc-card
  - status/implemented
---

# CRC Card: RedemptionService

**Class:** RedemptionService (module-level functions)
**Module:** backend/services/redemption_service.py

## Knows (Data)

| Attribute | Type | Description |
|-----------|------|-------------|
| RedemptionResult | Class | Result object with success, status, message, data |

## Does (Behavior)

| Function | Description |
|----------|-------------|
| validate(db, token) | Check if QR code is valid without redeeming |
| redeem(db, token, ...) | Perform redemption, create record, increment usage |
| get_redemption_stats(db, campaign_id) | Get overall redemption statistics |
| get_recent_redemptions(db, limit, campaign_id) | Get recent redemption records with details |
| get_hourly_redemptions(db, campaign_id, days) | Get redemption counts by hour |
| get_campaign_redemption_stats(db) | Get stats grouped by campaign |

## Collaborators

| Collaborator | Relationship |
|--------------|--------------|
| QRCode | Queries and updates usage_count |
| Redemption | Creates redemption records |
| Customer | Queries for customer details |
| Campaign | Queries for campaign details |
| app.py | Routes call service functions |

## Sequences

- seq-qr-redemption.md: Full validation and redemption flow

## Validation Rules

| Status | Condition |
|--------|-----------|
| not_found | Token doesn't exist in database |
| expired | QRCode.expires_at < now |
| already_used | QRCode.usage_count >= QRCode.max_usage |
| invalid | Missing customer or campaign reference |
| valid | All checks pass |

## RedemptionResult Object

```python
RedemptionResult(
    success=True/False,
    status='valid'/'invalid'/'expired'/'already_used'/'not_found'/'redeemed',
    message='Human readable message',
    data={...}  # Customer name, campaign info, etc.
)
```

## Implementation Notes

- All functions take db session as first parameter
- validate() is read-only, redeem() writes to database
- Analytics functions support optional campaign_id filtering
- Fraud detection: device_info and ip_address captured on redeem
