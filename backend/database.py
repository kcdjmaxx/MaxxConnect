from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

# Fix Railway's postgres:// URL to postgresql:// for SQLAlchemy
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

def init_db():
    """Initialize database tables"""
    # Import all models to register them with Base.metadata
    from backend.models import Customer, Campaign, CampaignSend, QRCode, EmailDelivery, Redemption
    Base.metadata.create_all(bind=engine)
