---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# Sequence: CSV Import with Consent

**Source CRC:** crc-CSVImporter.md

## Participants
- User
- ImportView (templates/import.html)
- FlaskApp (app.py)
- CSVImporter (backend/csv_importer.py)
- Customer (backend/models.py)
- Database

## Flow

```
User              ImportView        FlaskApp          CSVImporter       Customer          Database
  |                   |                 |                  |                |                 |
  |--GET /import----->|                 |                  |                |                 |
  |                   |<--render form---|                  |                |                 |
  |<--import.html-----|                 |                  |                |                 |
  |                   |                 |                  |                |                 |
  | [Select file, set consent checkboxes]                  |                |                 |
  |                   |                 |                  |                |                 |
  |--POST /import---->|                 |                  |                |                 |
  |  (file, email_consent, sms_consent) |                  |                |                 |
  |                   |--import_contacts()                 |                |                 |
  |                   |                 |--import_csv()--->|                |                 |
  |                   |                 |  (path, tag,     |                |                 |
  |                   |                 |   email_consent, |                |                 |
  |                   |                 |   sms_consent)   |                |                 |
  |                   |                 |                  |                |                 |
  |                   |                 |                  |--read CSV----->|                 |
  |                   |                 |                  |--normalize---->|                 |
  |                   |                 |                  |--dedupe------->|                 |
  |                   |                 |                  |                |                 |
  |                   |                 |                  |  [For each row]                  |
  |                   |                 |                  |--find_by_email()                 |
  |                   |                 |                  |                |--query--------->|
  |                   |                 |                  |                |<--result--------|
  |                   |                 |                  |                |                 |
  |                   |                 |                  |  [If exists]   |                 |
  |                   |                 |                  |--update------->|                 |
  |                   |                 |                  |  (apply consent flags)           |
  |                   |                 |                  |                |--UPDATE-------->|
  |                   |                 |                  |                |                 |
  |                   |                 |                  |  [If new]      |                 |
  |                   |                 |                  |--create------->|                 |
  |                   |                 |                  |  (consent-based subscription)    |
  |                   |                 |                  |                |--INSERT-------->|
  |                   |                 |                  |                |                 |
  |                   |                 |                  |--commit()----->|                 |
  |                   |                 |                  |                |                 |
  |                   |                 |<--stats----------|                |                 |
  |                   |<--render(stats)-|                  |                |                 |
  |<--success msg-----|                 |                  |                |                 |
```

## Consent Logic

### New Contacts
| email_consent | sms_consent | phone | Result |
|---------------|-------------|-------|--------|
| True | False | any | subscribed=True, sms_subscribed=False |
| True | True | exists | subscribed=True, sms_subscribed=True |
| True | True | null | subscribed=True, sms_subscribed=False |
| False | True | exists | subscribed=False, sms_subscribed=True |
| False | False | any | subscribed=False, sms_subscribed=False |

### Existing Contacts
- Only subscribes if consent=True AND not already subscribed
- Never unsubscribes (preserves existing status)
- Phone number stored regardless of SMS consent

## Error Handling
- Invalid CSV format: Return error message
- Missing email column: Raise ValueError
- Invalid emails: Filtered out (counted as invalid)
- Invalid phones: Stored as null (email still imported)
