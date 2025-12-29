# Phase 3: Public Customer Signup & Acquisition

**Status:** Planned
**Date:** 2025-12-24
**Dependencies:** Phase 1 (Email/SMS integration), Phase 2 (Campaign Management)

## Overview

Phase 3 adds public-facing customer acquisition features, enabling customers to sign up for email/SMS marketing directly through web forms and QR codes. This transforms the platform from admin-only to a complete customer lifecycle system with both acquisition and engagement capabilities.

## Business Requirements

### 1. Public Signup Form with QR Code Access

**Requirement:** Customers can scan a QR code or visit a URL to sign up for email and/or SMS marketing without admin intervention.

**Rationale:**
- Enables in-restaurant customer acquisition (QR codes on table tents, receipts, posters)
- Reduces friction for customers (no need to give info to staff)
- Ensures proper TCPA/CAN-SPAM compliance with explicit opt-in
- Works outside Square's ecosystem (independent data ownership)
- Can be hosted on custom domain separate from main restaurant website

**Specifications:**

**Public Signup Page (`/signup`):**
- Clean, mobile-responsive form (majority of scans will be from phones)
- Required fields:
  - Email address (with validation)
  - Email subscription checkbox (explicit opt-in for CAN-SPAM)
- Optional fields:
  - Name (first name or full name)
  - Phone number (with E.164 normalization)
  - SMS subscription checkbox (explicit opt-in for TCPA)
- Privacy disclosure text:
  - "We'll send you exclusive deals and updates. You can unsubscribe anytime."
  - Link to privacy policy (if exists)
- Form validation:
  - Email format validation
  - Phone format validation (if provided)
  - At least one subscription type must be checked
- Success redirect to `/signup/success` with confirmation message

**QR Code Generation (`/qr-code`):**
- Generates printable QR code image pointing to signup URL
- QR code format: PNG image, 300x300px minimum
- URL encoded in QR: `https://yourdomain.com/signup`
- Admin can download QR code for printing (table tents, posters, receipts)
- Optional: Generate QR code with UTM parameters for tracking source
  - Example: `https://yourdomain.com/signup?source=table-tent`

**Backend Processing:**
- POST endpoint accepts form data
- Normalizes email (lowercase, trim)
- Normalizes phone to E.164 format (if provided)
- Checks for duplicate email (update existing customer if found)
- Creates new Customer record with:
  - `subscribed = True` if email checkbox checked
  - `sms_subscribed = True` if SMS checkbox checked
  - `opted_in_date = now()` for email
  - `sms_opted_in_date = now()` for SMS
- Optionally add segment tag (e.g., `qr-signup` to track acquisition source)
- Send confirmation email/SMS (welcome message)

**Example Use Case:**
> Fric & Frac restaurant places QR code table tents with "Scan for exclusive deals!" Customer Alice scans QR code with phone camera, lands on signup form, enters email alice@example.com and phone +1234567890, checks both email and SMS boxes, submits. System creates Customer record with both subscriptions enabled. Alice receives welcome email with first-time customer discount.

---

### 2. Success Page & Confirmation

**Requirement:** After signup, customer sees confirmation and optionally receives immediate welcome communication.

**Success Page (`/signup/success`):**
- Thank you message: "You're all set! Check your email/phone for exclusive deals."
- Clear statement of what to expect: "You'll receive our weekly specials every Monday."
- Reminder about opt-out: "You can unsubscribe anytime using the link in our emails."
- Optional: Display first deal/offer immediately
- Optional: Social media links

**Welcome Email (Automated):**
- Triggered immediately on signup
- Subject: "Welcome to [Business Name] Exclusive Deals!"
- Content:
  - Thank you for signing up
  - What to expect (frequency, types of offers)
  - First-time customer discount (optional)
  - Unsubscribe link (legal requirement)

**Welcome SMS (Automated):**
- Triggered immediately on SMS opt-in
- Example: "Welcome to [Business Name]! Reply STOP to opt out. Here's 10% off your next visit: [short URL]"
- Must include opt-out instructions (TCPA requirement)
- Character limit: 160 chars (single SMS)

---

### 3. QR Code Download & Printing Tools

**Requirement:** Admin can generate and download printable QR codes for physical marketing materials.

**QR Code Generator Page (`/admin/qr-generator`):**
- Input fields:
  - Destination URL (default: `/signup`)
  - UTM campaign source (optional: `table-tent`, `receipt`, `poster`, etc.)
  - QR code size (small/medium/large: 200px, 400px, 600px)
