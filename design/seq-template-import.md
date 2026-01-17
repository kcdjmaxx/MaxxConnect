---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/planned
  - tool/flask
---

# Sequence: Template Import

**Source Spec:** Template Management System Plan
**Status:** PLANNED (Phase 2.5)

## Participants
- User: Person importing template
- ImportWizard: Flask route handling import flow
- TemplateProcessor: Service for validation and processing
- FileSystem: Template storage in templates/email/

## Sequence

```
User              ImportWizard         TemplateProcessor        FileSystem
  |                    |                      |                      |
  | GET /template/import                      |                      |
  |------------------->|                      |                      |
  |<-------------------|                      |                      |
  |  Show upload form  |                      |                      |
  |                    |                      |                      |
  | POST (upload HTML) |                      |                      |
  |------------------->|                      |                      |
  |                    | validate(html)       |                      |
  |                    |--------------------->|                      |
  |                    |<---------------------|                      |
  |                    |  ValidationReport    |                      |
  |                    |                      |                      |
  |                    | process_all(html)    |                      |
  |                    |--------------------->|                      |
  |                    |<---------------------|                      |
  |                    |  processed_html      |                      |
  |                    |                      |                      |
  |<-------------------|                      |                      |
  |  Show review page  |                      |                      |
  |  (proposed changes)|                      |                      |
  |                    |                      |                      |
  | POST (confirm save)|                      |                      |
  |------------------->|                      |                      |
  |                    |                      | write template file  |
  |                    |--------------------------------------------->|
  |                    |<---------------------------------------------|
  |                    |                      |                      |
  |<-------------------|                      |                      |
  |  Success + preview |                      |                      |
  |                    |                      |                      |
```

## Steps Detail

### Step 1: Upload
- User uploads HTML file or pastes HTML code
- Form validates file type (.html) and size limit

### Step 2: Analyze
- TemplateProcessor.validate() checks for required elements
- TemplateProcessor.process_all() proposes modifications:
  - inject_customer_name() - Add [[CUSTOMER_NAME]] at greeting
  - inject_unsubscribe_link() - Add to footer if missing
  - inject_qr_section() - Add comment marker if missing
  - inject_privacy_link() - Add to footer
  - inject_address() - Add physical address
  - process_images() - Convert to Jinja2 pattern

### Step 3: Review
- Show diff-style view of proposed changes
- Green: Auto-added elements
- Yellow: Manual review suggested
- Red: Critical issues requiring attention

### Step 4: Configure
- User provides template display name
- User confirms or adjusts customer name location
- User reviews and approves changes

### Step 5: Save
- Write processed HTML to templates/email/{name}.html
- Run final validation
- Redirect to template list with success message

## Error Handling
- Invalid HTML structure: Show error, suggest fixes
- Missing required elements after processing: Show warning, allow save anyway
- File write failure: Show error, don't lose user's HTML

## Routes

| Route | Method | Purpose |
|-------|--------|---------|
| /templates | GET | List all templates |
| /template/import | GET | Show upload form |
| /template/import | POST | Process uploaded HTML |
| /template/edit/<name> | GET | Edit template |
| /template/edit/<name> | POST | Save template changes |
| /template/preview/<name> | GET | Preview with sample data |
| /template/validate/<name> | POST | Run validation |
| /template/delete/<name> | POST | Delete template |
