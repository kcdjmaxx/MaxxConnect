#!/usr/bin/env python
"""Quick test script to verify Twilio SMS configuration"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def test_twilio(test_phone=None):
    """Test Twilio SMS sending"""

    # Get config
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_phone = os.getenv('TWILIO_PHONE_NUMBER')
    business_name = os.getenv('SENDER_NAME')

    print("📱 Testing Twilio SMS Configuration")
    print(f"From: {from_phone}")
    print(f"Business: {business_name}")
    print()

    # Use provided phone or ask for it
    if not test_phone:
        test_phone = input("Enter your verified phone number (E.164 format, e.g., +18165551234): ").strip()

    if not test_phone:
        print("❌ No phone number provided")
        return

    # Create test SMS message
    message_body = f"""🎉 Twilio SMS Test Successful!

Hello from {business_name}!

This is a test message from your mailChimpClone app.

Reply STOP to unsubscribe. - {business_name}"""

    try:
        print(f"📤 Sending test SMS to {test_phone}...")

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=from_phone,
            to=test_phone
        )

        print(f"✅ Success! Message SID: {message.sid}")
        print(f"📱 Check your phone at {test_phone}")
        print()
        print(f"Status: {message.status}")

        if message.error_code:
            print(f"⚠️  Error Code: {message.error_code}")
            print(f"⚠️  Error Message: {message.error_message}")

        print()
        print("Note: Trial accounts will show 'Sent from your Twilio trial account' prefix")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify your Twilio credentials are correct")
        print("2. Make sure the 'To' phone number is verified in Twilio (trial requirement)")
        print("3. Check phone number format is E.164 (+1XXXXXXXXXX)")
        print("4. Check Twilio Console logs for details")

if __name__ == '__main__':
    import sys
    phone = sys.argv[1] if len(sys.argv) > 1 else None
    test_twilio(phone)
