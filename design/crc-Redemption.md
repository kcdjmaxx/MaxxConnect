---
tags:
  - project/mailchimp-clone
  - subject/software-architecture
  - type/crc-card
  - status/implemented
---

# CRC Card: Redemption

**Class:** Redemption
**Module:** backend/models.py

## Knows (Data)

| Attribute | Type | Description |
|-----------|------|-------------|
| id | Integer | Primary key |
| qr_code_id | Integer | FK to QRCode |
| customer_id | Integer | FK to Customer |
| campaign_id | Integer | FK to Campaign |
| redeemed_at | DateTime | When redemption occurred |
| redeemed_by | String(255) | Staff identifier (optional) |
| redemption_method | String(50) | 'scan' or 'manual' |
| device_info | String(500) | User agent for fraud detection |
| ip_address | String(45) | Client IP for fraud detection |

## Does (Behavior)

| Method | Description |
|--------|-------------|
| (none) | Model is data-only; behavior in RedemptionService |

## Collaborators

| Collaborator | Relationship |
|--------------|--------------|
| QRCode | Many-to-one (each redemption references one QR code) |
| Customer | Many-to-one (each redemption references one customer) |
| Campaign | Many-to-one (each redemption references one campaign) |
| RedemptionService | Uses Redemption model for CRUD |

## Sequences

- seq-qr-redemption.md: Creating redemption records

## Implementation Notes

- Indexes on qr_code_id, customer_id, campaign_id for query performance
- Tracks fraud detection info (device_info, ip_address) for security auditing
- redeemed_by allows tracking which staff member performed redemption
- redemption_method distinguishes camera scans from manual token entry
