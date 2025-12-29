# Configuration Guide

This guide explains how to configure the MaxxConnect application for different environments (development vs production).

## Overview

The application automatically detects the environment and configures itself accordingly:

- **Development**: Simple setup, base64 images, SQLite database
- **Production**: Optimized for Railway deployment, external URLs, PostgreSQL

## Environment Detection

The environment is determined by the `FLASK_ENV` variable in your `.env` file:

```bash
FLASK_ENV=development  # For local testing
FLASK_ENV=production   # For Railway deployment
```

## Configuration Files

### 1. `.env` (Local Development)

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

**Development Configuration:**
```bash
# Environment
FLASK_ENV=development

# Email Service
SENDGRID_API_KEY=your_api_key_here
SENDER_EMAIL=your-email@domain.com
SENDER_NAME=Your Business

# URLs (localhost)
BASE_URL=http://localhost:5001
STATIC_URL=http://localhost:5001/static

# Database (SQLite)
DATABASE_URL=sqlite:///database.db

# Images (base64 - automatic, no hosting needed)
IMAGE_STRATEGY=base64

# Business Info
BUSINESS_ADDRESS=123 Main St, City, State 12345

# Security
SECRET_KEY=dev-secret-key-change-in-production
ENCRYPTION_KEY=your_fernet_key_here
```

### 2. Railway Environment Variables (Production)

Set these in Railway dashboard:

```bash
# Environment
FLASK_ENV=production

# Email Service
SENDGRID_API_KEY=your_api_key_here
SENDER_EMAIL=your-email@domain.com
SENDER_NAME=Your Business

# URLs (Railway provides your domain)
BASE_URL=https://your-app.railway.app
STATIC_URL=https://your-app.railway.app/static

# Database (Railway provides this automatically)
DATABASE_URL=postgresql://...

# Images (external URLs - better for production)
IMAGE_STRATEGY=external

# Business Info
BUSINESS_ADDRESS=123 Main St, City, State 12345

# Security
SECRET_KEY=<generate-secure-random-key>
ENCRYPTION_KEY=<your-fernet-key>

# SMS (if using)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Image Handling Strategies

The application handles images differently based on environment:

### Development: Base64 Strategy (Default)

**How it works:**
- Images are converted to base64 data URIs
- Embedded directly in email HTML
- No external hosting needed

**Usage:**
```html
<!-- In your email HTML -->
<img src="logo.png">
<!-- or -->
<img src="static/images/logo.png">

<!-- Automatically converts to base64 in development -->
```

**Pros:**
- Simple setup
- No image hosting required
- Images always display

**Cons:**
- Larger email size
- Some email clients may block base64 images

### Production: External URL Strategy

**How it works:**
- Images are hosted on your server
- Referenced via absolute URLs
- Industry standard approach

**Usage:**
```html
<!-- In your email HTML -->
<img src="/static/images/logo.png">

<!-- Automatically converts to: -->
<!-- <img src="https://your-app.railway.app/static/images/logo.png"> -->
```

**Pros:**
- Smaller email size
- Better deliverability
- Standard email practice

**Cons:**
- Requires image hosting setup
- Images won't show if recipient blocks external images

## Setting Up Images

### For Development

1. Create images folder:
```bash
mkdir -p static/images
```

2. Add your images:
```bash
cp logo.png static/images/
```

3. Reference in HTML:
```html
<img src="static/images/logo.png" alt="Logo">
```

The system automatically converts to base64.

### For Production (Railway)

1. Add images to your repository:
```bash
git add static/images/logo.png
git commit -m "Add email images"
git push
```

2. Railway deploys and serves them automatically

3. Reference in HTML (same as development):
```html
<img src="static/images/logo.png" alt="Logo">
```

The system automatically converts to external URLs.

## Configuration API

The `backend/config.py` module provides a centralized configuration:

```python
from backend.config import Config

# Check environment
if Config.is_production():
    print("Running in production")

if Config.is_development():
    print("Running in development")

# Get image strategy
strategy = Config.get_image_strategy()  # 'base64' or 'external'

# Get full URLs
url = Config.get_full_url('/static/images/logo.png')
# Development: http://localhost:5001/static/images/logo.png
# Production: https://your-app.railway.app/static/images/logo.png

