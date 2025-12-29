"""
Configuration management for development and production environments

CRC: crc-Config.md
Spec: phase-2-campaign-management.md
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration with environment detection"""

    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

    # URLs
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5001')
    STATIC_URL = os.getenv('STATIC_URL', f"{BASE_URL}/static")

    # Email Service
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_NAME = os.getenv('SENDER_NAME', 'Your Business')
    BUSINESS_ADDRESS = os.getenv('BUSINESS_ADDRESS', '')

    # SMS Service
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

    # Image Strategy
    IMAGE_STRATEGY = os.getenv('IMAGE_STRATEGY', 'base64' if ENV == 'development' else 'external')

    # App Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    @staticmethod
    def is_production():
        """Check if running in production environment"""
        return Config.ENV == 'production'

    @staticmethod
    def is_development():
        """Check if running in development environment"""
        return Config.ENV == 'development'

    @staticmethod
    def get_image_strategy():
        """
        Get the image handling strategy for emails

        Returns:
            str: 'base64' for development, 'external' for production
        """
        return Config.IMAGE_STRATEGY

    @staticmethod
    def get_full_url(path):
        """
        Convert a relative path to a full URL

        Args:
            path (str): Relative path (e.g., '/static/images/logo.png')

        Returns:
            str: Full URL with base URL prepended
        """
        if path.startswith('http'):
            return path
        return f"{Config.BASE_URL}{path}"

    @staticmethod
    def get_static_url(filename):
        """
        Get full URL for a static file

        Args:
            filename (str): Filename in static folder (e.g., 'images/logo.png')

        Returns:
            str: Full URL to static file
        """
        return f"{Config.STATIC_URL}/{filename}"


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    IMAGE_STRATEGY = 'base64'


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    IMAGE_STRATEGY = 'external'


# Select appropriate config based on environment
def get_config():
    """Get configuration object based on environment"""
    if Config.is_production():
        return ProductionConfig
    return DevelopmentConfig
