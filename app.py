"""
Flask Application - Email/SMS Marketing Platform

CRC: crc-CampaignManager.md
Spec: phase-2-campaign-management.md
"""
from flask import Flask, render_template, request, redirect, url_for, flash, render_template_string, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from backend.database import init_db, get_db
from backend.models import Customer, Campaign, CampaignSend, QRCode, EmailDelivery, Redemption
from backend.csv_importer import import_csv, is_valid_email
from backend.sms_service import format_phone_number, validate_phone_number
from backend.email_service import send_test_email, render_email_template, send_email
from backend.sms_service import send_test_sms
from backend.services import qr_generator
from dotenv import load_dotenv

load_dotenv()

# Basic HTTP Authentication
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    """Verify admin credentials from environment variables"""
    admin_user = os.getenv('ADMIN_USERNAME')
    admin_pass = os.getenv('ADMIN_PASSWORD')

    # If no credentials configured, deny all access in production
    if not admin_user or not admin_pass:
        # Allow access in development if not configured
        if os.getenv('FLASK_ENV') == 'development' or os.getenv('RAILWAY_ENVIRONMENT') is None:
            return True
        return False

    if username == admin_user and password == admin_pass:
        return True
    return False

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
init_db()

@app.route('/')
@auth.login_required
def dashboard():
    """Dashboard with statistics"""
    db = get_db()
    try:
        total_contacts = db.query(Customer).count()
        subscribed = db.query(Customer).filter_by(subscribed=True).count()
        unsubscribed = db.query(Customer).filter_by(subscribed=False).count()

        # SMS stats
        sms_subscribed = db.query(Customer).filter_by(sms_subscribed=True).count()
        # Only count active unsubscribes (people who opted out), not everyone without SMS subscription
        sms_unsubscribed = db.query(Customer).filter(Customer.sms_unsubscribed_date.isnot(None)).count()

        return render_template('dashboard.html',
                             total_contacts=total_contacts,
                             subscribed=subscribed,
                             unsubscribed=unsubscribed,
                             sms_subscribed=sms_subscribed,
                             sms_unsubscribed=sms_unsubscribed)
    finally:
        db.close()

@app.route('/contacts')
@auth.login_required
def contacts():
    """View all contacts"""
    db = get_db()
    try:
        customers = db.query(Customer).order_by(Customer.created_at.desc()).all()
        return render_template('contacts.html', customers=customers)
    finally:
        db.close()

# Default segment tags that always appear
DEFAULT_SEGMENTS = ['test', 'vip', 'new']

@app.route('/api/customer/<int:customer_id>/segments', methods=['POST'])
@auth.login_required
def update_customer_segments(customer_id):
    """Update a customer's segment tags"""
    db = get_db()
    try:
        customer = db.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return {'success': False, 'error': 'Customer not found'}, 404

        data = request.get_json()
        segments = data.get('segments', [])

        # Clean and join segments
        customer.segments = ','.join(filter(None, [s.strip() for s in segments]))
        db.commit()

        return {'success': True, 'segments': customer.segments}
    except Exception as e:
        db.rollback()
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()


@app.route('/api/campaign-send/<int:send_id>/progress')
@auth.login_required
def campaign_send_progress(send_id):
    """
    Get progress of a campaign send operation

    Returns JSON with sent/failed counts and percentage
    """
    db = get_db()
    try:
        send_record = db.query(CampaignSend).filter_by(id=send_id).first()

        if not send_record:
            return {'error': 'Send record not found'}, 404

        # Check if complete and update status
        if send_record.is_complete() and send_record.status == 'sending':
            send_record.status = 'completed'
            send_record.completed_at = datetime.now()

            # Update campaign status
            campaign = db.query(Campaign).filter_by(id=send_record.campaign_id).first()
            if campaign:
                campaign.status = 'sent'
                campaign.sent_date = datetime.now()
            db.commit()

        return {
            'send_id': send_id,
            'campaign_id': send_record.campaign_id,
            'total_emails': send_record.total_emails,
            'emails_sent': send_record.emails_sent,
            'emails_failed': send_record.emails_failed,
            'progress_percent': send_record.progress_percent(),
            'status': send_record.status,
            'started_at': send_record.started_at.isoformat() if send_record.started_at else None,
            'completed_at': send_record.completed_at.isoformat() if send_record.completed_at else None
        }
    finally:
        db.close()


@app.route('/api/campaign/<int:campaign_id>/progress')
@auth.login_required
def campaign_progress(campaign_id):
    """
    Get progress of the latest send for a campaign

    Returns JSON with sent/failed counts and percentage
    """
    db = get_db()
    try:
        # Get the most recent CampaignSend for this campaign
        send_record = db.query(CampaignSend).filter_by(
            campaign_id=campaign_id
        ).order_by(CampaignSend.started_at.desc()).first()

        if not send_record:
            return {'error': 'No send record found for campaign'}, 404

        # Check if complete and update status
        if send_record.is_complete() and send_record.status == 'sending':
            send_record.status = 'completed'
            send_record.completed_at = datetime.now()

            # Update campaign status
            campaign = db.query(Campaign).filter_by(id=campaign_id).first()
            if campaign:
                campaign.status = 'sent'
                campaign.sent_date = datetime.now()
            db.commit()

        return {
            'send_id': send_record.id,
            'campaign_id': campaign_id,
            'total_emails': send_record.total_emails,
            'emails_sent': send_record.emails_sent,
            'emails_failed': send_record.emails_failed,
            'progress_percent': send_record.progress_percent(),
            'status': send_record.status,
            'started_at': send_record.started_at.isoformat() if send_record.started_at else None,
            'completed_at': send_record.completed_at.isoformat() if send_record.completed_at else None
        }
    finally:
        db.close()


@app.route('/import', methods=['GET', 'POST'])
@auth.login_required
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
                email_consent = request.form.get('email_consent') == 'on'
                sms_consent = request.form.get('sms_consent') == 'on'
                stats = import_csv(
                    filepath,
                    segment_tag=segment if segment else None,
                    email_consent=email_consent,
                    sms_consent=sms_consent
                )

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

@app.route('/contact/add', methods=['POST'])
@auth.login_required
def add_single_contact():
    """Add a single contact manually"""
    email = request.form.get('email', '').strip().lower()
    name = request.form.get('name', '').strip()
    phone_raw = request.form.get('phone', '').strip()
    segment = request.form.get('segment', '').strip()
    email_consent = request.form.get('email_consent') == 'on'
    sms_consent = request.form.get('sms_consent') == 'on'

    # Validate email
    if not email:
        return render_template('import.html',
                             message='Email address is required',
                             message_type='error')

    if not is_valid_email(email):
        return render_template('import.html',
                             message='Invalid email address format',
                             message_type='error')

    # Format and validate phone if provided
    phone = None
    if phone_raw:
        formatted = format_phone_number(phone_raw)
        if formatted and validate_phone_number(formatted):
            phone = formatted
        else:
            return render_template('import.html',
                                 message=f'Invalid phone number format: {phone_raw}',
                                 message_type='error')

    # Check SMS consent requires phone
    if sms_consent and not phone:
        return render_template('import.html',
                             message='Phone number required for SMS subscription',
                             message_type='error')

    db = get_db()
    try:
        # Check if customer exists
        existing = Customer.find_by_email(db, email)

        if existing:
            # Update existing contact
            if name:
                existing.name = name
            if phone:
                existing.phone = phone
            if email_consent and not existing.subscribed:
                existing.subscribed = True
                existing.opted_in_date = datetime.now()
            if sms_consent and phone and not existing.sms_subscribed:
                existing.sms_subscribed = True
                existing.sms_opted_in_date = datetime.now()
            if segment:
                tags = set(existing.segments.split(',')) if existing.segments else set()
                tags.add(segment)
                existing.segments = ','.join(filter(None, tags))
            existing.updated_at = datetime.now()
            db.commit()
            return render_template('import.html',
                                 message=f'Contact updated: {email}',
                                 message_type='success')
        else:
            # Create new contact
            customer = Customer(
                email=email,
                phone=phone,
                name=name,
                segments=segment if segment else '',
                subscribed=email_consent,
                opted_in_date=datetime.now() if email_consent else None,
                sms_subscribed=sms_consent and phone is not None,
                sms_opted_in_date=datetime.now() if (sms_consent and phone) else None
            )
            db.add(customer)
            db.commit()
            return render_template('import.html',
                                 message=f'Contact added: {email}',
                                 message_type='success')
    except Exception as e:
        db.rollback()
        return render_template('import.html',
                             message=f'Failed to add contact: {str(e)}',
                             message_type='error')

@app.route('/preview', methods=['GET', 'POST'])
@auth.login_required
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
                <p>{os.getenv('BUSINESS_NAME')}<br>
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
        customer = Customer.find_by_email(db, email)

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

@app.route('/sms-preview', methods=['GET', 'POST'])
@auth.login_required
def sms_preview():
    """Preview and test SMS"""
    if request.method == 'POST':
        message = request.form.get('message', '')
        action = request.form.get('action', '')
        test_phone = request.form.get('test_phone', '')

        if action == 'preview':
            # Generate preview
            preview_message = message
            # Show character count
            char_count = len(message)
            optout_addition = f"\n\nReply STOP to unsubscribe. - {os.getenv('BUSINESS_NAME')}"
            total_chars = char_count + len(optout_addition)

            return render_template('sms_preview.html',
                                 message=message,
                                 test_phone=test_phone,
                                 preview_message=preview_message,
                                 char_count=char_count,
                                 total_chars=total_chars)

        elif action == 'test':
            if not test_phone:
                return render_template('sms_preview.html',
                                     message=message,
                                     sms_message='Please enter a test phone number',
                                     message_type='error')

            try:
                result = send_test_sms(test_phone, message)

                if result['success']:
                    return render_template('sms_preview.html',
                                         message=message,
                                         test_phone=test_phone,
                                         sms_message=f'Test SMS sent successfully to {test_phone}!',
                                         message_type='success')
                else:
                    return render_template('sms_preview.html',
                                         message=message,
                                         test_phone=test_phone,
                                         sms_message=f'Failed to send: {result.get("error", "Unknown error")}',
                                         message_type='error')

            except Exception as e:
                return render_template('sms_preview.html',
                                     message=message,
                                     test_phone=test_phone,
                                     sms_message=f'Error: {str(e)}',
                                     message_type='error')

    return render_template('sms_preview.html')

