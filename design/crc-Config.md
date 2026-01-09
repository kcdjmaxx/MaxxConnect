---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/software-architecture
  - type/design-specification
  - status/active
  - tool/flask
---

# Config
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- ENV: Environment name from FLASK_ENV ('development' or 'production', defaults to 'development')
- DEBUG: Debug mode flag (True in development, False in production)
- DATABASE_URL: Database connection string (SQLite dev, PostgreSQL prod)
- BASE_URL: Application base URL (localhost:5001 dev, Railway URL prod)
- STATIC_URL: Static files base URL
- SENDGRID_API_KEY: SendGrid API credentials
- SENDER_EMAIL: From email address
- SENDER_NAME: Business name for email sender (falls back to BUSINESS_NAME env var)
- BUSINESS_ADDRESS: Physical address for CAN-SPAM compliance
- TWILIO_* credentials: SMS service credentials
- ENCRYPTION_KEY: Fernet encryption key for PII
- IMAGE_STRATEGY: Image handling strategy ('base64' in dev, 'external' in prod)
- SECRET_KEY: Flask session secret
- UPLOAD_FOLDER: CSV upload directory
- MAX_CONTENT_LENGTH: Max upload size (16MB)

### Does
- is_production(): Check if FLASK_ENV == 'production'
- is_development(): Check if FLASK_ENV == 'development'
- get_image_strategy(): Return current image handling strategy based on environment
- get_full_url(path): Convert relative path to full URL with BASE_URL
- get_static_url(filename): Get full URL for static file

## Collaborators
- ImageHandler: Uses Config to determine image strategy (base64 vs external URLs)
- CampaignManager (app.py): Uses Config.is_development() for template variable selection
- EmailService: Uses Config for sender name and base URL

## Sequences
- seq-campaign-create.md: Environment-aware template rendering
- seq-campaign-send.md: Environment-aware email generation with debug logging

## Implementation
- **Source:** `backend/config.py`
- **Classes:** Config (base), DevelopmentConfig, ProductionConfig
- **Environment Detection:** FLASK_ENV environment variable (set to 'production' on Railway)
- **Fallback Chain:** SENDER_NAME <- BUSINESS_NAME <- 'Your Business'
