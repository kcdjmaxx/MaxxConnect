# Test Design: UI Components

**Source Specs**: specs/phase-2-campaign-management.md
**UI Specs**: ui-campaign-list.md, ui-campaign-create.md, ui-campaign-preview.md, ui-campaign-analytics.md, ui-segment-list.md, ui-qr-display.md

## Overview

Tests for UI views, forms, interactions, and rendering.

## Test Cases

### Test: Campaign list displays all campaigns

**Purpose**: Verify campaign list shows all records

**Input**:
- Database with 10 campaigns in various states

**References**:
- UI Spec: ui-campaign-list.md

**Expected Results**:
- All 10 campaigns shown
- Sorted by created_at descending
- Status badges colored correctly
- Actions appropriate per status

---

### Test: Campaign list status filtering

**Purpose**: Verify status badge rendering

**Input**:
- Campaign with status "draft"
- Campaign with status "sending"
- Campaign with status "completed"

**References**:
- UI Spec: ui-campaign-list.md - CSS Classes

**Expected Results**:
- Draft: gray badge
- Sending: blue badge with animation
- Completed: green badge

---

### Test: Campaign create form validation

**Purpose**: Verify client-side form validation

**Input**:
- Empty required fields
- SMS content over 160 chars

**References**:
- UI Spec: ui-campaign-create.md

**Expected Results**:
- Required field errors shown
- Character count warning for SMS
- Form submission blocked

---

### Test: Segment selection updates count

**Purpose**: Verify customer count updates on selection

**Input**:
- Select "vip" segment (150 customers)
- Select additional "pizza-lover" (2300 unique customers)

**References**:
- UI Spec: ui-campaign-create.md - Events

**Expected Results**:
- Count updates dynamically
- Deduplicated count shown
- ALL selection shows total

---

### Test: SMS character counter

**Purpose**: Verify character count display

**Input**:
- Type message incrementally
- Exceed 160 characters

**References**:
- UI Spec: ui-campaign-create.md - CSS Classes

**Expected Results**:
- Counter updates on keyup
- Warning style when > 160
- Includes opt-out footer in count

---

### Test: Campaign preview renders email

**Purpose**: Verify email preview display

**Input**:
- Campaign with HTML content
- Sample customer data

**References**:
- UI Spec: ui-campaign-preview.md

**Expected Results**:
- HTML rendered correctly
- QR code image displayed
- Personalization substituted
- Unsubscribe link present

---

### Test: Campaign preview renders SMS

**Purpose**: Verify SMS preview display

**Input**:
- Campaign with SMS content

**References**:
- UI Spec: ui-campaign-preview.md

**Expected Results**:
- SMS text displayed
- Short URL shown
- Opt-out footer present
- Character count accurate

---

### Test: Send confirmation dialog

**Purpose**: Verify confirmation before send

**Input**:
- Click "Send Campaign" button

**References**:
- UI Spec: ui-campaign-preview.md - Events

**Expected Results**:
- Confirmation modal shown
- Customer count displayed
- Cancel option available
- Confirm triggers send

---

### Test: Analytics dashboard progress bar

**Purpose**: Verify progress visualization

**Input**:
- Campaign at 50% complete
- Campaign at 100% complete

**References**:
- UI Spec: ui-campaign-analytics.md

**Expected Results**:
- Progress bar fills correctly
- Percentage text accurate
- Animation during active send
- Static when complete

---

### Test: Analytics auto-refresh

**Purpose**: Verify refresh during active send

**Input**:
- Campaign in "sending" status

**References**:
- UI Spec: ui-campaign-analytics.md - Notes

**Expected Results**:
- Page refreshes every 5 seconds
- Metrics update in real-time
- Stops refresh when complete

---

### Test: Segment list displays counts

**Purpose**: Verify segment table rendering

**Input**:
- Database with multiple segments

**References**:
- UI Spec: ui-segment-list.md

**Expected Results**:
- All segments shown
- Customer counts accurate
- View Customers links work

---

### Test: QR display page renders

**Purpose**: Verify public QR display

**Input**:
- Valid QR token

**References**:
- UI Spec: ui-qr-display.md

**Expected Results**:
- QR code image large and centered
- Campaign/deal name shown
- Expiration date displayed
- Mobile-optimized layout

---

### Test: QR display expired state

**Purpose**: Verify expired QR handling

**Input**:
- Expired QR token

**References**:
- UI Spec: ui-qr-display.md

**Expected Results**:
- "EXPIRED" message shown
- No QR code displayed
- Expiration date shown
- Graceful error handling

---

### Test: QR display invalid token

**Purpose**: Verify invalid token handling

**Input**:
- Non-existent QR token

**References**:
- UI Spec: ui-qr-display.md

**Expected Results**:
- 404 or error page
- No sensitive info leaked
- Appropriate error message

---

### Test: CSV export download

**Purpose**: Verify report export functionality

**Input**:
- Click "Export CSV" button

**References**:
- UI Spec: ui-campaign-analytics.md - Events

**Expected Results**:
- CSV file downloads
- Filename includes campaign name
- Data matches displayed metrics

---

### Test: Navigation links work

**Purpose**: Verify all nav routes accessible

**Input**:
- Click each navigation link

**References**:
- manifest-ui.md - Routes

**Expected Results**:
- All routes resolve
- Correct page loads
- Active state highlighted

## Coverage Summary

**Responsibilities Covered**:
- Campaign list rendering
- Campaign form creation
- Segment selection
- Character counting
- Preview rendering
- Confirmation dialogs
- Progress visualization
- Auto-refresh
- QR display
- Export functionality
- Navigation

**Scenarios Covered**:
- All UI specs covered

**Gaps**:
- Accessibility testing
- Browser compatibility
- Mobile responsiveness
