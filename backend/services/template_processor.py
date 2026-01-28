"""
Template Processor Service - Validate and process email templates

CRC: crc-TemplateProcessor.md
Seq: seq-template-import.md
"""
import re
import os
from dataclasses import dataclass, field
from typing import List, Tuple
from backend.config import Config


# Starter template with professional email layout (~180 lines)
# Based on common patterns from existing templates
STARTER_TEMPLATE_HTML = '''<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<!-- utf-8 works for most cases -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Forcing initial-scale shouldn't be necessary -->
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<!-- Use the latest (edge) version of IE rendering engine -->
<title>Your Email Title Here</title>
<!-- The title tag shows in email notifications, like Android 4.4. -->

<!-- CSS Reset -->
<style type="text/css">
/* What it does: Remove spaces around the email design added by some email clients. */
html, body {
	margin: 0 !important;
	padding: 0 !important;
	height: 100% !important;
	width: 100% !important;
}
/* What it does: Stops email clients resizing small text. */
* {
	-ms-text-size-adjust: 100%;
	-webkit-text-size-adjust: 100%;
}
/* What it does: Forces Outlook.com to display emails full width. */
.ExternalClass {
	width: 100%;
}
/* What is does: Centers email on Android 4.4 */
div[style*="margin: 16px 0"] {
	margin: 0 !important;
}
/* What it does: Stops Outlook from adding extra spacing to tables. */
table, td {
	mso-table-lspace: 0pt !important;
	mso-table-rspace: 0pt !important;
}
/* What it does: Fixes webkit padding issue. Fix for Yahoo mail table alignment bug. */
table {
	border-spacing: 0 !important;
	border-collapse: collapse !important;
	table-layout: fixed !important;
	margin: 0 auto !important;
}
table table table {
	table-layout: auto;
}
/* What it does: Uses a better rendering method when resizing images in IE. */
img {
	-ms-interpolation-mode: bicubic;
}
/* What it does: Overrides styles added when Yahoo's auto-senses a link. */
.yshortcuts a {
	border-bottom: none !important;
}
/* What it does: Another work-around for iOS meddling in triggered links. */
a[x-apple-data-detectors] {
	color: inherit !important;
}
</style>

<!-- Progressive Enhancements -->
<style type="text/css">
/* What it does: Hover styles for buttons */
.button-td, .button-a {
	transition: all 100ms ease-in;
}
.button-td:hover, .button-a:hover {
	background: #555555 !important;
	border-color: #555555 !important;
}
</style>
</head>
<body width="100%" height="100%" bgcolor="#e0e0e0" style="margin: 0;" yahoo="yahoo">
<table cellpadding="0" cellspacing="0" border="0" height="100%" width="100%" bgcolor="#e0e0e0" style="border-collapse:collapse;">
  <tr>
    <td><center style="width: 100%;">

        <!-- Visually Hidden Preheader Text : BEGIN -->
        <div style="display:none;font-size:1px;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;mso-hide:all;font-family: sans-serif;">Your preheader text goes here - this shows in email previews.</div>
        <!-- Visually Hidden Preheader Text : END -->

        <div style="max-width: 600px;">
          <!--[if (gte mso 9)|(IE)]>
            <table cellspacing="0" cellpadding="0" border="0" width="600" align="center">
            <tr>
            <td>
            <![endif]-->

          <!-- Email Header : BEGIN -->
          <table cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px;">
            <tr>
              <td style="padding: 20px 0; text-align: center">
                <img src="{{ logo_url }}" width="200" height="50" alt="Your Logo" border="0">
              </td>
            </tr>
          </table>
          <!-- Email Header : END -->

          <!-- Email Body : BEGIN -->
          <table cellspacing="0" cellpadding="0" border="0" align="center" bgcolor="#ffffff" width="100%" style="max-width: 600px;">

            <!-- Hero Image, Flush : BEGIN -->
            <tr>
              <td class="full-width-image" align="center">
                <img src="{{ hero_image_url }}" width="600" alt="Hero Image" border="0" style="width: 100%; max-width: 600px; height: auto;">
              </td>
            </tr>
            <!-- Hero Image, Flush : END -->

            <!-- 1 Column Text : BEGIN -->
            <tr>
              <td style="padding: 40px 20px; text-align: center; font-family: sans-serif;">
                <h1 style="color: #2c3e50; font-size: 28px; margin: 0 0 20px 0; font-family: sans-serif;">Hello, [[CUSTOMER_NAME]]!</h1>

                <p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0; font-family: sans-serif;">
                  Your email content goes here. This is a great place to share your message with your subscribers.
                </p>

                <p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0; font-family: sans-serif;">
                  Add more paragraphs as needed to tell your story. Remember to keep your message clear and engaging.
                </p>

                <p style="color: #888888; font-size: 14px; font-style: italic; margin: 0; font-family: sans-serif;">
                  Your closing message here.<br><br>
                  <em>Your Team Name</em>
                </p>
              </td>
            </tr>
            <!-- 1 Column Text : END -->

            <!-- QR_CODE_SECTION -->

          </table>
          <!-- Email Body : END -->

          <!-- Email Footer : BEGIN -->
          <table cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px;">
            <tr>
              <td style="padding: 40px 10px; font-family: sans-serif; font-size: 12px; line-height: 18px; text-align: center; color: #888888;">
                <p style="margin: 0 0 10px 0;">
                  Fric &amp; Frac<br>
                  1700 West 39th St. Kansas City, MO 64111
                </p>
                <p style="margin: 0;">
                  <a href="{{ unsubscribe_link }}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>
                  &nbsp;|&nbsp;
                  <a href="https://fricandfrac.net/privacy/" style="color: #888888; text-decoration: underline;">Privacy Policy</a>
                </p>
              </td>
            </tr>
          </table>
          <!-- Email Footer : END -->

          <!--[if (gte mso 9)|(IE)]>
            </td>
            </tr>
            </table>
            <![endif]-->
        </div>
      </center></td>
  </tr>
</table>
</body>
</html>
'''

