---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# CSVImporter
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- Supported CSV formats (simple, Square POS export)
- Column mappings for different formats
- Phone number formatting rules (E.164)
- Email validation pattern

### Does
- import_csv(file_path, segment_tag, email_consent, sms_consent): Import contacts with explicit consent flags
- is_valid_email(email): Validate email format
- Normalize email addresses (lowercase, trim)
- Format phone numbers to E.164
- Deduplicate contacts within CSV
- Merge with existing customers (update vs create)
- Track import statistics (added, updated, invalid)

## Collaborators
- Customer: Creates or updates customer records
- SMSService: Uses format_phone_number, validate_phone_number

## Sequences
- seq-csv-import.md: CSV import with consent handling

## Design Notes

### Consent Handling (TCPA Compliance)
- `email_consent` (default: True): Subscribe imported contacts to email
- `sms_consent` (default: False): Subscribe imported contacts to SMS
- Phone numbers stored regardless of consent (for future opt-in)
- SMS subscription requires explicit consent checkbox

### Import Logic
1. Read and normalize CSV (handle Square format mapping)
2. Validate emails, format phone numbers
3. Deduplicate within CSV by email
4. For each contact:
   - If exists: Update missing fields, apply consent if not already subscribed
   - If new: Create with consent-based subscription status
5. Return stats: {total_rows, added, updated, invalid}

### CSV Format Support
**Simple format:**
```
email,name,phone
john@example.com,John Doe,+11234567890
```

**Square POS format:**
```
Email Address,First Name,Last Name,Phone Number,...
```
Automatically detected and mapped.
