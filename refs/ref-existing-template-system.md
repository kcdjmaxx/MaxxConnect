# ref-existing-template-system

- **Source:** local:backend/services/template_processor.py, templates/template_edit.html, app.py
- **Type:** local
- **Fetched:** 2026-02-07
- **Requirements:** TBD
- **Status:** active
- **Summary:** Existing MaxxConnect template management system - code editor, validation, import wizard, image upload.

## Key Details

### Existing Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/templates` | GET | List all templates with validation badges |
| `/template/new` | GET/POST | Create from starter/blank template |
| `/template/import` | GET/POST | Import wizard (upload/paste HTML) |
| `/template/edit/<filename>` | GET/POST | Code editor with live preview |
| `/template/preview/<filename>` | GET | Preview with sample data |
| `/template/delete/<filename>` | POST | Delete template |
| `/api/template/upload-image` | POST | Upload image, returns JSON with url + html_snippet |
| `/template/images/<filename>` | GET | Serve uploaded images |

### Template Storage
- Bundled templates: `templates/email/`
- User templates: `uploads/templates/` (Railway volume at `/app/uploads/templates`)
- Uploaded images: `uploads/images/` (Railway volume at `/app/uploads/images`)

### TemplateProcessor Service
- `validate(html)` - Returns ValidationReport (errors/warnings/info)
- `process_all(html)` - Auto-inject all missing elements, return processed + report
- `inject_*` methods for each compliance element
- `list_templates(dir)` - List with validation info
- `get_starter_template()` / `get_blank_template()` - Template starting points

### Required Placeholders (CAN-SPAM)
- `{{ unsubscribe_link }}` - Functional unsubscribe
- Physical mailing address
- Privacy policy link

### Recommended Placeholders
- `[[CUSTOMER_NAME]]` - Personalization
- `<!-- QR_CODE_SECTION -->` - QR code campaigns
- Preheader text

### Image Handling
- Development: base64 encoded
- Production: external URLs via `url_for('template_image', filename=...)`
- Upload endpoint validates type (PNG/JPG/GIF) and size (max 2MB)

### Base Template
- `templates/base.html` with nav bar, flash messages, content block
- Templates nav item highlights for all `/template*` paths
