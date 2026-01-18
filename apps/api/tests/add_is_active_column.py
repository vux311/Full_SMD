"""
Migration script to add is_active column to academic_years table
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import sys

load_dotenv()

def add_is_active_column():
    try:
        # Use the same DATABASE_URI from .env
        database_uri = os.getenv('DATABASE_URI')
        if not database_uri:
            print("✗ DATABASE_URI not found in .env")
            return False
        
        # Connect to database
        engine = create_engine(database_uri)
        conn = engine.connect()
        
        # Check if column exists
        result = conn.execute(text("""
            SELECT COUNT(*) as cnt
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'academic_years' 
            AND COLUMN_NAME = 'is_active'
        """))
        
        exists = result.fetchone()[0]
        
        if exists:
            print("✓ Column 'is_active' already exists in academic_years table")
        else:
            # Add the column
            conn.execute(text("""
                ALTER TABLE academic_years
                ADD is_active BIT NOT NULL DEFAULT 0
            """))
            conn.commit()
            print("✓ Successfully added 'is_active' column to academic_years table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_is_active_column()
    sys.exit(0 if success else 1)
