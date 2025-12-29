# Sequence: Campaign Preview
**Source Spec:** phase-2-campaign-management.md

## Participants
- Admin: Business user previewing campaign
- Browser: Web browser rendering HTML
- FlaskRoute: campaign_preview() in app.py
- Campaign: SQLAlchemy model
- Database: SQLite/PostgreSQL persistence

## Sequence
```
     Admin               Browser              FlaskRoute            Campaign            Database
       |                   |                    |                    |                    |
       |  click preview    |                    |                    |                    |
       |------------------>|                    |                    |                    |
       |                   |                    |                    |                    |
       |                   | GET /campaign/preview/<id>              |                    |
       |                   |------------------->|                    |                    |
       |                   |                    |                    |                    |
       |                   |                    | query Campaign     |                    |
       |                   |                    |------------------->|                    |
       |                   |                    |                    | SELECT             |
       |                   |                    |                    |------------------->|
       |                   |                    |                    |<-------------------|
       |                   |                    |                    | campaign           |
       |                   |                    |<-------------------|                    |
       |                   |                    |                    |                    |
       |                   |                    | return html_content|                    |
       |                   |<-------------------|                    |                    |
       |                   |                    |                    |                    |
       |<------------------|                    |                    |                    |
       | display rendered HTML                  |                    |                    |
       |                   |                    |                    |                    |
```

## Notes
- Preview returns raw HTML content stored in campaign
- HTML was rendered at campaign creation time with sample data
- Images already processed (base64 or external URLs)
- Opens in new tab/window via target="_blank"
- Shows personalization placeholders with sample values
