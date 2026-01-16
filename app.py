"""
Flask Application - Email/SMS Marketing Platform

CRC: crc-CampaignManager.md
Spec: phase-2-campaign-management.md
"""
from flask import Flask, render_template, request, redirect, url_for, flash, render_template_string
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from backend.database import init_db, get_db
from backend.models import Customer, Campaign, CampaignSend, QRCode
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
                          customer_name='Test Customer',
                          logo_url='/static/images/FNFWebLogo200x50.png',
                          hero_image_url='/static/images/FNFFront600x300.png',
                          unsubscribe_link='/unsubscribe?token=test123')

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
    html = html.replace('{{QR_CODE_DATA_URI}}', dummy_qr)

    return html

def get_available_templates():
    """
    Scan templates/email directory for available email templates

    CRC: crc-CampaignManager.md
    Sequence: seq-campaign-create.md
    """
    templates_dir = os.path.join(app.template_folder, 'email')
    templates = []

    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith('.html'):
                # Create friendly name from filename
                name = filename.replace('.html', '').replace('_', ' ').replace('-', ' ').title()
                templates.append({
                    'filename': f'email/{filename}',
                    'name': name
                })

    return sorted(templates, key=lambda x: x['name'])

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
                # Note: Don't include unsubscribe_link here - it will be added when sending
                template_vars = {
                    'customer_name': 'Sample Customer'
                }

                # Use base64 for development, external URLs for production
                if Config.is_development():
                    template_vars['logo_base64'] = ImageHandler.get_image_url('FNFWebLogo200x50.png').replace('data:image/png;base64,', '')
                    template_vars['hero_image_base64'] = ImageHandler.get_image_url('FNFFront600x300.png').replace('data:image/png;base64,', '')
                else:
                    template_vars['logo_url'] = url_for('static', filename='images/FNFWebLogo200x50.png', _external=True)
                    template_vars['hero_image_url'] = url_for('static', filename='images/FNFFront600x300.png', _external=True)

                html_content = render_template(template, **template_vars)

                # If QR codes enabled, inject QR placeholder HTML
                has_qr_code = request.form.get('has_qr_code') == 'on'
                if has_qr_code:
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
                    html_content = html_content.replace('<!-- QR_CODE_SECTION -->', qr_placeholder_html)
            except Exception as e:
                flash(f'Error rendering template: {str(e)}', 'error')
                return redirect('/campaign/new')

            # Create campaign
            has_qr_code = request.form.get('has_qr_code') == 'on'
            campaign = Campaign(
                name=name,
                subject=subject,
                template_name=template,
                html_content=html_content,
                has_qr_code=has_qr_code,
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
                            'customer_name': 'Test Customer',
                            'unsubscribe_link': '#test-unsubscribe'
                        }

                        personalized_html = render_template_string(
                            campaign.html_content,
                            **template_vars
                        )

                        # Generate real QR code for test if campaign has it enabled
                        # Replace the {{QR_CODE_DATA_URI}} placeholder with actual QR data
                        if campaign.has_qr_code:
                            from backend.config import Config
                            test_token = f"TEST-{campaign.id}-preview"
                            test_url = f"{Config.BASE_URL}/redeem/{test_token}"
                            qr_image = qr_generator.generate_qr_image(test_url)
                            qr_base64 = qr_generator.encode_base64(qr_image)
                            qr_data_uri = f"data:image/png;base64,{qr_base64}"
                            personalized_html = personalized_html.replace('{{QR_CODE_DATA_URI}}', qr_data_uri)

                        # Send test email
                        result = send_email(test_email, 'Test Customer', campaign.subject, personalized_html)

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

            # Re-render template if template changed OR QR setting changed
            if template != campaign.template_name or qr_setting_changed:
                try:
                    from backend.config import Config
                    from backend.image_handler import ImageHandler

                    # Build template variables
                    # Note: Don't include unsubscribe_link here - it will be added when sending
                    template_vars = {
                        'customer_name': 'Sample Customer'
                    }

                    # Use base64 for development, external URLs for production
                    if Config.is_development():
                        template_vars['logo_base64'] = ImageHandler.get_image_url('FNFWebLogo200x50.png').replace('data:image/png;base64,', '')
                        template_vars['hero_image_base64'] = ImageHandler.get_image_url('FNFFront600x300.png').replace('data:image/png;base64,', '')
                    else:
                        template_vars['logo_url'] = url_for('static', filename='images/FNFWebLogo200x50.png', _external=True)
                        template_vars['hero_image_url'] = url_for('static', filename='images/FNFFront600x300.png', _external=True)

                    # Use new template if changed, otherwise use existing
                    template_to_render = template if template != campaign.template_name else campaign.template_name
                    html_content = render_template(template_to_render, **template_vars)

                    # If QR codes enabled, inject QR placeholder HTML
                    if new_has_qr_code:
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

        return render_template('campaign_send_confirm.html',
                             campaign=campaign,
                             total_subscribers=total_subscribers,
                             email_only=email_only,
                             sms_only=sms_only,
                             both=both,
                             segments=segments)
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
                    'customer_name': 'Test Customer',
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

                    # If QR codes enabled, inject QR placeholder HTML and generate actual QR
                    if campaign.has_qr_code:
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
                        personalized_html = personalized_html.replace('<!-- QR_CODE_SECTION -->', qr_placeholder_html)

                        # Generate real QR code for test
                        test_token = f"TEST-{campaign.id}-{test_customer.id if test_customer else 'preview'}"
                        test_url = f"{Config.BASE_URL}/redeem/{test_token}"
                        qr_image = qr_generator.generate_qr_image(test_url)
                        qr_base64 = qr_generator.encode_base64(qr_image)
                        qr_data_uri = f"data:image/png;base64,{qr_base64}"
                        personalized_html = personalized_html.replace('{{QR_CODE_DATA_URI}}', qr_data_uri)

                    print(f"DEBUG: Template rendered successfully. HTML length: {len(personalized_html)}")
                    print(f"DEBUG: First 200 chars of HTML: {personalized_html[:200]}")
                except Exception as render_error:
                    print(f"ERROR: Template rendering failed: {str(render_error)}")
                    import traceback
                    traceback.print_exc()
                    raise

                # Send test email
                print("DEBUG: About to send email...")
                result = send_email(test_email, 'Test Customer', campaign.subject, personalized_html)
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

if __name__ == '__main__':
    # For development only - use proper WSGI server for production
    app.run(host='0.0.0.0', port=5001, debug=True)