@app.route('/sms-optout', methods=['GET', 'POST'])
def sms_optout():
    """
    Handle SMS opt-out requests
    This endpoint is called by Twilio webhook when someone replies STOP
    """
    if request.method == 'POST':
        # Twilio sends POST request with From and Body
        from_phone = request.form.get('From', '')
        message_body = request.form.get('Body', '').upper()

        if 'STOP' in message_body or 'UNSUBSCRIBE' in message_body:
            db = get_db()
            try:
                customer = Customer.find_by_phone(db, from_phone)

                if customer:
                    customer.sms_subscribed = False
                    customer.sms_unsubscribed_date = datetime.now()
                    db.commit()

                    # Twilio expects TwiML response
                    return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>', 200

            finally:
                db.close()

    # Manual opt-out via web (with token verification)
    phone = request.args.get('phone')
    token = request.args.get('token')

    if not phone or not token:
        return render_template('unsubscribe.html',
                             title='Invalid Request',
                             message='Missing required parameters.'), 400

    db = get_db()
    try:
        customer = Customer.find_by_phone(db, phone)

        if not customer:
            return render_template('unsubscribe.html',
                                 title='Not Found',
                                 message='Phone number not found in our system.'), 404

        # Verify token
        expected_token = customer.get_sms_optout_token()
        if token != expected_token:
            return render_template('unsubscribe.html',
                                 title='Invalid Token',
                                 message='Invalid opt-out link.'), 403

        # Opt out
        customer.sms_subscribed = False
        customer.sms_unsubscribed_date = datetime.now()
        db.commit()

        return render_template('unsubscribe.html',
                             title='Unsubscribed from SMS',
                             message='You have been successfully unsubscribed from SMS messages.')

    finally:
        db.close()

@app.route('/test-template')
@auth.login_required
def test_template():
    """Test the Monday special email template with QR code placeholder approach"""
    # Render base template
    html = render_template('email/monday_special.html',
                          logo_url='/static/images/FNFWebLogo200x50.png',
                          hero_image_url='/static/images/FNFFront600x300.png',
                          unsubscribe_link='/unsubscribe?token=test123')

    # Replace customer name placeholder
    html = html.replace('[[CUSTOMER_NAME]]', 'Test Customer')

    # Inject QR placeholder HTML
    qr_placeholder_html = '''
    <table cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 20px auto;">
      <tr>
        <td style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
          <p style="margin: 0 0 10px 0; font-weight: bold; color: #d32f2f;">SHOW THIS QR CODE TO REDEEM:</p>
          <img src="{{QR_CODE_DATA_URI}}" width="200" height="200" alt="Redemption QR Code" style="display: block; margin: 0 auto;">
          <p style="margin: 10px 0 0 0; font-size: 11px; color: #888;">One-time use only.</p>
        </td>
      </tr>
    </table>
    '''
    html = html.replace('<!-- QR_CODE_SECTION -->', qr_placeholder_html)

    # Replace with dummy QR image for testing
    dummy_qr = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    html = html.replace('[[QR_CODE_DATA_URI]]', dummy_qr)

    return html

def get_available_templates():
    """
    Scan templates/email and uploads/templates for available email templates

    CRC: crc-CampaignManager.md
    Sequence: seq-campaign-create.md
    """
    templates = []

    # Bundled templates in templates/email/
    templates_dir = os.path.join(app.template_folder, 'email')
    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith('.html'):
                name = filename.replace('.html', '').replace('_', ' ').replace('-', ' ').title()
                templates.append({
                    'filename': f'email/{filename}',
                    'name': name
                })

    # User-created templates in uploads/templates/
    user_templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'templates')
    if os.path.exists(user_templates_dir):
        for filename in os.listdir(user_templates_dir):
            if filename.endswith('.html') and not filename.endswith('.grapes.json'):
                name = filename.replace('.html', '').replace('_', ' ').replace('-', ' ').title()
                templates.append({
                    'filename': f'user:{filename}',
                    'name': f'{name} (Custom)'
                })

    return sorted(templates, key=lambda x: x['name'])


