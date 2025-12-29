from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Template
from backend.models import Customer
from backend.config import Config
from backend.image_handler import ImageHandler

def send_email(to_email, to_name, subject, html_content):
    """
    Send single email via SendGrid

    Images are automatically processed based on environment:
    - Development: Converted to base64
    - Production: External URLs
    """
    # Process images based on environment
    processed_html = ImageHandler.process_html_images(html_content)

    message = Mail(
        from_email=(Config.SENDER_EMAIL, Config.SENDER_NAME),
        to_emails=to_email,
        subject=subject,
        html_content=processed_html
    )

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

    # Create temporary customer object for rendering
    temp_customer = Customer(
        id=0,
        email=test_email,
        name="Test User"
    )

    # Render email
    html_content = render_email_template(
        'templates/email/base_email.html',
        temp_customer,
        custom_body
    )

    # Send
    result = send_email(test_email, "Test User", subject, html_content)
    return result
