import os
from twilio.rest import Client
from backend.models import Customer
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
BUSINESS_NAME = os.getenv('SENDER_NAME')
BASE_URL = os.getenv('BASE_URL')

def send_sms(to_phone, message, include_optout=True):
    """
    Send SMS via Twilio

    Args:
        to_phone: Phone number in E.164 format (+1234567890)
        message: Message body (max 160 chars for single SMS)
        include_optout: Whether to append opt-out message (required by law)

    Returns:
        dict with success status and message_sid or error
    """

    # Add opt-out message if requested (legal requirement)
    if include_optout:
        optout_text = f"\n\nReply STOP to unsubscribe. - {BUSINESS_NAME}"
        # Truncate message if too long
        max_length = 160 - len(optout_text)
        if len(message) > max_length:
            message = message[:max_length-3] + "..."
        message = message + optout_text

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_obj = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        return {
            'success': True,
            'message_sid': message_obj.sid,
            'status': message_obj.status
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def send_test_sms(test_phone, message):
    """Send test SMS to yourself"""

    result = send_sms(test_phone, message, include_optout=True)
    return result

def format_phone_number(phone):
    """
    Format phone number to E.164 format

    Args:
        phone: Phone number in various formats

    Returns:
        Phone number in E.164 format (+1234567890) or None if invalid
    """
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))

    # Handle US/Canada numbers
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+{digits}"
    elif digits.startswith('+'):
        return phone

    return None

def validate_phone_number(phone):
    """
    Validate phone number format

    Returns:
        True if valid E.164 format, False otherwise
    """
    if not phone:
        return False

    # Basic E.164 validation
    if not phone.startswith('+'):
        return False

    digits = phone[1:]
    if not digits.isdigit():
        return False

    if len(digits) < 10 or len(digits) > 15:
        return False

    return True
