---
tags:
  - project/mailchimp-clone
  - subject/web-development
  - subject/api-integration
  - subject/deployment
  - tool/flask
  - tool/railway
  - status/active
  - type/implementation-guide
---

# Phase 1: Foundation - Step by Step Guide

## Overview
Phase 1 establishes the core foundation for sending emails with proper deliverability, legal compliance, and testing capabilities. **Single Flask application** - easy to run and manage.

## Prerequisites

1. **Choose Email Service Provider**
   - Option A: SendGrid (12,000 free emails/month)
   - Option B: Amazon SES (62,000 free emails/month first year)
   - Option C: Mailgun (5,000 free emails/month)

   **Recommendation**: Start with SendGrid for simplicity

2. **Get API Credentials**
   - Sign up for chosen provider
   - Generate API key
   - Verify sender email/domain

---

## Step 1: Project Setup

### 1.1 Create Project Structure
```
MaxxConnect/
├── app.py                     # Main Flask application
├── backend/
│   ├── __init__.py
│   ├── database.py            # Database connection
│   ├── models.py              # SQLAlchemy models
│   ├── email_service.py       # Email sending logic
│   └── csv_importer.py        # CSV import with deduplication
├── templates/
│   ├── base.html              # Base layout template
│   ├── dashboard.html         # Dashboard page
│   ├── contacts.html          # View contacts page
│   ├── import.html            # Import CSV page
│   ├── preview.html           # Email preview & test page
│   ├── unsubscribe.html       # Unsubscribe confirmation page
│   └── email/
│       └── base_email.html    # Email template (for campaigns)
├── static/
│   └── style.css              # Simple CSS styling
├── uploads/                   # Temporary CSV uploads (created automatically)
├── .env                       # Environment variables (DO NOT COMMIT)
├── .gitignore
├── requirements.txt
└── database.db               # SQLite database (created automatically)
```

### 1.2 Install Python Dependencies
Create `requirements.txt`:
```
flask==3.0.0
sqlalchemy==2.0.23
python-dotenv==1.0.0
sendgrid==6.11.0
# OR for SES: boto3==1.34.0
pandas==2.1.4
jinja2==3.1.2
qrcode==7.4.2
pillow==10.1.0
werkzeug==3.0.1
```

Install:
```bash
python3 -m venv venv
source venv/bin/activate  # On Raspberry Pi/Linux/Mac
# On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1.3 Environment Variables
Create `.env` file:
```
# Email Service
SENDGRID_API_KEY=your_api_key_here
SENDER_EMAIL=your-verified-email@domain.com
SENDER_NAME=Your Business Name

# Business Info (Legal requirement)
BUSINESS_ADDRESS=123 Main St, City, State 12345

# App Config
DATABASE_URL=sqlite:///database.db
SECRET_KEY=generate-a-random-secret-key-here
BASE_URL=http://localhost:5000
```

### 1.4 Create .gitignore
```
.env
*.db
__pycache__/
venv/
.DS_Store
*.pyc
uploads/
```

---

## Step 2: Database Models

### 2.1 Create `backend/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
```

### 2.2 Create `backend/models.py`
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base
import hashlib

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    subscribed = Column(Boolean, default=True)
    opted_in_date = Column(DateTime, default=func.now())
    unsubscribed_date = Column(DateTime, nullable=True)
    segments = Column(Text)  # Comma-separated tags
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Customer {self.email}>"

    def get_unsubscribe_token(self):
        """Generate secure unsubscribe token"""
        data = f"{self.id}:{self.email}".encode()
        return hashlib.sha256(data).hexdigest()

class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    status = Column(String(50), default='draft')  # draft, sent, sending
    sent_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Campaign {self.name}>"
```

---

## Step 3: CSV Import with Deduplication

