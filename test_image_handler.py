#!/usr/bin/env python3
"""
Test ImageHandler to verify image conversion
"""
from backend.image_handler import ImageHandler
from backend.email_service import send_email

# Simple HTML with images
html_with_images = """
<html>
<body>
    <h1>Testing Image Handler</h1>
    <p>Logo test:</p>
    <img src="/static/images/FNFWebLogo200x50.png" width="200" height="50" alt="Logo">
    <p>Hero image test:</p>
    <img src="/static/images/FNFFront600x300.png" width="600" alt="Hero">
</body>
</html>
"""

print("Processing HTML with ImageHandler...")
processed_html = ImageHandler.process_html_images(html_with_images)

# Check if images were converted to base64
if 'data:image' in processed_html:
    print("✓ Images converted to base64!")
    print(f"Processed HTML length: {len(processed_html)} bytes")
else:
    print("✗ Images NOT converted to base64")
    print("Processed HTML:")
    print(processed_html[:500])

# Send test email
test_email = input("\nEnter email to send test (or press Enter to skip): ")
if test_email:
    print(f"\nSending to {test_email}...")
    result = send_email(test_email, 'Test User', 'Image Test - MailChimp Clone', processed_html)

    if result.get('success'):
        print(f"✓ Email sent! Status: {result.get('status_code')}")
    else:
        print(f"✗ Failed: {result.get('error')}")
