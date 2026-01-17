---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/planned
  - tool/flask
---

# TemplateProcessor

**Source Spec:** Template Management System Plan
**Status:** IMPLEMENTED

## Knows
- required_elements: List of elements templates must have
- recommended_elements: List of elements templates should have
- injection_patterns: Regex patterns for finding injection points
- business_address: Physical address for CAN-SPAM compliance
- privacy_policy_url: URL to privacy policy

## Does
- validate(html): Analyze template and return ValidationReport with issues/warnings
- inject_unsubscribe_link(html): Add {{ unsubscribe_link }} to footer if missing
- inject_customer_name(html): Add [[CUSTOMER_NAME]] placeholder at greeting
- inject_qr_section(html): Add <!-- QR_CODE_SECTION --> comment if missing
- inject_privacy_link(html): Add privacy policy link to footer
- inject_address(html): Add physical mailing address to footer
- process_images(html): Convert image sources to Jinja2 environment-aware pattern
- process_all(html): Run all injections and return processed HTML
- get_validation_report(html): Return detailed report of template status

## Collaborators
- ImageHandler: For image processing patterns
- Config: For business address, privacy URL, environment settings

## Sequences
- seq-template-import.md

## Validation Rules

### Required (Hard Fail)
- `{{ unsubscribe_link }}` in an `<a>` tag
- Physical mailing address text
- Valid HTML structure (DOCTYPE, html, head, body)

### Recommended (Soft Warning)
- `[[CUSTOMER_NAME]]` placeholder for personalization
- `<!-- QR_CODE_SECTION -->` comment for QR code injection
- Preheader text (hidden preview text)
- Privacy policy link
- Inline CSS (not external stylesheets)

### Best Practices (Info)
- Table-based layout for email client compatibility
- Max-width 600px container
- Alt text on all images

## Implementation Notes

File: `backend/services/template_processor.py`

```python
class ValidationReport:
    is_valid: bool
    errors: List[str]      # Required elements missing
    warnings: List[str]    # Recommended elements missing
    info: List[str]        # Best practice suggestions

class TemplateProcessor:
    def validate(self, html: str) -> ValidationReport
    def inject_unsubscribe_link(self, html: str) -> str
    def inject_customer_name(self, html: str) -> str
    def inject_qr_section(self, html: str) -> str
    def inject_privacy_link(self, html: str) -> str
    def inject_address(self, html: str) -> str
    def process_images(self, html: str) -> str
    def process_all(self, html: str) -> Tuple[str, ValidationReport]
```
