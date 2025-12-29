---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - tool/flask
  - status/active
  - type/project-planning
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a custom email and SMS marketing platform (MailChimp clone) designed for small business use, deployed on Railway.app. The system sends promotional emails and SMS messages with unique QR codes for deal redemption tracking.

**Environment-Aware Configuration:**
- **Development**: Base64 images, SQLite database, localhost URLs
- **Production**: External image URLs, PostgreSQL, Railway URLs
- See `CONFIGURATION.md` for complete setup guide

## Architecture

The system consists of three main components:

1. **Flask Web Application** - Single unified app with HTML/CSS interface for campaign creation, CSV contact imports, analytics, email/SMS preview
2. **Flask REST API** - API endpoints for iOS redemption app, unsubscribe/opt-out handling
3. **iOS Scanner App** - QR code scanning for deal redemption validation

### Data Flow
```
Flask Web UI → Database → Email/SMS Services (SendGrid/Twilio)
                   ↓
              QR Codes → iOS Scanner → API Validation → Redemption Tracking
```

## Database Schema

Core entities to track:
- **Customers**:
  - email, phone (E.164 format), name
  - Email: subscription_status, opted_in_timestamp
  - SMS: sms_subscribed, sms_opted_in_date, sms_unsubscribed_date
  - segments/tags (comma-separated)
- **Campaigns**: subject, content, sent_date, a_b_test_variant, status
- **QR Codes**: unique_token (format: `{campaign_id}-{customer_id}-{hash}`), usage_count, expiration_date
- **Redemptions**: timestamp, qr_code_id, customer_id

Start with SQLite for development, PostgreSQL for production.

## Tech Stack

**Backend:**
- Flask (unified web app + REST API)
- SQLAlchemy (ORM)
- Jinja2 (HTML templates)
- Celery + Redis (email/SMS queue system - Phase 2)

**Email:**
- SendGrid (email delivery API)
- python-qrcode (QR code generation)
- Jinja2 (HTML email templates)

**SMS:**
- Twilio (SMS delivery API)
- Automatic STOP/opt-out handling
- 160-character limit enforcement

**iOS:**
- Swift + AVFoundation (QR scanning)
- URLSession (API communication)

**Database:**
- SQLite (development)
- PostgreSQL (production)

## Email Template System

HTML email templates use Jinja2 with these required placeholders:
- `{{ customer_name }}` - Personalization
- `{{ qr_code_base64 }}` - Base64-encoded QR image
- `{{ unsubscribe_link }}` - Legal requirement (CAN-SPAM)
- Physical mailing address in footer (legal requirement)

QR code tokens must be cryptographically secure with format: `{campaign_id}-{customer_id}-{random_hash}`

## SMS System

SMS messages via Twilio with these requirements:
- 160 character limit for single SMS
- Automatic opt-out footer: "Reply STOP to unsubscribe. - {Business Name}"
- Phone numbers stored in E.164 format (+1234567890)
- Format validation and normalization on import
- Webhook endpoint `/sms-optout` for Twilio STOP replies

## Campaign Management System

**Overview:**
Complete CRUD system for email campaigns with template selection, audience targeting, and test mode.

**Campaign Workflow:**
1. **Create Campaign** (`/campaign/new`)
   - Select from available email templates in `templates/email/`
   - Templates automatically discovered and listed
   - Enter campaign name and subject line
   - Preview or save as draft

2. **Edit Campaign** (`/campaign/edit/<id>`)
   - Click campaign name in campaigns list
   - Update name, subject, or template
   - Re-renders HTML if template changed
   - Preview changes before saving

3. **Send Campaign** (`/campaign/send-confirm/<id>`)
   - Click Send button → Opens confirmation page
   - Select target audience:
     - All Subscribers
     - Email Only
     - SMS Only (future)
     - Email + SMS (future)
   - **Test Mode Option:**
     - Checkbox to enable test mode
     - Send to single test email address
     - Orange button: "📧 Send Test Email Only"
     - Does NOT send to real subscribers
   - **Live Mode:**
     - Green button: "📧 Send Campaign"
     - Sends to selected audience
     - Warning confirmation required
   - Personalization:
     - `{{ customer_name }}` replaced with actual names
     - `{{ unsubscribe_link }}` with secure token
   - Images handled based on environment:
     - Development: Base64 embedded
     - Production: External URLs

