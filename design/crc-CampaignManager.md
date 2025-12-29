# CampaignManager (Flask Routes)
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- db: Database session (via get_db())
- templates_dir: Path to email templates directory
- Config: Environment configuration

### Does
- campaigns(): List all campaigns (GET /campaigns)
- campaign_new(): Create new campaign with optional QR toggle (GET/POST /campaign/new)
- campaign_edit(id): Edit existing campaign, QR toggle editable before send (GET/POST /campaign/edit/<id>)
- campaign_delete(id): Delete campaign (POST /campaign/delete/<id>)
- campaign_preview(id): Preview campaign HTML (GET /campaign/preview/<id>)
- campaign_send_confirm(id): Show send confirmation with QR status (GET /campaign/send-confirm/<id>)
- campaign_send(id): Execute campaign send, generate QR codes if enabled (POST /campaign/send/<id>)
- get_available_templates(): Scan templates/email/ for available templates
- render_email_with_qr(customer, campaign, qr_code): Render email template with QR code if present

## Collaborators
- Campaign: SQLAlchemy model for persistence
- Customer: Query for audience selection (all, email_only, sms_only, both)
- ImageHandler: Environment-aware image processing
- Config: Determines base64 vs external URL strategy
- EmailService: Sends individual emails (send_email function)
- QRCodeGenerator: Generates unique QR codes per recipient when campaign.has_qr_code=True
- Templates: Jinja2 email templates (conditionally include QR code section)

## Sequences
- seq-campaign-create.md: Create campaign with template selection and QR toggle
- seq-campaign-send.md: Send without QR codes (has_qr_code=False)
- seq-campaign-send-qr.md: Send with QR code generation per recipient
- seq-campaign-preview.md: Preview rendered HTML

## Implementation
- **Source:** `app.py` (Flask routes)
- **Templates:** `templates/campaigns.html`, `templates/campaign_create.html`, `templates/campaign_edit.html`, `templates/campaign_send_confirm.html`
