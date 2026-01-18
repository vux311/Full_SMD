import os
import sys

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.databases.mssql import SessionLocal
from sqlalchemy import text

def add_created_at_column():
    session = SessionLocal()
    try:
        # Check if column exists
        result = session.execute(text("""
            IF NOT EXISTS (
                SELECT * FROM sys.columns 
                WHERE object_id = OBJECT_ID('student_reports') 
                AND name = 'created_at'
            )
            BEGIN
                ALTER TABLE student_reports ADD created_at DATETIME DEFAULT GETDATE();
            END
        """))
        session.commit()
        print("Successfully added created_at column to student_reports table")
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    add_created_at_column()
