"""
Simple migration to add hashes in small batches
"""
import hashlib
from backend.database import get_db, engine
from backend.models import Customer
from sqlalchemy import text

# Step 1: Add columns
print("Step 1: Adding columns...")
with engine.begin() as conn:  # Use begin() for auto-commit
    try:
        conn.execute(text("ALTER TABLE customers ADD COLUMN email_hash VARCHAR(64)"))
        print("  Added email_hash")
    except:
        print("  email_hash already exists")

    try:
        conn.execute(text("ALTER TABLE customers ADD COLUMN phone_hash VARCHAR(64)"))
        print("  Added phone_hash")
    except:
        print("  phone_hash already exists")

# Step 2: Populate hashes in small batches
print("\nStep 2: Populating hashes...")
BATCH_SIZE = 100
offset = 0

while True:
    db = get_db()
    try:
        # Get batch of customers
        customers = db.query(Customer).offset(offset).limit(BATCH_SIZE).all()

        if not customers:
            break

        print(f"  Processing customers {offset+1} to {offset+len(customers)}...")

        for customer in customers:
            try:
                email = customer.email
                phone = customer.phone

                if email and not customer.email_hash:
                    customer.email_hash = hashlib.sha256(email.encode()).hexdigest()

                if phone and not customer.phone_hash:
                    customer.phone_hash = hashlib.sha256(phone.encode()).hexdigest()

            except Exception as e:
                print(f"    Error with customer {customer.id}: {e}")
                continue

        # Commit this batch
        db.commit()
        offset += BATCH_SIZE

    except Exception as e:
        print(f"  Error processing batch: {e}")
        db.rollback()
        break
    finally:
        db.close()

print("\n✅ Migration complete!")

# Verify
db = get_db()
sample = db.query(Customer).first()
print(f"\nVerification:")
print(f"  Sample email: {sample.email}")
print(f"  Sample hash: {sample.email_hash}")
db.close()
