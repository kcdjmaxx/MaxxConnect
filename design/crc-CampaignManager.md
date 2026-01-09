---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# CampaignManager (Flask Routes)
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- db: Database session (via get_db())
- templates_dir: Path to email templates directory
- Config: Environment configuration (FLASK_ENV detection)

### Does
- campaigns(): List all campaigns (GET /campaigns)
- campaign_new(): Create new campaign with optional QR toggle (GET/POST /campaign/new)
- campaign_edit(id): Edit existing campaign, QR toggle editable before send (GET/POST /campaign/edit/<id>)
- campaign_delete(id): Delete campaign (POST /campaign/delete/<id>)
- campaign_preview(id): Preview campaign HTML (GET /campaign/preview/<id>)
- campaign_send_confirm(id): Show send confirmation with QR status (GET /campaign/send-confirm/<id>)
- campaign_send(id): Execute campaign send with environment-aware image handling and debug logging (POST /campaign/send/<id>)
- get_available_templates(): Scan templates/email/ for available templates
- render_email_with_qr(customer, campaign, qr_code): Render email template with QR code if present

### Debug & Error Handling (campaign_send)
- Logs template name being used
- Logs environment mode (Config.ENV)
- Logs unsubscribe_link generation
- Logs image strategy (base64 vs external URL)
- Logs template rendering success/failure with HTML length
- Logs email send results
- Full traceback on exceptions

## Collaborators
- Campaign: SQLAlchemy model for persistence
- Customer: Query for audience selection (all, email_only, sms_only, both)
- ImageHandler: Environment-aware image processing (get_image_url for base64)
- Config: Determines base64 vs external URL strategy via is_development()/is_production()
- EmailService: Sends individual emails (send_email function)
- QRCodeGenerator: Generates unique QR codes per recipient when campaign.has_qr_code=True
- Templates: Jinja2 email templates (conditionally include QR code section)
- Flask url_for: Generates external URLs for images in production mode

## Sequences
- seq-campaign-create.md: Create campaign with template selection and QR toggle
- seq-campaign-send.md: Send with environment-aware image handling and debug logging
- seq-campaign-send-qr.md: Send with QR code generation per recipient
- seq-campaign-preview.md: Preview rendered HTML

## Implementation
- **Source:** `app.py` (Flask routes)
- **Templates:** `templates/campaigns.html`, `templates/campaign_create.html`, `templates/campaign_edit.html`, `templates/campaign_send_confirm.html`

## Environment-Aware Behavior
- **Development (FLASK_ENV != 'production'):**
  - Uses `logo_base64`, `hero_image_base64` template variables
  - Images converted via ImageHandler.get_image_url()
- **Production (FLASK_ENV == 'production'):**
  - Uses `logo_url`, `hero_image_url` template variables
  - Images served via Flask url_for with `_external=True`
