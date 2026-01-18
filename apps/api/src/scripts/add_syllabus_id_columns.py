"""
Migration script: Add dean_id and head_department_id to syllabuses table
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

def add_columns():
    # Create engine and session
    engine = create_engine(Config.DATABASE_URI, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("🔄 Adding ID columns to syllabuses table...")
        
        # Check if columns already exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'syllabuses'
        """)
        
        result = session.execute(check_query)
        existing_columns = [row[0] for row in result]
        
        columns_to_add = [
            ("dean_id", "BIGINT REFERENCES users(id)"),
            ("head_department_id", "BIGINT REFERENCES users(id)")
        ]
        
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"➕ Adding column: {col_name}")
                # SQL Server syntax: ALTER TABLE table ADD col_name type
                session.execute(text(f"ALTER TABLE syllabuses ADD {col_name} {col_type}"))
            else:
                print(f"✅ Column {col_name} already exists")
        
        session.commit()
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during migration: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    add_columns()
