"""
QR Code Generator Service - Generate unique QR codes for campaign redemption

CRC: crc-QRCodeGenerator.md
Seq: seq-campaign-send-qr.md
"""
import secrets
import qrcode
import io
import base64
from datetime import datetime, timedelta
from backend.models import QRCode
import logging

logger = logging.getLogger(__name__)

# Default expiration: 30 days
DEFAULT_EXPIRATION_DAYS = 30


def generate_token(campaign_id, customer_id):
    """
    Generate cryptographically secure unique token

    Format: {campaign_id}-{customer_id}-{16-byte-hex-hash}
    """
    random_hash = secrets.token_hex(16)
    return f"{campaign_id}-{customer_id}-{random_hash}"


def generate_qr_image(url):
    """
    Generate QR code image as PNG bytes

    Args:
        url: The URL to encode in the QR code

    Returns:
        PNG image bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to PNG bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return img_buffer.getvalue()


def encode_base64(image_bytes):
    """Convert image bytes to base64 string for email embedding"""
    return base64.b64encode(image_bytes).decode('utf-8')


def create_qr_code(db, campaign, customer, base_url, expiration_days=DEFAULT_EXPIRATION_DAYS):
    """
    Generate and persist a unique QR code for a customer/campaign

    Args:
        db: Database session
        campaign: Campaign model instance
        customer: Customer model instance
        base_url: Application base URL for redemption link
        expiration_days: Days until QR code expires

    Returns:
        dict with 'qr_code' model and 'base64' image string
    """
    # Generate unique token
    token = generate_token(campaign.id, customer.id)

    # Build redemption URL
    redemption_url = f"{base_url}/redeem/{token}"

    # Generate QR image
    image_bytes = generate_qr_image(redemption_url)
    base64_image = encode_base64(image_bytes)

    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(days=expiration_days)

    # Create database record
    qr_code = QRCode(
        campaign_id=campaign.id,
        customer_id=customer.id,
        token=token,
        expires_at=expires_at,
        usage_count=0,
        max_usage=1
    )

    db.add(qr_code)
    db.commit()

    logger.info(f"Created QR code {token[:30]}... for customer {customer.id}, campaign {campaign.id}")

    return {
        'qr_code': qr_code,
        'base64': base64_image
    }


def get_existing_qr_code(db, campaign_id, customer_id):
    """
    Check if a QR code already exists for this campaign/customer pair

    Args:
        db: Database session
        campaign_id: Campaign ID
        customer_id: Customer ID

    Returns:
        QRCode model if exists, None otherwise
    """
    return db.query(QRCode).filter_by(
        campaign_id=campaign_id,
        customer_id=customer_id
    ).first()


def regenerate_base64(qr_code, base_url):
    """
    Regenerate base64 image for existing QR code

    Useful when we already have the QR code in DB but need the image again
    """
    redemption_url = f"{base_url}/redeem/{qr_code.token}"
    image_bytes = generate_qr_image(redemption_url)
    return encode_base64(image_bytes)
