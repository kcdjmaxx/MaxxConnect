# ImageHandler
**Source Spec:** phase-2-campaign-management.md

## Responsibilities
### Knows
- Image MIME types mapping (.jpg, .png, .gif, .svg, .webp)
- Static images directory path ('static/images/')

### Does
- process_html_images(html_content): Process images based on environment strategy
- _convert_to_base64(html_content): Convert local images to base64 data URIs
- _convert_to_external_urls(html_content): Convert local paths to external URLs
- _resolve_image_path(src): Resolve relative image path to absolute file path
- _image_to_base64(file_path): Convert image file to base64 data URI
- save_uploaded_image(file, filename): Save uploaded image to static folder
- get_image_url(filename): Get appropriate URL based on environment

## Collaborators
- Config: Determines image strategy (base64 vs external)
- Campaign: Provides HTML content for image processing

## Sequences
- seq-campaign-create.md: Image processing during template rendering
- seq-campaign-send.md: Image processing during email generation

## Implementation
- **Source:** `backend/image_handler.py`