def render_campaign_template(template_name, **template_vars):
    """
    Render a template by name, handling both bundled (email/...) and user (user:...) templates.
    Bundled templates use Flask's render_template; user templates are loaded from uploads/templates/.
    """
    if template_name.startswith('user:'):
        filename = template_name[5:]  # Strip 'user:' prefix
        user_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'templates', filename)
        with open(user_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return render_template_string(html_content, **template_vars)
    else:
        return render_template(template_name, **template_vars)


def get_unique_segments(db):
    """
    Get all unique segment tags from customers with counts

    Returns list of dicts: [{'name': 'vip', 'count': 15}, ...]
    Includes default segments (test, vip, new) even if count is 0
    """
    customers = db.query(Customer).filter(Customer.segments != None, Customer.segments != '').all()
    segment_counts = {}

    # Initialize default segments with 0 count
    for default_seg in DEFAULT_SEGMENTS:
        segment_counts[default_seg] = 0

    for customer in customers:
        if customer.segments:
            for tag in customer.segments.split(','):
                tag = tag.strip()
                if tag:
                    segment_counts[tag] = segment_counts.get(tag, 0) + 1

    return sorted([{'name': k, 'count': v} for k, v in segment_counts.items()], key=lambda x: x['name'])

@app.route('/campaigns')
@auth.login_required
def campaigns():
    """
    View all campaigns

    CRC: crc-CampaignManager.md
    UI: ui-campaign-list.md
    """
    db = get_db()
    try:
        all_campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
        return render_template('campaigns.html', campaigns=all_campaigns)
    finally:
        db.close()

@app.route('/campaign/new', methods=['GET', 'POST'])
@auth.login_required
def campaign_new():
    """
    Create new campaign

    CRC: crc-CampaignManager.md
    Sequence: seq-campaign-create.md
    UI: ui-campaign-create.md
    """
    db = get_db()
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            subject = request.form.get('subject')
            template = request.form.get('template')
            segment = request.form.get('segment', 'all')
            action = request.form.get('action')
            test_mode = request.form.get('test_mode') == 'on'
            test_email = request.form.get('test_email', '')

            # Render the selected template with sample data
            try:
                from backend.config import Config
                from backend.image_handler import ImageHandler

                # Build template variables
                # Note: Don't include customer_name or unsubscribe_link here
                # [[CUSTOMER_NAME]] placeholder will be replaced at send time
                template_vars = {}

                # Use base64 for development, external URLs for production
                if Config.is_development():
                    template_vars['logo_base64'] = ImageHandler.get_image_url('FNFWebLogo200x50.png').replace('data:image/png;base64,', '')
                    template_vars['hero_image_base64'] = ImageHandler.get_image_url('FNFFront600x300.png').replace('data:image/png;base64,', '')
                else:
                    template_vars['logo_url'] = url_for('static', filename='images/FNFWebLogo200x50.png', _external=True)
                    template_vars['hero_image_url'] = url_for('static', filename='images/FNFFront600x300.png', _external=True)

                html_content = render_campaign_template(template, **template_vars)

                # If QR codes enabled, inject QR placeholder HTML
                has_qr_code = request.form.get('has_qr_code') == 'on'
                if has_qr_code:
                    qr_placeholder_html = '''
                    <table cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 20px auto;">
                      <tr>
                        <td style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
                          <p style="margin: 0 0 10px 0; font-weight: bold; color: #d32f2f;">SHOW THIS QR CODE TO REDEEM:</p>
                          <img src="[[QR_CODE_DATA_URI]]" width="200" height="200" alt="Redemption QR Code" style="display: block; margin: 0 auto;">
                          <p style="margin: 10px 0 0 0; font-size: 11px; color: #888;">One-time use only.</p>
                        </td>
                      </tr>
                    </table>
                    '''
                    html_content = html_content.replace('<!-- QR_CODE_SECTION -->', qr_placeholder_html)
            except Exception as e:
                flash(f'Error rendering template: {str(e)}', 'error')
                return redirect('/campaign/new')

            # Create campaign
            has_qr_code = request.form.get('has_qr_code') == 'on'
            deal_description = request.form.get('deal_description', '').strip() if has_qr_code else None
            campaign = Campaign(
                name=name,
                subject=subject,
                template_name=template,
                html_content=html_content,
                has_qr_code=has_qr_code,
                deal_description=deal_description,
                status='draft'
            )
            db.add(campaign)
            db.commit()

            if action == 'preview':
                return redirect(f'/campaign/preview/{campaign.id}')
            elif action == 'send':
                # Handle test mode - send only to test email
                if test_mode and test_email:
                    try:
                        # Generate personalized test email
                        template_vars = {
                            'unsubscribe_link': '#test-unsubscribe'
                        }

                        # Replace placeholders before Jinja2 rendering
                        html_to_render = campaign.html_content
                        html_to_render = html_to_render.replace('[[CUSTOMER_NAME]]', 'Test Customer')

                        # Generate real QR code for test if campaign has it enabled
                        # Use CID approach for Gmail compatibility
                        inline_attachments = []
                        if campaign.has_qr_code:
                            from backend.config import Config
                            test_token = f"TEST-{campaign.id}-preview"
                            test_url = f"{Config.BASE_URL}/redeem/{test_token}"
                            qr_image_bytes = qr_generator.generate_qr_image(test_url)
                            content_id = f"qr-test-{campaign.id}"
                            html_to_render = html_to_render.replace('[[QR_CODE_DATA_URI]]', f'cid:{content_id}')
                            inline_attachments.append({
                                'content_id': content_id,
                                'image_bytes': qr_image_bytes
                            })

                        personalized_html = render_template_string(
                            html_to_render,
                            **template_vars
                        )

                        # Send test email with CID attachment
                        result = send_email(
                            test_email, 'Test Customer', campaign.subject, personalized_html,
                            inline_attachments=inline_attachments if inline_attachments else None
                        )

                        if result.get('success'):
                            flash(f'✓ Test email sent successfully to {test_email}! (Status: {result.get("status_code", "N/A")})', 'success')
                        else:
                            flash(f'✗ Failed to send test email: {result.get("error", "Unknown error")}', 'error')

                        return redirect('/campaigns')
                    except Exception as e:
                        flash(f'Error sending test email: {str(e)}', 'error')
                        return redirect('/campaigns')
                else:
                    # Normal send - redirect to send route
                    return redirect(f'/campaign/send/{campaign.id}')
            else:  # save
                flash('Campaign saved as draft!', 'success')
                return redirect('/campaigns')

        # GET request - show form
        templates = get_available_templates()
        total_subscribers = db.query(Customer).filter_by(subscribed=True).count()
        email_only = db.query(Customer).filter_by(subscribed=True, sms_subscribed=False).count()
        sms_only = db.query(Customer).filter_by(sms_subscribed=True, subscribed=False).count()
        both = db.query(Customer).filter_by(subscribed=True, sms_subscribed=True).count()

        return render_template('campaign_create.html',
                             templates=templates,
                             total_subscribers=total_subscribers,
                             email_only=email_only,
                             sms_only=sms_only,
                             both=both)
    finally:
        db.close()

@app.route('/campaign/preview/<int:campaign_id>')
@auth.login_required
def campaign_preview(campaign_id):
    """
    Preview a campaign

    CRC: crc-CampaignManager.md
    Sequence: seq-campaign-preview.md
    """
    db = get_db()
    try:
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect('/campaigns')

        # Return the HTML content directly for preview
        return campaign.html_content
    finally:
        db.close()

@app.route('/campaign/edit/<int:campaign_id>', methods=['GET', 'POST'])
@auth.login_required
def campaign_edit(campaign_id):
    """
    Edit an existing campaign

    CRC: crc-CampaignManager.md
    Sequence: seq-campaign-create.md
    """
    db = get_db()
    try:
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect('/campaigns')

        if request.method == 'POST':
            # Update campaign
            campaign.name = request.form.get('name')
            campaign.subject = request.form.get('subject')
            template = request.form.get('template')
            action = request.form.get('action')

            # Update QR code setting only if campaign hasn't been sent
            new_has_qr_code = request.form.get('has_qr_code') == 'on'
            qr_setting_changed = (campaign.status != 'sent' and new_has_qr_code != campaign.has_qr_code)

            if campaign.status != 'sent':
                campaign.has_qr_code = new_has_qr_code

            # Update deal description (can be updated even for sent campaigns)
            if new_has_qr_code:
                campaign.deal_description = request.form.get('deal_description', '').strip() or None
            else:
                campaign.deal_description = None

            # Re-render template if template changed OR QR setting changed
            if template != campaign.template_name or qr_setting_changed:
                try:
                    from backend.config import Config
                    from backend.image_handler import ImageHandler

                    # Build template variables
                    # Note: Don't include customer_name or unsubscribe_link here
                    # [[CUSTOMER_NAME]] placeholder will be replaced at send time
                    template_vars = {}

                    # Use base64 for development, external URLs for production
                    if Config.is_development():
                        template_vars['logo_base64'] = ImageHandler.get_image_url('FNFWebLogo200x50.png').replace('data:image/png;base64,', '')
                        template_vars['hero_image_base64'] = ImageHandler.get_image_url('FNFFront600x300.png').replace('data:image/png;base64,', '')
                    else:
                        template_vars['logo_url'] = url_for('static', filename='images/FNFWebLogo200x50.png', _external=True)
                        template_vars['hero_image_url'] = url_for('static', filename='images/FNFFront600x300.png', _external=True)

                    # Use new template if changed, otherwise use existing
                    template_to_render = template if template != campaign.template_name else campaign.template_name
                    html_content = render_campaign_template(template_to_render, **template_vars)

                    # If QR codes enabled, inject QR placeholder HTML
                    if new_has_qr_code:
                        qr_placeholder_html = '''
                    <table cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 20px auto;">
                      <tr>
                        <td style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
                          <p style="margin: 0 0 10px 0; font-weight: bold; color: #d32f2f;">SHOW THIS QR CODE TO REDEEM:</p>
                          <img src="[[QR_CODE_DATA_URI]]" width="200" height="200" alt="Redemption QR Code" style="display: block; margin: 0 auto;">
                          <p style="margin: 10px 0 0 0; font-size: 11px; color: #888;">One-time use only.</p>
                        </td>
                      </tr>
                    </table>
                    '''
                        html_content = html_content.replace('<!-- QR_CODE_SECTION -->', qr_placeholder_html)

                    campaign.html_content = html_content
                    campaign.template_name = template_to_render
                except Exception as e:
                    flash(f'Error rendering template: {str(e)}', 'error')
                    return redirect(f'/campaign/edit/{campaign_id}')

            db.commit()

            if action == 'preview':
                return redirect(f'/campaign/preview/{campaign.id}')
            else:
                flash('✓ Campaign updated successfully!', 'success')
                return redirect('/campaigns')

        # GET request - show form with existing data
        templates = get_available_templates()
        total_subscribers = db.query(Customer).filter_by(subscribed=True).count()
        email_only = db.query(Customer).filter_by(subscribed=True, sms_subscribed=False).count()
        sms_only = db.query(Customer).filter_by(sms_subscribed=True, subscribed=False).count()
        both = db.query(Customer).filter_by(subscribed=True, sms_subscribed=True).count()

        return render_template('campaign_edit.html',
                             campaign=campaign,
                             templates=templates,
                             total_subscribers=total_subscribers,
                             email_only=email_only,
                             sms_only=sms_only,
                             both=both)
    finally:
        db.close()

@app.route('/campaign/delete/<int:campaign_id>', methods=['POST'])
@auth.login_required
def campaign_delete(campaign_id):
    """
    Delete a campaign

    CRC: crc-CampaignManager.md
    """
    db = get_db()
    try:
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect('/campaigns')

        campaign_name = campaign.name
        db.delete(campaign)
        db.commit()

        flash(f'✓ Campaign "{campaign_name}" deleted successfully', 'success')
        return redirect('/campaigns')
    except Exception as e:
        flash(f'Error deleting campaign: {str(e)}', 'error')
        return redirect('/campaigns')
    finally:
        db.close()

@app.route('/campaign/send-confirm/<int:campaign_id>')
@auth.login_required
def campaign_send_confirm(campaign_id):
    """
    Show send confirmation page with audience selection

    CRC: crc-CampaignManager.md
    Sequence: seq-campaign-send.md
    UI: ui-campaign-send-confirm.md
    """
    db = get_db()
    try:
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect('/campaigns')

        # Get audience counts
        total_subscribers = db.query(Customer).filter_by(subscribed=True).count()
        email_only = db.query(Customer).filter_by(subscribed=True, sms_subscribed=False).count()
        sms_only = db.query(Customer).filter_by(sms_subscribed=True, subscribed=False).count()
        both = db.query(Customer).filter_by(subscribed=True, sms_subscribed=True).count()

        # Get unique segments for filtering
        segments = get_unique_segments(db)

        # Get delivery stats for resume feature
        emails_sent = db.query(EmailDelivery).filter_by(
            campaign_id=campaign_id,
            status='sent'
        ).count()
        emails_failed = db.query(EmailDelivery).filter_by(
            campaign_id=campaign_id,
            status='failed'
        ).count()
        emails_pending = total_subscribers - emails_sent

        return render_template('campaign_send_confirm.html',
                             campaign=campaign,
                             total_subscribers=total_subscribers,
                             email_only=email_only,
                             sms_only=sms_only,
                             both=both,
                             segments=segments,
                             emails_sent=emails_sent,
                             emails_failed=emails_failed,
                             emails_pending=emails_pending)
    finally:
        db.close()

@app.route('/campaign/send/<int:campaign_id>', methods=['POST'])
@auth.login_required
def campaign_send(campaign_id):
    """
    Send a campaign based on confirmation form

    CRC: crc-CampaignManager.md
    Sequence: seq-campaign-send.md
    """
    db = get_db()
    try:
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect('/campaigns')

        # Get form data
        channel = request.form.get('channel', 'all')
        segment = request.form.get('segment', 'all')
        test_mode = request.form.get('test_mode') == 'on'
        test_email = request.form.get('test_email', '')

        # Handle test mode
        if test_mode:
            if not test_email:
                flash('Test email address is required in test mode', 'error')
                return redirect(f'/campaign/send-confirm/{campaign_id}')

            try:
                # Get the real customer for generating unsubscribe link
                test_customer = Customer.find_by_email(db, test_email)

                # Generate test email with working unsubscribe link
                if test_customer:
                    unsubscribe_link = url_for('unsubscribe',
                                              email=test_customer.email,
                                              token=test_customer.get_unsubscribe_token(),
                                              _external=True)
                else:
                    unsubscribe_link = url_for('unsubscribe', _external=True)

                # Build complete template variables
                from backend.config import Config
                from backend.image_handler import ImageHandler

                # DEBUG: Log template being used
                print(f"DEBUG: Using template: {campaign.template_name}")
                print(f"DEBUG: Environment: {Config.ENV}")

                template_vars = {
                    'unsubscribe_link': unsubscribe_link
                }

                print(f"DEBUG: unsubscribe_link = {unsubscribe_link}")

                # Add image URLs based on environment
                if Config.is_development():
                    template_vars['logo_base64'] = ImageHandler.get_image_url('FNFWebLogo200x50.png').replace('data:image/png;base64,', '')
                    template_vars['hero_image_base64'] = ImageHandler.get_image_url('FNFFront600x300.png').replace('data:image/png;base64,', '')
                    print("DEBUG: Using base64 images (development mode)")
                else:
                    template_vars['logo_url'] = url_for('static', filename='images/FNFWebLogo200x50.png', _external=True)
                    template_vars['hero_image_url'] = url_for('static', filename='images/FNFFront600x300.png', _external=True)
                    print(f"DEBUG: Using external image URLs (production mode)")
                    print(f"DEBUG: logo_url = {template_vars['logo_url']}")
                    print(f"DEBUG: hero_image_url = {template_vars['hero_image_url']}")

                print(f"DEBUG: Template vars keys: {list(template_vars.keys())}")

                # Render fresh from template file with all variables
                print("DEBUG: About to render template...")
                try:
                    personalized_html = render_template(
                        campaign.template_name,
                        **template_vars
                    )

                    # Replace customer name placeholder (survives Jinja2 rendering)
                    personalized_html = personalized_html.replace('[[CUSTOMER_NAME]]', 'Test Customer')

                    # If QR codes enabled, inject QR placeholder HTML with CID reference
                    inline_attachments = []
                    if campaign.has_qr_code:
                        # Generate CID for this test email
                        content_id = f"qr-test-{campaign.id}-{test_customer.id if test_customer else 'preview'}"
                        qr_placeholder_html = f'''
                    <table cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 20px auto;">
                      <tr>
                        <td style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
                          <p style="margin: 0 0 10px 0; font-weight: bold; color: #d32f2f;">SHOW THIS QR CODE TO REDEEM:</p>
                          <img src="cid:{content_id}" width="200" height="200" alt="Redemption QR Code" style="display: block; margin: 0 auto;">
                          <p style="margin: 10px 0 0 0; font-size: 11px; color: #888;">One-time use only.</p>
                        </td>
                      </tr>
                    </table>
                    '''
                        personalized_html = personalized_html.replace('<!-- QR_CODE_SECTION -->', qr_placeholder_html)

                        # Generate real QR code bytes for CID attachment
                        test_token = f"TEST-{campaign.id}-{test_customer.id if test_customer else 'preview'}"
                        test_url = f"{Config.BASE_URL}/redeem/{test_token}"
                        qr_image_bytes = qr_generator.generate_qr_image(test_url)
                        inline_attachments.append({
                            'content_id': content_id,
                            'image_bytes': qr_image_bytes
                        })

                    print(f"DEBUG: Template rendered successfully. HTML length: {len(personalized_html)}")
                    print(f"DEBUG: First 200 chars of HTML: {personalized_html[:200]}")
                except Exception as render_error:
                    print(f"ERROR: Template rendering failed: {str(render_error)}")
                    import traceback
                    traceback.print_exc()
                    raise

                # Send test email with CID attachment
                print("DEBUG: About to send email...")
                result = send_email(
                    test_email, 'Test Customer', campaign.subject, personalized_html,
                    inline_attachments=inline_attachments if inline_attachments else None
                )
                print(f"DEBUG: Send result: {result}")

                if result.get('success'):
                    flash(f'✓ Test email sent successfully to {test_email}! (Status: {result.get("status_code", "N/A")})', 'success')
                else:
                    flash(f'✗ Failed to send test email: {result.get("error", "Unknown error")}', 'error')

                return redirect('/campaigns')
            except Exception as e:
                print(f"ERROR: Exception in campaign send: {str(e)}")
                import traceback
                traceback.print_exc()
                flash(f'Error sending test email: {str(e)}', 'error')
                return redirect('/campaigns')

        # Get subscribers based on channel
        if channel == 'email_only':
            query = db.query(Customer).filter_by(subscribed=True, sms_subscribed=False)
        elif channel == 'sms_only':
            query = db.query(Customer).filter_by(sms_subscribed=True, subscribed=False)
        elif channel == 'both':
            query = db.query(Customer).filter_by(subscribed=True, sms_subscribed=True)
        else:  # 'all'
            query = db.query(Customer).filter_by(subscribed=True)

        # Apply segment filter if specified
        if segment and segment != 'all':
            query = query.filter(Customer.segments.like(f'%{segment}%'))

        subscribers = query.all()
        total_count = len(subscribers)

        if total_count == 0:
            flash('No subscribers match the selected criteria', 'warning')
            return redirect(f'/campaign/send-confirm/{campaign_id}')

        # Create CampaignSend record for progress tracking
        campaign_send_record = CampaignSend(
            campaign_id=campaign_id,
            total_emails=total_count,
            emails_sent=0,
            emails_failed=0,
            status='sending'
        )
        db.add(campaign_send_record)
        db.commit()
        campaign_send_id = campaign_send_record.id

        # Queue all tasks (non-blocking)
        from backend.tasks.email_task import send_campaign_email

        for customer in subscribers:
            send_campaign_email.delay(
                campaign_id=campaign.id,
                customer_id=customer.id,
                campaign_send_id=campaign_send_id
            )

        # Update campaign status to 'sending'
        campaign.status = 'sending'
        db.commit()

        flash(f'Campaign queued! Sending to {total_count} subscribers in background. Check campaigns page for progress.', 'success')
        return redirect('/campaigns')

    except Exception as e:
        flash(f'Error sending campaign: {str(e)}', 'error')
        return redirect('/campaigns')
    finally:
        db.close()


@app.route('/campaign/resume/<int:campaign_id>', methods=['POST'])
@auth.login_required
def campaign_resume(campaign_id):
    """
    Resume a campaign - only send to customers who haven't received it yet

    Uses EmailDelivery tracking to identify unsent recipients.
    """
    db = get_db()
    try:
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            flash('Campaign not found', 'error')
            return redirect('/campaigns')

        # Get form data (same as regular send)
        channel = request.form.get('channel', 'all')
        segment = request.form.get('segment', 'all')

        # Get subscribers based on channel
        if channel == 'email_only':
            query = db.query(Customer).filter_by(subscribed=True, sms_subscribed=False)
        elif channel == 'sms_only':
            query = db.query(Customer).filter_by(sms_subscribed=True, subscribed=False)
        elif channel == 'both':
            query = db.query(Customer).filter_by(subscribed=True, sms_subscribed=True)
        else:  # 'all'
            query = db.query(Customer).filter_by(subscribed=True)

        # Apply segment filter if specified
        if segment and segment != 'all':
            query = query.filter(Customer.segments.like(f'%{segment}%'))

        all_subscribers = query.all()

        # Find customers who already received this campaign successfully
        sent_deliveries = db.query(EmailDelivery.customer_id).filter_by(
            campaign_id=campaign_id,
            status='sent'
        ).all()
        sent_customer_ids = {d.customer_id for d in sent_deliveries}

        # Filter to only unsent customers
        unsent_subscribers = [c for c in all_subscribers if c.id not in sent_customer_ids]
        total_count = len(unsent_subscribers)
        already_sent = len(sent_customer_ids)

        if total_count == 0:
            flash(f'All {already_sent} subscribers have already received this campaign!', 'info')
            return redirect('/campaigns')

        # Create new CampaignSend record for this resume batch
        campaign_send_record = CampaignSend(
            campaign_id=campaign_id,
            total_emails=total_count,
            emails_sent=0,
            emails_failed=0,
            status='sending'
        )
        db.add(campaign_send_record)
        db.commit()
        campaign_send_id = campaign_send_record.id

        # Queue tasks only for unsent customers
        from backend.tasks.email_task import send_campaign_email

        for customer in unsent_subscribers:
            send_campaign_email.delay(
                campaign_id=campaign.id,
                customer_id=customer.id,
                campaign_send_id=campaign_send_id
            )

        # Update campaign status
        campaign.status = 'sending'
        db.commit()

        flash(f'Campaign resumed! Sending to {total_count} remaining subscribers ({already_sent} already sent). Check campaigns page for progress.', 'success')
        return redirect('/campaigns')

    except Exception as e:
        flash(f'Error resuming campaign: {str(e)}', 'error')
        return redirect('/campaigns')
    finally:
        db.close()


# =============================================================================
# Template Management Routes
# CRC: crc-TemplateProcessor.md
# Seq: seq-template-import.md
# =============================================================================

@app.route('/templates')
@auth.login_required
def template_list():
    """
    List all email templates with validation status

    Shows both bundled templates (templates/email/) and user-created templates (uploads/templates/)

    UI: ui-template-list.md
    """
    from backend.services.template_processor import TemplateProcessor

    processor = TemplateProcessor()

    # Get bundled templates
    bundled_templates = processor.list_templates(app.template_folder)
    for t in bundled_templates:
        t['is_user_template'] = False
        t['has_designer'] = os.path.exists(get_sidecar_path(t['path']))

    # Get user-created templates
    user_templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    user_templates = processor.list_templates(user_templates_dir, subfolder='templates')
    for t in user_templates:
        t['is_user_template'] = True
        t['has_designer'] = os.path.exists(get_sidecar_path(t['path']))
        t['filename'] = 'user:' + t['filename']  # Prefix to distinguish

    # Combine and sort
    all_templates = bundled_templates + user_templates
    all_templates.sort(key=lambda x: x['name'])

    return render_template('template_list.html', templates=all_templates)


@app.route('/template/new', methods=['GET', 'POST'])
@auth.login_required
def template_new():
    """
    Create a new template from starter or blank template

    UI: ui-template-create.md
    """
    from backend.services.template_processor import TemplateProcessor

    processor = TemplateProcessor()

    if request.method == 'POST':
        template_name = request.form.get('template_name', '').strip()
        template_type = request.form.get('template_type', 'starter')
        editor_mode = request.form.get('editor_mode', 'code')

        # Validate template name
        if not template_name:
            flash('Template name is required', 'error')
            return redirect('/template/new')

        # Sanitize: only allow alphanumeric and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', template_name):
            flash('Template name can only contain letters, numbers, and underscores', 'error')
            return redirect('/template/new')

        # Create safe filename
        safe_name = template_name.lower()
        if not safe_name.endswith('.html'):
            safe_name += '.html'

        # User-created templates go to uploads/templates/ (Railway volume for persistence)
        # Bundled templates stay in templates/email/ (read-only, part of deploy)
        user_templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'templates')
        os.makedirs(user_templates_dir, exist_ok=True)
        template_path = os.path.join(user_templates_dir, safe_name)

        # Also check bundled templates to avoid name conflicts
        bundled_path = os.path.join(app.template_folder, 'email', safe_name)

        if os.path.exists(template_path) or os.path.exists(bundled_path):
            flash(f'Template "{safe_name}" already exists. Please choose a different name.', 'error')
            return redirect('/template/new')

        # Route to visual designer if selected
        if editor_mode == 'visual':
            starter = request.form.get('starter_template', 'basic-announcement')
            return redirect(f'/template/designer/new?name=user:{safe_name}&starter={starter}')

        # Code editor path: create file and redirect
        if template_type == 'blank':
            html_content = processor.get_blank_template()
        else:
            html_content = processor.get_starter_template()

        # Save the template
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            flash(f'Template "{safe_name}" created successfully!', 'success')
            # Use 'user:' prefix to indicate user template
            return redirect(f'/template/edit/user:{safe_name}')
        except Exception as e:
            flash(f'Error creating template: {str(e)}', 'error')
            return redirect('/template/new')

    # GET request - show form with preview
    starter_html = processor.get_starter_template()
    blank_html = processor.get_blank_template()

    return render_template('template_create.html',
                         starter_html=starter_html,
                         blank_html=blank_html)


