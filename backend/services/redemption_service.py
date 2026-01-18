"""
Redemption Service - Validate and redeem QR codes

CRC: crc-RedemptionService.md
Seq: seq-qr-redemption.md
"""
from datetime import datetime
from backend.models import QRCode, Redemption, Customer, Campaign
import logging

logger = logging.getLogger(__name__)


class RedemptionResult:
    """Result object for redemption operations"""

    def __init__(self, success, status, message, data=None):
        self.success = success
        self.status = status  # 'valid', 'invalid', 'expired', 'already_used', 'not_found'
        self.message = message
        self.data = data or {}

    def to_dict(self):
        return {
            'success': self.success,
            'status': self.status,
            'message': self.message,
            'data': self.data
        }


def validate(db, token):
    """
    Validate a QR code token without redeeming it

    Args:
        db: Database session
        token: QR code token string

    Returns:
        RedemptionResult with validation status and customer/campaign info
    """
    # Look up the QR code
    qr_code = db.query(QRCode).filter_by(token=token).first()

    if not qr_code:
        logger.warning(f"QR code not found: {token[:30]}...")
        return RedemptionResult(
            success=False,
            status='not_found',
            message='QR code not found'
        )

    # Check if expired
    if qr_code.is_expired():
        logger.info(f"QR code expired: {token[:30]}... (expired at {qr_code.expires_at})")
        return RedemptionResult(
            success=False,
            status='expired',
            message='This QR code has expired'
        )

    # Check if already used (max usage reached)
    if not qr_code.can_redeem():
        logger.info(f"QR code already used: {token[:30]}... (usage: {qr_code.usage_count}/{qr_code.max_usage})")
        return RedemptionResult(
            success=False,
            status='already_used',
            message='This QR code has already been redeemed'
        )

    # Get customer and campaign details
    customer = db.query(Customer).filter_by(id=qr_code.customer_id).first()
    campaign = db.query(Campaign).filter_by(id=qr_code.campaign_id).first()

    if not customer or not campaign:
        logger.error(f"QR code references missing customer/campaign: {token[:30]}...")
        return RedemptionResult(
            success=False,
            status='invalid',
            message='QR code data is invalid'
        )

    # Valid!
    logger.info(f"QR code valid: {token[:30]}... for customer {customer.id}, campaign {campaign.id}")
    return RedemptionResult(
        success=True,
        status='valid',
        message='QR code is valid and ready to redeem',
        data={
            'qr_code_id': qr_code.id,
            'customer_id': customer.id,
            'customer_name': customer.name or 'Guest',
            'customer_email': customer.email,
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'campaign_subject': campaign.subject,
            'deal_description': campaign.deal_description,
            'expires_at': qr_code.expires_at.isoformat(),
            'usage_count': qr_code.usage_count,
            'max_usage': qr_code.max_usage
        }
    )


