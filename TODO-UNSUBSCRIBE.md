---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - type/documentation
  - status/complete
  - tool/flask
  - tool/sendgrid
  - tool/twilio
---

# Unsubscribe Issue - RESOLVED

## Status: COMPLETE ✅

**Fixed:** 2026-01-08

### The Problem
Unsubscribe links returned "Email address not found" even though the email existed in the database.

### Root Cause (ACTUAL)
**Fernet encryption is non-deterministic.** Each time you encrypt the same email, you get different ciphertext:

```python
encrypt("test@example.com")  # → gAAAAABl...abc123
encrypt("test@example.com")  # → gAAAAABl...xyz789  (different!)
```

This broke `find_by_email()` which was trying to encrypt the search email and compare ciphertexts - they never matched.

### Solution Implemented
Added **hash-based lookup** alongside encryption:

1. Added `email_hash` and `phone_hash` columns to Customer table
2. Store SHA-256 hash (deterministic) alongside encrypted email
3. Updated `find_by_email()` and `find_by_phone()` to search by hash
4. Kept encrypted values for display/storage (privacy preserved)

**Why this works:**
- SHA-256 is deterministic: `hash("email") == hash("email")` always
- We hash plaintext before lookup, compare hashes in database
- Original encrypted email remains for display/privacy

### Files Modified
- `backend/models.py` - Added hash columns, updated setters and find methods

### Testing
- ✅ Local Flask app unsubscribe works
- ✅ Production (Railway) unsubscribe works
- ✅ Database migration complete (local SQLite + Railway PostgreSQL)

### Cleanup Done
- ✅ Removed debug logging from `app.py`
- ✅ Deleted migration scripts (in git history)

---
**Created:** 2024-12-31
**Resolved:** 2026-01-08
**Priority:** HIGH - Legal compliance (CAN-SPAM)
