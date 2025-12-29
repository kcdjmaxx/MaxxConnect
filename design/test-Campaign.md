# Test Design: Campaign

**Source Specs**: specs/phase-2-campaign-management.md
**CRC Cards**: crc-Campaign.md, crc-CampaignManager.md
**Sequences**: seq-campaign-create.md, seq-campaign-send.md, seq-campaign-send-qr.md, seq-campaign-preview.md

## Overview

Tests for Campaign model and CampaignManager service covering campaign lifecycle, validation, status transitions, and customer targeting.

## Test Cases

### Test: Create campaign with valid data

**Purpose**: Verify campaign can be created with all required fields populated

**Input**:
- name: "Pizza Deal"
- subject: "20% Off Pizza!"
- email_content: valid HTML with placeholders
- sms_content: "Get 20% off!" (under 160 chars)
- target_segments: "vip,pizza-lover"
- qr_expiration_days: 30

**References**:
- CRC: crc-CampaignManager.md - "Does: create_campaign()"
- Sequence: seq-campaign-create.md

**Expected Results**:
- Campaign created in database
- status = "draft"
- created_at timestamp set
- Returns campaign object with id

---

### Test: Validate campaign before send

**Purpose**: Ensure campaigns with missing required fields cannot be sent

**Input**:
- Campaign with missing subject
- Campaign with missing email_content
- Campaign with no target_segments

**References**:
- CRC: crc-CampaignManager.md - "Does: validate_campaign()"
- CRC: crc-Campaign.md - "Does: is_ready_to_send()"

**Expected Results**:
- Validation error raised for missing subject
- Validation error raised for missing content
- Validation error raised for no segments
- Campaign remains in draft status

---

### Test: Status transitions follow valid flow

**Purpose**: Verify only valid status transitions are allowed

**Input**:
- draft -> queued (valid)
- draft -> sending (invalid)
- queued -> sending (valid)
- sending -> completed (valid)
- sending -> failed (valid)
- completed -> draft (invalid)

**References**:
- CRC: crc-Campaign.md - "Does: validate_status_transition()"

**Expected Results**:
- Valid transitions succeed
- Invalid transitions raise error
- Status field updated only on valid transitions

---

### Test: Calculate target customer count

**Purpose**: Verify customer count calculation for segments

**Input**:
- Campaign targeting "vip" segment (150 customers)
- Campaign targeting "ALL" (5000 customers)
- Campaign targeting "vip,pizza-lover" (2450 unique customers)

**References**:
- CRC: crc-Campaign.md - "Does: get_target_customer_count()"
- CRC: crc-CampaignManager.md - "Does: get_targeted_customers()"

**Expected Results**:
- Correct count returned for single segment
- Correct count for ALL
- Deduplicated count for multiple segments

---

### Test: Estimate send duration

**Purpose**: Verify duration estimation based on rate limits

**Input**:
- 5000 customers, 100 emails/min rate = ~50 minutes
- 1000 customers, 50 emails/min rate = ~20 minutes

**References**:
- CRC: crc-Campaign.md - "Does: calculate_estimated_duration()"

**Expected Results**:
- Duration calculated correctly
- Includes both email and SMS send times

---

### Test: Campaign preview generation

**Purpose**: Verify preview generates sample email and SMS

**Input**:
- Campaign with email_content containing {{ customer_name }}
- Campaign with sms_content containing short URL placeholder

**References**:
- CRC: crc-CampaignManager.md - "Does: preview_campaign()"
- Sequence: seq-campaign-preview.md

**Expected Results**:
- Email HTML rendered with sample customer data
- QR code generated (temporary, not persisted)
- SMS rendered with short URL
- Character count displayed for SMS

---

### Test: Send campaign queues tasks

**Purpose**: Verify campaign send creates Celery tasks

**Input**:
- Campaign targeting 100 customers
- Campaign with both email and SMS content

**References**:
- CRC: crc-CampaignManager.md - "Does: send_campaign()"
- Sequence: seq-campaign-send.md

**Expected Results**:
- Campaign status changed to "queued"
- QR codes generated for all customers
- Email tasks enqueued for email-subscribed customers
- SMS tasks enqueued for SMS-subscribed customers
- Function returns immediately (non-blocking)

---

### Test: Update campaign metrics

**Purpose**: Verify metrics update correctly during send

**Input**:
- Successful email send
- Failed email send
- Successful SMS send

**References**:
- CRC: crc-Campaign.md - "Knows: emails_sent, emails_failed"
- CRC: crc-CampaignAnalytics.md - "Does: update_metrics()"

**Expected Results**:
- emails_sent incremented on success
- emails_failed incremented on failure
- sms_sent/sms_failed updated correctly

---

### Test: Progress percentage calculation

**Purpose**: Verify progress updates correctly during send

**Input**:
- Campaign with 1000 targeted, 500 sent
- Campaign with 1000 targeted, 1000 sent

**References**:
- CRC: crc-Campaign.md - "Does: get_progress_percentage()"

**Expected Results**:
- 50% progress shown for half sent
- 100% progress shown when complete
- Progress updates in real-time

## Coverage Summary

**Responsibilities Covered**:
- Campaign creation and validation
- Status transitions
- Target customer calculation
- Preview generation
- Task queuing
- Metrics tracking
- Progress calculation

**Scenarios Covered**:
- seq-campaign-create.md: Full flow
- seq-campaign-preview.md: Full flow
- seq-campaign-send.md: Task queuing portion

