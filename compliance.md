---
tags:
  - project/maxxconnect
  - subject/twilio
  - type/documentation
  - status/active
---

# A2P 10DLC Compliance Fix Guide

**Rejection Reason:** "The campaign submission has been reviewed and rejected due to issues verifying the Call to Action (CTA) provided for the campaign."

**What This Means:** TCR reviewers couldn't verify your opt-in process. They need to see WHERE and HOW customers sign up to receive SMS messages.

---

## 1. Fixed Sample Messages

Copy these exactly into your Twilio campaign. All include business name and opt-out language.

### Message Sample #1
```
Fric & Frac: This week only - buy one burger, get one free! Show this text to redeem. Reply STOP to opt out.
```

### Message Sample #2
```
Fric & Frac: It's 2-for-1 Burger Night every Monday! Join us tonight. Reply STOP to unsubscribe.
```

### Message Sample #3
```
Fric & Frac: Here's your exclusive QR code for 10% off your next meal. Show at checkout. Reply STOP to opt out.
```

### Message Sample #4
```
Fric & Frac: We miss you! Come back for a free appetizer with any entree this week. Reply STOP to unsubscribe.
```

### Message Sample #5
```
Fric & Frac: You're one of our most loyal customers! Enjoy 15% off your next meal of $35+. Reply STOP to opt out.
```

---

## 2. Opt-In Description (Message Flow)

Copy this into the "How do end-users consent to receive messages?" field:

```
Customers provide consent to receive promotional SMS messages from Fric & Frac through these methods:

1. WEBSITE OPT-IN: Customers visit https://fricandfrac.net/sms-signup and enter their phone number. Before submitting, they must check a box confirming: "I agree to receive promotional SMS messages from Fric & Frac. Message frequency varies. Msg & data rates may apply. Reply STOP to opt out." The checkbox is unchecked by default and submission is blocked until checked.

2. IN-STORE SIGN-UP: Customers voluntarily provide their phone number on a physical sign-up card at our restaurant. The card clearly displays: "By providing your phone number, you agree to receive promotional text messages from Fric & Frac. Message frequency varies. Message and data rates may apply. Reply STOP to unsubscribe."

All opt-ins are recorded with timestamp and consent method. Customers can opt out at any time by replying STOP to any message. Our privacy policy is available at https://fricandfrac.net/privacy/
```

---

## 3. Campaign Description

Replace the current description with:

```
Fric & Frac restaurant sends promotional SMS messages to customers who have opted in. Messages include weekly specials, exclusive discounts, loyalty rewards, and QR codes for deal redemption. Customers opt-in via our website signup form or in-store sign-up cards. All messages include opt-out instructions.
```

---

## 4. Website Requirements

You MUST add an SMS sign-up page to fricandfrac.net that TCR reviewers can verify.

### Ready-to-Use Signup Page

A complete signup page has been created: `sms-signup.html`

**Before deploying, update ONE line in the file:**

Open `sms-signup.html` and find this line near the bottom:
```javascript
const MAXXCONNECT_API_URL = 'https://YOUR-APP.railway.app/api/public/signup';
```

Replace `YOUR-APP` with your actual Railway app name (e.g., `maxxconnect-production`).

### Deployment Steps

1. Open `sms-signup.html` in a text editor
2. Update the `MAXXCONNECT_API_URL` to your Railway URL
3. Upload the file to the same location as your privacy policy
4. Verify it's accessible at `https://fricandfrac.net/sms-signup` (or similar)

### What the page includes (all compliant):
- Checkbox that is UNCHECKED by default
- Checkbox is REQUIRED (form won't submit without it)
- Links to your privacy policy
- Mentions: message frequency, data rates, STOP to opt out
- Full TCPA disclaimer in footer
- Posts directly to MaxxConnect API
- Mobile-friendly design
- Phone number auto-formatting

### API Endpoint Added

A new endpoint was added to MaxxConnect:
- **URL:** `/api/public/signup`
- **Method:** POST (with CORS support)
- **Tags contacts as:** `website-signup` for tracking

---

## 5. In-Store Sign-Up Card Template

If you collect numbers in-store, print cards with this text:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        FRIC & FRAC TEXT CLUB
     Get Exclusive Deals & Rewards!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: _________________________________

Phone: ________________________________

Email (optional): _____________________

☐ I agree to receive promotional text
  messages from Fric & Frac. Message
  frequency varies. Msg & data rates
  may apply. Reply STOP to opt out.

Privacy Policy: fricandfrac.net/privacy

Date: _____________  Staff: ___________
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Take a photo of this card and host it at:**
`https://fricandfrac.net/images/sms-signup-card.jpg`

Then reference it in your opt-in description so reviewers can verify it exists.

---

## 6. Privacy Policy Checklist

Verify https://fricandfrac.net/privacy/ includes:

- [ ] Business name: "Fric & Frac"
- [ ] What data you collect: phone numbers, email addresses
- [ ] Purpose: promotional SMS messages, deals, rewards
- [ ] Message frequency: "Message frequency varies"
- [ ] Data rates: "Message and data rates may apply"
- [ ] Opt-out method: "Reply STOP to any message to unsubscribe"
- [ ] Contact information for questions
- [ ] Data sharing policy (who you share data with, if anyone)

---

## 7. Submission Checklist

Before resubmitting your campaign:

- [ ] SMS sign-up page live at fricandfrac.net/sms-signup
- [ ] Sign-up form has required checkbox (unchecked by default)
- [ ] Privacy policy updated and accessible
- [ ] All 5 sample messages include "Fric & Frac" business name
- [ ] All 5 sample messages include opt-out language
- [ ] Campaign description is detailed (not just "sends deals")
- [ ] Opt-in description matches what's actually on your website
- [ ] "Embedded links" = Yes (since you're sending QR codes/links)

---

## 8. Common Mistakes to Avoid

| Mistake | Why It Fails |
|---------|--------------|
| Pre-checked consent checkbox | Violates TCPA - must be unchecked by default |
| No opt-out in sample messages | Every marketing SMS must include opt-out |
| Generic sample messages without business name | At least one sample must identify sender |
| Opt-in URL that doesn't exist | Reviewers will check - page must be live |
| Opt-in description doesn't match website | Description must match actual implementation |
| Privacy policy behind login/paywall | Must be publicly accessible |

---

## 9. After Approval

Once approved, remember:
- Include opt-out instructions in EVERY message
- Honor STOP replies immediately (MaxxConnect handles this via webhook)
- Keep records of all opt-ins with timestamps
- Don't send to numbers that haven't opted in
- Respect quiet hours (9 AM - 9 PM local time recommended)