### 3.1 Create `backend/csv_importer.py`
```python
import pandas as pd
from backend.database import SessionLocal
from backend.models import Customer
import re
from datetime import datetime

def is_valid_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def import_csv(file_path, segment_tag=None):
    """
    Import contacts from CSV with deduplication

    Supports two CSV formats:
    1. Simple format: email,name,phone
    2. Square export format: Email Address,First Name,Last Name,Phone Number,...
    """
    db = SessionLocal()

    try:
        # Read CSV
        df = pd.read_csv(file_path)

        # Map Square column names to our expected names
        column_mapping = {
            'Email Address': 'email',
            'Phone Number': 'phone',
            'First Name': 'first_name',
            'Last Name': 'last_name'
        }

        # Rename columns if they match Square format
        df.rename(columns=column_mapping, inplace=True)

        # Validate that we have email column
        if 'email' not in df.columns:
            raise ValueError("CSV must have 'email' or 'Email Address' column")

        # Combine first_name and last_name into name if they exist
        if 'first_name' in df.columns or 'last_name' in df.columns:
            first = df.get('first_name', pd.Series([''] * len(df))).fillna('')
            last = df.get('last_name', pd.Series([''] * len(df))).fillna('')
            df['name'] = (first.astype(str) + ' ' + last.astype(str)).str.strip()

        # Drop rows with missing emails
        df = df.dropna(subset=['email'])

        # Normalize emails (lowercase, strip whitespace)
        df['email'] = df['email'].astype(str).str.strip().str.lower()

        # Remove invalid emails
        df = df[df['email'].apply(is_valid_email)]

        # Remove duplicates within CSV
        df = df.drop_duplicates(subset=['email'])

        stats = {
            'total_rows': len(df),
            'added': 0,
            'updated': 0,
            'invalid': 0
        }

        for _, row in df.iterrows():
            email = row['email']
            name = row.get('name', '')

            # Check if customer exists
            existing = db.query(Customer).filter_by(email=email).first()

            if existing:
                # Update name if provided and not already set
                if name and not existing.name:
                    existing.name = name

                # Add segment tag if provided
                if segment_tag:
                    tags = set(existing.segments.split(',')) if existing.segments else set()
                    tags.add(segment_tag)
                    existing.segments = ','.join(filter(None, tags))

                existing.updated_at = datetime.now()
                stats['updated'] += 1
            else:
                # Create new customer
                customer = Customer(
                    email=email,
                    name=name,
                    segments=segment_tag if segment_tag else '',
                    subscribed=True
                )
                db.add(customer)
                stats['added'] += 1

        db.commit()
        return stats

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
```

---

## Step 4: Email Service

### 4.1 Create `backend/email_service.py`
```python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Template
from backend.models import Customer
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_NAME = os.getenv('SENDER_NAME')
BUSINESS_ADDRESS = os.getenv('BUSINESS_ADDRESS')
BASE_URL = os.getenv('BASE_URL')

def send_email(to_email, to_name, subject, html_content):
    """Send single email via SendGrid"""

    message = Mail(
        from_email=(SENDER_EMAIL, SENDER_NAME),
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return {
            'success': True,
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def render_email_template(template_path, customer, custom_body):
    """Render email with template and customer data"""

    # Read template
    with open(template_path, 'r') as f:
        template_content = f.read()

    # Generate unsubscribe link
    token = customer.get_unsubscribe_token()
    unsubscribe_link = f"{BASE_URL}/unsubscribe?token={token}&email={customer.email}"

    # Render template
    template = Template(template_content)
    rendered = template.render(
        customer_name=customer.name or 'Valued Customer',
        email_body=custom_body,
        business_name=SENDER_NAME,
        business_address=BUSINESS_ADDRESS,
        unsubscribe_link=unsubscribe_link
    )

    return rendered

def send_test_email(test_email, subject, custom_body):
    """Send test email to yourself"""

    # Create temporary customer object for rendering
    temp_customer = Customer(
        id=0,
        email=test_email,
        name="Test User"
    )

    # Render email
    html_content = render_email_template(
        'templates/email/base_email.html',
        temp_customer,
        custom_body
    )

    # Send
    result = send_email(test_email, "Test User", subject, html_content)
    return result
```