4. **Delete Campaign** (`/campaign/delete/<id>`)
   - Click trash icon (🗑️)
   - Confirmation dialog required
   - Permanently removes campaign

**Routes:**
- `GET /campaigns` - List all campaigns
- `GET /campaign/new` - Create campaign form
- `POST /campaign/new` - Save new campaign
- `GET /campaign/edit/<id>` - Edit campaign form
- `POST /campaign/edit/<id>` - Update campaign
- `GET /campaign/preview/<id>` - Preview campaign HTML
- `GET /campaign/send-confirm/<id>` - Send confirmation page
- `POST /campaign/send/<id>` - Execute send (with audience/test mode)
- `POST /campaign/delete/<id>` - Delete campaign

**Template System:**
- Email templates stored in `templates/email/`
- Auto-discovered by scanning directory
- Support Jinja2 variables:
  - `{{ customer_name }}` - Personalization
  - `{{ logo_base64 }}` or `{{ logo_url }}` - Logo image
  - `{{ hero_image_base64 }}` or `{{ hero_image_url }}` - Hero banner
  - `{{ qr_code_base64 }}` - QR code (future)
  - `{{ unsubscribe_link }}` - Required unsubscribe link
- Image handling:
  - Development: Images converted to base64 via ImageHandler
  - Production: External URLs to Railway static files

## Critical Legal Requirements

**Email:**
- Unsubscribe link (functional, immediate processing)
- Physical mailing address in footer
- Store opt-in timestamps for all contacts
- Honor unsubscribe requests immediately

**SMS (TCPA Compliance):**
- Explicit opt-in required before sending
- Must honor STOP replies immediately
- Include opt-out instructions in every message
- Respect quiet hours (9 AM - 8 PM local time recommended)
- Store SMS opt-in timestamps

## CSV Import System

The system supports two CSV formats for contact imports:

**Simple Format:**
```csv
email,name,phone
john@example.com,John Doe,+11234567890
jane@example.com,Jane Smith,5551234567
```

**Square Export Format (supported as of Dec 2024):**
```csv
Email Address,First Name,Last Name,Phone Number,...
john@example.com,John,Doe,+11234567890,...
```

**Import Features:**
- Automatic column mapping (Square → simple format)
- Name combining (`First Name` + `Last Name` → `name`)
- Phone number normalization to E.164 format
- Email validation and deduplication
- Empty/invalid email filtering
- Segment tagging during import
- Update existing contacts or create new ones

**Implementation:** `backend/csv_importer.py` handles both formats automatically.

## Core Features (Must Implement)

1. **Unsubscribe Management** - Automatic opt-out processing (email + SMS)
2. **Bounce Handling** - Auto-remove invalid emails
3. **Email/SMS Queue System** - Rate-limited sending to avoid spam flags
4. **Rate Limiting** - Respect service provider limits
5. **Analytics Dashboard** - Redemption rates, campaign performance metrics
6. **Customer Segments** - Tag-based targeting for campaigns
7. **Export Reports** - CSV/Excel export for redemption data
8. **Email/SMS Preview** - Test rendering before campaign send
9. **A/B Testing** - Subject line variants with performance tracking
10. **Contact Deduplication** - Merge duplicate emails/phones during CSV import
11. **SMS Opt-out Handling** - Twilio webhook for STOP replies
12. **Multi-format CSV Import** - Support for Square POS exports and simple CSV format

## Email Deliverability

**Critical**: Do NOT send emails directly from Raspberry Pi (spam filters will block).

Required setup:
- Use SendGrid/SES/Mailgun API for sending
- Configure SPF/DKIM/DMARC DNS records
- Implement rate limiting (avoid sudden volume spikes)
- Track bounce rates and remove bad addresses

## Development Phases

**Phase 1 - Foundation:** ✅ COMPLETE
- Email API integration (SendGrid) ✓
- SMS API integration (Twilio) ✓
- CSV import with deduplication (email + phone) ✓
  - Simple CSV format support ✓
  - Square POS export format support ✓