@app.route('/api/template/upload-image', methods=['POST'])
@auth.login_required
def api_template_upload_image():
    """
    Upload an image for use in email templates

    Accepts multipart image upload, validates type and size,
    saves to templates/images/ with unique filename.

    Returns JSON with filename, url, and html_snippet for insertion.
    """
    import time

    if 'image' not in request.files:
        return {'success': False, 'error': 'No image file provided'}, 400

    file = request.files['image']
    if file.filename == '':
        return {'success': False, 'error': 'No file selected'}, 400

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return {'success': False, 'error': 'Invalid file type. Use PNG, JPG, or GIF.'}, 400

    # Validate file size (max 2MB)
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    if size > 2 * 1024 * 1024:
        return {'success': False, 'error': 'File too large. Maximum size is 2MB.'}, 400

    # Generate unique filename
    original_name = secure_filename(file.filename.rsplit('.', 1)[0])
    timestamp = int(time.time())
    new_filename = f"{original_name}_{timestamp}.{ext}"

    # Save to uploads/images/ (separate from app assets, mounted as Railway volume in production)
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, new_filename)

    try:
        file.save(save_path)

        # Generate HTML snippet with Jinja2 url_for so it works in dev and production
        # When the template is rendered at send time, this becomes the correct full URL
        html_snippet = f'<img src="{{{{ url_for(\'template_image\', filename=\'{new_filename}\', _external=True) }}}}" width="600" alt="{original_name}" border="0" style="width: 100%; max-width: 600px; height: auto;">'

        image_url = url_for('template_image', filename=new_filename, _external=True)
        return {
            'success': True,
            'filename': new_filename,
            'url': image_url,
            'html_snippet': html_snippet,
            'data': [image_url]  # GrapesJS asset manager expected format
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


@app.route('/template/images/<filename>')
def template_image(filename):
    """
    Serve uploaded images from uploads/images/ directory

    Used for images uploaded via the template editor.
    In production, this folder is mounted as a Railway volume for persistence.
    """
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        return "Invalid filename", 400

    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'images')
    image_path = os.path.join(images_dir, safe_filename)

    if not os.path.exists(image_path):
        return "Image not found", 404

    # Determine content type
    ext = safe_filename.rsplit('.', 1)[-1].lower()
    content_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif'
    }
    content_type = content_types.get(ext, 'application/octet-stream')

    with open(image_path, 'rb') as f:
        response = make_response(f.read())
        response.headers['Content-Type'] = content_type
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response