**Gaps**:
- A/B testing (Phase 4)
- Campaign pause/resume

---

## QR Code Toggle Tests

### Test: Create campaign with QR code toggle enabled

**Purpose**: Verify campaign can be created with has_qr_code flag set to True

**Input**:
- name: "Burger Deal with QR"
- subject: "Scan for 20% Off!"
- template_name: "email/monday_special.html"
- has_qr_code: True

**References**:
- CRC: crc-Campaign.md - "Knows: has_qr_code"
- CRC: crc-CampaignManager.md - "Does: campaign_new()"
- UI: ui-campaign-create.md - "QR Code Toggle" section

**Expected Results**:
- Campaign created with has_qr_code = True
- status = "draft"
- Toggle value persisted in database

---

### Test: Create campaign with QR code toggle disabled (default)

**Purpose**: Verify campaign defaults to has_qr_code = False when not specified

**Input**:
- name: "Standard Newsletter"
- subject: "Weekly Update"
- template_name: "email/monday_special.html"
- (has_qr_code not provided)

**References**:
- CRC: crc-Campaign.md - "Knows: has_qr_code"

**Expected Results**:
- Campaign created with has_qr_code = False
- Standard email flow will be used (no QR generation)

---

### Test: Edit campaign QR toggle before send

**Purpose**: Verify QR toggle can be changed while campaign is in draft status

**Input**:
- Existing campaign with has_qr_code = False, status = "draft"
- Update has_qr_code to True

**References**:
- CRC: crc-CampaignManager.md - "Does: campaign_edit()"
- CRC: crc-Campaign.md - "Knows: has_qr_code, status"

**Expected Results**:
- QR toggle updated successfully
- Campaign remains in draft status
- Updated value persisted

---

### Test: Cannot edit QR toggle after campaign is sent

**Purpose**: Verify QR toggle is immutable after campaign status = "sent"

**Input**:
- Existing campaign with has_qr_code = True, status = "sent"
- Attempt to update has_qr_code to False

**References**:
- CRC: crc-Campaign.md - "Knows: has_qr_code, status"
- UI: ui-campaign-send-confirm.md - "QR status displayed but not editable"

**Expected Results**:
- Edit rejected or toggle disabled in UI
- has_qr_code value unchanged
- Error message or disabled control indicates immutability

---

### Test: Send campaign with QR codes generates unique codes per recipient

**Purpose**: Verify QR code generation occurs during send when has_qr_code = True

**Input**:
- Campaign with has_qr_code = True
- 3 target customers

**References**:
- CRC: crc-CampaignManager.md - "Does: campaign_send()"
- CRC: crc-QRCodeGenerator.md - "Does: create_qr_code()"
- Sequence: seq-campaign-send-qr.md

**Expected Results**:
- 3 unique QR codes generated (one per customer)
- Each QR code has token format: {campaign_id}-{customer_id}-{hash}
- QR codes persisted to database before email send
- Emails contain QR code images as base64

---

### Test: Send campaign without QR codes skips generation

**Purpose**: Verify no QR codes generated when has_qr_code = False

**Input**:
- Campaign with has_qr_code = False
- 3 target customers

**References**:
- CRC: crc-CampaignManager.md - "Does: campaign_send()"
- Sequence: seq-campaign-send.md

**Expected Results**:
- No QR codes generated
- No QR code records in database for this campaign
- Emails sent without QR code images
- Template conditional {% if qr_code_base64 %} evaluates to false

---

### Test: QR code section conditionally rendered in email template

**Purpose**: Verify email template correctly shows/hides QR code section

**Input**:
- Template with {% if qr_code_base64 %}...{% endif %} block
- Render with qr_code_base64 provided
- Render without qr_code_base64

**References**:
- CRC: crc-CampaignManager.md - "Does: render_email_with_qr()"
- UI: ui-campaign-create.md - Notes on conditional template rendering

**Expected Results**:
- With qr_code_base64: QR section rendered, image displayed
- Without qr_code_base64: QR section omitted from output
- Template renders cleanly in both cases

---

### Test: Send confirmation shows QR status

**Purpose**: Verify send confirmation page displays correct QR status

**Input**:
- Campaign with has_qr_code = True
- Campaign with has_qr_code = False

**References**:
- UI: ui-campaign-send-confirm.md - "QR Code Status Display" section

**Expected Results**:
- QR enabled campaign: Shows checkmark icon, green info box
- QR disabled campaign: Shows dash icon, no info box
- QR status not editable on this page

---

### Test: Test mode send generates QR code for test email

**Purpose**: Verify test mode respects QR toggle setting

**Input**:
- Campaign with has_qr_code = True
- Test mode enabled
- Test email address provided

**References**:
- Sequence: seq-campaign-send-qr.md - "Test mode" note
- CRC: crc-CampaignManager.md - "Does: campaign_send()"

**Expected Results**:
- Single QR code generated for test email recipient
- QR code visible in test email
- No QR codes generated for actual subscribers
- Campaign status remains "draft"

---

## QR Toggle Coverage Summary

**Responsibilities Covered**:
- Campaign.has_qr_code field storage and default
- Toggle editable only in draft status
- Conditional QR generation during send
- Template conditional rendering
- UI display of QR status

**Scenarios Covered**:
- seq-campaign-send-qr.md: Full flow with QR generation
- ui-campaign-create.md: QR toggle interaction
- ui-campaign-send-confirm.md: QR status display

**Gaps**:
- QR code validation/redemption (Phase 2 - out of scope for toggle feature)
