import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from create_app import create_app
from dependency_container import Container

def run_deadline_check():
    """Script to be run by CRON daily to check for overdue syllabuses"""
    print("Starting Syllabus Deadline Check...")
    
    # Initialize the app and container
    app = create_app()
    with app.app_context():
        container = Container()
        # We need to get the syllabus_service
        syllabus_service = container.syllabus_service()
        
        count = syllabus_service.check_workflow_deadlines()
        print(f"Finished. Sent {count} overdue notifications.")

if __name__ == "__main__":
    run_deadline_check()