- Preview QR code before download
- Download as PNG image
- Optional: Generate PDF with multiple QR codes for printing

**Use Cases:**
- Print QR codes on table tents (5"x7" cards on restaurant tables)
- Add QR code to receipts ("Scan for 10% off next visit!")
- Create posters for windows ("Join our VIP list!")
- Include in physical mailers/flyers

---

### 4. Source Tracking & Attribution

**Requirement:** Track where signups originated (QR code location, online vs. in-person, etc.)

**Implementation:**
- Use `source` query parameter in signup URL
- Examples:
  - `/signup?source=table-tent`
  - `/signup?source=receipt`
  - `/signup?source=instagram-bio`
  - `/signup?source=email-signature`
- Store source in Customer record as segment tag
- Analytics dashboard shows signups by source

**Example Analytics:**
```
Signup Sources (Last 30 Days):
- table-tent: 145 signups
- receipt: 89 signups
- instagram-bio: 34 signups
- email-signature: 12 signups
```

---

## Technical Requirements

### Database Schema Changes

**Modified Table: `customers`**
- Existing fields support Phase 3 (no changes needed)
- Use `segments` field to store source tracking tags

**Example Customer Record (QR Signup):**
```python
{
  "email": "alice@example.com",
  "phone": "+12345678901",
  "name": "Alice",
  "subscribed": True,
  "sms_subscribed": True,
  "opted_in_date": "2025-12-24T10:30:00",
  "sms_opted_in_date": "2025-12-24T10:30:00",
  "segments": "qr-signup,table-tent"
}
```

### New Routes

**Public-Facing:**
- `GET /signup` - Display signup form
- `POST /signup` - Process form submission
- `GET /signup/success` - Show confirmation message

**Admin-Facing:**
- `GET /admin/qr-generator` - QR code generation tool
- `GET /qr-code` - Generate QR code image (with URL parameters)

### Dependencies

**New Python Libraries:**
- `qrcode` - Already in requirements.txt (Phase 1/2)
- `pillow` - Already in requirements.txt (image processing)

### Form Validation

**Email Validation:**
- Regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Normalize to lowercase
- Check for existing customer (merge if found)

**Phone Validation:**
- Use existing `format_phone_number()` from `backend/sms_service.py`
- Convert to E.164 format (+1234567890)
- Reject invalid formats

**Subscription Validation:**
- At least one of email or SMS must be checked
- If phone provided without SMS checkbox, warn user

### Security Considerations

**CSRF Protection:**
- Use Flask-WTF CSRF tokens on signup form
- Prevent automated bot submissions

**Rate Limiting:**
- Limit signup attempts per IP (e.g., 5 signups per hour per IP)
- Prevent spam/abuse

**Data Privacy:**
- Email/phone encryption (already implemented in Phase 1)
- No personally identifiable information in QR codes
- Compliance with GDPR/CCPA (if applicable)

---

## UI/UX Design

### Signup Form Layout

```
┌─────────────────────────────────────┐
│   [Business Logo]                   │
│                                     │
│   Join Our VIP List                 │
│   Get exclusive deals & updates!    │
│                                     │
│   Email: [________________]         │
│   ☑ Send me email updates          │
│                                     │
│   Phone: [________________]         │
│   ☐ Send me SMS updates            │
│                                     │
│   Name (optional): [_________]      │
│                                     │
│   [  Sign Me Up!  ]                │
│                                     │
│   We respect your privacy.          │
│   Unsubscribe anytime.              │
└─────────────────────────────────────┘
```

### QR Code Table Tent Design

```
┌─────────────────────────────────────┐
│                                     │
│    Exclusive Deals Await! 🎉        │
│                                     │
│         [QR CODE IMAGE]             │
│                                     │
│   Scan to join our VIP list         │
│   and get 10% off your next visit   │
│                                     │
└─────────────────────────────────────┘
```

---

## Phase 3 Workflow

1. **Admin generates QR code:**
   - Visits `/admin/qr-generator`
   - Selects source tag (e.g., "table-tent")
   - Downloads PNG image
   - Prints on table tents and places in restaurant

2. **Customer scans QR code:**
   - Phone camera opens signup URL
   - Customer sees mobile-optimized signup form

3. **Customer fills form:**
   - Enters email: alice@example.com
   - Enters phone: (234) 567-8901
   - Checks both email and SMS boxes
   - Submits form

