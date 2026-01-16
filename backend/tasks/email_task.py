"""
Email Queue Task - Background task for sending campaign emails

CRC: crc-EmailQueueTask.md
Seq: seq-email-process.md, seq-email-retry.md
"""
from backend.tasks.celery_app import celery_app
from backend.database import SessionLocal
from backend.models import Customer, Campaign, CampaignSend, EmailDelivery
from datetime import datetime
from backend.email_service import send_email
from backend.services.rate_limiter import RateLimiter
from backend.services import qr_generator
from backend.config import Config
from backend.image_handler import ImageHandler
from jinja2 import Template
import logging
import os

logger = logging.getLogger(__name__)


def get_db():
    """Get database session for task"""
    return SessionLocal()


def build_template_vars(db, customer, campaign, base_url):
    """
    Build template variables for email personalization

    Extracted from app.py lines 978-997 for reuse in async task

    Returns:
        dict with 'vars' (template variables) and 'qr_attachment' (optional CID attachment data)
    """
    # Extract first name for friendlier greeting
    first_name = customer.name.split()[0] if customer.name else 'Valued Customer'

    # Build unsubscribe link without Flask context
    unsubscribe_link = f"{base_url}/unsubscribe?email={customer.email}&token={customer.get_unsubscribe_token()}"

    template_vars = {
        'customer_name': first_name,
        'unsubscribe_link': unsubscribe_link
    }

    # Add image URLs based on environment
    if Config.is_development():
        template_vars['logo_base64'] = ImageHandler.get_image_url('FNFWebLogo200x50.png').replace('data:image/png;base64,', '')
        template_vars['hero_image_base64'] = ImageHandler.get_image_url('FNFFront600x300.png').replace('data:image/png;base64,', '')
    else:
        static_url = Config.STATIC_URL
        template_vars['logo_url'] = f"{static_url}/images/FNFWebLogo200x50.png"
        template_vars['hero_image_url'] = f"{static_url}/images/FNFFront600x300.png"

    # QR code attachment data (for CID approach)
    qr_attachment = None

    # QR code if campaign has it enabled
    if campaign.has_qr_code:
        try:
            # Check if QR code already exists for this customer/campaign
            existing_qr = qr_generator.get_existing_qr_code(db, campaign.id, customer.id)
            if existing_qr:
                # Regenerate image bytes from existing token
                qr_bytes = qr_generator.regenerate_bytes(existing_qr, base_url)
                logger.info(f"Reused existing QR code for customer {customer.id}")
            else:
                # Generate new QR code
                result = qr_generator.create_qr_code(db, campaign, customer, base_url)
                # Get bytes from the token we just created
                qr_bytes = qr_generator.generate_qr_image(f"{base_url}/redeem/{result['qr_code'].token}")

            # Create CID attachment data
            content_id = qr_generator.generate_content_id(campaign.id, customer.id)
            qr_attachment = {
                'content_id': content_id,
                'image_bytes': qr_bytes
            }
            # Store content_id in template_vars for HTML replacement
            template_vars['qr_content_id'] = content_id

        except Exception as e:
            logger.error(f"Failed to generate QR code for customer {customer.id}: {e}")
            # Continue without QR code rather than failing the email

    return {'vars': template_vars, 'qr_attachment': qr_attachment}


def update_send_progress(db, campaign_send_id, success, error=None):
    """Update CampaignSend progress record"""
    try:
        send_record = db.query(CampaignSend).filter_by(id=campaign_send_id).first()
        if send_record:
            if success:
                send_record.emails_sent += 1
            else:
                send_record.emails_failed += 1
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update send progress: {e}")
        db.rollback()


def get_or_create_delivery(db, campaign_id, customer_id, campaign_send_id=None):
    """Get existing delivery record or create new one"""
    delivery = db.query(EmailDelivery).filter_by(
        campaign_id=campaign_id,
        customer_id=customer_id
    ).first()

    if not delivery:
        delivery = EmailDelivery(
            campaign_id=campaign_id,
            customer_id=customer_id,
            campaign_send_id=campaign_send_id,
            status='queued'
        )
        db.add(delivery)
        db.commit()

    return delivery