# Get static file URL
image_url = Config.get_static_url('images/logo.png')
```

## Database Configuration

### Development: SQLite

Automatic, no setup needed:

```bash
DATABASE_URL=sqlite:///database.db
```

File is created automatically in your project directory.

### Production: PostgreSQL

Railway provides this automatically. The `DATABASE_URL` variable is set by Railway.

To initialize:
```bash
# Railway runs this automatically
python -c "from backend.database import init_db; init_db()"
```

## Testing Your Configuration

### Test Development Setup

```bash
# Start the app
python app.py

# Visit http://localhost:5001
# Try importing contacts
# Send a test email with images
```

### Test Production Setup

```bash
# Set environment to production temporarily
export FLASK_ENV=production

# Test that external URLs are generated correctly
python -c "from backend.config import Config; print(Config.BASE_URL)"

# Should output your production URL
```

## Switching Between Environments

### Quick Switch for Testing

```bash
# Test in production mode locally
FLASK_ENV=production python app.py

# Back to development
FLASK_ENV=development python app.py
```

### Permanent Switch

Edit `.env` file:
```bash
# Change this line
FLASK_ENV=production  # or development
```

## Common Configuration Scenarios

### Scenario 1: Local Development with Test Images

```bash
FLASK_ENV=development
IMAGE_STRATEGY=base64
BASE_URL=http://localhost:5001
```

✓ Simple, images work immediately

### Scenario 2: Production on Railway

```bash
FLASK_ENV=production
IMAGE_STRATEGY=external
BASE_URL=https://your-app.railway.app
```

✓ Optimized, smaller emails, better deliverability

### Scenario 3: Local Testing with Production-like Setup

```bash
FLASK_ENV=development
IMAGE_STRATEGY=external
BASE_URL=http://localhost:5001
```

✓ Test external URL handling locally

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | Yes | `development` | Environment mode |
| `BASE_URL` | Yes | `http://localhost:5001` | Application base URL |
| `STATIC_URL` | No | `{BASE_URL}/static` | Static files URL |
| `DATABASE_URL` | No | `sqlite:///database.db` | Database connection |
| `IMAGE_STRATEGY` | No | Auto-detected | `base64` or `external` |
| `SENDGRID_API_KEY` | Yes | - | SendGrid API key |
| `SENDER_EMAIL` | Yes | - | Verified sender email |
| `SENDER_NAME` | Yes | - | Sender display name |
| `BUSINESS_ADDRESS` | Yes | - | Physical address (legal) |
| `SECRET_KEY` | Yes | Dev default | Flask secret key |
| `ENCRYPTION_KEY` | Yes | - | Fernet encryption key |

## Troubleshooting

### Images Not Showing in Development

**Problem:** Images don't display in test emails

**Solution:**
1. Check `IMAGE_STRATEGY=base64` in `.env`
2. Verify images exist in `static/images/`
3. Check file paths in HTML (use relative paths)

### Images Not Showing in Production

**Problem:** Images don't load in production emails

**Solution:**
1. Verify `IMAGE_STRATEGY=external`
2. Check images are committed to git
3. Verify `BASE_URL` matches your Railway domain
4. Test URL directly: `https://your-app.railway.app/static/images/logo.png`

### Database Connection Failed

**Problem:** Can't connect to database

**Solution:**
- **Development:** Check `database.db` file exists and has write permissions
- **Production:** Verify Railway `DATABASE_URL` variable is set

### Wrong Environment Detected

**Problem:** App thinks it's in production when developing locally

**Solution:**
1. Check `.env` file has `FLASK_ENV=development`
2. Restart the application
3. Verify with: `python -c "from backend.config import Config; print(Config.ENV)"`

## Best Practices

1. **Never commit `.env`** - Use `.env.example` as template
2. **Use strong secrets in production** - Generate random keys
3. **Test both environments** - Ensure features work in dev and prod
4. **Keep images small** - Optimize for email (< 100KB per image)
5. **Use descriptive image names** - `logo.png`, not `img1.png`
6. **Version control images** - Commit to git for production deployment

## Security Notes

### Secret Key Generation

Generate a secure secret key for production:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Encryption Key Generation

Generate Fernet encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Railway Configuration

Set secrets in Railway dashboard, not in code:
1. Go to your project settings
2. Click "Variables"
3. Add sensitive values
4. Railway injects them as environment variables

## Next Steps

- Review `.env.example` for all available options
- Set up development environment first
- Test thoroughly before deploying to production
- Monitor Railway logs for configuration issues
