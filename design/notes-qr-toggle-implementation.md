# Implementation Notes: QR Code Toggle Feature

**Source Spec:** User story for QR code toggle
**Design Artifacts:** crc-Campaign.md, crc-CampaignManager.md, seq-campaign-send-qr.md, ui-campaign-create.md, ui-campaign-send-confirm.md

## Summary

Add a checkbox to campaign creation that enables unique QR code generation per recipient during campaign send. This integrates the existing QR code system (designed for Phase 2) with the implemented campaign management system (Phase 1).

## Implementation Approach

### 1. Database Migration

**File:** `backend/models.py`

Add `has_qr_code` column to Campaign model:

```python
has_qr_code = db.Column(db.Boolean, default=False, nullable=False)
```

**Migration required:** Add column with default False for existing campaigns.

### 2. Campaign Create/Edit Form

**File:** `templates/campaign_create.html`, `templates/campaign_edit.html`

Add checkbox after template selection:

```html
<div class="qr-toggle-section">
    <label>
        <input type="checkbox" name="has_qr_code" value="true"
               {% if campaign and campaign.has_qr_code %}checked{% endif %}
               {% if campaign and campaign.status != 'draft' %}disabled{% endif %}>
        Include QR Code for redemption
    </label>
    <p class="help-text">
        Each recipient will receive a unique QR code for tracking deal redemptions
    </p>
</div>
```

### 3. Route Handlers

**File:** `app.py`

**campaign_new():**
- Read `has_qr_code` from form (checkbox value)
- Save to Campaign model

**campaign_edit():**
- Only allow QR toggle change if `campaign.status == 'draft'`
- Disable checkbox in template for sent campaigns

**campaign_send():**
- Check `campaign.has_qr_code` before send loop
- If True: Generate QR code for each recipient before sending
- If False: Send without QR code (existing behavior)

### 4. QR Code Generation Integration

**Dependencies:** `crc-QRCodeGenerator.md` (existing design)

For each recipient when `has_qr_code = True`:

```python
if campaign.has_qr_code:
    from backend.services.qr_generator import QRCodeGenerator
    qr_gen = QRCodeGenerator()
    qr_code = qr_gen.create_qr_code(campaign, customer)
    qr_code_base64 = qr_gen.encode_base64(qr_code.image)
else:
    qr_code_base64 = None

# Render template with or without QR
html = render_template_string(
    campaign.html_content,
    customer_name=customer.name,
    qr_code_base64=qr_code_base64,
    unsubscribe_link=unsubscribe_url
)
```

### 5. Email Template Changes

**File:** `templates/email/monday_special.html` (and other templates)

Add conditional QR code section:

```html
{% if qr_code_base64 %}
<div style="text-align: center; padding: 20px; background: #f5f5f5; margin: 20px 0;">
    <p style="font-weight: bold; margin-bottom: 10px;">
        Your Exclusive QR Code
    </p>
    <img src="data:image/png;base64,{{ qr_code_base64 }}"
         alt="Redemption QR Code"
         style="max-width: 200px;">
    <p style="font-size: 12px; color: #666; margin-top: 10px;">
        Show this code at checkout to redeem your offer
    </p>
</div>
{% endif %}
```

### 6. Send Confirmation Page

**File:** `templates/campaign_send_confirm.html`

Display QR status in campaign summary:

```html
<p>
    <strong>QR Codes:</strong>
    {% if campaign.has_qr_code %}
        <span class="qr-enabled">Enabled</span>
    {% else %}
        <span class="qr-disabled">Disabled</span>
    {% endif %}
</p>

{% if campaign.has_qr_code %}
<div class="qr-info-box">
    Each recipient will receive a unique QR code for redemption tracking.
    QR codes will be generated during send and cannot be changed afterward.
</div>
{% endif %}
```

## CSS Additions

```css
.qr-toggle-section {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
}

.qr-toggle-section .help-text {
    font-size: 0.85em;
    color: #6c757d;
    margin: 5px 0 0 22px;
}

.qr-enabled {
    color: #28a745;
}
.qr-enabled::before {
    content: "[checkmark] ";
}

.qr-disabled {
    color: #6c757d;
}

.qr-info-box {
    background: #d4edda;
    border: 2px solid #28a745;
    color: #155724;
    padding: 15px;
    border-radius: 4px;
    margin: 15px 0;
}
```

## Implementation Order

1. **Database:** Add `has_qr_code` column with migration
2. **UI:** Add checkbox to create/edit forms
3. **Routes:** Handle form field in create/edit routes
4. **Send confirm:** Display QR status
5. **QR Generator:** Implement or stub `QRCodeGenerator` service
6. **Send logic:** Integrate QR generation into send loop
7. **Templates:** Add conditional QR section to email templates
8. **Testing:** Verify all test cases in test-Campaign.md

## Dependencies on Existing Phase 2 Design

This feature bridges Phase 1 (implemented) and Phase 2 (planned):

| Component | Status | Action Needed |
|-----------|--------|---------------|
| Campaign model | Implemented | Add has_qr_code field |
| CampaignManager routes | Implemented | Extend for QR toggle |
| QRCodeGenerator service | Designed (crc) | Implement for first time |
| QRCode model | Designed (crc) | Implement for first time |
| Email templates | Implemented | Add conditional QR section |

## Out of Scope (Future)

- QR code expiration dates
- Multi-use vs single-use QR codes
- QR code validation/redemption tracking
- Analytics on QR code scans
- SMS short URLs for QR codes
