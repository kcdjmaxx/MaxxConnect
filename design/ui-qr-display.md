# QRDisplay
**Source:** phase-2-campaign-management.md
**Route:** /qr/<token> (see manifest-ui.md)

## Data (see crc-QRCode.md)
- `qr_code: QRCode` - QR code entity
- `qr_image_base64: string` - QR code image data
- `campaign_name: string` - Associated campaign name
- `expires_at: datetime` - Expiration timestamp
- `is_expired: bool` - Whether QR is past expiration

## Layout
```
+------------------------------------------------------------------+
|                                                                  |
|                     Pizza Palace                                 |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |                                                            |  |
|  |                                                            |  |
|  |                    [QR CODE IMAGE]                         |  |
|  |                       (large)                              |  |
|  |                                                            |  |
|  |                                                            |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|                   20% Off Pizza Deal                             |
|                                                                  |
|              Show this code at checkout                          |
|                                                                  |
|              Valid until: Jan 15, 2024                           |
|                                                                  |
+------------------------------------------------------------------+

EXPIRED STATE:
+------------------------------------------------------------------+
|                                                                  |
|                     Pizza Palace                                 |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |                                                            |  |
|  |                      EXPIRED                               |  |
|  |                                                            |  |
|  |               This offer has expired                       |  |
|  |                                                            |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|              Expired on: Jan 15, 2024                            |
|                                                                  |
+------------------------------------------------------------------+
```

## Events
- None (display only, no user interaction)

## CSS Classes
- `qr-page` - Full page container
- `qr-container` - Centered content box
- `qr-image` - Large QR code image
- `qr-title` - Business name heading
- `qr-offer` - Campaign/deal name
- `qr-instructions` - "Show at checkout" text
- `qr-expiry` - Expiration date
- `qr-expired` - Expired state styling
- `expired-badge` - Red expired label

## Notes
- Public page (no authentication)
- Mobile-optimized layout
- Large QR for easy scanning
- Clear expiration display
- Graceful expired state
- No navigation (standalone page)
- Token validated server-side on load