def redeem(db, token, redeemed_by=None, redemption_method='scan', device_info=None, ip_address=None):
    """
    Redeem a QR code - performs validation and creates redemption record

    Args:
        db: Database session
        token: QR code token string
        redeemed_by: Optional staff identifier who performed the redemption
        redemption_method: 'scan' or 'manual'
        device_info: User agent string for fraud detection
        ip_address: Client IP for fraud detection

    Returns:
        RedemptionResult with redemption status
    """
    # First validate the code
    validation_result = validate(db, token)

    if not validation_result.success:
        return validation_result

    # Get the QR code for redemption
    qr_code = db.query(QRCode).filter_by(token=token).first()

    try:
        # Increment usage count
        qr_code.increment_usage()

        # Create redemption record
        redemption = Redemption(
            qr_code_id=qr_code.id,
            customer_id=qr_code.customer_id,
            campaign_id=qr_code.campaign_id,
            redeemed_at=datetime.utcnow(),
            redeemed_by=redeemed_by,
            redemption_method=redemption_method,
            device_info=device_info,
            ip_address=ip_address
        )
        db.add(redemption)
        db.commit()

        logger.info(f"QR code redeemed: {token[:30]}... by {redeemed_by or 'unknown'} via {redemption_method}")

        return RedemptionResult(
            success=True,
            status='redeemed',
            message='QR code successfully redeemed!',
            data={
                'redemption_id': redemption.id,
                'customer_name': validation_result.data.get('customer_name'),
                'campaign_name': validation_result.data.get('campaign_name'),
                'redeemed_at': redemption.redeemed_at.isoformat()
            }
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error redeeming QR code {token[:30]}...: {str(e)}")
        return RedemptionResult(
            success=False,
            status='error',
            message=f'Failed to redeem: {str(e)}'
        )


def get_redemption_stats(db, campaign_id=None):
    """
    Get redemption statistics

    Args:
        db: Database session
        campaign_id: Optional campaign ID to filter by

    Returns:
        dict with stats: total_codes, redeemed_codes, redemption_rate
    """
    qr_query = db.query(QRCode)
    redemption_query = db.query(Redemption)

    if campaign_id:
        qr_query = qr_query.filter_by(campaign_id=campaign_id)
        redemption_query = redemption_query.filter_by(campaign_id=campaign_id)

    total_codes = qr_query.count()
    total_redemptions = redemption_query.count()
    redeemed_codes = qr_query.filter(QRCode.usage_count > 0).count()

    redemption_rate = (redeemed_codes / total_codes * 100) if total_codes > 0 else 0

    return {
        'total_codes': total_codes,
        'redeemed_codes': redeemed_codes,
        'total_redemptions': total_redemptions,
        'redemption_rate': round(redemption_rate, 1)
    }


def get_recent_redemptions(db, limit=50, campaign_id=None):
    """
    Get recent redemptions with customer and campaign details

    Args:
        db: Database session
        limit: Maximum number of records to return
        campaign_id: Optional campaign ID to filter by

    Returns:
        List of redemption records with joined data
    """
    query = db.query(Redemption)

    if campaign_id:
        query = query.filter_by(campaign_id=campaign_id)

    redemptions = query.order_by(Redemption.redeemed_at.desc()).limit(limit).all()

    results = []
    for r in redemptions:
        customer = db.query(Customer).filter_by(id=r.customer_id).first()
        campaign = db.query(Campaign).filter_by(id=r.campaign_id).first()

        results.append({
            'id': r.id,
            'redeemed_at': r.redeemed_at,
            'redeemed_by': r.redeemed_by,
            'redemption_method': r.redemption_method,
            'customer_name': customer.name if customer else 'Unknown',
            'customer_email': customer.email if customer else 'Unknown',
            'campaign_name': campaign.name if campaign else 'Unknown'
        })

    return results


def get_hourly_redemptions(db, campaign_id=None, days=7):
    """
    Get redemption counts by hour for the last N days

    Args:
        db: Database session
        campaign_id: Optional campaign ID to filter by
        days: Number of days to look back

    Returns:
        dict mapping hour (0-23) to count
    """
    from datetime import timedelta
    from sqlalchemy import extract

    cutoff = datetime.utcnow() - timedelta(days=days)

    query = db.query(Redemption).filter(Redemption.redeemed_at >= cutoff)

    if campaign_id:
        query = query.filter_by(campaign_id=campaign_id)

    redemptions = query.all()

    # Count by hour
    hourly_counts = {hour: 0 for hour in range(24)}
    for r in redemptions:
        hour = r.redeemed_at.hour
        hourly_counts[hour] += 1

    return hourly_counts


def get_campaign_redemption_stats(db):
    """
    Get redemption stats grouped by campaign

    Returns:
        List of dicts with campaign info and redemption counts
    """
    from sqlalchemy import func

    campaigns = db.query(Campaign).filter_by(has_qr_code=True).all()
    results = []

    for campaign in campaigns:
        total_codes = db.query(QRCode).filter_by(campaign_id=campaign.id).count()
        redeemed = db.query(QRCode).filter(
            QRCode.campaign_id == campaign.id,
            QRCode.usage_count > 0
        ).count()
        total_redemptions = db.query(Redemption).filter_by(campaign_id=campaign.id).count()

        redemption_rate = (redeemed / total_codes * 100) if total_codes > 0 else 0

        results.append({
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'sent_date': campaign.sent_date,
            'total_codes': total_codes,
            'redeemed_codes': redeemed,
            'total_redemptions': total_redemptions,
            'redemption_rate': round(redemption_rate, 1)
        })

    return sorted(results, key=lambda x: x.get('sent_date') or datetime.min, reverse=True)