# ── Visual Template Designer Routes ──────────────────────────────
# CRC: crc-DesignerAPI.md | CRC: crc-GrapesDesigner.md


@app.route('/template/designer/<path:filename>')
@auth.login_required
def template_designer(filename):
    """
    Visual drag-and-drop template designer using GrapesJS

    Seq: seq-designer-load.md
    UI: ui-template-designer.md
    """
    import json

    # Get list of existing uploaded images for asset manager
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'images')
    existing_images = []
    if os.path.exists(images_dir):
        for img_file in sorted(os.listdir(images_dir)):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                existing_images.append(
                    url_for('template_image', filename=img_file, _external=True)
                )

    # Handle new template creation with starter
    if filename == 'new':
        template_name = request.args.get('name', '')
        starter = request.args.get('starter', 'basic-announcement')

        # Load starter HTML for the visual designer
        raw_html = get_starter_html(starter)
        return render_template('template_designer.html',
                             filename=template_name,
                             project_json=None,
                             raw_html=raw_html,
                             existing_images=existing_images)

    # Existing template - resolve path
    template_path, is_user_template = get_template_path(filename)
    if not os.path.exists(template_path):
        flash('Template not found', 'error')
        return redirect('/templates')

    # Check for sidecar JSON
    sidecar_path = get_sidecar_path(template_path)
    project_json = None
    raw_html = None

    if os.path.exists(sidecar_path):
        with open(sidecar_path, 'r', encoding='utf-8') as f:
            project_json = json.load(f)
    else:
        with open(template_path, 'r', encoding='utf-8') as f:
            raw_html = f.read()

    return render_template('template_designer.html',
                         filename=filename,
                         project_json=project_json,
                         raw_html=raw_html,
                         existing_images=existing_images)


@app.route('/api/template/save-design', methods=['POST'])
@auth.login_required
def api_template_save_design():
    """
    Save template from visual designer: JSON sidecar + inlined HTML

    Seq: seq-designer-save.md
    """
    import json
    from backend.services.template_processor import TemplateProcessor

    data = request.get_json()
    if not data:
        return {'success': False, 'error': 'No data provided'}, 400

    filename = data.get('filename', '')
    html_content = data.get('html', '')
    project_data = data.get('project_data', {})

    if not filename or not html_content:
        return {'success': False, 'error': 'Filename and HTML are required'}, 400

    # GrapesJS gjs-get-inlined-html exports body content only (no DOCTYPE/html/head/body).
    # Wrap in a proper email document structure if missing.
    if '<!doctype' not in html_content.lower() and '<html' not in html_content.lower():
        html_content = ('<!DOCTYPE html>\n<html>\n<head>\n'
                        '<meta charset="UTF-8">\n'
                        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                        '</head>\n<body>\n'
                        + html_content +
                        '\n</body>\n</html>')

    # Validate the exported HTML
    processor = TemplateProcessor()
    report = processor.validate(html_content)

    report_dict = {
        'is_valid': report.is_valid,
        'errors': report.errors,
        'warnings': report.warnings,
        'info': report.info
    }

    # Block save if required elements are missing
    if not report.is_valid:
        return {
            'success': False,
            'report': report_dict,
            'error': 'Template has validation errors'
        }

    # Resolve file path - use get_template_path for existing templates,
    # user templates (user: prefix or no path separator) go to uploads/templates/
    if filename.startswith('user:') or '/' not in filename:
        safe_name = filename[5:] if filename.startswith('user:') else filename
        if not safe_name.endswith('.html'):
            safe_name += '.html'
        user_templates_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'uploads', 'templates'
        )
        os.makedirs(user_templates_dir, exist_ok=True)
        template_path = os.path.join(user_templates_dir, secure_filename(safe_name))
    else:
        template_path, _ = get_template_path(filename)

    # Save HTML file
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Save sidecar JSON for re-editing
        sidecar_path = get_sidecar_path(template_path)
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f)

        return {
            'success': True,
            'report': report_dict
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


def get_starter_html(starter_name):
    """
    Get starter template HTML for the visual designer.

    Returns table-based email HTML that GrapesJS can parse via setComponents().
    Each starter provides a different layout so the user isn't starting from scratch.

    CRC: crc-CustomBlocks.md
    """
    # Build absolute image URLs so they work in email clients
    logo_url = url_for('static', filename='images/FNFWebLogo200x50.png', _external=True)
    hero_url = url_for('static', filename='images/FNFFront600x300.png', _external=True)

    # Shared preheader (hidden preview text) used by all starters
    preheader = (
        '<div style="display:none;font-size:1px;line-height:1px;max-height:0px;max-width:0px;'
        'opacity:0;overflow:hidden;mso-hide:all;font-family: sans-serif;">'
        'Preview text that shows in the inbox before opening the email. Edit this!'
        '</div>'
    )

    # Shared compliance footer used by all starters
    footer = (
        '<table cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px;">'
        '<tr><td style="padding: 30px 10px; font-family: sans-serif; font-size: 12px; line-height: 18px; text-align: center; color: #888888;">'
        '<p style="margin: 0 0 10px 0;">Fric &amp; Frac<br>1700 West 39th St. Kansas City, MO 64111</p>'
        '<p style="margin: 0;">'
        '<a href="{{ unsubscribe_link }}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>'
        ' &nbsp;|&nbsp; '
        '<a href="https://fricandfrac.net/privacy/" style="color: #888888; text-decoration: underline;">Privacy Policy</a>'
        '</p></td></tr></table>'
    )

    if starter_name == 'special-offer':
        return (
            preheader +
            '<table cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px; background: #ffffff;">'
            '<!-- Header -->'
            '<tr><td style="padding: 20px 0; text-align: center;">'
            '<img src="' + logo_url + '" width="200" alt="Logo" border="0">'
            '</td></tr>'
            '<!-- Hero Image -->'
            '<tr><td align="center">'
            '<img src="' + hero_url + '" width="600" alt="Special Offer" border="0" style="width: 100%; max-width: 600px; height: auto;">'
            '</td></tr>'
            '<!-- Offer Text -->'
            '<tr><td style="padding: 30px 20px; text-align: center; font-family: sans-serif;">'
            '<h1 style="color: #2c3e50; font-size: 28px; margin: 0 0 15px 0;">Special Offer for [[CUSTOMER_NAME]]!</h1>'
            '<p style="color: #555555; font-size: 18px; line-height: 1.6; margin: 0 0 20px 0;">Your exclusive deal details go here. Make it compelling!</p>'
            '</td></tr>'
            '<!-- QR Code Section -->'
            '<tr><td style="padding: 20px; text-align: center; font-family: sans-serif;">'
            '<!-- QR_CODE_SECTION -->'
            '<p style="color: #888888; font-size: 14px;">[QR Code will appear here when campaign is sent]</p>'
            '</td></tr>'
            '</table>'
            + footer
        )

    elif starter_name == 'newsletter':
        return (
            preheader +
            '<table cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px; background: #ffffff;">'
            '<!-- Header -->'
            '<tr><td style="padding: 20px 0; text-align: center;">'
            '<img src="' + logo_url + '" width="200" alt="Logo" border="0">'
            '</td></tr>'
            '<!-- Title -->'
            '<tr><td style="padding: 20px 20px 10px 20px; text-align: center; font-family: sans-serif;">'
            '<h1 style="color: #2c3e50; font-size: 24px; margin: 0;">Weekly Newsletter</h1>'
            '<p style="color: #888888; font-size: 14px; margin: 5px 0 0 0;">Hello, [[CUSTOMER_NAME]]!</p>'
            '</td></tr>'
            '<!-- Two Column Section -->'
            '<tr><td style="padding: 10px 20px;">'
            '<table cellspacing="0" cellpadding="0" border="0" width="100%">'
            '<tr>'
            '<td valign="top" width="48%" style="padding-right: 2%; font-family: sans-serif;">'
            '<h2 style="color: #2c3e50; font-size: 18px; margin: 0 0 10px 0;">Section One</h2>'
            '<p style="color: #555555; font-size: 14px; line-height: 1.5; margin: 0;">First column content goes here. Share news, updates, or featured items.</p>'
            '</td>'
            '<td valign="top" width="48%" style="padding-left: 2%; font-family: sans-serif;">'
            '<h2 style="color: #2c3e50; font-size: 18px; margin: 0 0 10px 0;">Section Two</h2>'
            '<p style="color: #555555; font-size: 14px; line-height: 1.5; margin: 0;">Second column content goes here. Add more details or a different topic.</p>'
            '</td>'
            '</tr></table>'
            '</td></tr>'
            '<!-- Divider -->'
            '<tr><td style="padding: 10px 20px;">'
            '<hr style="border: none; border-top: 1px solid #e5e7eb; margin: 0;">'
            '</td></tr>'
            '<!-- Full Width Text -->'
            '<tr><td style="padding: 10px 20px 30px 20px; font-family: sans-serif;">'
            '<p style="color: #555555; font-size: 14px; line-height: 1.6; margin: 0;">Additional content area. Use this for announcements, upcoming events, or any full-width message.</p>'
            '</td></tr>'
            '</table>'
            + footer
        )

    else:  # basic-announcement (default)
        return (
            preheader +
            '<table cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px; background: #ffffff;">'
            '<!-- Header -->'
            '<tr><td style="padding: 20px 0; text-align: center;">'
            '<img src="' + logo_url + '" width="200" alt="Logo" border="0">'
            '</td></tr>'
            '<!-- Content -->'
            '<tr><td style="padding: 30px 20px; text-align: center; font-family: sans-serif;">'
            '<h1 style="color: #2c3e50; font-size: 28px; margin: 0 0 20px 0;">Hello, [[CUSTOMER_NAME]]!</h1>'
            '<p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">Your announcement message goes here. Keep it clear and engaging.</p>'
            '<p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">Add more details as needed to tell your story.</p>'
            '<!-- CTA Button -->'
            '<table cellspacing="0" cellpadding="0" border="0" align="center">'
            '<tr><td class="button-td" style="border-radius: 4px; background: #2563eb;">'
            '<a class="button-a" href="#" style="background: #2563eb; border: 15px solid #2563eb; font-family: sans-serif; font-size: 14px; line-height: 1.1; text-align: center; text-decoration: none; display: block; border-radius: 4px; font-weight: bold;">'
            '<span class="button-link" style="color: #ffffff;">Learn More</span>'
            '</a></td></tr></table>'
            '</td></tr>'
            '</table>'
            + footer
        )


def get_sidecar_path(template_path):
    """Get the GrapesJS sidecar JSON path for a template HTML file"""
    return template_path.rsplit('.html', 1)[0] + '.grapes.json'


def get_template_path(filename):
    """
    Resolve template filename to full path

    Handles both bundled templates (templates/email/) and user templates (uploads/templates/)
    User templates are prefixed with 'user:'

    Returns: (full_path, is_user_template)
    """
    if filename.startswith('user:'):
        # User-created template in uploads/templates/
        actual_filename = filename[5:]  # Remove 'user:' prefix
        safe_filename = secure_filename(actual_filename)
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'templates', safe_filename)
        return path, True
    else:
        # Bundled template in templates/email/
        safe_filename = secure_filename(filename)
        path = os.path.join(app.template_folder, 'email', safe_filename)
        return path, False


