from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId
from jinja2 import Template
from backend.models import Customer
from backend.config import Config
from backend.image_handler import ImageHandler
import base64

def send_email(to_email, to_name, subject, html_content, inline_attachments=None):
    """
    Send single email via SendGrid

    Images are automatically processed based on environment:
    - Development: Converted to base64
    - Production: External URLs

    Args:
        to_email: Recipient email address
        to_name: Recipient name
        subject: Email subject
        html_content: HTML body content
        inline_attachments: Optional list of dicts with keys:
            - content_id: CID for reference in HTML (e.g., "qr-1-2")
            - image_bytes: PNG image as bytes
            - filename: Optional filename (defaults to "{content_id}.png")
    """
    # Debug: Check QR CID reference before processing
    import re
    qr_before = re.search(r'<img[^>]*alt="Redemption QR Code"[^>]*>', html_content)
    if qr_before:
        print(f"QR DEBUG email_service BEFORE ImageHandler: {qr_before.group(0)[:150]}")

    # Process images based on environment
    processed_html = ImageHandler.process_html_images(html_content)

    # Debug: Check QR CID reference after processing
    qr_after = re.search(r'<img[^>]*alt="Redemption QR Code"[^>]*>', processed_html)
    if qr_after:
        print(f"QR DEBUG email_service AFTER ImageHandler: {qr_after.group(0)[:150]}")

    message = Mail(
        from_email=(Config.SENDER_EMAIL, Config.SENDER_NAME),
        to_emails=to_email,
        subject=subject,
        html_content=processed_html
    )

    # Add inline attachments (CID images) if provided
    if inline_attachments:
        for att in inline_attachments:
            content_id = att['content_id']
            image_bytes = att['image_bytes']
            filename = att.get('filename', f"{content_id}.png")

            # Encode bytes to base64 for SendGrid
            encoded_content = base64.b64encode(image_bytes).decode('utf-8')

            attachment = Attachment(
                FileContent(encoded_content),
                FileName(filename),
                FileType('image/png'),
                Disposition('inline'),
                ContentId(content_id)
            )
            message.add_attachment(attachment)
            print(f"QR DEBUG: Added inline attachment with CID: {content_id}")

    try:
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        return {
            'success': True,
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def render_email_template(template_path, customer, custom_body):
    """Render email with template and customer data"""

    # Read template
    with open(template_path, 'r') as f:
        template_content = f.read()

    # Generate unsubscribe link
    token = customer.get_unsubscribe_token()
    unsubscribe_link = f"{Config.BASE_URL}/unsubscribe?token={token}&email={customer.email}"

    # Render template
    template = Template(template_content)
    rendered = template.render(
        customer_name=customer.name or 'Valued Customer',
        email_body=custom_body,
        business_name=Config.SENDER_NAME,
        business_address=Config.BUSINESS_ADDRESS,
        unsubscribe_link=unsubscribe_link,
        base_url=Config.BASE_URL,
        static_url=Config.STATIC_URL
    )

    return rendered

def send_test_email(test_email, subject, custom_body):
    """Send test email to yourself"""

    # Build simple HTML email with footer
    html_content = f"""
    <div style="background-color: white; padding: 2rem; border-radius: 8px;">
        {custom_body}
    </div>
    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ccc;
                font-size: 12px; color: #666; text-align: center;">
        <p>{Config.SENDER_NAME}<br>
        {Config.BUSINESS_ADDRESS}</p>
        <p><a href="{Config.BASE_URL}/unsubscribe" style="color: #666;">Unsubscribe from this list</a></p>
    </div>
    """

    # Send
    result = send_email(test_email, "Test User", subject, html_content)
    return result
