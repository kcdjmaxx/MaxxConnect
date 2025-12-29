# Config
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- ENV: Environment name ('development' or 'production')
- DEBUG: Debug mode flag
- DATABASE_URL: Database connection string
- BASE_URL: Application base URL
- STATIC_URL: Static files base URL
- SENDGRID_API_KEY: SendGrid API credentials
- SENDER_EMAIL: From email address
- SENDER_NAME: Business name for email sender
- BUSINESS_ADDRESS: Physical address for CAN-SPAM compliance
- TWILIO_* credentials: SMS service credentials
- ENCRYPTION_KEY: Fernet encryption key for PII
- IMAGE_STRATEGY: Image handling strategy ('base64' or 'external')
- SECRET_KEY: Flask session secret
- UPLOAD_FOLDER: CSV upload directory
- MAX_CONTENT_LENGTH: Max upload size (16MB)

### Does
- is_production(): Check if running in production
- is_development(): Check if running in development
- get_image_strategy(): Return current image handling strategy
- get_full_url(path): Convert relative path to full URL
- get_static_url(filename): Get full URL for static file

## Collaborators
- ImageHandler: Uses Config to determine image strategy
- Campaign routes: Use Config for environment-aware rendering

## Sequences
- seq-campaign-create.md: Environment-aware template rendering
- seq-campaign-send.md: Environment-aware email generation

## Implementation
- **Source:** `backend/config.py`
- **Classes:** Config, DevelopmentConfig, ProductionConfig
