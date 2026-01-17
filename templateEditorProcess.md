# Template Editor Process

## Overview

The Template Management System (Phase 2.5) provides tools for importing, validating, and editing email templates. This reduces the manual work of adding required placeholders when creating templates in external editors like DreamWeaver.

## Features Implemented

### Template List (`/templates`)
- Grid view of all email templates in `templates/email/`
- Thumbnail previews using scaled iframes
- Validation status badges:
  - **Valid** (green) - All required elements present
  - **Warning** (yellow) - Missing recommended elements
  - **Error** (red) - Missing required elements
- Actions: Edit, Preview, Delete

### Template Import Wizard (`/template/import`)
3-step wizard for importing HTML templates:

1. **Upload** - Upload HTML file or paste code directly
2. **Review** - See validation report and proposed auto-injections
3. **Save** - Confirm template name and save to `templates/email/`

**Auto-injection features:**
- Detects greeting patterns and adds `[[CUSTOMER_NAME]]`
- Adds `{{ unsubscribe_link }}` if missing
- Adds `<!-- QR_CODE_SECTION -->` comment if missing
- Adds privacy policy link if missing
- Adds physical mailing address if missing

### Template Editor (`/template/edit/<filename>`)
- Code editor with syntax highlighting (monospace font)
- Live preview panel (updates on typing with 500ms debounce)
- Validation status panel showing errors/warnings/suggestions
- Test email functionality
- **Insert snippet buttons** for required and optional elements

### Template Processor Service (`backend/services/template_processor.py`)
Validation rules:

**Required (Hard Fail):**
- `{{ unsubscribe_link }}` - CAN-SPAM compliance
- Physical mailing address - CAN-SPAM compliance
- Privacy policy link - Compliance requirement
- Valid HTML structure (DOCTYPE, html, head, body)

**Recommended (Warning):**
- `[[CUSTOMER_NAME]]` placeholder - Personalization
- `<!-- QR_CODE_SECTION -->` comment - QR code campaigns
- Preheader text - Email preview optimization

**Best Practices (Info):**
- Table-based layout for email client compatibility
- Max-width 600px for mobile
- Alt text on images
- Inline CSS (not external stylesheets)

## Insert Snippet Buttons

The editor includes buttons to insert required code snippets:

| Button | Snippet |
|--------|---------|
| 🔗 Unsubscribe Link | `<a href="{{ unsubscribe_link }}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>` |
| 📍 Address | Physical address paragraph with Fric & Frac details |
| 🔒 Privacy Link | `<a href="https://fricandfrac.net/privacy/" style="color: #888888; text-decoration: underline;">Privacy Policy</a>` |
| 👤 Customer Name | `[[CUSTOMER_NAME]]` |
| 📱 QR Section | `<!-- QR_CODE_SECTION -->` |

---

## Issues

### Insert buttons place content in wrong section

**Status:** FIXED (Jan 17, 2026)

**Description:** The insert snippet buttons were inserting code at the cursor position instead of the appropriate template section.

**Solution Implemented:** Smart insertion logic that finds the correct location for each snippet type:

| Snippet | Placement Logic |
|---------|-----------------|
| **Unsubscribe Link** | Finds `<!-- Email Footer` comment and inserts in footer area, or falls back to before `</body>` |
| **Address** | Finds existing unsubscribe link and inserts before it, or falls back to footer/body end |
| **Privacy Link** | Finds existing unsubscribe link and appends after it with ` | ` separator |
| **Customer Name** | Searches for greeting patterns (Hey, Hello, Hi, Welcome, Dear) and inserts after them |
| **QR Section** | Inserts before `<!-- Email Footer` comment, or before last `</table>` before `</body>` |

**Fallback Behavior:** If smart detection fails, snippets fall back to cursor position insertion.

---

## Files

| File | Purpose |
|------|---------|
| `backend/services/template_processor.py` | Validation and auto-injection service |
| `templates/template_list.html` | Template gallery UI |
| `templates/template_import.html` | Import wizard UI |
| `templates/template_edit.html` | Code editor UI |
| `app.py` | Routes for `/templates`, `/template/import`, `/template/edit`, `/template/preview`, `/template/delete` |

## Related Design Documents

- `design/crc-TemplateProcessor.md`
- `design/seq-template-import.md`
- `design/ui-template-list.md`
- `design/ui-template-import.md`
- `design/ui-template-edit.md`
