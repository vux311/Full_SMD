"""
Migration script: Add content columns to syllabuses table
Adds: description, objectives, student_duties, other_requirements, 
      pre_courses, co_courses, course_type, component_type,
      date_prepared, date_edited, dean, head_department
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
        print("🔄 Adding content columns to syllabuses table...")
        
        # Check if columns already exist
        check_query = text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'syllabuses' 
            AND COLUMN_NAME IN ('description', 'objectives', 'student_duties')
        """)
        
        existing = session.execute(check_query).fetchall()
        if existing:
            print(f"⚠️  Some columns already exist: {[row[0] for row in existing]}")
            print("Skipping migration...")
            return
        
        # Add new columns
        alter_queries = [
            "ALTER TABLE syllabuses ADD description NVARCHAR(MAX) NULL",
            "ALTER TABLE syllabuses ADD objectives NVARCHAR(MAX) NULL",
            "ALTER TABLE syllabuses ADD student_duties NVARCHAR(MAX) NULL",
            "ALTER TABLE syllabuses ADD other_requirements NVARCHAR(MAX) NULL",
            "ALTER TABLE syllabuses ADD pre_courses NVARCHAR(MAX) NULL",
            "ALTER TABLE syllabuses ADD co_courses NVARCHAR(MAX) NULL",
            "ALTER TABLE syllabuses ADD course_type NVARCHAR(50) NULL",
            "ALTER TABLE syllabuses ADD component_type NVARCHAR(100) NULL",
            "ALTER TABLE syllabuses ADD date_prepared NVARCHAR(20) NULL",
            "ALTER TABLE syllabuses ADD date_edited NVARCHAR(20) NULL",
            "ALTER TABLE syllabuses ADD dean NVARCHAR(255) NULL",
            "ALTER TABLE syllabuses ADD head_department NVARCHAR(255) NULL",
        ]
        
        for query in alter_queries:
            print(f"   Executing: {query}")
            session.execute(text(query))
        
        session.commit()
        print("✅ Successfully added all columns!")
        
        # Verify
        verify_query = text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'syllabuses' 
            AND COLUMN_NAME IN ('description', 'objectives', 'student_duties', 
                                'other_requirements', 'pre_courses', 'co_courses',
                                'course_type', 'component_type', 'date_prepared',
                                'date_edited', 'dean', 'head_department')
            ORDER BY COLUMN_NAME
        """)
        
        results = session.execute(verify_query).fetchall()
        print("\n📋 Verified columns:")
        for row in results:
            print(f"   - {row[0]}: {row[1]} (nullable={row[2]})")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    add_columns()
