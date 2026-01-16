# QR Code Implementation Issues

## Status: IMPLEMENTED - String Placeholder Approach

Last updated: 2026-01-15

---

## Summary

Email sends were broken after commit `2412ddc` which attempted to render templates from files in the Celery worker context. This was reverted in commit `5e66eec` to restore functionality.

QR code generation requires a different approach (documented below) and is deferred for future implementation.

---

## What We Were Trying to Do

Implement QR code generation for campaign emails where each customer gets a unique QR code embedded in their email when `has_qr_code=True` on the campaign.

---

## What Went Wrong

### The Core Problem

When campaigns are created, the HTML template is rendered with Flask's `render_template()`. This evaluates all Jinja2 conditionals immediately:

```html
{% if qr_code_base64 %}
  <img src="data:image/png;base64,{{ qr_code_base64 }}">
{% endif %}
```

Since no QR code exists at creation time, this evaluates to **False** and the entire QR section is removed from `html_content`. At send time, we have QR data but nowhere to put it.

### The Failed Solution

Commit `2412ddc` tried to fix this by re-rendering from the original template file at send time:

```python
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template(campaign.template_name)
```

This failed because:
1. `campaign.template_name` might be `None` for older campaigns
2. Path calculation may not work reliably in Railway's containerized Celery worker
3. File system access in Celery worker context is fragile

### Resolution

Reverted to using stored `html_content` with `Template()` class. Email sends work again, but QR codes are not implemented.

---

## Recommended Solution: String Placeholder Approach

Instead of Jinja2 conditionals that get evaluated at creation time, use literal placeholder strings that survive template rendering.

### Implementation Plan

**1. Update email templates:**

Replace the Jinja2 conditional:
```html
{% if qr_code_base64 %}
<table>...</table>
{% endif %}
```

With a literal placeholder:
```html
<!-- QR_CODE_SECTION -->
```

**2. Modify campaign creation (`app.py`):**

When saving `html_content`, if `has_qr_code=True`, inject a placeholder block:
```python
if has_qr_code:
    qr_placeholder = '''
    <table cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 20px auto;">
      <tr>
        <td style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
          <p style="margin: 0 0 10px 0; font-weight: bold; color: #d32f2f;">SHOW THIS QR CODE TO REDEEM:</p>
          <img src="[[QR_CODE_DATA_URI]]" width="200" height="200" alt="Redemption QR Code">
          <p style="margin: 10px 0 0 0; font-size: 11px; color: #888;">One-time use only.</p>
        </td>
      </tr>
    </table>
    '''
    html_content = html_content.replace('<!-- QR_CODE_SECTION -->', qr_placeholder)
```

**3. Modify email sending (`email_task.py`):**

At send time, replace the placeholder with actual QR data:
```python
if campaign.has_qr_code and 'qr_code_base64' in template_vars:
    qr_data_uri = f"data:image/png;base64,{template_vars['qr_code_base64']}"
    personalized_html = personalized_html.replace('[[QR_CODE_DATA_URI]]', qr_data_uri)
```

### Why This Works

- **No file system dependencies** - Works in Celery worker context
- **Simple string operations** - Fast and reliable
- **Backward compatible** - Existing campaigns without placeholder still work
- **Clear intent** - Placeholder is obvious in the template HTML

---

## Commits Made During This Session

1. `6e30157` - Add QR code generation for campaign emails (model + service)
2. `7c6d8b4` - Import QRCode model in app.py for table creation
3. `86b93cf` - Add QR code placeholder to all email templates
4. `c303c9d` - Fix test emails to generate real QR codes
5. `2412ddc` - Fix QR code rendering by using original template files <- **REVERTED**
6. `5e66eec` - Revert "Fix QR code rendering by using original template files" <- **CURRENT**

---

## Files That Need Changes (When Implementing)

### Email Templates (`templates/email/*.html`)

Replace `{% if qr_code_base64 %}...{% endif %}` with `<!-- QR_CODE_SECTION -->`:
- `monday_special.html`
- `WelcomeTemplate.html`
- `base_email.html`

### Campaign Creation/Edit (`app.py`)

- `create_campaign()` - Inject QR placeholder when `has_qr_code=True`
- `edit_campaign()` - Handle QR placeholder on template change

### Email Sending (`backend/tasks/email_task.py`)

