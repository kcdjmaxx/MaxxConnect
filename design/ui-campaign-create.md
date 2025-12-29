# CampaignCreate
**Source:** phase-2-campaign-management.md
**Route:** /campaign/new
**Template:** templates/campaign_create.html

## Data (see crc-Campaign.md, crc-CampaignManager.md)
- `templates: dict[]` - Available email templates from templates/email/
  - `filename: string` - Template path (e.g., 'email/monday_special.html')
  - `name: string` - Friendly name (e.g., 'Monday Special')
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
|  Create New Campaign                                             |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |  Campaign Name                                              |  |
|  |  [e.g., Monday Burger Special - Dec 2024_______________]    |  |
|  |                                                             |  |
|  |  Email Subject Line                                         |  |
|  |  [e.g., DOUBLE UP THIS MONDAY at Fric & Frac!__________]    |  |
|  |                                                             |  |
|  |  Select Email Template                                      |  |
|  |  [-- Choose a template -- v]                                |  |
|  |  (Choose from your email templates)                         |  |
|  |                                                             |  |
|  |  +--------------------------------------------------------+ |  |
|  |  | [ ] Include QR Code for redemption                     | |  |
|  |  | (i) Each recipient will receive a unique QR code for   | |  |
|  |  |     tracking deal redemptions                          | |  |
|  |  +--------------------------------------------------------+ |  |
|  |                                                             |  |
|  |  Target Audience                                            |  |
|  |  [All Subscribers (150) v]                                  |  |
|  |     Email Only (50)                                         |  |
|  |     SMS Only (30)                                           |  |
|  |     Email + SMS (70)                                        |  |
|  |                                                             |  |
|  |  [ ] Test Mode (Send to test email only)                    |  |
|  |                                                             |  |
|  |  (When checked, shows:)                                     |  |
|  |  Test Email Address                                         |  |
|  |  [your@email.com_____________________________]              |  |
|  |                                                             |  |
|  |  [Preview Campaign]  [Save as Draft]  [Send Campaign]       |  |
|  +------------------------------------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
```

## QR Code Toggle (see crc-Campaign.md)
- **Position:** After template selection, before audience selection
- **Default:** Unchecked (standard email without QR code)
- **Behavior:** When checked, sets `campaign.has_qr_code = True`
- **Help text:** Info icon with explanation of QR code purpose
- **Constraint:** Editable only when campaign status = 'draft'

## Events (see crc-CampaignManager.md)
- `[Preview Campaign]` - POST form with action=preview, redirect to /campaign/preview/{id}
- `[Save as Draft]` - POST form with action=save, redirect to /campaigns
- `[Send Campaign]` - POST form with action=send
  - Test mode: Send to test email only (with QR if enabled)
  - Live mode: Redirect to /campaign/send-confirm/{id}
- `test_mode checkbox` - Toggle test email field visibility
- `has_qr_code checkbox` - Toggle QR code generation flag
- `confirmSend()` - JavaScript confirm dialog before sending

## CSS Classes
- `.card` - White form container with shadow
- `.form-group` - Label + input wrapper (margin-bottom: 20px)
- `.form-input` - Text input styling (100% width, padding, border)
- `select` - Dropdown styling
- `input[type="checkbox"]` - Checkbox with margin-right
- `.qr-toggle-section` - Bordered box for QR code toggle
  - Light gray background (#f8f9fa)
  - Subtle border (1px solid #dee2e6)
  - Padding: 15px
  - Border-radius: 4px
- `.help-text` - Small gray text for checkbox explanation
- `.form-actions` - Button container with gap and border-top
- `.btn-primary` - Gradient purple (Save as Draft)
- `.btn-secondary` - Gray (Preview)
- `.btn-success` - Green (Send Campaign)
- Orange button (#ff9800) when test mode enabled

## Notes
- Template dropdown auto-populated from templates/email/*.html
- Audience counts queried from Customer table
- Test mode changes Send button color to orange
- JavaScript confirms before send (different messages for test/live)
- Form validation: name, subject, template required
- QR toggle state persisted with campaign on save
- Templates must include conditional QR section: `{% if qr_code_base64 %}...{% endif %}`
