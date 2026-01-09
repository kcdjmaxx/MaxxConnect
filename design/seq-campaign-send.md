---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# Sequence: Campaign Send
**Source Spec:** phase-2-campaign-management.md

## Participants
- Admin: Business user sending campaign
- SendConfirmForm: campaign_send_confirm.html template
- FlaskRoute: campaign_send_confirm() and campaign_send() in app.py
- Config: Environment configuration (FLASK_ENV detection)
- ImageHandler: Base64 image conversion (development only)
- Customer: SQLAlchemy model for audience
- EmailService: send_email() function
- Campaign: SQLAlchemy model
- Database: SQLite/PostgreSQL persistence

## Sequence
```
     Admin          SendConfirmForm         FlaskRoute            Config           ImageHandler          Customer           EmailService          Campaign            Database
       |                  |                    |                    |                    |                    |                    |                    |                    |
       | click Send       |                    |                    |                    |                    |                    |                    |                    |
       |----------------->|                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  | GET /campaign/send-confirm/<id>         |                    |                    |                    |                    |                    |
       |                  |------------------->|                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | query Campaign     |                    |                    |                    |                    |                    |
       |                  |                    |------------------------------------------------------------------------------------------------------------>               |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |<------------------------------------------------------------------------------------------------------------|               |
       |                  |                    | campaign           |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | query audience counts                   |                    |                    |                    |                    |
       |                  |                    |------------------------------------------->                   |                    |                    |                    |
       |                  |                    |                    |                    |<-------------------|                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |                    |                    |
       | render confirm page with audience options                  |                    |                    |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       | select audience + test mode           |                    |                    |                    |                    |                    |                    |
       |----------------->|                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       | confirm send     |                    |                    |                    |                    |                    |                    |                    |
       |----------------->|                    |                    |                    |                    |                    |                    |                    |
       |                  | POST /campaign/send/<id>                |                    |                    |                    |                    |                    |
       |                  |------------------->|                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | DEBUG: log template name               |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | is_development()   |                    |                    |                    |                    |                    |
       |                  |                    |------------------->|                    |                    |                    |                    |                    |
       |                  |                    |<-------------------|                    |                    |                    |                    |                    |
       |                  |                    | true/false         |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | DEBUG: log environment mode             |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | [IF DEVELOPMENT]   |                    |                    |                    |                    |                    |
       |                  |                    | get_image_url(logo)|                    |                    |                    |                    |                    |
       |                  |                    |----------------------------------------->                    |                    |                    |                    |
       |                  |                    |<-----------------------------------------                    |                    |                    |                    |
       |                  |                    | logo_base64, hero_image_base64          |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | [IF PRODUCTION]    |                    |                    |                    |                    |                    |
       |                  |                    | url_for('static', _external=True)       |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |                    | logo_url, hero_image_url                |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | DEBUG: log image strategy used          |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | [TEST MODE]        |                    |                    |                    |                    |                    |
       |                  |                    | render_template(template_name, **vars)  |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | DEBUG: log render success + HTML length |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | send_email(test_email)                  |                    |                    |                    |                    |
       |                  |                    |------------------------------------------------------------------------------------>                    |                    |
       |                  |                    |                    |                    |                    |                    | SendGrid API       |                    |
       |                  |                    |                    |                    |                    |                    |----+               |                    |
       |                  |                    |                    |                    |                    |                    |<---+               |                    |
       |                  |                    |<------------------------------------------------------------------------------------                    |                    |
       |                  |                    | DEBUG: log send result                  |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |                    |                    |
       | flash "test sent"|                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | [EXCEPTION]        |                    |                    |                    |                    |                    |
       |                  |                    | print full traceback                    |                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |                    |                    |
       | flash error msg  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | [LIVE MODE]        |                    |                    |                    |                    |                    |
       |                  |                    | query subscribers by segment            |                    |                    |                    |                    |
       |                  |                    |------------------------------------------->                   |                    |                    |                    |
       |                  |                    |                    |                    |<-------------------|                    |                    |                    |
       |                  |                    | subscribers[]      |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |======= LOOP for each subscriber ============================================     |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | is_development()   |                    |                    |                    |                    |                    |
       |                  |                    |------------------->|                    |                    |                    |                    |                    |
       |                  |                    |<-------------------|                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | render_template(template_name, customer)|                    |                    |                    |                    |
       |                  |                    |----+               |                    |                    |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | send_email(customer.email)              |                    |                    |                    |                    |
       |                  |                    |------------------------------------------------------------------------------------>                    |                    |
       |                  |                    |                    |                    |                    |                    | SendGrid API       |                    |
       |                  |                    |                    |                    |                    |                    |----+               |                    |
       |                  |                    |                    |                    |                    |                    |<---+               |                    |
       |                  |                    |<------------------------------------------------------------------------------------                    |                    |
       |                  |                    | track sent/failed  |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    |======= END LOOP ========================================================================               |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |                    | update campaign status='sent'           |                    |                    |                    |                    |
       |                  |                    |------------------------------------------------------------------------------------------------------------>               |
       |                  |                    |                    |                    |                    |                    |                    | UPDATE             |
       |                  |                    |                    |                    |                    |                    |                    |------------------->|
       |                  |                    |                    |                    |                    |                    |                    |<-------------------|
       |                  |                    |<------------------------------------------------------------------------------------------------------------|               |
       |                  |                    |                    |                    |                    |                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |                    |                    |
       | flash "X sent, Y failed"              |                    |                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |                    |                    |
```

## Audience Selection Options
- **all**: All email subscribers (subscribed=True)
- **email_only**: Subscribed to email only (subscribed=True, sms_subscribed=False)
- **sms_only**: Subscribed to SMS only (sms_subscribed=True, subscribed=False)
- **both**: Subscribed to both (subscribed=True, sms_subscribed=True)

## Environment-Aware Image Handling
- **Development (FLASK_ENV != 'production'):**
  - Template variables: `logo_base64`, `hero_image_base64`
  - Images converted via `ImageHandler.get_image_url()`
  - Strips `data:image/png;base64,` prefix for template use
- **Production (FLASK_ENV == 'production'):**
  - Template variables: `logo_url`, `hero_image_url`
  - Images served via `url_for('static', filename=..., _external=True)`
  - Uses full Railway.app URLs

## Debug Logging (campaign_send route)
- Template name being used
- Environment mode (Config.ENV value)
- Unsubscribe link generation
- Image strategy (base64 vs external URL)
- Image URLs generated (in production mode)
- Template rendering success with HTML length
- First 200 chars of rendered HTML
- Email send results
- Full traceback on any exception

## Notes
- Two-step process: Confirm page -> Send execution
- Test mode: Sends to single test email address only
- Live mode: Sends to all customers matching audience criteria
- Fresh template rendering: Uses `render_template()` instead of `render_template_string()`
- Personalization: customer_name, unsubscribe_link, logo/hero images
- Campaign status: draft -> sent
- Currently synchronous (Phase 2 will add async queue)
