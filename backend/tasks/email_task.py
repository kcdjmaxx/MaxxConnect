"""
Email Queue Task - Background task for sending campaign emails

CRC: crc-EmailQueueTask.md
Seq: seq-email-process.md, seq-email-retry.md
"""
from backend.tasks.celery_app import celery_app
from backend.database import SessionLocal
from backend.models import Customer, Campaign, CampaignSend
from backend.email_service import send_email
from backend.services.rate_limiter import RateLimiter
from backend.config import Config
from backend.image_handler import ImageHandler
from jinja2 import Template
import logging
import os

logger = logging.getLogger(__name__)


def get_db():
    """Get database session for task"""
    return SessionLocal()


def build_template_vars(customer, campaign, base_url):
    """
    Build template variables for email personalization

    Extracted from app.py lines 978-997 for reuse in async task
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

    # QR code if campaign has it enabled
    if campaign.has_qr_code:
        # TODO: Generate unique QR code per customer (Phase 2)
        template_vars['qr_code_base64'] = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='

    return template_vars


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

        # Build template variables
        base_url = Config.BASE_URL
        template_vars = build_template_vars(customer, campaign, base_url)

        # Render template (using Jinja2 directly since no Flask context)
        # The campaign.html_content contains the raw template
        # But we need to render from the template file for proper personalization
        # For now, use Jinja2 Template with the stored html_content
        template = Template(campaign.html_content)
        personalized_html = template.render(**template_vars)

        # Send email
        result = send_email(
            customer.email,
            customer.name or 'Valued Customer',
            campaign.subject,
            personalized_html
        )

        if result.get('success'):
            # Increment rate counter
            rate_limiter.increment_email_count(campaign_id)

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
                if campaign_send_id:
                    update_send_progress(db, campaign_send_id, success=False, error=error_msg)
                return {'success': False, 'error': error_msg, 'permanent_failure': True}

            # Otherwise let Celery retry
            raise Exception(f"SendGrid error: {error_msg}")

    except Exception as e:
        logger.error(f"Email task failed for customer {customer_id}: {str(e)}")

        # Check if max retries exceeded
        if self.request.retries >= self.max_retries:
            if campaign_send_id:
                update_send_progress(db, campaign_send_id, success=False, error=str(e))
            return {'success': False, 'error': str(e), 'permanent_failure': True}

        # Re-raise for Celery retry
        raise

    finally:
        db.close()
