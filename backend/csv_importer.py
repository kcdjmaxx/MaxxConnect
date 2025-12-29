import pandas as pd
from backend.database import SessionLocal
from backend.models import Customer
from backend.sms_service import format_phone_number, validate_phone_number
import re
from datetime import datetime

def is_valid_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def import_csv(file_path, segment_tag=None):
    """
    Import contacts from CSV with deduplication

    Supports two CSV formats:
    1. Simple format: email,name,phone
    2. Square export format: Email Address,First Name,Last Name,Phone Number,...
    """
    db = SessionLocal()

    try:
        # Read CSV
        df = pd.read_csv(file_path)

        # Map Square column names to our expected names
        column_mapping = {
            'Email Address': 'email',
            'Phone Number': 'phone',
            'First Name': 'first_name',
            'Last Name': 'last_name'
        }

        # Rename columns if they match Square format
        df.rename(columns=column_mapping, inplace=True)

        # Validate that we have email column
        if 'email' not in df.columns:
            raise ValueError("CSV must have 'email' or 'Email Address' column")

        # Combine first_name and last_name into name if they exist
        if 'first_name' in df.columns or 'last_name' in df.columns:
            first = df.get('first_name', pd.Series([''] * len(df))).fillna('')
            last = df.get('last_name', pd.Series([''] * len(df))).fillna('')
            df['name'] = (first.astype(str) + ' ' + last.astype(str)).str.strip()

        # Drop rows with missing emails
        df = df.dropna(subset=['email'])

        # Normalize emails (lowercase, strip whitespace)
        df['email'] = df['email'].astype(str).str.strip().str.lower()

        # Remove invalid emails
        df = df[df['email'].apply(is_valid_email)]

        # Process phone numbers if column exists
        has_phone = 'phone' in df.columns
        if has_phone:
            # Fill NaN with empty string
            df['phone'] = df['phone'].fillna('')
            # Convert to string and strip whitespace
            df['phone'] = df['phone'].astype(str).str.strip()

        # Remove duplicates within CSV
        df = df.drop_duplicates(subset=['email'])

        stats = {
            'total_rows': len(df),
            'added': 0,
            'updated': 0,
            'invalid': 0
        }

        for _, row in df.iterrows():
            email = row['email']
            name = row.get('name', '')
            phone_raw = row.get('phone', '') if has_phone else ''

            # Format phone number if provided
            phone = None
            if phone_raw and phone_raw != 'nan' and phone_raw != '':
                formatted = format_phone_number(phone_raw)
                if formatted and validate_phone_number(formatted):
                    phone = formatted

            # Check if customer exists
            existing = db.query(Customer).filter_by(email=email).first()

            if existing:
                # Update name if provided and not already set
                if name and not existing.name:
                    existing.name = name

                # Update phone if provided and not already set
                if phone and not existing.phone:
                    existing.phone = phone
                    # Auto-subscribe to SMS if phone is added
                    existing.sms_subscribed = True
                    existing.sms_opted_in_date = datetime.now()

                # Add segment tag if provided
                if segment_tag:
                    tags = set(existing.segments.split(',')) if existing.segments else set()
                    tags.add(segment_tag)
                    existing.segments = ','.join(filter(None, tags))

                existing.updated_at = datetime.now()
                stats['updated'] += 1
            else:
                # Create new customer
                customer = Customer(
                    email=email,
                    phone=phone,
                    name=name,
                    segments=segment_tag if segment_tag else '',
                    subscribed=True,
                    sms_subscribed=True if phone else False,
                    sms_opted_in_date=datetime.now() if phone else None
                )
                db.add(customer)
                stats['added'] += 1

        db.commit()
        return stats

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
