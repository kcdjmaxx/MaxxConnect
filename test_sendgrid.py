#!/usr/bin/env python
"""Quick test script to verify SendGrid configuration"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

def test_sendgrid(test_email=None):
    """Test SendGrid email sending"""

    # Get config
    api_key = os.getenv('SENDGRID_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    sender_name = os.getenv('SENDER_NAME')
    business_address = os.getenv('BUSINESS_ADDRESS')

    print("📧 Testing SendGrid Configuration")
    print(f"From: {sender_name} <{sender_email}>")
    print(f"Business Address: {business_address}")
    print()

    # Use provided email or ask for it
    if not test_email:
        test_email = input("Enter your email address to receive test email: ").strip()

    if not test_email:
        print("❌ No email provided")
        return

    # Create test email
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>🎉 SendGrid Test Successful!</h2>
            <p>Hello from your MaxxConnect app!</p>
            <p>If you're reading this, your SendGrid configuration is working correctly.</p>
            <hr>
            <h3>Configuration Details:</h3>
            <ul>
                <li><strong>Sender:</strong> {sender_name}</li>
                <li><strong>Email:</strong> {sender_email}</li>
                <li><strong>Domain:</strong> fricandfrac.net</li>
                <li><strong>Authentication:</strong> ✅ Verified</li>
            </ul>
            <hr>
            <p style="color: #666; font-size: 12px;">
                {sender_name}<br>
                {business_address}
            </p>
        </body>
    </html>
    """

    message = Mail(
        from_email=(sender_email, sender_name),
        to_emails=test_email,
        subject='✅ SendGrid Test - MaxxConnect',
        html_content=html_content
    )

    try:
        print(f"📤 Sending test email to {test_email}...")
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        print(f"✅ Success! Status code: {response.status_code}")
        print(f"📬 Check your inbox at {test_email}")
        print("   (Don't forget to check spam folder)")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify your SendGrid API key is correct")
        print("2. Verify deals@fricandfrac.net is authenticated in SendGrid")
        print("3. Check SendGrid Activity dashboard for details")

if __name__ == '__main__':
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else None
    test_sendgrid(email)
