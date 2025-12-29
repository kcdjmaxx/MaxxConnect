#!/usr/bin/env python3
"""
Direct test of email sending functionality
"""
from backend.email_service import send_email
from backend.config import Config

def test_email():
    test_email = input("Enter your email address to test: ")

    print(f"\nSending test email to: {test_email}")
    print(f"From: {Config.SENDER_EMAIL} ({Config.SENDER_NAME})")
    print(f"API Key configured: {'Yes' if Config.SENDGRID_API_KEY else 'No'}")

    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h1 style="color: #d32f2f;">Test Email from MailChimp Clone</h1>
        <p>This is a test email to verify SendGrid integration is working correctly.</p>
        <p>If you receive this, your email system is configured properly! 🎉</p>
    </body>
    </html>
    """

    result = send_email(test_email, 'Test User', 'Test Email - MailChimp Clone', html_content)

    print("\n--- Result ---")
    if result.get('success'):
        print(f"✓ SUCCESS! Status code: {result.get('status_code')}")
        print(f"Check your inbox at: {test_email}")
    else:
        print(f"✗ FAILED!")
        print(f"Error: {result.get('error')}")

if __name__ == '__main__':
    test_email()
