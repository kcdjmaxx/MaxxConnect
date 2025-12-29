# CampaignPreview
**Source:** phase-2-campaign-management.md
**Route:** /campaigns/<id>/preview (see manifest-ui.md)

## Data (see crc-Campaign.md, crc-QRCodeGenerator.md)
- `campaign: Campaign` - Campaign to preview
- `sample_customer: Customer` - Sample customer for preview
- `preview_email_html: string` - Rendered email HTML
- `preview_sms: string` - Rendered SMS message
- `qr_code_base64: string` - Sample QR code image
- `target_count: int` - Number of customers to receive

## Layout
```
+------------------------------------------------------------------+
|  [Nav: Dashboard | Contacts | Import | Campaigns | Segments]     |
+------------------------------------------------------------------+
|                                                                  |
|  Preview: Pizza Deal Campaign                                    |
|                                                                  |
|  +------------------------+  +-------------------------------+   |
|  | Email Preview          |  | SMS Preview                   |   |
|  +------------------------+  +-------------------------------+   |
|  |                        |  |                               |   |
|  | Subject: 20% Off Pizza |  | Get 20% off your next pizza! |   |
|  |                        |  | Show this code:               |   |
|  | Dear John,             |  | example.com/qr/abc123         |   |
|  |                        |  |                               |   |
|  | Get 20% off your next  |  | Reply STOP to unsubscribe.    |   |
|  | pizza order!           |  | - Pizza Palace                |   |
|  |                        |  |                               |   |
|  | [QR CODE IMAGE]        |  | Characters: 142/160           |   |
|  |                        |  +-------------------------------+   |
|  | Show this QR code at   |                                      |
|  | checkout.              |                                      |
|  |                        |                                      |
|  | Pizza Palace           |                                      |
|  | 123 Main St            |                                      |
|  | Unsubscribe            |                                      |
|  +------------------------+                                      |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Campaign Summary                                            |  |
|  +------------------------------------------------------------+  |
|  | Target Segments: vip, pizza-lover                           |  |
|  | Customers: 2,450 (2,300 email, 1,200 SMS)                   |  |
|  | QR Expiration: 30 days from send                            |  |
|  | Estimated Duration: ~25 minutes (100 emails/min)            |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  [Back to Edit]  [Send Test Email]  [Send Campaign]              |
|                                                                  |
+------------------------------------------------------------------+
```

## Events (see crc-CampaignManager.md)
- `backToEdit()` - Navigate to /campaigns/{id}
- `sendTestEmail()` - Send preview to admin email
- `sendCampaign()` - Confirm and queue campaign for send

## CSS Classes
- `preview-container` - Two-column layout
- `preview-card` - Individual preview card
- `preview-email` - Email preview frame
- `preview-sms` - SMS preview (phone mockup style)
- `qr-preview` - QR code image
- `campaign-summary` - Summary card
- `summary-row` - Key-value row
- `btn-primary` - Send Campaign button
- `btn-secondary` - Send Test / Back buttons
- `confirm-modal` - Send confirmation dialog

## Notes
- Email preview shows full HTML rendering
- SMS preview shows character count
- Sample customer from target segments
- Confirmation shows customer count
- Test email uses admin's email address
