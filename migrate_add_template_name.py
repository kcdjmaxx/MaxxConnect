#!/usr/bin/env python3
"""
Migration script to add template_name column to campaigns table
Run this once to update your database schema
"""

from backend.database import get_db
from sqlalchemy import text

def migrate():
    db = get_db()
    try:
        # Check if column already exists
        result = db.execute(text("PRAGMA table_info(campaigns)"))
        columns = [row[1] for row in result]

        if 'template_name' not in columns:
            print("Adding template_name column to campaigns table...")
            db.execute(text("ALTER TABLE campaigns ADD COLUMN template_name VARCHAR(255)"))
            db.commit()
            print("✓ Migration completed successfully!")
        else:
            print("✓ Column already exists, no migration needed.")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    migrate()
