---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# EmailService
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- SendGrid API key (from Config)
- Sender email and name (from Config)
- Image processing mode (base64 vs external URL)

### Does
- send_email(to_email, to_name, subject, html_content, inline_attachments=None): Send via SendGrid
  - Processes images via ImageHandler
  - Attaches inline images with CID references for Gmail compatibility
  - inline_attachments: List of `{'content_id': str, 'image_bytes': bytes}`
- render_email_template(template_path, customer, custom_body): Render with personalization
- send_test_email(test_email, subject, custom_body): Quick test email

## CID Attachment Implementation
Gmail strips base64 data URIs for security. The CID (Content-ID) approach:

1. HTML references image via CID: `<img src="cid:qr-1-2">`
2. Image attached with matching Content-ID header
3. SendGrid Attachment created with:
   - `Disposition('inline')` - marks as inline, not download
   - `ContentId(content_id)` - matches HTML cid: reference

```python
Attachment(
    FileContent(base64_encoded_bytes),
    FileName(f'{content_id}.png'),
    FileType('image/png'),
    Disposition('inline'),
    ContentId(content_id)
)
```

## Collaborators
- Config: API keys, sender info, environment detection
- ImageHandler: Process HTML images for environment
- SendGridAPIClient: External API for email delivery

## Sequences
- seq-email-process.md: Email sending with CID attachments
- seq-campaign-send-qr.md: QR code email flow
