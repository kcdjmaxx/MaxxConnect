# Sequence: Campaign Create
**Source Spec:** phase-2-campaign-management.md

## Participants
- Admin: Business user creating campaign
- CreateForm: campaign_create.html template
- FlaskRoute: campaign_new() in app.py
- ImageHandler: Environment-aware image processor
- Config: Environment configuration
- Campaign: SQLAlchemy model
- Database: SQLite/PostgreSQL persistence

## Sequence
```
     Admin              CreateForm           FlaskRoute          ImageHandler           Config              Campaign            Database
       |                     |                    |                    |                    |                    |                    |
       |  GET /campaign/new  |                    |                    |                    |                    |                    |
       |-------------------->|                    |                    |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |                     | get_available_templates()               |                    |                    |                    |
       |                     |------------------->|                    |                    |                    |                    |
       |                     |                    | scan templates/email/                  |                    |                    |
       |                     |                    |----+               |                    |                    |                    |
       |                     |                    |<---+               |                    |                    |                    |
       |                     |<-------------------|                    |                    |                    |                    |
       |                     | templates, audience counts              |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |<--------------------|                    |                    |                    |                    |                    |
       | render form         |                    |                    |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       | fill form + select template              |                    |                    |                    |                    |
       |-------------------->|                    |                    |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       | submit (save/preview/send)               |                    |                    |                    |                    |
       |-------------------->|                    |                    |                    |                    |                    |
       |                     | POST form data     |                    |                    |                    |                    |
       |                     |------------------->|                    |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |                     |                    | is_development()   |                    |                    |                    |
       |                     |                    |----------------------------------->      |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |                     |                    |<-----------------------------------|     |                    |                    |
       |                     |                    | env_type           |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |                     |                    | get_image_url()    |                    |                    |                    |
       |                     |                    |------------------->|                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |                     |                    |<-------------------|                    |                    |                    |
       |                     |                    | base64 or URL      |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |                     |                    | render_template(template, images)      |                    |                    |
       |                     |                    |----+               |                    |                    |                    |
       |                     |                    |<---+               |                    |                    |                    |
       |                     |                    | html_content       |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
       |                     |                    |                    |                    |  new Campaign()    |                    |
       |                     |                    |------------------------------------------------------------------->               |
       |                     |                    |                    |                    |                    |                    |
       |                     |                    |                    |                    |                    | INSERT             |
       |                     |                    |                    |                    |                    |------------------->|
       |                     |                    |                    |                    |                    |                    |
       |                     |                    |                    |                    |                    |<-------------------|
       |                     |                    |                    |                    |                    | campaign.id        |
       |                     |                    |<-------------------------------------------------------------------|               |
       |                     |                    |                    |                    |                    |                    |
       |                     |<-------------------|                    |                    |                    |                    |
       |<--------------------|                    |                    |                    |                    |                    |
       | redirect based on action (preview/list/send)                  |                    |                    |                    |
       |                     |                    |                    |                    |                    |                    |
```

## Notes
- Campaign created in 'draft' status by default
- Template selection via dropdown (scanned from templates/email/)
- Environment-aware image handling:
  - Development: base64 encoded images
  - Production: external URLs via Railway
- Actions: Save Draft, Preview, or Send
- Test mode available for single-email testing