4. **Backend processes signup:**
   - Validates email format
   - Normalizes phone to +12345678901
   - Checks for duplicate (email not found)
   - Creates new Customer record
   - Tags with "qr-signup,table-tent"
   - Sends welcome email via SendGrid
   - Sends welcome SMS via Twilio

5. **Customer sees success page:**
   - "You're all set! Check your inbox for a special offer."
   - Customer receives welcome email and SMS within seconds

6. **Admin views analytics:**
   - Dashboard shows new signup
   - Source attribution: "table-tent"
   - Customer now included in future campaigns

---

## Success Criteria

Phase 3 is complete when:
- [ ] Public signup form is accessible at `/signup`
- [ ] Form validates email and phone formats
- [ ] Form requires at least one subscription type (email or SMS)
- [ ] Duplicate emails update existing customer instead of creating new record
- [ ] Phone numbers are normalized to E.164 format
- [ ] Signup creates Customer record with proper opt-in timestamps
- [ ] Success page displays confirmation message
- [ ] Welcome email is sent automatically on email opt-in
- [ ] Welcome SMS is sent automatically on SMS opt-in
- [ ] Admin can generate QR codes with source tracking parameters
- [ ] QR codes download as PNG images ready for printing
- [ ] Source tracking tags are stored in customer segments
- [ ] Analytics dashboard shows signups by source
- [ ] Form has CSRF protection
- [ ] Rate limiting prevents spam submissions
- [ ] Mobile-responsive design works on all phone sizes

---

## Out of Scope (Future Phases)

- Double opt-in email confirmation (send verification email before activating subscription)
- Social media signup integration (Facebook/Instagram login)
- Multiple language support (Spanish signup form)
- Custom fields per business (birthday, favorite menu item, etc.)
- A/B testing for signup page conversion optimization
- Integration with Square POS for automatic customer sync

---

## Implementation Notes

### QR Code Generation Example

```python
import qrcode
from io import BytesIO
from flask import send_file

@app.route('/qr-code')
def generate_qr_code():
    signup_url = request.args.get('url', 'https://yourdomain.com/signup')
    source = request.args.get('source', '')

    if source:
        signup_url += f'?source={source}'

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(signup_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Return as PNG
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return send_file(buf, mimetype='image/png',
                     download_name='signup-qr-code.png')
```

### Signup Form Processing Example

```python
@app.route('/signup', methods=['POST'])
def signup_submit():
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    name = request.form.get('name', '').strip()
    email_opt_in = request.form.get('email_opt_in') == 'on'
    sms_opt_in = request.form.get('sms_opt_in') == 'on'
    source = request.args.get('source', 'web')

    # Validation
    if not email or not is_valid_email(email):
        return render_template('signup.html', error='Invalid email')

    if not email_opt_in and not sms_opt_in:
        return render_template('signup.html',
            error='Please select at least one subscription type')

    # Normalize phone
    formatted_phone = None
    if phone:
        formatted_phone = format_phone_number(phone)
        if not validate_phone_number(formatted_phone):
            return render_template('signup.html', error='Invalid phone')

    # Check for duplicate
    db = get_db()
    customer = db.query(Customer).filter_by(email=email).first()

    if customer:
        # Update existing customer
        if name and not customer.name:
            customer.name = name
        if formatted_phone and not customer.phone:
            customer.phone = formatted_phone
        if email_opt_in and not customer.subscribed:
            customer.subscribed = True
            customer.opted_in_date = datetime.now()
        if sms_opt_in and formatted_phone and not customer.sms_subscribed:
            customer.sms_subscribed = True
            customer.sms_opted_in_date = datetime.now()
    else:
        # Create new customer
        customer = Customer(
            email=email,
            phone=formatted_phone,
            name=name,
            subscribed=email_opt_in,
            sms_subscribed=sms_opt_in and formatted_phone is not None,
            opted_in_date=datetime.now() if email_opt_in else None,
            sms_opted_in_date=datetime.now() if sms_opt_in else None,
            segments=f'qr-signup,{source}'
        )
        db.add(customer)

    db.commit()

    # Send welcome messages
    if email_opt_in:
        send_welcome_email(customer)
    if sms_opt_in and formatted_phone:
        send_welcome_sms(customer)

    return redirect('/signup/success')
```

---

## Related Documents

- `phase01.md` - Phase 1 foundation (email/SMS sending, CSV import)
- `specs/phase-2-campaign-management.md` - Phase 2 campaign system
- `backend/sms_service.py` - Phone number normalization functions
- `backend/models.py` - Customer database model

---

## Timeline Estimate

**Not provided** - User decides implementation timeline based on priorities.
