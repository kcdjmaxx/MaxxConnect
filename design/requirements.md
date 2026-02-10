# Requirements

## Feature: Phase 1 - Foundation
**Source:** phase01.md

- **R1:** System sends emails via SendGrid API with proper deliverability
- **R2:** CSV import supports simple format (email, name, phone) and Square POS export format
- **R3:** CSV import deduplicates contacts by email address
- **R4:** CSV import normalizes emails to lowercase and validates format
- **R5:** Test email functionality allows previewing before campaign send
- **R6:** Unsubscribe links are included in all emails (CAN-SPAM compliance)
- **R7:** Unsubscribe requests are processed immediately
- **R8:** Business address is included in email footer (legal requirement)
- **R9:** Dashboard displays contact statistics (total, subscribed, unsubscribed)
- **R10:** Contacts page displays all customers with status and segments

## Feature: Phase 2 - Campaign Management
**Source:** specs/phase-2-campaign-management.md

### QR Code Generation
- **R11:** Each customer receives unique QR code per campaign
- **R12:** QR token format: `{campaign_id}-{customer_id}-{secure_random_hash}`
- **R13:** QR codes embedded in emails as CID attachments (Gmail compatible)
- **R14:** SMS messages include short URL to QR code display page
- **R15:** QR codes have configurable expiration dates
- **R16:** System prevents duplicate redemptions (track usage count)
- **R17:** QR token generation uses cryptographically secure random hashes
- **R18:** QR validation occurs server-side only

### Customer Segmentation
- **R19:** Customers can have multiple tags (comma-separated)
- **R20:** Tags assigned during CSV import or manually per customer
- **R21:** Campaign creation allows selecting target segments
- **R22:** Tags are case-insensitive (normalize to lowercase)
- **R23:** System shows customer count per segment before campaign send

### Async Queue System
- **R24:** Emails/SMS sent through Celery background queue with Redis
- **R25:** Configurable send rate (default: 100 emails/min, 10 SMS/min)
- **R26:** Failed sends retry up to 3 times with exponential backoff
- **R27:** Campaign states: draft, queued, sending, completed, failed
- **R28:** Real-time progress updates in admin UI

### Campaign Analytics
- **R29:** Track total emails/SMS sent and failed per campaign
- **R30:** Track customers targeted with segment breakdown
- **R31:** Campaign list shows status, date, send counts
- **R32:** (inferred) Export campaign report as CSV

## Feature: Phase 2 - QR Redemption System
**Source:** specs/phase-2-campaign-management.md (Phase 3 deliverable, implemented)

- **R33:** Staff scanner PWA with camera-based QR scanning
- **R34:** Manual token entry fallback for scanner
- **R35:** Audio/voice feedback on scan result
- **R36:** Redemption analytics dashboard with rates and distribution
- **R37:** Fraud detection via device info and IP tracking
- **R38:** iOS home screen support (PWA meta tags)

## Feature: Phase 2 - Template Management
**Source:** (inferred from implementation)

- **R39:** Template import wizard with auto-placeholder injection
- **R40:** Template validation checks required elements
- **R41:** Template editor with live preview
- **R42:** Template list with validation status badges

## Feature: Phase 3 - Public Customer Signup
**Source:** specs/phase-3-public-signup.md

### Public Signup Form
- **R43:** Public signup form at `/signup` (no auth required)
- **R44:** Form validates email and phone formats
- **R45:** At least one subscription type required (email or SMS)
- **R46:** Duplicate emails update existing customer
- **R47:** Phone numbers normalized to E.164 format
- **R48:** Signup creates Customer with proper opt-in timestamps
- **R49:** Success page displays confirmation message

### Welcome Messages
- **R50:** Welcome email sent automatically on email opt-in
- **R51:** Welcome SMS sent automatically on SMS opt-in
- **R52:** SMS includes opt-out instructions (TCPA requirement)

### QR Code Generator for Signup
- **R53:** Admin can generate QR codes with source tracking parameters
- **R54:** QR codes download as PNG for printing
- **R55:** Source tracking tags stored in customer segments

### Security
- **R56:** CSRF protection on signup form
- **R57:** Rate limiting prevents spam submissions
- **R58:** Mobile-responsive design

## Feature: Phase 4 - Advanced Features (Planned)
**Source:** specs/phase-2-campaign-management.md (Out of Scope section)

- **R59:** Bounce handling automation via SendGrid Suppressions API
- **R60:** A/B testing for subject lines
- **R61:** Email open rate tracking
- **R62:** Redemption report exports

## Feature: GrapesJS Drag-and-Drop Template Designer
**Source:** specs/grapesjs-template-designer.md

### Visual Designer Core
- **R63:** Visual drag-and-drop email template designer using GrapesJS with newsletter preset
- **R64:** Editor canvas renders email template visually with inline editing
- **R65:** Side panel with block library, style manager, and layer manager

### Content Blocks
- **R66:** Standard email blocks: text, image, button, divider, quote, grid/list items
- **R67:** Layout blocks: full-width (sect100), 2-column (sect50), 3-column (sect30), 30/70 split (sect37)
- **R68:** Custom compliance footer block with unsubscribe link, address, and privacy link
- **R69:** Custom QR code section block with `<!-- QR_CODE_SECTION -->` marker
- **R70:** Custom customer greeting block with `[[CUSTOMER_NAME]]` placeholder

### Image Handling
- **R71:** Drag-and-drop images from desktop onto canvas
- **R72:** GrapesJS asset manager connected to existing image upload endpoint
- **R73:** Image gallery shows previously uploaded images for reuse
- **R74:** (inferred) Image upload validates file type (PNG/JPG/GIF) and size (max 2MB) - reuses existing endpoint

### Save and Load
- **R75:** Save stores GrapesJS project JSON (for re-editing) and inlined HTML (for sending)
- **R76:** Project JSON stored as sidecar file `<name>.grapes.json` alongside `<name>.html`
- **R77:** Load detects sidecar JSON and opens visual designer; otherwise opens code editor
- **R78:** Templates without JSON sidecar can be imported into visual designer

### Compliance Validation
- **R79:** On save, run existing TemplateProcessor.validate() on exported HTML
- **R80:** Show validation results (errors/warnings/info) in designer panel
- **R81:** Block saving if required CAN-SPAM elements are missing (unsubscribe, address, privacy)

### Mode Switching
- **R82:** Template list indicates whether template has visual designer data
- **R83:** Visual designer has "Switch to Code Editor" button (with data loss warning)
- **R84:** Code editor has "Switch to Visual Designer" button (imports HTML into GrapesJS)
- **R85:** New template creation offers choice between Visual Designer and Code Editor

### Starter Templates
- **R86:** Pre-built GrapesJS starter templates: Basic Announcement, Special Offer, Newsletter
- **R87:** Starters include all compliance elements pre-configured
- **R88:** User selects starter when creating new template in visual mode
