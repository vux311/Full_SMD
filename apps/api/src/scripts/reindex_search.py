import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from config import Config
from infrastructure.databases import init_db
from infrastructure.databases.mssql import session
from infrastructure.models.syllabus_model import Syllabus
from services.search_service import SearchService
from dependency_container import Container

def reindex_all():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    
    with app.app_context():
        search_service = SearchService()
        syllabuses = session.query(Syllabus).all()
        print(f"Found {len(syllabuses)} syllabuses in database.")
        
        count = 0
        for s in syllabuses:
            try:
                content = {
                    "subject_code": s.subject.code if s.subject else "",
                    "subject_name_vi": s.subject.name_vi if s.subject else "",
                    "description": s.description or "",
                    "status": s.status,
                    "version": s.version,
                    "program_name": s.program.name if s.program else "",
                    "academic_year": s.academic_year.code if s.academic_year else "",
                    "content": s.description or ""
                }
                search_service.index_syllabus(s.id, content)
                count += 1
                if count % 10 == 0:
                    print(f"Indexed {count} syllabuses...")
            except Exception as e:
                print(f"Error indexing syllabus {s.id}: {e}")
        
        print(f"Success! Indexed {count} syllabuses to Elasticsearch.")

if __name__ == "__main__":
    reindex_all()
