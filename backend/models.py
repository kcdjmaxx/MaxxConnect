"""
Database Models - Customer and Campaign entities

CRC: crc-Customer.md, crc-Campaign.md
Spec: phase-2-campaign-management.md
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from backend.database import Base
from backend.encryption import encrypt_string, decrypt_string
import hashlib

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    _email_encrypted = Column('email', String(500), unique=True, nullable=False, index=True)  # Encrypted storage
    email_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hash for lookups
    _phone_encrypted = Column('phone', String(500), nullable=True, index=True)  # Encrypted storage
    phone_hash = Column(String(64), unique=True, nullable=True, index=True)  # SHA-256 hash for lookups
    name = Column(String(255))

    # Email property with automatic encryption/decryption
    @hybrid_property
    def email(self):
        """Decrypt email when reading"""
        return decrypt_string(self._email_encrypted) if self._email_encrypted else None

    @email.setter
    def email(self, value):
        """Encrypt email and generate hash when writing"""
        if value:
            self._email_encrypted = encrypt_string(value)
            self.email_hash = hashlib.sha256(value.encode()).hexdigest()
        else:
            self._email_encrypted = None
            self.email_hash = None

    @email.expression
    def email(cls):
        """Allow querying by encrypted email"""
        return cls._email_encrypted

    # Phone property with automatic encryption/decryption
    @hybrid_property
    def phone(self):
        """Decrypt phone when reading"""
        return decrypt_string(self._phone_encrypted) if self._phone_encrypted else None

    @phone.setter
    def phone(self, value):
        """Encrypt phone and generate hash when writing"""
        if value:
            self._phone_encrypted = encrypt_string(value)
            self.phone_hash = hashlib.sha256(value.encode()).hexdigest()
        else:
            self._phone_encrypted = None
            self.phone_hash = None

    @phone.expression
    def phone(cls):
        """Allow querying by encrypted phone"""
        return cls._phone_encrypted

    # Email subscription
    subscribed = Column(Boolean, default=True)
    opted_in_date = Column(DateTime, default=func.now())
    unsubscribed_date = Column(DateTime, nullable=True)

    # SMS subscription
    sms_subscribed = Column(Boolean, default=False)
    sms_opted_in_date = Column(DateTime, nullable=True)
    sms_unsubscribed_date = Column(DateTime, nullable=True)

    segments = Column(Text)  # Comma-separated tags
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Customer {self.email}>"

    def get_unsubscribe_token(self):
        """Generate secure unsubscribe token"""
        data = f"{self.id}:{self.email}".encode()
        return hashlib.sha256(data).hexdigest()

    def get_sms_optout_token(self):
        """Generate secure SMS opt-out token"""
        data = f"{self.id}:{self.phone}".encode()
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def find_by_email(cls, db_session, email):
        """Find customer by email (uses hash for lookup)"""
        email_hash = hashlib.sha256(email.encode()).hexdigest()
        return db_session.query(cls).filter(cls.email_hash == email_hash).first()

    @classmethod
    def find_by_phone(cls, db_session, phone):
        """Find customer by phone (uses hash for lookup)"""
        phone_hash = hashlib.sha256(phone.encode()).hexdigest()
        return db_session.query(cls).filter(cls.phone_hash == phone_hash).first()

class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    template_name = Column(String(255), nullable=True)  # Email template filename
    html_content = Column(Text, nullable=False)
    has_qr_code = Column(Boolean, default=False)  # Whether campaign includes QR codes
    status = Column(String(50), default='draft')  # draft, sent, sending
    sent_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Campaign {self.name}>"

    def requires_qr_generation(self):
        """Check if campaign needs QR codes during send"""
        return self.has_qr_code is True


class CampaignSend(Base):
    """
    Track progress of a campaign send operation

    CRC: crc-CampaignManager.md
    Seq: seq-campaign-send.md
    """
    __tablename__ = 'campaign_sends'

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, nullable=False, index=True)
    total_emails = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    emails_failed = Column(Integer, default=0)
    total_sms = Column(Integer, default=0)
    sms_sent = Column(Integer, default=0)
    sms_failed = Column(Integer, default=0)
    status = Column(String(50), default='pending')  # pending, sending, completed, failed
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    def progress_percent(self):
        """Calculate percentage of messages processed"""
        total = self.total_emails + self.total_sms
        processed = self.emails_sent + self.sms_sent + self.emails_failed + self.sms_failed
        return int((processed / total * 100)) if total > 0 else 0

    def is_complete(self):
        """Check if all messages have been processed"""
        total = self.total_emails + self.total_sms
        processed = self.emails_sent + self.sms_sent + self.emails_failed + self.sms_failed
        return processed >= total

    def __repr__(self):
        return f"<CampaignSend campaign_id={self.campaign_id} {self.emails_sent}/{self.total_emails}>"
