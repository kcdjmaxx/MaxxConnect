"""
SMS Queue Task - Background task for sending campaign SMS messages

CRC: crc-SMSQueueTask.md
Seq: seq-sms-process.md, seq-sms-retry.md
"""
from backend.tasks.celery_app import celery_app
from backend.database import SessionLocal
from backend.models import Customer, Campaign, CampaignSend
from backend.sms_service import send_sms
from backend.services.rate_limiter import RateLimiter
import logging

logger = logging.getLogger(__name__)


def get_db():
    """Get database session for task"""
    return SessionLocal()


def update_sms_progress(db, campaign_send_id, success, error=None):
    """Update CampaignSend SMS progress record"""
    try:
        send_record = db.query(CampaignSend).filter_by(id=campaign_send_id).first()
        if send_record:
            if success:
                send_record.sms_sent += 1
            else:
                send_record.sms_failed += 1
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update SMS progress: {e}")
        db.rollback()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=2,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    acks_late=True,
    name='backend.tasks.sms_task.send_campaign_sms'
)
def send_campaign_sms(self, campaign_id, customer_id, message, campaign_send_id=None):
    """
    Send single SMS for a campaign

    Args:
        campaign_id: ID of campaign
        customer_id: ID of customer
        message: SMS message text (without opt-out footer, added by send_sms)
        campaign_send_id: Optional ID for progress tracking

    Returns:
        dict with success status and details
    """
    db = get_db()
    rate_limiter = RateLimiter()

    try:
        # Rate limit check (stricter for SMS: 10/min default)
        rate_limiter.wait_if_needed(campaign_id, 'sms')

        # Load customer
        customer = db.query(Customer).filter_by(id=customer_id).first()

        if not customer:
            logger.error(f"Customer {customer_id} not found")
            return {'success': False, 'error': 'Customer not found'}

        if not customer.phone:
            logger.error(f"Customer {customer_id} has no phone number")
            if campaign_send_id:
                update_sms_progress(db, campaign_send_id, success=False, error='No phone')
            return {'success': False, 'error': 'No phone number', 'skipped': True}

        if not customer.sms_subscribed:
            logger.info(f"Customer {customer_id} SMS unsubscribed, skipping")
            if campaign_send_id:
                update_sms_progress(db, campaign_send_id, success=False, error='Unsubscribed')
            return {'success': False, 'error': 'Customer SMS unsubscribed', 'skipped': True}

        # Personalize message
        first_name = customer.name.split()[0] if customer.name else 'Friend'
        personalized_message = message.replace('{{ customer_name }}', first_name)

        # Send SMS (opt-out footer added by send_sms function)
        result = send_sms(customer.phone, personalized_message, include_optout=True)

        if result.get('success'):
            rate_limiter.increment_sms_count(campaign_id)

            if campaign_send_id:
                update_sms_progress(db, campaign_send_id, success=True)

            logger.info(f"SMS sent to customer {customer_id} for campaign {campaign_id}")
            return {'success': True, 'message_sid': result.get('message_sid')}
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Twilio error for customer {customer_id}: {error_msg}")

            # Check for permanent failures
            if 'invalid' in error_msg.lower() or 'unsubscribed' in error_msg.lower():
                if campaign_send_id:
                    update_sms_progress(db, campaign_send_id, success=False, error=error_msg)
                return {'success': False, 'error': error_msg, 'permanent_failure': True}

            raise Exception(f"Twilio error: {error_msg}")

    except Exception as e:
        logger.error(f"SMS task failed for customer {customer_id}: {str(e)}")

        if self.request.retries >= self.max_retries:
            if campaign_send_id:
                update_sms_progress(db, campaign_send_id, success=False, error=str(e))
            return {'success': False, 'error': str(e), 'permanent_failure': True}

        raise

    finally:
        db.close()