---

## Step 5: HTML Templates

### 5.1 Create `static/style.css`
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    background-color: #f5f5f5;
    color: #333;
}

nav {
    background-color: #2c3e50;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

nav ul {
    list-style: none;
    display: flex;
    gap: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

nav a:hover {
    color: #3498db;
}

.container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 2rem;
}

.card {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

h1 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
}

h2 {
    color: #34495e;
    margin-bottom: 1rem;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
}

.stat-card h3 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.stat-card p {
    opacity: 0.9;
}

.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #555;
}

input[type="text"],
input[type="email"],
input[type="file"],
textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
}

textarea {
    resize: vertical;
    min-height: 200px;
    font-family: 'Courier New', monospace;
}

button {
    background-color: #3498db;
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
}

button:hover {
    background-color: #2980b9;
}

button.secondary {
    background-color: #95a5a6;
}

button.secondary:hover {
    background-color: #7f8c8d;
}

.alert {
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.alert.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.alert.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.alert.info {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    text-align: left;
    padding: 0.75rem;
    border-bottom: 1px solid #ddd;
}

th {
    background-color: #f8f9fa;
    font-weight: 600;
}

tr:hover {
    background-color: #f8f9fa;
}

.preview-box {
    border: 2px solid #ddd;
    padding: 2rem;
    background-color: #fafafa;
    border-radius: 4px;
    margin-top: 1rem;
}

.button-group {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.info-box {
    background-color: #e7f3ff;
    border-left: 4px solid #3498db;
    padding: 1rem;
    margin-bottom: 1rem;
}

### 5.2 Create `templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Email Marketing Platform{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav>
        <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/contacts">Contacts</a></li>
            <li><a href="/import">Import CSV</a></li>
            <li><a href="/preview">Preview & Test</a></li>
        </ul>
    </nav>

    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

### 5.3 Create `templates/dashboard.html`
```html
{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<h1>Dashboard</h1>

<div class="stats">
    <div class="stat-card">
        <h3>{{ total_contacts }}</h3>
        <p>Total Contacts</p>
    </div>
    <div class="stat-card">
        <h3>{{ subscribed }}</h3>
        <p>Subscribed</p>
    </div>
    <div class="stat-card">
        <h3>{{ unsubscribed }}</h3>
        <p>Unsubscribed</p>
    </div>
</div>

<div class="card">
    <h2>Quick Start</h2>
    <p>1. <a href="/import">Import contacts</a> from a CSV file</p>
    <p>2. <a href="/preview">Create and test</a> your email campaign</p>
    <p>3. Send to all subscribed contacts</p>
</div>
{% endblock %}
```

### 5.4 Create `templates/contacts.html`
```html
{% extends "base.html" %}

{% block title %}Contacts{% endblock %}

{% block content %}
<h1>All Contacts</h1>

<div class="card">
    {% if customers %}
    <table>
        <thead>
            <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Status</th>
                <th>Segments</th>
                <th>Joined</th>
            </tr>
        </thead>
        <tbody>
            {% for customer in customers %}
            <tr>
                <td>{{ customer.email }}</td>
                <td>{{ customer.name or '-' }}</td>
                <td>
                    {% if customer.subscribed %}
                    <span style="color: green;">✓ Subscribed</span>
                    {% else %}
                    <span style="color: #999;">✗ Unsubscribed</span>
                    {% endif %}
                </td>
                <td>{{ customer.segments or '-' }}</td>
                <td>{{ customer.opted_in_date.strftime('%Y-%m-%d') if customer.opted_in_date else '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>No contacts yet. <a href="/import">Import some contacts</a> to get started!</p>
    {% endif %}
</div>
{% endblock %}
```

### 5.5 Create `templates/import.html`
```html
{% extends "base.html" %}

{% block title %}Import Contacts{% endblock %}

{% block content %}
<h1>Import Contacts from CSV</h1>

<div class="card">
    {% if message %}
    <div class="alert {{ message_type }}">
        {{ message }}
    </div>
    {% endif %}

    {% if stats %}
    <div class="alert success">
        <strong>Import completed!</strong><br>
        Total rows processed: {{ stats.total_rows }}<br>
        New contacts added: {{ stats.added }}<br>
        Existing contacts updated: {{ stats.updated }}
    </div>
    {% endif %}

    <div class="info-box">
        <strong>CSV Formats Supported:</strong><br>
        <strong>1. Simple format:</strong> <code>email,name,phone</code><br>
        <strong>2. Square POS export:</strong> Automatically detected and imported<br>
        <strong>Example (Simple):</strong><br>
        <code>
        email,name,phone<br>
        john@example.com,John Doe,+15551234567<br>
        jane@example.com,Jane Smith,5559876543
        </code>
    </div>

    <form method="POST" enctype="multipart/form-data">
        <div class="form-group">
            <label for="csvfile">Choose CSV File</label>
            <input type="file" id="csvfile" name="csvfile" accept=".csv" required>
        </div>

        <div class="form-group">
            <label for="segment">Segment Tag (optional)</label>
            <input type="text" id="segment" name="segment" placeholder="e.g., newsletter, promo2024">
        </div>

        <button type="submit">Import Contacts</button>
    </form>
</div>
{% endblock %}
```

### 5.6 Create `templates/preview.html`
```html
{% extends "base.html" %}

{% block title %}Preview & Test Email{% endblock %}

{% block content %}
<h1>Preview & Test Email</h1>

<div class="card">
    {% if message %}
    <div class="alert {{ message_type }}">
        {{ message }}
    </div>
    {% endif %}

    <form method="POST" action="/preview">
        <div class="form-group">
            <label for="subject">Email Subject</label>
            <input type="text" id="subject" name="subject" value="{{ subject or '' }}" 
                   placeholder="Special Offer Just for You!" required>
        </div>

        <div class="form-group">
            <label for="email_body">Email Content (HTML)</label>
            <div class="info-box">
                You can use HTML here. The content will be wrapped in the base template with unsubscribe link.
            </div>
            <textarea id="email_body" name="email_body" required>{{ email_body or '<h2>Special Deal!</h2>\n<p>Check out our amazing offer!</p>\n<p>Your unique QR code will appear here in actual campaigns.</p>' }}</textarea>
        </div>

        <div class="button-group">
            <button type="submit" name="action" value="preview">Preview Email</button>
            <button type="submit" name="action" value="test" class="secondary">Send Test Email</button>
        </div>

        <div class="form-group" style="margin-top: 1rem;">
            <label for="test_email">Test Email Address (for sending test)</label>
            <input type="email" id="test_email" name="test_email" value="{{ test_email or '' }}" 
                   placeholder="you@example.com">
        </div>
    </form>

    {% if preview_html %}
    <h2 style="margin-top: 2rem;">Preview</h2>
    <div class="preview-box">
        {{ preview_html|safe }}
    </div>
    {% endif %}
</div>
{% endblock %}
```

### 5.7 Create `templates/unsubscribe.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f5f5f5;
        }
        .message {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="message">
        <h1>{{ title }}</h1>
        <p>{{ message }}</p>
    </div>
</body>
</html>
```

### 5.8 Create `templates/email/base_email.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
    <div style="background-color: white; padding: 2rem; border-radius: 8px;">
        <!-- Custom email content goes here -->
        {{ email_body|safe }}
    </div>

    <!-- Footer (Legal requirement) -->
    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 12px; color: #666; text-align: center;">
        <p>{{ business_name }}<br>
        {{ business_address }}</p>

        <p>
            <a href="{{ unsubscribe_link }}" style="color: #666; text-decoration: underline;">Unsubscribe from this list</a>
        </p>
    </div>
</body>
</html>
```

---

## Step 6: Main Flask Application

### 6.1 Create `app.py`
```python
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from backend.database import init_db, get_db
from backend.models import Customer, Campaign
from backend.csv_importer import import_csv
from backend.email_service import send_test_email, render_email_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
init_db()

@app.route('/')
def dashboard():
    """Dashboard with statistics"""
    db = get_db()
    try:
        total_contacts = db.query(Customer).count()
        subscribed = db.query(Customer).filter_by(subscribed=True).count()
        unsubscribed = db.query(Customer).filter_by(subscribed=False).count()

        return render_template('dashboard.html',
                             total_contacts=total_contacts,
                             subscribed=subscribed,
                             unsubscribed=unsubscribed)
    finally:
        db.close()

@app.route('/contacts')
def contacts():
    """View all contacts"""
    db = get_db()
    try:
        customers = db.query(Customer).order_by(Customer.created_at.desc()).all()
        return render_template('contacts.html', customers=customers)
    finally:
        db.close()

@app.route('/import', methods=['GET', 'POST'])
def import_contacts():
    """Import contacts from CSV"""
    if request.method == 'POST':
        if 'csvfile' not in request.files:
            return render_template('import.html',
                                 message='No file uploaded',
                                 message_type='error')

        file = request.files['csvfile']
        if file.filename == '':
            return render_template('import.html',
                                 message='No file selected',
                                 message_type='error')

        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                segment = request.form.get('segment', '').strip()
                stats = import_csv(filepath, segment if segment else None)

                # Clean up uploaded file
                os.remove(filepath)

                return render_template('import.html',
                                     stats=stats,
                                     message_type='success')

            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return render_template('import.html',
                                     message=f'Import failed: {str(e)}',
                                     message_type='error')
        else:
            return render_template('import.html',
                                 message='Please upload a CSV file',
                                 message_type='error')

    return render_template('import.html')

@app.route('/preview', methods=['GET', 'POST'])
def preview_email():
    """Preview and test email"""
    if request.method == 'POST':
        subject = request.form.get('subject', '')
        email_body = request.form.get('email_body', '')
        action = request.form.get('action', '')
        test_email = request.form.get('test_email', '')

        if action == 'preview':
            # Generate preview HTML
            preview_html = f"""
            <div style="background-color: white; padding: 2rem; border-radius: 8px;">
                {email_body}
            </div>
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ccc; 
                        font-size: 12px; color: #666; text-align: center;">
                <p>{os.getenv('SENDER_NAME')}<br>
                {os.getenv('BUSINESS_ADDRESS')}</p>
                <p><a href="#" style="color: #666;">Unsubscribe from this list</a></p>
            </div>
            """

            return render_template('preview.html',
                                 subject=subject,
                                 email_body=email_body,
                                 test_email=test_email,
                                 preview_html=preview_html)

        elif action == 'test':
            if not test_email:
                return render_template('preview.html',
                                     subject=subject,
                                     email_body=email_body,
                                     message='Please enter a test email address',
                                     message_type='error')

            try:
                result = send_test_email(test_email, subject, email_body)

                if result['success']:
                    return render_template('preview.html',
                                         subject=subject,
                                         email_body=email_body,
                                         test_email=test_email,
                                         message=f'Test email sent successfully to {test_email}!',
                                         message_type='success')
                else:
                    return render_template('preview.html',
                                         subject=subject,
                                         email_body=email_body,
                                         test_email=test_email,
                                         message=f'Failed to send: {result.get("error", "Unknown error")}',
                                         message_type='error')

            except Exception as e:
                return render_template('preview.html',
                                     subject=subject,
                                     email_body=email_body,
                                     test_email=test_email,
                                     message=f'Error: {str(e)}',
                                     message_type='error')

    return render_template('preview.html')

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    """Handle unsubscribe requests"""
    email = request.args.get('email')
    token = request.args.get('token')

    if not email or not token:
        return render_template('unsubscribe.html',
                             title='Invalid Request',
                             message='Missing required parameters.'), 400

    db = get_db()
    try:
        customer = db.query(Customer).filter_by(email=email).first()

        if not customer:
            return render_template('unsubscribe.html',
                                 title='Not Found',
                                 message='Email address not found in our system.'), 404

        # Verify token
        expected_token = customer.get_unsubscribe_token()
        if token != expected_token:
            return render_template('unsubscribe.html',
                                 title='Invalid Token',
                                 message='Invalid unsubscribe link.'), 403

        # Unsubscribe
        customer.subscribed = False
        customer.unsubscribed_date = datetime.now()
        db.commit()

        return render_template('unsubscribe.html',
                             title='Unsubscribed',
                             message='You have been successfully unsubscribed from our mailing list.')

    finally:
        db.close()

if __name__ == '__main__':
    # For development only - use proper WSGI server for production
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## Step 7: Testing the System

### 7.1 Initialize Database
```bash
cd MaxxConnect
source venv/bin/activate
python -c "from backend.database import init_db; init_db()"
```

### 7.2 Start the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### 7.3 Test Workflow
1. Open browser to `http://localhost:5000`
2. Click "Import CSV" in navigation
3. Create test CSV file (`test_contacts.csv`):
   ```csv
   email,name,phone
   test1@example.com,Test User 1,+15551234567
   test2@example.com,Test User 2,5559876543
   your-actual-email@example.com,Your Name,
   ```
   **Note:** You can also use Square POS customer exports directly - the system will automatically detect and convert the column names.
4. Upload and import the CSV
5. Go to "Contacts" to verify import
6. Go to "Preview & Test"
7. Enter subject and email content
8. Click "Preview Email" to see how it looks
9. Enter your email address
10. Click "Send Test Email"
11. Check your inbox
12. Click unsubscribe link to test

---

## Step 8: Validation Checklist

- [ ] Database created successfully
- [ ] Flask app starts without errors
- [ ] All pages load correctly
- [ ] CSV import works with deduplication
- [ ] Duplicate emails in CSV are removed
- [ ] Invalid emails are rejected
- [ ] Dashboard shows correct contact counts
- [ ] Test email sends successfully
- [ ] Email includes unsubscribe link
- [ ] Unsubscribe link works correctly
- [ ] Email includes business address
- [ ] Preview shows email correctly

---

## Common Issues & Solutions

### Issue: "SendGrid API key invalid"
**Solution**:
- Verify API key in SendGrid dashboard
- Check `.env` file has correct key
- Ensure no extra spaces/quotes

### Issue: "Module not found"
**Solution**:
```bash
# Make sure you're in venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Permission denied on uploads folder"
**Solution**:
```bash
mkdir uploads
chmod 755 uploads
```

### Issue: "Email not received"
**Solution**:
- Check spam folder
- Verify sender email is verified in SendGrid
- Check SendGrid activity dashboard for errors
- Ensure BASE_URL in .env matches your actual URL

---

## Running on Raspberry Pi

### For Production (using Gunicorn):
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (more stable than Flask dev server)
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Auto-start on Boot (systemd service):
Create `/etc/systemd/system/emailmarketing.service`:
```ini
[Unit]
Description=Email Marketing Platform
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/MaxxConnect
Environment="PATH=/home/pi/MaxxConnect/venv/bin"
ExecStart=/home/pi/MaxxConnect/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable emailmarketing
sudo systemctl start emailmarketing
```

---

## Next Steps

Once Phase 1 is complete:
- **Phase 2**: Add QR code generation and campaign management
- **Phase 3**: Build iOS scanner app and redemption API
- **Phase 4**: Add analytics and advanced features

---

## Phase 1 Complete!

You now have:
- ✓ Single Flask application (easy to run!)
- ✓ Working email sending via SendGrid API
- ✓ CSV import with deduplication
- ✓ Test email functionality
- ✓ Email preview system
- ✓ Legal-compliant unsubscribe management
- ✓ Clean HTML/CSS interface
- ✓ All features accessible from web browser
- ✓ Ready to deploy on Raspberry Pi

**Just one command to run everything:** `python app.py`