- Test email functionality ✓
- Email preview system ✓
- Unsubscribe management ✓
- Campaign management (CRUD operations) ✓
  - Create campaigns with template selection ✓
  - Edit campaigns ✓
  - Delete campaigns ✓
  - Preview campaigns ✓
- Send confirmation workflow ✓
  - Audience selection (All, Email Only, SMS Only, Both) ✓
  - Test mode with test email option ✓
  - Safety confirmations ✓
- Image handling (environment-aware) ✓
  - Base64 encoding for development ✓
  - External URLs for production ✓

**Phase 2 - QR Code & Redemption:**
- QR code generation with unique tokens
- Customer segmentation/tagging
- Email queue with rate limiting
- Campaign analytics and tracking

**Phase 3 - Redemption System:**
- iOS QR scanner app
- Redemption validation API
- Usage tracking (prevent multi-redemption)
- Analytics dashboard

**Phase 4 - Advanced Features:**
- Bounce handling automation
- Redemption report exports
- A/B testing infrastructure
- Performance optimization

## Project Structure (Recommended)

```
mailChimpClone/
├── backend/
│   ├── api/          # Flask/FastAPI REST endpoints
│   ├── models/       # SQLAlchemy database models
│   ├── services/     # Email queue, QR generation, etc.
│   └── templates/    # Jinja2 email templates
├── dashboard/        # Streamlit admin UI
├── ios-scanner/      # Swift iOS app
├── migrations/       # Database migrations
└── tests/
```

## Security Considerations

- QR tokens must use cryptographically secure random hashes
- Validate all QR scans server-side (never trust client)
- Store email service API keys in environment variables
- Implement API authentication for iOS scanner
- Track redemption attempts (detect fraud patterns)
- Add expiration dates to all QR codes
# Project Instructions

## CRC Modeling Workflow

**DO NOT generate code directly from `specs/*.md` files!**

**Use a three-tier system:**
```
Level 1: Human specs (specs/*.md)
   ↓
Level 2: Design models (design/*.md) ← CREATE THESE FIRST
   ↓
Level 3: Implementation (source code)
```

**Workflow:**
1. Read human specs (`specs/*.md`) for design intent
2. Use `designer` agent to create Level 2 specs (CRC cards, sequences, UI specs, architecture mapping, **and test designs**)
   - Designer agent MUST invoke test-designer sub-agent (automatic, mandatory step)
   - Verify test design files (`design/test-*.md`) are created before proceeding
3. Generate code following complete specification with traceability comments

**When Designer Agent is Required vs Direct CRC Creation:**

| Scenario | Use Designer Agent? | Required Follow-up |
|----------|---------------------|-------------------|
| New feature design | YES | Full workflow (sequences, test designs, gap analysis) |
| Significant architectural change | YES | Full workflow |
| Documenting existing code | Optional | Run gap-analyzer to verify completeness |
| Fixing/cleaning up CRC cards | No | Verify sequence references exist |
| Creating CRC for existing interface | Optional | Run gap-analyzer to verify completeness |

**CRITICAL: Regardless of how CRC cards are created:**
1. All sequence references must point to existing files (fix or create)
2. Non-trivial "Does" behaviors need sequence diagrams
3. Run `gap-analyzer` agent after creating/modifying CRC cards
4. Update `design/traceability.md` and `design/architecture.md`

**Design Entry Point:**
- `design/architecture.md` serves as the "main program" for the design
- Shows how design elements are organized into logical systems
- Start here to understand the overall architecture
- **Use for problem diagnosis and impact analysis** - quickly localize issues and assess change scope

**When to Read architecture.md:**
- **When working with design files, implementing features, or diagnosing issues, always read `design/architecture.md` first to understand the system structure and component relationships.**

**Traceability Comment Format:**
- Use simple filenames WITHOUT directory paths
- ✅ Correct: `CRC: crc-Person.md`, `Spec: main.md`, `Sequence: seq-create-user.md`
- ❌ Wrong: `CRC: design/crc-Person.md`, `Spec: specs/main.md`

**Finding Implementations:**
- To find where a design element is implemented, grep for its filename (e.g., `grep "seq-get-file.md"`)

