---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/documentation
  - status/active
  - tool/flask
---

# UI Manifest
**Source Spec:** phase-2-campaign-management.md

## Routes

| Route | View | Auth | Description | Status |
|-------|------|------|-------------|--------|
| `/` | Dashboard | Yes | Overview stats and quick actions | Implemented |
| `/contacts` | ContactList | Yes | View all customers | Implemented |
| `/import` | ImportCSV | Yes | CSV contact import with consent | Implemented |
| `/preview` | EmailPreview | Yes | Test email composition | Implemented |
| `/sms-preview` | SMSPreview | Yes | Test SMS composition | Implemented |
| `/campaigns` | CampaignList | Yes | All campaigns with status | Implemented |
| `/campaign/new` | CampaignCreate | Yes | Create new campaign | Implemented |
| `/campaign/edit/<id>` | CampaignEdit | Yes | Edit existing campaign | Implemented |
| `/campaign/preview/<id>` | CampaignPreview | Yes | Preview HTML content | Implemented |
| `/campaign/send-confirm/<id>` | CampaignSendConfirm | Yes | Confirm before send | Implemented |
| `/campaign/send/<id>` | CampaignSend | Yes | Execute campaign send | Implemented |
| `/campaign/delete/<id>` | CampaignDelete | Yes | Delete campaign | Implemented |
| `/test-template` | TestTemplate | Yes | Test email template render | Implemented |
| `/segments` | SegmentList | Yes | Manage customer segments | Planned Phase 2 |
| `/staff/redeem` | StaffScanner | Yes | QR scanner PWA for staff | Implemented |
| `/redeem/<token>` | RedeemResult | No | Public QR code landing page | Implemented |
| `/api/redeem/<token>` | RedeemAPI | Yes | Perform QR redemption | Implemented |
| `/api/validate/<token>` | ValidateAPI | Yes | Validate QR without redeeming | Implemented |
| `/analytics/redemptions` | RedemptionAnalytics | Yes | Redemption metrics dashboard | Implemented |
| `/signup` | PublicSignup | No | Public subscription form | Implemented |
| `/unsubscribe` | Unsubscribe | No | Email unsubscribe handler | Implemented |
| `/sms-optout` | SMSOptout | No | SMS opt-out handler (Twilio webhook) | Implemented |
| `/templates` | TemplateList | Yes | Template gallery with validation badges | Implemented |
| `/template/new` | TemplateCreate | Yes | Create template (editor choice) | Implemented (to modify) |
| `/template/import` | TemplateImport | Yes | Import HTML template wizard | Implemented |
| `/template/edit/<filename>` | TemplateEdit | Yes | Code editor with live preview | Implemented |
| `/template/designer/<filename>` | TemplateDesigner | Yes | GrapesJS visual designer | Planned |
| `/template/preview/<filename>` | TemplatePreview | Yes | Preview with sample data | Implemented |
| `/template/delete/<filename>` | TemplateDelete | Yes | Delete template + sidecar | Implemented (to modify) |
| `/api/template/save-design` | DesignerSaveAPI | Yes | Save JSON + HTML from designer | Planned |
| `/api/template/load-design/<filename>` | DesignerLoadAPI | Yes | Load project JSON for designer | Planned |
| `/api/template/upload-image` | ImageUploadAPI | Yes | Upload image for templates | Implemented |
| `/template/images/<filename>` | ImageServe | No | Serve uploaded images | Implemented |

**Auth:** HTTP Basic Auth via flask-httpauth. See cross-cutting: Authentication in design.md.

## View Hierarchy

```
base.html
  |-- dashboard.html
  |-- contacts.html
  |-- import.html                  [consent checkboxes added]
  |-- preview.html
  |-- sms_preview.html
  |-- campaigns.html
  |-- campaign_create.html
  |-- campaign_edit.html
  |-- campaign_send_confirm.html
  |-- signup.html                  [public form]
  |-- unsubscribe.html             [public]
  |-- redemption_analytics.html    [Phase 3]
  |-- email/
  |     |-- monday_special.html    [sample template]
  |-- template_list.html             [template gallery]
  |-- template_create.html           [create with editor choice]
  |-- template_import.html           [import wizard]
  |-- template_edit.html             [code editor]
  |-- template_designer.html         [GrapesJS visual designer - PLANNED]
  |-- segments/
  |     |-- list.html              [PLANNED Phase 2]

staff_redeem.html                  [standalone PWA, no base.html]
redeem_result.html                 [standalone public page]
```

## Global Components

### Navigation (base.html)
- Horizontal nav bar with route links
- Active state highlighting
- Consistent across all views

### Stat Cards
- Gradient background
- Large number heading
- Description text
- Used in Dashboard, Analytics

### Form Cards
- White background card
- Form inputs with labels
- Submit/action buttons
- Message display (success/error)

### Data Tables
- Header row with column names
- Sortable columns (future)
- Row hover states
- Action buttons per row

### Message Alerts
- Success: green background
- Error: red background
- Info: blue background
- Auto-dismiss optional

## UI Patterns

### Form Submission
1. POST to same route
2. Validate server-side
3. Re-render with message or redirect

### Progress Indicators
- Campaign send progress bar
- Percentage text display
- Auto-refresh during send (AJAX)

### Confirmation Dialogs
- Used before campaign send
- JavaScript confirm() or modal
- Show customer count before action

### Segment Selection
- Multi-select dropdown or checkboxes
- "ALL" option for entire list
- Show count per segment

## Theme

### Colors
- Primary: #667eea (purple-blue gradient)
- Secondary: #764ba2 (purple)
- Success: #43e97b (green)
- Error: #f5576c (red)
- Info: #4facfe (blue)
- Background: #f5f5f5
- Card: #ffffff
- Text: #333333

### Typography
- Headings: System sans-serif, bold
- Body: System sans-serif, regular
- Monospace: For code/tokens

### Spacing
- Container padding: 2rem
- Card padding: 1.5rem
- Form element margin: 1rem

## Browser History

- Standard page navigation (full reload)
- Form submissions use POST-redirect-GET
- Campaign progress uses AJAX (no reload)
- Deep linking supported for all routes

## Accessibility

- Semantic HTML elements
- Form labels associated with inputs
- Color contrast ratios for text
- Focus states for interactive elements

## Responsive Behavior

- Mobile: Single column layout
- Tablet: 2-column stat cards
- Desktop: Full navigation, multi-column