- `send_campaign_email()` - Replace `[[QR_CODE_DATA_URI]]` with actual base64 data

---

## Test Plan

1. Create campaign with `has_qr_code=True`
2. Verify `html_content` contains `[[QR_CODE_DATA_URI]]` placeholder
3. Send test email - verify QR code appears in email
4. Send to real customer - verify unique QR code generated and saved to database
5. Scan QR code - verify redemption works

---

## Database State

The `qr_codes` table exists and the QR generation service (`qr_generator.py`) is working. Only the template integration needs to be fixed.

---

## Implementation Completed (2026-01-15)

The String Placeholder Approach has been implemented:

### Changes Made

**1. Email Templates** (`templates/email/*.html`)
- Replaced `{% if qr_code_base64 %}...{% endif %}` blocks with `<!-- QR_CODE_SECTION -->` comment
- Files updated: `monday_special.html`, `WelcomeTemplate.html`, `base_email.html`

**2. Campaign Creation** (`app.py:create_campaign()`)
- After `render_template()`, if `has_qr_code=True`, replaces `<!-- QR_CODE_SECTION -->` with QR HTML block containing `[[QR_CODE_DATA_URI]]`
- The placeholder survives Jinja2 rendering since it's not Jinja2 syntax

**3. Campaign Edit** (`app.py:edit_campaign()`)
- Same logic applied when template is re-rendered due to template change or QR setting change

**4. Email Sending** (`backend/tasks/email_task.py`)
- After Jinja2 rendering, replaces `[[QR_CODE_DATA_URI]]` with actual `data:image/png;base64,{qr_code_base64}`
- Uses the already-working `build_template_vars()` which generates unique QR codes per customer

**5. Test Email Paths** (app.py)
- Updated test email handlers to inject QR placeholder HTML and replace with generated QR code
- `/test-template` route updated to demonstrate new approach

### How It Works

1. **Campaign Creation**: Template renders with `<!-- QR_CODE_SECTION -->` comment. If `has_qr_code=True`, this gets replaced with QR HTML containing `[[QR_CODE_DATA_URI]]` literal string.

2. **Database Storage**: `html_content` stores the HTML with `[[QR_CODE_DATA_URI]]` placeholder.

3. **Send Time**: Celery worker generates unique QR code, then does simple string replace: `[[QR_CODE_DATA_URI]]` → `data:image/png;base64,{actual_qr_base64}`

### Ready for Testing

Use the Test Plan above to verify the implementation works end-to-end.

---

## Gmail Compatibility Issue (Discovered 2026-01-16)

### Problem

Base64 data URI images (`data:image/png;base64,...`) are **blocked by Gmail** (web and mobile app) for security reasons. QR codes display correctly in Apple Mail but are stripped in Gmail.

### Debug Confirmation

Worker logs confirmed the QR code is correctly generated and embedded:
```
QR DEBUG: has_qr_code=True, qr_base64_in_vars=True
QR DEBUG: Placeholder found in html_content: True
QR DEBUG: After Jinja2 render, has data:image/png: True
QR DEBUG: QR img tag after render: <img src="data:image/png;base64,iVBORw0KGgo...
```

The HTML is correct when sent to SendGrid. Gmail strips the data URI on the receiving end.

### Solution: External QR Code Hosting

Use an external QR code generation service instead of base64 embedding.

**Recommended: QR Server API** (https://api.qrserver.com)
- Free, no account needed
- No API key required
- Just construct URL: `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=REDEMPTION_URL`

### Implementation Plan

1. **Modify `qr_generator.py`:**
   - Add function to generate QR Server API URL instead of base64
   - Keep existing token generation and database storage (unchanged)

2. **Modify `email_task.py`:**
   - Replace `[[QR_CODE_DATA_URI]]` with external URL instead of base64 data URI

3. **Example output:**
   ```html
   <!-- Instead of -->
   <img src="data:image/png;base64,iVBORw0KGgo...">

   <!-- Use -->
   <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://maxxconnect.up.railway.app/redeem/29-1-abc123">
   ```

### What Stays The Same

- Token generation and uniqueness
- Database storage (`qr_codes` table)
- Redemption endpoint (`/redeem/{token}`)
- All tracking and validation logic

Only the **image delivery method** changes from embedded base64 to external URL.

### Status: PENDING IMPLEMENTATION