**Test Implementation:**
- **Test designs are Level 2 artifacts**: Designer agent automatically generates test design specs (`design/test-*.md`) via the test-designer sub-agent
- **ALWAYS read test designs BEFORE writing test code**: Test designs specify what to test, test code implements those specifications
- **Test code MUST implement all scenarios from test designs**: Every test scenario in `design/test-*.md` must have corresponding test code
- **Traceability**: Test files reference test designs in comments: `// Test Design: test-ComponentName.md`
- Test files belong in top-level `tests/` directory (NOT nested under `src/`)
- When configuring build tools (Vite, Webpack, etc.), ensure test runner configurations are separate from application build configurations
- If build config sets a custom `root` directory, create a separate test configuration file to avoid test discovery issues
- Run `npm test` to verify test discovery works correctly before considering tests complete

**Test Design Workflow:**
1. Designer agent creates CRC cards and sequences (Level 2)
2. Designer agent invokes test-designer agent (automatic, mandatory)
3. Test-designer generates test design specs (`design/test-*.md`)
4. Read test designs to understand what needs testing
5. Implement tests following test design specifications
6. Reference test designs in test code comments

See `.claude/doc/crc.md` for complete documentation.

### 🔄 Bidirectional Traceability Principle

**When changes occur at any level, propagate updates through the documentation hierarchy:**

**Source Code Changes → Design Specs:**
- Modified implementation → Update CRC cards/sequences/UI specs if structure/behavior changed
- New classes/methods → Create corresponding CRC cards
- Changed interactions → Update sequence diagrams
- Template/view changes → Update UI specs

**Use the `design-maintainer` agent to automate this:**
```
When you've made code changes, invoke the design-maintainer agent to:
- Update CRC cards with new methods/fields
- Update sequence diagrams for changed workflows
- Add traceability comments to new code
- Check off traceability.md checkboxes
```

**Design Spec Changes → Architectural Specs:**
- Modified CRC cards/sequences → Update high-level specs if requirements/architecture affected
- New components → Document in feature specs and update `design/architecture.md`
- Changed workflows → Update architectural documentation
- System reorganization → Update `design/architecture.md` to reflect new system boundaries

**Key Rules:**
1. **Always update up**: When code/design changes, ripple changes upward through documentation
2. **Maintain abstraction**: Each level documents at its appropriate abstraction
3. **Keep consistency**: All three tiers must tell the same story at their respective levels
4. **Update traceability comments**: When docs change, update CRC/spec references in code comments

**Agent Workflow:**
- **Requirements → Design**: Use `designer` agent (Level 1 → Level 2)
- **Code → Design**: Use `design-maintainer` agent (Level 3 → Level 2)
- **Design → Documentation**: Use `documenter` agent (Level 2 → Docs)

### 🔧 Design Update Requests

**When the user asks to update, modify, or add to the design (Level 2 artifacts), ALWAYS use the appropriate agent:**

| User Request | Agent to Use |
|--------------|--------------|
| "Update the design for X" | `designer` |
| "Add X to the design" | `designer` |
| "Reflect spec changes in design" | `designer` |
| "Update CRC cards / sequences" | `designer` |
| "Update design based on these changes" | `designer` |
| "Update design after code changes" | `design-maintainer` |
| "Run gap analysis" | `gap-analyzer` |
| "Generate/update documentation" | `documenter` |

**Do NOT manually edit design files** unless it's a trivial fix (typo, formatting). Always delegate to the appropriate agent to ensure:
- Consistency across CRC cards, sequences, and architecture
- Proper traceability updates
- Test design updates when needed

### 📚 Documentation Generation

**After completing design or implementation work, offer to generate or update project documentation.**

Use the `documenter` agent to create:
- `docs/requirements.md` - Requirements documentation from specs
- `docs/design.md` - Design overview from CRC cards and sequences
- `docs/developer-guide.md` - Developer documentation with architecture and setup
- `docs/user-manual.md` - User manual with features and how-to guides
- `design/traceability-docs.md` - Documentation traceability map

**When to offer documentation generation:**
- After creating/updating Level 2 design specs
- After implementing Level 3 code
- When specs or design changes significantly
- When user explicitly requests it

**Example offer:**
"I've completed the [design/implementation]. Would you like me to generate/update the project documentation (requirements, design overview, developer guide, and user manual)?"
