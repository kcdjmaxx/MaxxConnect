# CampaignSendConfirm
**Source:** phase-2-campaign-management.md
**Route:** /campaign/send-confirm/<id>
**Template:** templates/campaign_send_confirm.html

## Data (see crc-Campaign.md)
- `campaign: Campaign` - Campaign to send
  - `id: int` - Campaign identifier
  - `name: string` - Campaign title
  - `subject: string` - Email subject line
  - `template_name: string` - Template filename
  - `has_qr_code: boolean` - QR code generation flag
  - `created_at: datetime` - Creation timestamp
- `total_subscribers: int` - Count of email subscribers
- `email_only: int` - Count of email-only subscribers
- `sms_only: int` - Count of SMS-only subscribers
- `both: int` - Count of subscribers with both

## Layout
```
+------------------------------------------------------------------+
|  [Nav: Dashboard | Contacts | Import | Campaigns | SMS Preview]  |
+------------------------------------------------------------------+
|                                                                  |
|  Send Campaign                                                   |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |  [Purple gradient header card]                              |  |
|  |  Campaign Name: Monday Burger Special                       |  |
|  |  Subject: DOUBLE UP THIS MONDAY!                            |  |
|  |  Template: email/monday_special.html                        |  |
|  |  Created: 2024-12-21 14:30                                  |  |
|  |  QR Codes: [x] Enabled  OR  [ ] Disabled                    |  |
|  |  --------------------------------------------------------   |  |
|  |  [Preview Campaign button - white on purple]                |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  (When QR codes enabled, show info box:)                         |
|  +------------------------------------------------------------+  |
|  |  [Green info box - QR CODE MODE]                            |  |
|  |  Each recipient will receive a unique QR code for           |  |
|  |  redemption tracking. QR codes will be generated during     |  |
|  |  send and cannot be changed afterward.                      |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |  Send Options                                               |  |
|  |                                                             |  |
|  |  Target Audience                                            |  |
|  |  [All Subscribers (150) v]                                  |  |
|  |                                                             |  |
|  |  [ ] Test Mode (Send to test email only)                    |  |
|  |                                                             |  |
|  |  (Test email field - hidden by default)                     |  |
|  |                                                             |  |
|  |  +--------------------------------------------------------+ |  |
|  |  | [Yellow warning box - LIVE MODE]                       | |  |
|  |  | WARNING: This will send REAL EMAILS to the selected    | |  |
|  |  | audience. This action cannot be undone.                 | |  |
|  |  +--------------------------------------------------------+ |  |
|  |                                                             |  |
|  |  (OR when test mode checked:)                               |  |
|  |  +--------------------------------------------------------+ |  |
|  |  | [Blue info box - TEST MODE]                            | |  |
|  |  | Email will only be sent to your test address.          | |  |
|  |  | No subscribers will receive the campaign.               | |  |
|  |  +--------------------------------------------------------+ |  |
|  |                                                             |  |
|  |  [Cancel]  [Send Campaign]                                  |  |
|  +------------------------------------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
```

## QR Code Status Display (see crc-Campaign.md)
- Shows QR code status in campaign summary header
- Visual indicator: Checkmark icon when enabled, dash when disabled
- Green info box appears only when `has_qr_code = True`
- Informs user that QR setting is locked after send

## Events (see crc-CampaignManager.md)
- `[Preview Campaign]` - Open /campaign/preview/{id} in new tab
- `[Cancel]` - Navigate back to /campaigns
- `[Send Campaign]` - POST to /campaign/send/{id}
  - If has_qr_code: Triggers seq-campaign-send-qr.md flow
  - If not has_qr_code: Triggers seq-campaign-send.md flow
- `test_mode checkbox` - Toggle between test/live mode UI
- `confirmSend()` - JavaScript confirm dialog before POST

## CSS Classes
- `.card` - White form container with shadow
- `.campaign-summary` - Purple gradient header card
- `.form-group` - Label + input wrapper
- `.qr-status` - QR code status line in summary
  - `.qr-enabled` - Green checkmark icon
  - `.qr-disabled` - Gray dash icon
- `.qr-info-box` - Green info box for QR mode
  - Background: #d4edda
  - Border: 2px solid #28a745
  - Color: #155724
- `.warning-box` - Yellow warning (live mode)
  - Background: #fff3cd
  - Border: 2px solid #ffc107
  - Color: #856404
- `.info-box` - Blue info (test mode)
  - Background: #d1ecf1
  - Border: 2px solid #17a2b8
  - Color: #0c5460
- `.btn-secondary` - Gray (Cancel)
- `.btn-success` - Green (Send Campaign)
- Orange (#ff9800) when test mode enabled
- `.preview-link` - Preview button in header

## Notes
- Two-step confirmation flow (list -> confirm -> send)
- Visual distinction between test mode (orange/blue) and live mode (green/yellow)
- Preview opens in new tab
- JavaScript confirm with different messages for test vs live
- QR status displayed but not editable on confirmation page
- Cancel returns to campaign list