# Blank template with minimal valid structure (~30 lines)
# Contains only required compliance elements
BLANK_TEMPLATE_HTML = '''<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Title</title>
</head>
<body style="margin: 0; padding: 20px; font-family: sans-serif; background-color: #f5f5f5;">
  <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px;">

    <h1>Hello, [[CUSTOMER_NAME]]!</h1>

    <p>Your email content goes here.</p>

    <!-- QR_CODE_SECTION -->

    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

    <footer style="font-size: 12px; color: #888888; text-align: center;">
      <p>
        Fric &amp; Frac<br>
        1700 West 39th St. Kansas City, MO 64111
      </p>
      <p>
        <a href="{{ unsubscribe_link }}" style="color: #888888;">Unsubscribe</a>
        &nbsp;|&nbsp;
        <a href="https://fricandfrac.net/privacy/" style="color: #888888;">Privacy Policy</a>
      </p>
    </footer>

  </div>
</body>
</html>
'''


@dataclass
class ValidationReport:
    """Results of template validation"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)      # Required elements missing
    warnings: List[str] = field(default_factory=list)    # Recommended elements missing
    info: List[str] = field(default_factory=list)        # Best practice suggestions


class TemplateProcessor:
    """
    Validates email templates and auto-injects required elements

    Required Elements (hard fail):
    - {{ unsubscribe_link }} in an <a> tag
    - Physical mailing address
    - Valid HTML structure (DOCTYPE, html, head, body)

    Recommended Elements (soft warning):
    - [[CUSTOMER_NAME]] placeholder
    - <!-- QR_CODE_SECTION --> comment
    - Preheader text
    - Privacy policy link
    - Inline CSS

    Best Practices (info):
    - Table-based layout
    - Max-width 600px container
    - Alt text on images
    """

    # Patterns for detection
    UNSUBSCRIBE_PATTERN = re.compile(r'\{\{\s*unsubscribe_link\s*\}\}', re.IGNORECASE)
    CUSTOMER_NAME_PATTERN = re.compile(r'\[\[CUSTOMER_NAME\]\]', re.IGNORECASE)
    QR_SECTION_PATTERN = re.compile(r'<!--\s*QR_CODE_SECTION\s*-->', re.IGNORECASE)
    PRIVACY_LINK_PATTERN = re.compile(r'privacy', re.IGNORECASE)
    PREHEADER_PATTERN = re.compile(r'display:\s*none.*overflow:\s*hidden', re.IGNORECASE | re.DOTALL)
    DOCTYPE_PATTERN = re.compile(r'<!doctype\s+html>', re.IGNORECASE)

    # Common address patterns (US format)
    ADDRESS_PATTERN = re.compile(r'\d+\s+\w+.*(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane).*\d{5}', re.IGNORECASE)

    # Greeting patterns for customer name injection
    GREETING_PATTERNS = [
        (re.compile(r'(Hey there,?\s*)', re.IGNORECASE), r'\1[[CUSTOMER_NAME]]! '),
        (re.compile(r'(Hello,?\s*)', re.IGNORECASE), r'\1[[CUSTOMER_NAME]]! '),
        (re.compile(r'(Hi,?\s*)', re.IGNORECASE), r'\1[[CUSTOMER_NAME]]! '),
        (re.compile(r'(Dear\s+)', re.IGNORECASE), r'\1[[CUSTOMER_NAME]], '),
        (re.compile(r'(Welcome,?\s*)', re.IGNORECASE), r'\1[[CUSTOMER_NAME]]! '),
    ]

    def __init__(self):
        self.business_address = Config.BUSINESS_ADDRESS or "1700 West 39th St. Kansas City, MO 64111"
        self.privacy_policy_url = "https://fricandfrac.net/privacy/"

    def validate(self, html: str) -> ValidationReport:
        """
        Analyze template and return ValidationReport with issues/warnings

        Args:
            html: Raw HTML template content

        Returns:
            ValidationReport with is_valid, errors, warnings, info
        """
        report = ValidationReport()

        # Required checks (errors)
        if not self.DOCTYPE_PATTERN.search(html):
            report.errors.append("Missing DOCTYPE declaration")
            report.is_valid = False

        if '<html' not in html.lower():
            report.errors.append("Missing <html> tag")
            report.is_valid = False

        if '<head' not in html.lower():
            report.errors.append("Missing <head> section")
            report.is_valid = False

        if '<body' not in html.lower():
            report.errors.append("Missing <body> tag")
            report.is_valid = False

        if not self.UNSUBSCRIBE_PATTERN.search(html):
            report.errors.append("Missing {{ unsubscribe_link }} - required for CAN-SPAM compliance")
            report.is_valid = False

        if not self.ADDRESS_PATTERN.search(html):
            report.errors.append("Missing physical mailing address - required for CAN-SPAM compliance")
            report.is_valid = False

        if not self.PRIVACY_LINK_PATTERN.search(html):
            report.errors.append("Missing privacy policy link - required for compliance")
            report.is_valid = False

        # Recommended checks (warnings)
        if not self.CUSTOMER_NAME_PATTERN.search(html):
            report.warnings.append("Missing [[CUSTOMER_NAME]] placeholder - recommended for personalization")

        if not self.QR_SECTION_PATTERN.search(html):
            report.warnings.append("Missing <!-- QR_CODE_SECTION --> comment - required for QR code campaigns")

        if not self.PREHEADER_PATTERN.search(html):
            report.warnings.append("Missing preheader text - recommended for email previews")

        # Best practice checks (info)
        if '<table' not in html.lower():
            report.info.append("Consider using table-based layout for better email client compatibility")

        if 'max-width' not in html.lower() and '600' not in html:
            report.info.append("Consider using max-width: 600px for mobile compatibility")

        # Check for images without alt text
        img_without_alt = re.findall(r'<img(?![^>]*alt=)[^>]*>', html, re.IGNORECASE)
        if img_without_alt:
            report.info.append(f"Found {len(img_without_alt)} image(s) without alt text")

        # Check for external CSS (not inline)
        if '<link' in html.lower() and 'stylesheet' in html.lower():
            report.info.append("External stylesheets may not work in email clients - use inline CSS")

        return report

    def inject_unsubscribe_link(self, html: str) -> str:
        """Add {{ unsubscribe_link }} to footer if missing"""
        if self.UNSUBSCRIBE_PATTERN.search(html):
            return html

        # Find the footer or end of body to inject
        unsubscribe_html = '''
        <p style="margin: 10px 0;">
          <a href="{{ unsubscribe_link }}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>
        </p>'''

        # Try to inject before </body>
        if '</body>' in html.lower():
            # Find position case-insensitively
            body_pos = html.lower().rfind('</body>')
            return html[:body_pos] + unsubscribe_html + '\n' + html[body_pos:]

        # Fallback: append to end
        return html + unsubscribe_html

    def inject_customer_name(self, html: str) -> str:
        """Add [[CUSTOMER_NAME]] placeholder at greeting if missing"""
        if self.CUSTOMER_NAME_PATTERN.search(html):
            return html

        # Try to find and enhance greeting patterns
        for pattern, replacement in self.GREETING_PATTERNS:
            if pattern.search(html):
                # Only replace the first occurrence
                return pattern.sub(replacement, html, count=1)

        return html

    def inject_qr_section(self, html: str) -> str:
        """Add <!-- QR_CODE_SECTION --> comment if missing"""
        if self.QR_SECTION_PATTERN.search(html):
            return html

        qr_comment = '\n            <!-- QR_CODE_SECTION -->\n'

        # Try to inject before footer or end of main content table
        # Look for common footer patterns
        footer_patterns = [
            (r'(<!--\s*Email Footer)', r'\n            <!-- QR_CODE_SECTION -->\n\n\1'),
            (r'(</table>\s*<!--\s*Email Body\s*:\s*END)', r'\n            <!-- QR_CODE_SECTION -->\n\1'),
        ]

        for pattern, replacement in footer_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return re.sub(pattern, replacement, html, count=1, flags=re.IGNORECASE)

        # Fallback: inject before </body>
        if '</body>' in html.lower():
            body_pos = html.lower().rfind('</body>')
            return html[:body_pos] + qr_comment + html[body_pos:]

        return html

    def inject_privacy_link(self, html: str) -> str:
        """Add privacy policy link to footer if missing"""
        if self.PRIVACY_LINK_PATTERN.search(html):
            return html

        privacy_html = f'''
          &nbsp;|&nbsp;
          <a href="{self.privacy_policy_url}" style="color: #888888; text-decoration: underline;">Privacy Policy</a>'''

        # Try to inject after unsubscribe link
        unsubscribe_match = re.search(r'(<a[^>]*unsubscribe[^>]*>[^<]*</a>)', html, re.IGNORECASE)
        if unsubscribe_match:
            pos = unsubscribe_match.end()
            return html[:pos] + privacy_html + html[pos:]

        return html

    def inject_address(self, html: str, address: str = None) -> str:
        """Add physical mailing address to footer if missing"""
        if self.ADDRESS_PATTERN.search(html):
            return html

        addr = address or self.business_address
        address_html = f'''
        <p style="margin: 10px 0; font-size: 12px; color: #888888;">
          {addr}
        </p>'''

        # Try to inject before unsubscribe link or end of body
        unsubscribe_pos = html.lower().find('unsubscribe')
        if unsubscribe_pos > 0:
            # Find the start of the paragraph containing unsubscribe
            p_start = html.rfind('<p', 0, unsubscribe_pos)
            if p_start > 0:
                return html[:p_start] + address_html + '\n' + html[p_start:]

        # Fallback: inject before </body>
        if '</body>' in html.lower():
            body_pos = html.lower().rfind('</body>')
            return html[:body_pos] + address_html + '\n' + html[body_pos:]

        return html

    def process_images(self, html: str) -> str:
        """
        Convert static image sources to Jinja2 environment-aware pattern

        Converts:
        - src="images/logo.png" -> src="{{ logo_url }}"
        - src="static/images/banner.png" -> src="{{ hero_image_url }}"
        """
        # Pattern for common static image paths
        # This is a simplified version - in production you'd have more patterns

        # Convert relative image paths to Jinja2 url_for
        def replace_image(match):
            src = match.group(1)
            # Skip already-converted Jinja2 variables
            if '{{' in src or '}}' in src:
                return match.group(0)
            # Skip external URLs
            if src.startswith('http') or src.startswith('//'):
                return match.group(0)
            # Skip data URIs
            if src.startswith('data:'):
                return match.group(0)
            # Skip cid references
            if src.startswith('cid:'):
                return match.group(0)

            # Convert to Jinja2 url_for
            # Normalize path
            filename = src.lstrip('/')
            if filename.startswith('static/'):
                filename = filename[7:]

            return f'src="{{{{ url_for(\'static\', filename=\'{filename}\', _external=True) }}}}"'

        # Match src attributes
        html = re.sub(r'src="([^"]+)"', replace_image, html)
        html = re.sub(r"src='([^']+)'", replace_image, html)

        return html

    def process_all(self, html: str) -> Tuple[str, ValidationReport]:
        """
        Run all injections and return processed HTML with validation report

        Args:
            html: Raw HTML template content

        Returns:
            Tuple of (processed_html, ValidationReport)
        """
        # Run all injections
        processed = html
        processed = self.inject_customer_name(processed)
        processed = self.inject_unsubscribe_link(processed)
        processed = self.inject_qr_section(processed)
        processed = self.inject_privacy_link(processed)
        processed = self.inject_address(processed)
        processed = self.process_images(processed)

        # Validate the result
        report = self.validate(processed)

        return processed, report

    def get_template_info(self, template_path: str) -> dict:
        """
        Get information about a template file

        Args:
            template_path: Path to template file

        Returns:
            dict with name, path, validation status
        """
        if not os.path.exists(template_path):
            return None

        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()

        report = self.validate(html)
        name = os.path.basename(template_path).replace('.html', '')

        return {
            'name': name,
            'filename': os.path.basename(template_path),
            'path': template_path,
            'is_valid': report.is_valid,
            'error_count': len(report.errors),
            'warning_count': len(report.warnings),
            'report': report
        }

    def list_templates(self, templates_dir: str) -> List[dict]:
        """
        List all email templates with validation info

        Args:
            templates_dir: Path to templates/email/ directory

        Returns:
            List of template info dicts
        """
        templates = []
        email_dir = os.path.join(templates_dir, 'email')

        if not os.path.exists(email_dir):
            return templates

        for filename in sorted(os.listdir(email_dir)):
            if filename.endswith('.html'):
                template_path = os.path.join(email_dir, filename)
                info = self.get_template_info(template_path)
                if info:
                    templates.append(info)

        return templates

    def get_starter_template(self) -> str:
        """
        Get the starter template HTML with professional email layout

        Returns:
            Complete HTML template string with CSS reset, table layout,
            header, hero image, content area, QR section marker, and footer
        """
        return STARTER_TEMPLATE_HTML

    def get_blank_template(self) -> str:
        """
        Get the blank template HTML with minimal valid structure

        Returns:
            Minimal HTML template string with only required compliance elements
        """
        return BLANK_TEMPLATE_HTML
