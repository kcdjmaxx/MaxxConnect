---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - tool/flask
  - status/active
  - type/user-guide
---

# Campaign Management Guide

## Overview

Complete guide to creating, managing, and sending email campaigns in the MailChimp Clone platform.

## Quick Start

1. **Create your first campaign**: `/campaigns` → "Create New Campaign"
2. **Select a template**: Choose from available email templates
3. **Preview**: Check how it looks before sending
4. **Send**: Use test mode first, then send to audience

---

## Creating a Campaign

### Step 1: Navigate to Campaigns
- Click **"Campaigns"** in the navigation menu
- Or visit: `http://localhost:5001/campaigns`

### Step 2: Create New Campaign
Click **"Create New Campaign"** button

**Fill in the form:**
- **Campaign Name**: Internal name (e.g., "Monday Burger Special - Dec 2024")
- **Subject Line**: Email subject (e.g., "🍔 DOUBLE UP THIS MONDAY!")
- **Template**: Select from dropdown
  - Templates auto-discovered from `templates/email/`
  - Example: "Monday Special" template

**Action buttons:**
- **Preview Campaign**: See rendered email
- **Save as Draft**: Save for later
- **Send Campaign**: → Opens send confirmation page

---

## Managing Campaigns

### Viewing All Campaigns

The campaigns list shows:
- Campaign Name (click to edit)
- Subject Line
- Template Used
- Status (draft, sent)
- Created Date
- Actions (Preview, Send, Delete)

### Editing a Campaign

**To edit:**
1. Click the **campaign name** (blue/purple link)
2. Modify fields as needed
3. Click **"Save Changes"** or **"Preview Changes"**

**What you can edit:**
- Campaign name
- Subject line
- Template selection

**Notes:**
- Changing template re-renders the entire email
- Cannot edit campaigns marked as "sent"

### Deleting a Campaign

**To delete:**
1. Click the **🗑️ trash icon** in Actions column
2. Confirm deletion in popup dialog
3. Campaign permanently removed

**Warning:** Deletion cannot be undone!

---

## Sending Campaigns

### Send Confirmation Workflow

When you click **📧 Send** on a draft campaign:

**Step 1: Send Confirmation Page Opens**

Shows:
- Campaign summary (name, subject, template, created date)
- Preview link (opens in new tab)
- Audience selection dropdown
- Test mode checkbox
- Safety warnings

**Step 2: Select Your Audience**

Choose from:
- **All Subscribers** - Everyone with email subscription
- **Email Only** - Subscribers without SMS enabled
- **SMS Only** - Future feature
- **Email + SMS** - Future feature

Counts shown for each segment.

**Step 3: Choose Send Mode**

### Test Mode (Recommended First!)

**To use test mode:**
1. ✅ Check **"Test Mode"** checkbox
2. Enter your test email address
3. Button changes to: 📧 **"Send Test Email Only"** (orange)
4. Info box: "Email will only be sent to your test address"

**Confirmation:**
```
Send TEST email to: your@email.com

This will NOT send to your subscribers.
```

**When to use:**
- Testing new templates
- Checking images display correctly
- Verifying personalization
- Reviewing email content

### Live Mode (Sends to Real Subscribers!)

**To send to audience:**
1. ❌ Uncheck "Test Mode" checkbox
2. Select target audience
3. Button changes to: 📧 **"Send Campaign"** (green)
4. Warning box: "This will send REAL EMAILS..."

**Confirmation:**
```
⚠️ SEND TO ALL SUBSCRIBERS?

Target: All Subscribers (125)

This will send REAL emails and cannot be undone.

Continue?
```

**What happens:**
- Campaign sent to all matching subscribers
- Personalization applied (names, unsubscribe links)
- Campaign status changed to "sent"
- Cannot be edited after sending

---

## Email Templates

### Available Templates

Templates are stored in: `templates/email/`

**Current templates:**
- **Base Email** - Simple template
- **Monday Special** - Restaurant promotion template

### Template Variables

All templates support these Jinja2 variables:

**Required:**
- `{{ customer_name }}` - Customer's name or "Valued Customer"
- `{{ unsubscribe_link }}` - Legally required unsubscribe link

**Images (environment-aware):**
- **Development mode:**
  - `{{ logo_base64 }}` - Logo as base64
  - `{{ hero_image_base64 }}` - Hero banner as base64
- **Production mode:**
  - `{{ logo_url }}` - External URL to logo
  - `{{ hero_image_url }}` - External URL to banner

**Future:**
- `{{ qr_code_base64 }}` - QR code for redemption

### Adding New Templates

1. Create HTML file in `templates/email/`
2. Use template variables above
3. Test with "Create Campaign" → Select your template

