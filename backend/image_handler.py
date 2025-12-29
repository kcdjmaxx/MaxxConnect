"""
Image handling for email templates with environment-aware processing

CRC: crc-ImageHandler.md
Spec: phase-2-campaign-management.md
Sequence: seq-campaign-create.md, seq-campaign-send.md
"""
import os
import base64
import re
from pathlib import Path
from backend.config import Config


class ImageHandler:
    """Handle images in email HTML based on environment"""

    @staticmethod
    def process_html_images(html_content):
        """
        Process images in HTML based on environment strategy

        Args:
            html_content (str): HTML content with image tags

        Returns:
            str: Processed HTML with images handled appropriately
        """
        strategy = Config.get_image_strategy()

        if strategy == 'base64':
            return ImageHandler._convert_to_base64(html_content)
        elif strategy == 'external':
            return ImageHandler._convert_to_external_urls(html_content)
        else:
            return html_content

    @staticmethod
    def _convert_to_base64(html_content):
        """
        Convert local image paths to base64 data URIs

        Args:
            html_content (str): HTML content

        Returns:
            str: HTML with images as base64 data URIs
        """
        # Find all img tags with src attributes
        img_pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'

        def replace_img(match):
            img_tag = match.group(0)
            src = match.group(1)

            # Skip if already base64 or external URL
            if src.startswith('data:') or src.startswith('http'):
                return img_tag

            # Try to find local file
            file_path = ImageHandler._resolve_image_path(src)
            if file_path and os.path.exists(file_path):
                try:
                    base64_data = ImageHandler._image_to_base64(file_path)
                    return img_tag.replace(src, base64_data)
                except Exception as e:
                    print(f"Warning: Could not convert image {src} to base64: {e}")
                    return img_tag

            return img_tag

        return re.sub(img_pattern, replace_img, html_content)

    @staticmethod
    def _convert_to_external_urls(html_content):
        """
        Convert local image paths to external URLs

        Args:
            html_content (str): HTML content

        Returns:
            str: HTML with external image URLs
        """
        # Find all img tags with src attributes
        img_pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'

        def replace_img(match):
            img_tag = match.group(0)
            src = match.group(1)

            # Skip if already external URL or base64
            if src.startswith('http') or src.startswith('data:'):
                return img_tag

            # Convert to external URL
            if src.startswith('/static/'):
                external_url = Config.get_full_url(src)
            elif src.startswith('static/'):
                external_url = Config.get_full_url('/' + src)
            else:
                # Assume it's in static/images/
                external_url = Config.get_static_url(f"images/{src}")

            return img_tag.replace(src, external_url)

        return re.sub(img_pattern, replace_img, html_content)

    @staticmethod
    def _resolve_image_path(src):
        """
        Resolve relative image path to absolute file path

        Args:
            src (str): Image src attribute value

        Returns:
            str: Absolute file path or None
        """
        # Strip leading slash if present
        src_clean = src.lstrip('/')

        # Try different possible locations
        possible_paths = [
            src,  # Absolute path
            src_clean,  # Without leading slash
            f"static/{src_clean}",  # Relative to static
            f"static/images/{src_clean}",  # In images folder
        ]

        # If src starts with /static/, try without the /static/ prefix
        if src.startswith('/static/'):
            possible_paths.append(src[1:])  # Remove leading /

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    @staticmethod
    def _image_to_base64(file_path):
        """
        Convert image file to base64 data URI

        Args:
            file_path (str): Path to image file

        Returns:
            str: Base64 data URI
        """
        # Determine MIME type from extension
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')

        # Read and encode image
        with open(file_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')

        return f"data:{mime_type};base64,{base64_data}"

    @staticmethod
    def save_uploaded_image(file, filename):
        """
        Save uploaded image to static folder

        Args:
            file: File object from request.files
            filename (str): Desired filename

        Returns:
            str: Path to saved file
        """
        # Ensure images directory exists
        images_dir = os.path.join('static', 'images')
        os.makedirs(images_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(images_dir, filename)
        file.save(filepath)

        return filepath

    @staticmethod
    def get_image_url(filename):
        """
        Get the appropriate URL for an image based on environment

        Args:
            filename (str): Image filename

        Returns:
            str: URL or data URI depending on environment
        """
        strategy = Config.get_image_strategy()

        if strategy == 'base64':
            # Return base64 data URI
            filepath = os.path.join('static', 'images', filename)
            if os.path.exists(filepath):
                return ImageHandler._image_to_base64(filepath)
            return None
        else:
            # Return external URL
            return Config.get_static_url(f"images/{filename}")