def update_delivery_status(db, delivery, status, error_message=None):
    """Update delivery record status"""
    try:
        delivery.status = status
        if status == 'sent':
            delivery.sent_at = datetime.utcnow()
        if error_message:
            delivery.error_message = error_message
        db.commit()
    except Exception as e:
        logger.error(f"Failed to update delivery status: {e}")
        db.rollback()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=2,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    acks_late=True,
    name='backend.tasks.email_task.send_campaign_email'
)
def send_campaign_email(self, campaign_id, customer_id, campaign_send_id=None):
    """
    Send single email for a campaign

    Args:
        campaign_id: ID of campaign
        customer_id: ID of customer to send to
        campaign_send_id: Optional ID for progress tracking batch

    Returns:
        dict with success status and details
    """
    db = get_db()
    rate_limiter = RateLimiter()

    try:
        # Rate limit check - blocks if over limit
        rate_limiter.wait_if_needed(campaign_id, 'email')

        # Load campaign and customer
        campaign = db.query(Campaign).filter_by(id=campaign_id).first()
        customer = db.query(Customer).filter_by(id=customer_id).first()

        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return {'success': False, 'error': 'Campaign not found'}

        if not customer:
            logger.error(f"Customer {customer_id} not found")
            return {'success': False, 'error': 'Customer not found'}

        if not customer.subscribed:
            logger.info(f"Customer {customer_id} unsubscribed, skipping")
            if campaign_send_id:
                update_send_progress(db, campaign_send_id, success=False, error='Unsubscribed')
            return {'success': False, 'error': 'Customer unsubscribed', 'skipped': True}

        # Get or create delivery tracking record
        delivery = get_or_create_delivery(db, campaign_id, customer_id, campaign_send_id)

        # Check if already successfully sent (for resume scenarios)
        if delivery.status == 'sent':
            logger.info(f"Email already sent to customer {customer_id} for campaign {campaign_id}, skipping")
            return {'success': True, 'skipped': True, 'reason': 'already_sent'}

        # Build template variables (including QR code generation if enabled)
        base_url = Config.BASE_URL
        build_result = build_template_vars(db, customer, campaign, base_url)
        template_vars = build_result['vars']
        qr_attachment = build_result['qr_attachment']

        # Replace placeholders BEFORE Jinja2 rendering
        html_content = campaign.html_content
        inline_attachments = []

        # Replace customer name placeholder
        customer_name = template_vars.get('customer_name', 'Valued Customer')
        html_content = html_content.replace('[[CUSTOMER_NAME]]', customer_name)
        logger.info(f"Personalization: Replaced [[CUSTOMER_NAME]] with '{customer_name}'")

        logger.info(f"QR DEBUG: has_qr_code={campaign.has_qr_code}, qr_attachment={qr_attachment is not None}")
        if campaign.has_qr_code and qr_attachment:
            content_id = qr_attachment['content_id']
            cid_reference = f"cid:{content_id}"
            logger.info(f"QR DEBUG: Replacing [[QR_CODE_DATA_URI]] with {cid_reference}")
            placeholder_found = '[[QR_CODE_DATA_URI]]' in html_content
            logger.info(f"QR DEBUG: Placeholder found in html_content: {placeholder_found}")
            html_content = html_content.replace('[[QR_CODE_DATA_URI]]', cid_reference)
            inline_attachments.append(qr_attachment)

        # Render template (using Jinja2 directly since no Flask context)
        template = Template(html_content)
        personalized_html = template.render(**template_vars)

        # Debug: Check if CID reference survived Jinja2 rendering
        has_cid = 'cid:qr-' in personalized_html
        logger.info(f"QR DEBUG: After Jinja2 render, has cid:qr-: {has_cid}")
        if campaign.has_qr_code:
            # Find the img tag to see what's there
            import re
            img_match = re.search(r'<img[^>]*alt="Redemption QR Code"[^>]*>', personalized_html)
            if img_match:
                logger.info(f"QR DEBUG: QR img tag after render: {img_match.group(0)[:200]}")

        # Send email with CID attachments
        result = send_email(
            customer.email,
            customer.name or 'Valued Customer',
            campaign.subject,
            personalized_html,
            inline_attachments=inline_attachments if inline_attachments else None
        )

        if result.get('success'):
            # Increment rate counter
            rate_limiter.increment_email_count(campaign_id)

            # Mark delivery as sent
            update_delivery_status(db, delivery, 'sent')

            # Update progress tracking
            if campaign_send_id:
                update_send_progress(db, campaign_send_id, success=True)

            logger.info(f"Email sent to customer {customer_id} for campaign {campaign_id}")
            return {'success': True, 'status_code': result.get('status_code')}
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"SendGrid error for customer {customer_id}: {error_msg}")

            # Check if this is a permanent failure (bad email, etc)
            if 'invalid' in error_msg.lower() or 'bounce' in error_msg.lower():
                update_delivery_status(db, delivery, 'failed', error_msg)
                if campaign_send_id:
                    update_send_progress(db, campaign_send_id, success=False, error=error_msg)
                return {'success': False, 'error': error_msg, 'permanent_failure': True}

            # Otherwise let Celery retry
            raise Exception(f"SendGrid error: {error_msg}")

    except Exception as e:
        logger.error(f"Email task failed for customer {customer_id}: {str(e)}")

        # Check if max retries exceeded
        if self.request.retries >= self.max_retries:
            # Mark delivery as failed after all retries exhausted
            try:
                delivery = get_or_create_delivery(db, campaign_id, customer_id, campaign_send_id)
                update_delivery_status(db, delivery, 'failed', str(e))
            except Exception:
                pass  # Don't fail on tracking error
            if campaign_send_id:
                update_send_progress(db, campaign_send_id, success=False, error=str(e))
            return {'success': False, 'error': str(e), 'permanent_failure': True}

        # Re-raise for Celery retry
        raise

    finally:
        db.close()