@app.route('/template/import', methods=['GET', 'POST'])
@auth.login_required
def template_import():
    """
    Import wizard for email templates

    Seq: seq-template-import.md
    UI: ui-template-import.md
    """
    from backend.services.template_processor import TemplateProcessor

    processor = TemplateProcessor()

    if request.method == 'POST':
        step = request.form.get('step', '1')

        if step == '1':
            # Step 1: Receive HTML (file upload or paste)
            html_content = ''

            if 'htmlfile' in request.files and request.files['htmlfile'].filename:
                file = request.files['htmlfile']
                if file.filename.endswith('.html') or file.filename.endswith('.htm'):
                    html_content = file.read().decode('utf-8')
                else:
                    flash('Please upload an HTML file (.html or .htm)', 'error')
                    return render_template('template_import.html', step=1)
            else:
                html_content = request.form.get('html_paste', '')

            if not html_content.strip():
                flash('Please upload a file or paste HTML code', 'error')
                return render_template('template_import.html', step=1)

            # Process the HTML and get report
            processed_html, report = processor.process_all(html_content)

            return render_template('template_import.html',
                                 step=2,
                                 original_html=html_content,
                                 processed_html=processed_html,
                                 report=report)

        elif step == '2':
            # Step 2: Review and configure
            processed_html = request.form.get('processed_html', '')
            template_name = request.form.get('template_name', '').strip()

            if not template_name:
                flash('Template name is required', 'error')
                report = processor.validate(processed_html)
                return render_template('template_import.html',
                                     step=2,
                                     processed_html=processed_html,
                                     report=report)

            # Sanitize filename
            safe_name = secure_filename(template_name.lower().replace(' ', '_'))
            if not safe_name.endswith('.html'):
                safe_name += '.html'

            # Check if template already exists
            email_dir = os.path.join(app.template_folder, 'email')
            template_path = os.path.join(email_dir, safe_name)

            if os.path.exists(template_path):
                flash(f'Template "{safe_name}" already exists. Please choose a different name.', 'error')
                report = processor.validate(processed_html)
                return render_template('template_import.html',
                                     step=2,
                                     processed_html=processed_html,
                                     report=report,
                                     template_name=template_name)

            # Final validation before save
            report = processor.validate(processed_html)

            return render_template('template_import.html',
                                 step=3,
                                 processed_html=processed_html,
                                 template_name=safe_name,
                                 report=report)

        elif step == '3':
            # Step 3: Save template
            processed_html = request.form.get('processed_html', '')
            template_name = request.form.get('template_name', '')

            if not template_name or not processed_html:
                flash('Missing template data', 'error')
                return redirect('/template/import')

            # Save to templates/email/
            email_dir = os.path.join(app.template_folder, 'email')
            os.makedirs(email_dir, exist_ok=True)
            template_path = os.path.join(email_dir, template_name)

            try:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(processed_html)

                flash(f'Template "{template_name}" imported successfully!', 'success')
                return redirect('/templates')
            except Exception as e:
                flash(f'Error saving template: {str(e)}', 'error')
                return redirect('/template/import')

    # GET request - show step 1
    return render_template('template_import.html', step=1)


@app.route('/template/edit/<path:filename>', methods=['GET', 'POST'])
@auth.login_required
def template_edit(filename):
    """
    Edit an existing email template

    Handles both bundled templates and user-created templates (prefixed with 'user:')

    UI: ui-template-edit.md
    """
    from backend.services.template_processor import TemplateProcessor

    template_path, is_user_template = get_template_path(filename)

    if not os.path.exists(template_path):
        flash('Template not found', 'error')
        return redirect('/templates')

    # Extract just the filename for display
    display_filename = filename[5:] if filename.startswith('user:') else filename

    processor = TemplateProcessor()

    if request.method == 'POST':
        action = request.form.get('action', 'save')
        html_content = request.form.get('html_content', '')

        if action == 'validate':
            report = processor.validate(html_content)
            return render_template('template_edit.html',
                                 filename=display_filename,
                                 route_filename=filename,
                                 html_content=html_content,
                                 report=report)

        elif action == 'save':
            try:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                flash(f'Template "{display_filename}" saved successfully!', 'success')
                return redirect('/templates')
            except Exception as e:
                flash(f'Error saving template: {str(e)}', 'error')
                report = processor.validate(html_content)
                return render_template('template_edit.html',
                                     filename=display_filename,
                                     route_filename=filename,
                                     html_content=html_content,
                                     report=report)

        elif action == 'test':
            test_email = request.form.get('test_email', '')
            if not test_email:
                flash('Test email address is required', 'error')
                report = processor.validate(html_content)
                return render_template('template_edit.html',
                                     filename=display_filename,
                                     html_content=html_content,
                                     report=report)

            try:
                # Render with sample data
                from backend.config import Config

                template_vars = {
                    'unsubscribe_link': '#test-unsubscribe',
                    'logo_url': url_for('static', filename='images/FNFWebLogo200x50.png', _external=True),
                    'hero_image_url': url_for('static', filename='images/FNFFront600x300.png', _external=True)
                }

                rendered = render_template_string(html_content, **template_vars)
                rendered = rendered.replace('[[CUSTOMER_NAME]]', 'Test Customer')

                result = send_email(test_email, 'Test Customer', f'Template Test: {display_filename}', rendered)

                if result.get('success'):
                    flash(f'Test email sent to {test_email}!', 'success')
                else:
                    flash(f'Failed to send test: {result.get("error", "Unknown error")}', 'error')

            except Exception as e:
                flash(f'Error sending test: {str(e)}', 'error')

            report = processor.validate(html_content)
            return render_template('template_edit.html',
                                 filename=display_filename,
                                 route_filename=filename,
                                 html_content=html_content,
                                 report=report)

    # GET request - load template
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    report = processor.validate(html_content)

    return render_template('template_edit.html',
                         filename=display_filename,
                         route_filename=filename,
                         html_content=html_content,
                         report=report)