**File naming:**
- Use descriptive names: `monday_special.html`
- Dashes/underscores converted to spaces in UI
- Example: `monday_special.html` → "Monday Special"

---

## Image Handling

### Development (localhost)

Images automatically converted to **base64** and embedded in email.

**Why?**
- Email clients can't access `localhost:5001/static/images/`
- Base64 embeds image data directly in HTML
- Ensures images display correctly in test emails

### Production (Railway.app)

Images use **external URLs** pointing to Railway static files.

**Example:**
- `https://your-app.railway.app/static/images/logo.png`

### Adding Images

1. Place images in: `static/images/`
2. Reference in templates:
   ```html
   {% if logo_url %}
     <img src="{{ logo_url }}" alt="Logo">
   {% else %}
     <img src="data:image/png;base64,{{ logo_base64 }}" alt="Logo">
   {% endif %}
   ```

**Supported formats:**
- PNG, JPG, JPEG, GIF, SVG, WEBP

---

## Best Practices

### Before Sending

**Always test first:**
1. ✅ Use test mode
2. ✅ Check images display
3. ✅ Verify unsubscribe link works
4. ✅ Review on mobile and desktop
5. ✅ Check spam folder

### Email Content

**Legal requirements:**
- ✅ Include unsubscribe link
- ✅ Include physical mailing address
- ✅ Use verified sender email
- ✅ Honor opt-outs immediately

**Deliverability tips:**
- Avoid ALL CAPS subject lines
- Don't use excessive exclamation marks!!!
- Test spam score before sending
- Keep images reasonable size
- Include text version (future feature)

### Audience Targeting

**Start small:**
- Test with small segment first
- Monitor open/bounce rates
- Scale up gradually

**Segment your list:**
- Email Only vs Email+SMS
- Active vs Inactive subscribers
- Geographic targeting (future)

---

## Troubleshooting

### "Test email not received"

**Check:**
1. Spam/Junk folder
2. Promotions tab (Gmail)
3. Email address spelling
4. SendGrid activity log
5. Flask server logs

### "Images not showing"

**Development:**
- Verify images exist in `static/images/`
- Check ImageHandler is processing correctly
- Look for errors in Flask logs

**Production:**
- Verify images uploaded to Railway
- Check image URLs are accessible
- Test: `https://your-app.railway.app/static/images/logo.png`

### "Campaign won't send"

**Possible causes:**
1. No subscribers in selected audience
2. SendGrid API key invalid/expired
3. Sender email not verified
4. Network/API errors

**Check:**
- Campaign status (must be "draft")
- Subscriber count > 0
- Flask server logs for errors
- SendGrid dashboard for API errors

### "Unsubscribe link not working"

**Verify:**
- Link format: `/unsubscribe?email=...&token=...`
- Token matches customer email
- Unsubscribe route is working
- Database updates correctly

---

## Advanced Features (Future)

### QR Code Integration
- Unique QR codes per customer
- Track redemptions
- Prevent multi-use

### A/B Testing
- Test subject lines
- Test content variations
- Automatic winner selection

### Analytics
- Open rates
- Click rates
- Redemption rates
- Revenue tracking

### Scheduling
- Schedule campaigns for future send
- Time zone optimization
- Drip campaigns

---

## Quick Reference

### Campaign Lifecycle

```
Create → Draft → Preview → Test Send → Live Send → Sent
  ↓        ↓        ↓          ↓           ↓          ↓
 Edit    Edit    Edit       Edit        (No        (Cannot
                                        Edit)       Edit)
```

### Keyboard Shortcuts

None currently - use mouse/trackpad

### API Endpoints

For developers:

```
GET    /campaigns                    - List campaigns
GET    /campaign/new                 - Create form
POST   /campaign/new                 - Save campaign
GET    /campaign/edit/<id>           - Edit form
POST   /campaign/edit/<id>           - Update campaign
GET    /campaign/preview/<id>        - Preview HTML
GET    /campaign/send-confirm/<id>   - Send confirmation
POST   /campaign/send/<id>           - Execute send
POST   /campaign/delete/<id>         - Delete campaign
```

---

## Support

**Issues or Questions?**
- Check Flask server logs
- Review SendGrid activity
- Verify environment variables
- Test with simple template first

**Feature Requests:**
- Document in GitHub issues
- Discuss with development team
- Consider contributing!

---

## Changelog

**December 2024:**
- ✅ Campaign CRUD operations
- ✅ Template selection system
- ✅ Send confirmation workflow
- ✅ Test mode functionality
- ✅ Audience selection
- ✅ Image handling (dev/prod)
- ✅ Safety confirmations

**Future:**
- QR code generation
- Analytics dashboard
- A/B testing
- Campaign scheduling
