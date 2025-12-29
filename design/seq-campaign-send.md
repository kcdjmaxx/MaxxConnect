# Sequence: Campaign Send
**Source Spec:** phase-2-campaign-management.md

## Participants
- Admin: Business user sending campaign
- SendConfirmForm: campaign_send_confirm.html template
- FlaskRoute: campaign_send_confirm() and campaign_send() in app.py
- Customer: SQLAlchemy model for audience
- EmailService: send_email() function
- Campaign: SQLAlchemy model
- Database: SQLite/PostgreSQL persistence

## Sequence
```
     Admin          SendConfirmForm         FlaskRoute            Customer           EmailService          Campaign            Database
       |                  |                    |                    |                    |                    |                    |
       | click Send       |                    |                    |                    |                    |                    |
       |----------------->|                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  | GET /campaign/send-confirm/<id>         |                    |                    |                    |
       |                  |------------------->|                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | query Campaign     |                    |                    |                    |
       |                  |                    |----------------------------------------------------------------->               |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    |<-----------------------------------------------------------------|               |
       |                  |                    | campaign           |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | query audience counts                   |                    |                    |
       |                  |                    |------------------->|                    |                    |                    |
       |                  |                    |                    |---------------------------------------------------->          |
       |                  |                    |                    |<----------------------------------------------------|         |
       |                  |                    |<-------------------|                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |
       | render confirm page with audience options                  |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       | select audience + test mode           |                    |                    |                    |                    |
       |----------------->|                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       | confirm send     |                    |                    |                    |                    |                    |
       |----------------->|                    |                    |                    |                    |                    |
       |                  | POST /campaign/send/<id>                |                    |                    |                    |
       |                  |------------------->|                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | [TEST MODE]        |                    |                    |                    |
       |                  |                    | render_template_string(html, test_customer)                  |                    |
       |                  |                    |----+               |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | send_email(test_email)                  |                    |                    |
       |                  |                    |----------------------------------------->                    |                    |
       |                  |                    |                    |                    | SendGrid API       |                    |
       |                  |                    |                    |                    |----+               |                    |
       |                  |                    |                    |                    |<---+               |                    |
       |                  |                    |<-----------------------------------------                    |                    |
       |                  |                    | result             |                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |
       | flash "test sent"|                    |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | [LIVE MODE]        |                    |                    |                    |
       |                  |                    | query subscribers by segment            |                    |                    |
       |                  |                    |------------------->|                    |                    |                    |
       |                  |                    |                    |---------------------------------------------------->          |
       |                  |                    |                    |<----------------------------------------------------|         |
       |                  |                    |<-------------------|                    |                    |                    |
       |                  |                    | subscribers[]      |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    |======= LOOP for each subscriber ============================|                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | render_template_string(html, customer)  |                    |                    |
       |                  |                    |----+               |                    |                    |                    |
       |                  |                    |<---+               |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | send_email(customer.email)              |                    |                    |
       |                  |                    |----------------------------------------->                    |                    |
       |                  |                    |                    |                    | SendGrid API       |                    |
       |                  |                    |                    |                    |----+               |                    |
       |                  |                    |                    |                    |<---+               |                    |
       |                  |                    |<-----------------------------------------                    |                    |
       |                  |                    | track sent/failed  |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    |======= END LOOP ================================================                  |
       |                  |                    |                    |                    |                    |                    |
       |                  |                    | update campaign status='sent'           |                    |                    |
       |                  |                    |----------------------------------------------------------------->               |
       |                  |                    |                    |                    |                    | UPDATE             |
       |                  |                    |                    |                    |                    |------------------->|
       |                  |                    |                    |                    |                    |<-------------------|
       |                  |                    |<-----------------------------------------------------------------|               |
       |                  |                    |                    |                    |                    |                    |
       |                  |<-------------------|                    |                    |                    |                    |
       |<-----------------|                    |                    |                    |                    |                    |
       | flash "X sent, Y failed"              |                    |                    |                    |                    |
       |                  |                    |                    |                    |                    |                    |
```

## Audience Selection Options
- **all**: All email subscribers (subscribed=True)
- **email_only**: Subscribed to email only (subscribed=True, sms_subscribed=False)
- **sms_only**: Subscribed to SMS only (sms_subscribed=True, subscribed=False)
- **both**: Subscribed to both (subscribed=True, sms_subscribed=True)

## Notes
- Two-step process: Confirm page -> Send execution
- Test mode: Sends to single test email address only
- Live mode: Sends to all customers matching audience criteria
- Personalization: customer_name, unsubscribe_link
- Campaign status: draft -> sent
- Currently synchronous (Phase 2 will add async queue)