@app.route('/template/preview/<path:filename>')
@auth.login_required
def template_preview(filename):
    """Preview a template with sample data"""
    template_path, is_user_template = get_template_path(filename)

    if not os.path.exists(template_path):
        return "Template not found", 404

    # Render with sample data
    template_vars = {
        'unsubscribe_link': '#test-unsubscribe',
        'logo_url': url_for('static', filename='images/FNFWebLogo200x50.png', _external=True),
        'hero_image_url': url_for('static', filename='images/FNFFront600x300.png', _external=True)
    }

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        rendered = render_template_string(html_content, **template_vars)
        rendered = rendered.replace('[[CUSTOMER_NAME]]', 'Sample Customer')
        rendered = rendered.replace('<!-- QR_CODE_SECTION -->', '''
            <table cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 20px auto;">
              <tr>
                <td style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
                  <p style="margin: 0 0 10px 0; font-weight: bold; color: #d32f2f;">SHOW THIS QR CODE TO REDEEM:</p>
                  <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=SAMPLE" width="200" height="200" alt="Sample QR Code" style="display: block; margin: 0 auto;">
                  <p style="margin: 10px 0 0 0; font-size: 11px; color: #888;">Sample QR code for preview.</p>
                </td>
              </tr>
            </table>
        ''')

        return rendered
    except Exception as e:
        return f"Error rendering template: {str(e)}", 500


@app.route('/template/duplicate/<path:filename>', methods=['POST'])
@auth.login_required
def template_duplicate(filename):
    """Duplicate a template as a new user template"""
    import shutil

    template_path, is_user_template = get_template_path(filename)
    if not os.path.exists(template_path):
        flash('Template not found', 'error')
        return redirect('/templates')

    # Generate a unique name: original_copy, original_copy_2, etc.
    base_name = filename[5:] if filename.startswith('user:') else filename
    if base_name.startswith('email/'):
        base_name = base_name[6:]
    name_part = base_name.replace('.html', '')

    user_templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'templates')
    os.makedirs(user_templates_dir, exist_ok=True)

    copy_name = f'{name_part}_copy.html'
    counter = 2
    while os.path.exists(os.path.join(user_templates_dir, copy_name)):
        copy_name = f'{name_part}_copy_{counter}.html'
        counter += 1

    dest_path = os.path.join(user_templates_dir, copy_name)

    try:
        shutil.copy2(template_path, dest_path)
        # Also copy sidecar JSON if it exists
        sidecar_path = get_sidecar_path(template_path)
        if os.path.exists(sidecar_path):
            shutil.copy2(sidecar_path, get_sidecar_path(dest_path))
        flash(f'Template duplicated as "{copy_name}"', 'success')
    except Exception as e:
        flash(f'Error duplicating template: {str(e)}', 'error')

    return redirect('/templates')


@app.route('/template/delete/<path:filename>', methods=['POST'])
@auth.login_required
def template_delete(filename):
    """Delete a template (only user-created templates can be deleted in production)"""
    template_path, is_user_template = get_template_path(filename)
    display_filename = filename[5:] if filename.startswith('user:') else filename

    if not os.path.exists(template_path):
        flash('Template not found', 'error')
        return redirect('/templates')

    try:
        os.remove(template_path)
        # Also delete sidecar JSON if it exists
        sidecar_path = get_sidecar_path(template_path)
        if os.path.exists(sidecar_path):
            os.remove(sidecar_path)
        flash(f'Template "{display_filename}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting template: {str(e)}', 'error')

    return redirect('/templates')


@app.route('/api/public/signup', methods=['POST', 'OPTIONS'])
def api_public_signup():
    """
    Public API endpoint for external SMS/email signups (CORS-enabled)

    Used by external signup forms hosted on fricandfrac.net
    Accepts JSON payload and returns JSON response.

    Required fields:
    - phone: Phone number (will be normalized to E.164)

    Optional fields:
    - email: Email address
    - name: Customer name
    - subscribe_email: Boolean (default False)
    - subscribe_sms: Boolean (default True)
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Get JSON data
    data = request.get_json() or {}

    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    subscribe_sms = data.get('subscribe_sms', True)
    subscribe_email = data.get('subscribe_email', False)

    # Phone is required for SMS signup
    if not phone:
        response = make_response({'success': False, 'error': 'Phone number is required'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400

    # Normalize phone number
    normalized_phone = format_phone_number(phone)
    if not normalized_phone or not validate_phone_number(normalized_phone):
        response = make_response({'success': False, 'error': 'Invalid phone number format'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400

    # Generate placeholder email if not provided (required by database)
    # Format: sms_<hash>@sms.placeholder
    import hashlib as hl
    use_placeholder_email = False
    if not email:
        phone_hash = hl.sha256(normalized_phone.encode()).hexdigest()[:8]
        email = f"sms_{phone_hash}@sms.placeholder"
        subscribe_email = False  # Don't try to email placeholder addresses
        use_placeholder_email = True

    db = get_db()
    try:
        # Check if customer exists by phone first (primary for SMS signups)
        existing = None
        if normalized_phone:
            existing = Customer.find_by_phone(db, normalized_phone)
        if not existing and not use_placeholder_email:
            existing = Customer.find_by_email(db, email)

        if existing:
            # Update existing customer
            if name:
                existing.name = name
            if normalized_phone:
                existing.phone = normalized_phone
            if not use_placeholder_email and email:
                existing.email = email
            if subscribe_sms and not existing.sms_subscribed:
                existing.sms_subscribed = True
                existing.sms_opted_in_date = datetime.now()
            if subscribe_email and not existing.subscribed:
                existing.subscribed = True
                existing.opted_in_date = datetime.now()
            existing.updated_at = datetime.now()
            db.commit()

            response = make_response({
                'success': True,
                'message': 'Subscription updated successfully!',
                'is_new': False
            })
        else:
            # Create new customer - email is guaranteed to have a value now
            customer = Customer(
                email=email,
                phone=normalized_phone,
                name=name if name else None,
                subscribed=subscribe_email,
                opted_in_date=datetime.now() if subscribe_email else None,
                sms_subscribed=subscribe_sms,
                sms_opted_in_date=datetime.now() if subscribe_sms else None,
                segments='website-signup'
            )
            db.add(customer)
            db.commit()

            response = make_response({
                'success': True,
                'message': 'Thank you for signing up!',
                'is_new': True
            })

        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as e:
        db.rollback()
        response = make_response({'success': False, 'error': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500
    finally:
        db.close()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Public signup form for email and SMS marketing

    GET: Display the signup form
    POST: Process the signup
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        name = request.form.get('name', '').strip()
        subscribe_email = request.form.get('subscribe_email') == 'on'
        subscribe_sms = request.form.get('subscribe_sms') == 'on'

        # Validation
        if not email:
            return render_template('signup.html',
                                 error='Email address is required.',
                                 email=email,
                                 phone=phone,
                                 name=name)

        # Normalize phone number if provided
        normalized_phone = None
        if phone:
            from backend.sms_service import format_phone_number
            normalized_phone = format_phone_number(phone)
            if not normalized_phone:
                return render_template('signup.html',
                                     error='Invalid phone number format. Please use a valid US phone number.',
                                     email=email,
                                     phone=phone,
                                     name=name)

        db = get_db()
        try:
            # Check if customer already exists by email
            existing_customer = None
            if email:
                existing_customer = Customer.find_by_email(db, email)

            if existing_customer:
                # Update existing customer
                if name:
                    existing_customer.name = name
                if normalized_phone:
                    existing_customer.phone = normalized_phone
                if subscribe_email:
                    existing_customer.subscribed = True
                    existing_customer.opted_in_date = datetime.now()
                if subscribe_sms and normalized_phone:
                    existing_customer.sms_subscribed = True
                    existing_customer.sms_opted_in_date = datetime.now()
                db.commit()
                return render_template('signup.html',
                                     success=True,
                                     message='Thank you! Your subscription has been updated.')
            else:
                # Create new customer
                customer = Customer(
                    email=email,
                    phone=normalized_phone,
                    name=name if name else None,
                    subscribed=subscribe_email,
                    sms_subscribed=subscribe_sms if normalized_phone else False
                )
                if subscribe_email:
                    customer.opted_in_date = datetime.now()
                if subscribe_sms and normalized_phone:
                    customer.sms_opted_in_date = datetime.now()

                db.add(customer)
                db.commit()

                return render_template('signup.html',
                                     success=True,
                                     message='Thank you for signing up! You\'ll receive our latest news and special offers.')
        except Exception as e:
            return render_template('signup.html',
                                 error=f'An error occurred: {str(e)}',
                                 email=email,
                                 phone=phone,
                                 name=name)
        finally:
            db.close()

    # GET request - show form
    return render_template('signup.html')

# =============================================================================
# QR Code Redemption Routes
# CRC: crc-RedemptionService.md
# Seq: seq-qr-redemption.md
# =============================================================================

# Staff cookie settings
STAFF_COOKIE_NAME = 'staff_token'
STAFF_COOKIE_MAX_AGE = 90 * 24 * 60 * 60  # 90 days in seconds


def generate_staff_token():
    """Generate a secure staff authentication token"""
    import secrets
    return secrets.token_urlsafe(32)


def check_staff_cookie():
    """
    Check if valid staff cookie exists.
    Returns True if authenticated, False otherwise.
    """
    token = request.cookies.get(STAFF_COOKIE_NAME)
    if not token:
        return False
    # For simplicity, any non-empty token is valid
    # In production, you might want to store valid tokens in DB/Redis
    return len(token) > 20


def set_staff_cookie(response):
    """
    Set or refresh the staff authentication cookie with sliding expiration.
    """
    token = request.cookies.get(STAFF_COOKIE_NAME) or generate_staff_token()
    response.set_cookie(
        STAFF_COOKIE_NAME,
        token,
        max_age=STAFF_COOKIE_MAX_AGE,
        httponly=True,
        samesite='Lax',
        secure=request.is_secure  # Use secure flag in production (HTTPS)
    )
    return response


def staff_auth_required(f):
    """
    Decorator for routes that require staff authentication via cookie.
    Redirects to login if no valid cookie, refreshes cookie if valid.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_staff_cookie():
            return redirect(url_for('staff_login', next=request.url))
        # Execute the route
        response = f(*args, **kwargs)
        # Refresh cookie (sliding expiration)
        if isinstance(response, str):
            response = make_response(response)
        return set_staff_cookie(response)
    return decorated


