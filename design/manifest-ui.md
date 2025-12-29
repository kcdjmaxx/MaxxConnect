# UI Manifest
**Source Spec:** phase-2-campaign-management.md

## Routes

| Route | View | Description | Status |
|-------|------|-------------|--------|
| `/` | Dashboard | Overview stats and quick actions | Implemented |
| `/contacts` | ContactList | View all customers | Implemented |
| `/import` | ImportCSV | CSV contact import | Implemented |
| `/preview` | EmailPreview | Test email composition | Implemented |
| `/sms-preview` | SMSPreview | Test SMS composition | Implemented |
| `/campaigns` | CampaignList | All campaigns with status | **Implemented** |
| `/campaign/new` | CampaignCreate | Create new campaign | **Implemented** |
| `/campaign/edit/<id>` | CampaignEdit | Edit existing campaign | **Implemented** |
| `/campaign/preview/<id>` | CampaignPreview | Preview HTML content | **Implemented** |
| `/campaign/send-confirm/<id>` | CampaignSendConfirm | Confirm before send | **Implemented** |
| `/campaign/send/<id>` | CampaignSend | Execute campaign send | **Implemented** |
| `/campaign/delete/<id>` | CampaignDelete | Delete campaign | **Implemented** |
| `/segments` | SegmentList | Manage customer segments | Planned Phase 2 |
| `/qr/<token>` | QRDisplay | Public QR code display for SMS | Planned Phase 2 |
| `/unsubscribe` | Unsubscribe | Email unsubscribe handler | Implemented |
| `/sms-optout` | SMSOptout | SMS opt-out handler | Implemented |

## View Hierarchy

```
base.html
  |-- dashboard.html
  |-- contacts.html
  |-- import.html
  |-- preview.html
  |-- sms_preview.html
  |-- campaigns.html               [IMPLEMENTED]
  |-- campaign_create.html         [IMPLEMENTED]
  |-- campaign_edit.html           [IMPLEMENTED]
  |-- campaign_send_confirm.html   [IMPLEMENTED]
  |-- unsubscribe.html
  |-- email/
  |     |-- monday_special.html    [IMPLEMENTED - sample template]
  |-- segments/
  |     |-- list.html              [PLANNED Phase 2]
  |-- qr_display.html              [PLANNED Phase 2]
  |-- campaigns/
        |-- analytics.html         [PLANNED Phase 3]
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
