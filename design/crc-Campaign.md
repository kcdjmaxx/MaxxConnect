# Campaign
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- id: Unique campaign identifier (primary key)
- name: Campaign title for identification
- subject: Email subject line
- template_name: Email template filename (e.g., 'email/monday_special.html')
- html_content: Rendered HTML content with Jinja2 placeholders
- status: Campaign state (draft/sent)
- sent_date: When campaign was sent (nullable)
- created_at: Creation timestamp
- has_qr_code: Boolean flag for QR code generation (default: False)

### Does
- __repr__(): Return string representation of campaign
- requires_qr_generation(): Check if campaign needs QR codes during send

## Collaborators
- Customer: Target audience for campaign delivery (via audience selection)
- ImageHandler: Processes images for email rendering (base64 or external URLs)
- Config: Determines environment-aware rendering strategy
- EmailService: Sends individual emails to customers
- QRCodeGenerator: Generates unique QR codes when has_qr_code=True

## Sequences
- seq-campaign-create.md: Create new campaign with template selection
- seq-campaign-send.md: Send campaign with audience selection and test mode
- seq-campaign-send-qr.md: Send campaign with QR code generation per recipient
- seq-campaign-preview.md: Preview rendered campaign HTML

## Implementation
- **Model:** `backend/models.py` (Campaign class)
- **Routes:** `app.py` (campaign_* functions)