def staff_api_auth_required(f):
    """
    Decorator for API routes - returns 401 JSON instead of redirect.
    Also refreshes cookie on successful auth.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_staff_cookie():
            return {'error': 'Authentication required', 'status': 'unauthorized'}, 401
        response = f(*args, **kwargs)
        # If response is a dict, convert to JSON response so we can set cookie
        if isinstance(response, dict):
            response = make_response(response)
        return set_staff_cookie(response)
    return decorated


@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    """
    Staff login page for QR scanner.
    Sets a long-lived cookie on successful login.

    Accepts either:
    - STAFF_USERNAME / STAFF_PASSWORD (scanner-only access)
    - ADMIN_USERNAME / ADMIN_PASSWORD (full access, fallback)
    """
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Check staff credentials first (scanner-only access)
        staff_user = os.getenv('STAFF_USERNAME')
        staff_pass = os.getenv('STAFF_PASSWORD')

        # Fall back to admin credentials if staff not configured
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', '')

        is_valid_staff = staff_user and staff_pass and username == staff_user and password == staff_pass
        is_valid_admin = admin_pass and username == admin_user and password == admin_pass

        if is_valid_staff or is_valid_admin:
            # Create response with redirect
            next_url = request.args.get('next', url_for('staff_redeem'))
            response = make_response(redirect(next_url))
            # Set the staff cookie
            response = set_staff_cookie(response)
            return response
        else:
            error = 'Invalid username or password'

    return render_template('staff_login.html', error=error)


@app.route('/staff/logout')
def staff_logout():
    """Log out staff by clearing the cookie"""
    response = make_response(redirect(url_for('staff_login')))
    response.delete_cookie(STAFF_COOKIE_NAME)
    return response


@app.route('/redeem/<token>')
def redeem_landing(token):
    """
    Public QR code landing page - shows validity without redeeming

    This is what customers see when they scan their QR code.
    Staff will use /staff/redeem to actually perform redemptions.
    """
    from backend.services.redemption_service import validate as validate_qr

    db = get_db()
    try:
        result = validate_qr(db, token)
        return render_template('redeem_result.html',
                             result=result,
                             token=token)
    finally:
        db.close()


@app.route('/staff/redeem')
@staff_auth_required
def staff_redeem():
    """
    Staff scanner interface with camera QR scanning and manual entry

    Mobile-friendly page for staff to scan and redeem customer QR codes.
    Uses cookie-based auth with 90-day sliding expiration.
    """
    return render_template('staff_redeem.html')


@app.route('/api/redeem/<token>', methods=['POST'])
@staff_api_auth_required
def api_redeem(token):
    """
    API endpoint to perform QR code redemption

    Called by staff scanner interface after validation.

    Returns JSON with redemption result.
    """
    from backend.services.redemption_service import redeem as redeem_qr

    db = get_db()
    try:
        # Get optional metadata
        data = request.get_json() or {}
        redeemed_by = data.get('redeemed_by', 'staff')
        redemption_method = data.get('method', 'scan')

        # Get device/IP info for fraud detection
        device_info = request.headers.get('User-Agent', '')[:500]
        ip_address = request.remote_addr

        result = redeem_qr(
            db,
            token,
            redeemed_by=redeemed_by,
            redemption_method=redemption_method,
            device_info=device_info,
            ip_address=ip_address
        )

        return result.to_dict()
    finally:
        db.close()


@app.route('/api/validate/<token>')
@staff_api_auth_required
def api_validate(token):
    """
    API endpoint to validate a QR code without redeeming

    Used by staff scanner to show validity before confirming redemption.
    """
    from backend.services.redemption_service import validate as validate_qr

    db = get_db()
    try:
        result = validate_qr(db, token)
        return result.to_dict()
    finally:
        db.close()


@app.route('/analytics/redemptions')
@auth.login_required
def redemption_analytics():
    """
    Redemption analytics dashboard

    Shows redemption rates, recent redemptions, peak hours, etc.
    """
    from backend.services.redemption_service import (
        get_redemption_stats,
        get_campaign_redemption_stats,
        get_recent_redemptions,
        get_hourly_redemptions
    )

    db = get_db()
    try:
        # Get overall stats
        overall_stats = get_redemption_stats(db)

        # Get per-campaign stats
        campaign_stats = get_campaign_redemption_stats(db)

        # Get recent redemptions
        recent_redemptions = get_recent_redemptions(db, limit=20)

        # Get hourly distribution
        hourly_data = get_hourly_redemptions(db, days=30)

        return render_template('redemption_analytics.html',
                             overall_stats=overall_stats,
                             campaign_stats=campaign_stats,
                             recent_redemptions=recent_redemptions,
                             hourly_data=hourly_data)
    finally:
        db.close()


@app.route('/analytics/redemptions/<int:campaign_id>')
@auth.login_required
def campaign_redemption_detail(campaign_id):
    """
    Detailed redemption list for a specific campaign

    Shows all customers who redeemed, with timestamps and method.
    """
    from backend.services.redemption_service import (
        get_redemption_stats,
        get_recent_redemptions
    )

    db = get_db()
    try:
        # Get campaign info
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            return "Campaign not found", 404

        # Get stats for this campaign
        stats = get_redemption_stats(db, campaign_id=campaign_id)

        # Get all redemptions for this campaign (not just recent)
        redemptions = get_recent_redemptions(db, limit=1000, campaign_id=campaign_id)

        return render_template_string('''
{% extends "base.html" %}

{% block title %}{{ campaign.name }} - Redemptions{% endblock %}

{% block content %}
<div style="margin-bottom: 1rem;">
    <a href="/analytics/redemptions" style="color: #2563eb;">&larr; Back to Analytics</a>
</div>

<h1>{{ campaign.name }}</h1>
<p style="color: #6b7280;">
    {% if campaign.sent_date %}Sent {{ campaign.sent_date.strftime('%B %d, %Y') }}{% endif %}
    {% if campaign.deal_description %} &bull; {{ campaign.deal_description }}{% endif %}
</p>

<!-- Stats -->
<div class="stats" style="margin-bottom: 2rem;">
    <div class="stat-card">
        <h3>{{ stats.total_codes }}</h3>
        <p>QR Codes Sent</p>
    </div>
    <div class="stat-card" style="border-left-color: #10b981;">
        <h3>{{ stats.redeemed_codes }}</h3>
        <p>Unique Redemptions</p>
    </div>
    <div class="stat-card" style="border-left-color: #f59e0b;">
        <h3>{{ stats.redemption_rate }}%</h3>
        <p>Redemption Rate</p>
    </div>
</div>

<!-- Redemptions List -->
<div class="card">
    <h2>Redemptions ({{ redemptions|length }})</h2>
    {% if redemptions %}
    <table>
        <thead>
            <tr>
                <th>Date & Time</th>
                <th>Customer</th>
                <th>Email</th>
                <th>Method</th>
                <th>Staff</th>
            </tr>
        </thead>
        <tbody>
            {% for r in redemptions %}
            <tr>
                <td>
                    {{ r.redeemed_at.strftime('%b %d, %Y') }}
                    <br><small style="color: #6b7280;">{{ r.redeemed_at.strftime('%I:%M %p') }}</small>
                </td>
                <td><strong>{{ r.customer_name }}</strong></td>
                <td><small>{{ r.customer_email }}</small></td>
                <td>
                    <span class="badge {% if r.redemption_method == 'scan' %}badge-sent{% else %}badge-scheduled{% endif %}">
                        {{ r.redemption_method }}
                    </span>
                </td>
                <td>{{ r.redeemed_by or '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p style="color: #6b7280; text-align: center; padding: 2rem;">No redemptions yet for this campaign.</p>
    {% endif %}
</div>
{% endblock %}
        ''', campaign=campaign, stats=stats, redemptions=redemptions)
    finally:
        db.close()


@app.route('/admin/stuck-campaigns')
@auth.login_required
def list_stuck_campaigns():
    """List campaigns stuck in 'sending' status"""
    db = get_db()
    try:
        stuck = db.query(Campaign).filter_by(status='sending').all()
        campaigns = []
        for c in stuck:
            # Get the send record for progress info
            send_record = db.query(CampaignSend).filter_by(
                campaign_id=c.id
            ).order_by(CampaignSend.started_at.desc()).first()

            campaigns.append({
                'id': c.id,
                'name': c.name,
                'has_qr_code': c.has_qr_code,
                'emails_sent': send_record.emails_sent if send_record else 0,
                'emails_failed': send_record.emails_failed if send_record else 0,
                'total_emails': send_record.total_emails if send_record else 0,
                'started_at': send_record.started_at.isoformat() if send_record and send_record.started_at else None
            })

        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Stuck Campaigns</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 0 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #f5f5f5; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #218838; }
        .progress { color: #666; }
        h1 { color: #333; }
        .none { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>Stuck Campaigns (status = 'sending')</h1>
    {% if campaigns %}
    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Progress</th>
            <th>Has QR</th>
            <th>Started</th>
            <th>Action</th>
        </tr>
        {% for c in campaigns %}
        <tr>
            <td>{{ c.id }}</td>
            <td>{{ c.name }}</td>
            <td class="progress">{{ c.emails_sent }}/{{ c.total_emails }} sent, {{ c.emails_failed }} failed</td>
            <td>{{ 'Yes' if c.has_qr_code else 'No' }}</td>
            <td>{{ c.started_at or 'Unknown' }}</td>
            <td>
                <form action="/admin/force-complete/{{ c.id }}" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-success" onclick="return confirm('Mark campaign as sent?')">Force Complete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p class="none">No stuck campaigns found.</p>
    {% endif %}
    <p><a href="/campaigns">Back to Campaigns</a></p>
</body>
</html>
        ''', campaigns=campaigns)
    finally:
        db.close()


@app.route('/admin/force-complete/<int:campaign_id>', methods=['POST'])
@auth.login_required
def force_complete_campaign(campaign_id):
    """Force a stuck campaign to 'sent' status"""
    db = get_db()
    try:
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        if not campaign:
            return "Campaign not found", 404

        if campaign.status != 'sending':
            return f"Campaign status is '{campaign.status}', not 'sending'", 400

        # Update campaign status
        campaign.status = 'sent'
        campaign.sent_date = campaign.sent_date or datetime.now()

        # Update the send record
        send_record = db.query(CampaignSend).filter_by(
            campaign_id=campaign_id
        ).order_by(CampaignSend.started_at.desc()).first()

        if send_record:
            send_record.status = 'completed'
            send_record.completed_at = datetime.now()

        db.commit()

        return redirect('/admin/stuck-campaigns')
    finally:
        db.close()


if __name__ == '__main__':
    # For development only - use proper WSGI server for production
    app.run(host='0.0.0.0', port=5001, debug=True)
