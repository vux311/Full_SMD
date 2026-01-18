from celery import shared_task
import time
import logging
from services.ai_service import AiService
from dependency_container import Container

logger = logging.getLogger(__name__)

@shared_task(ignore_result=False)
def analyze_clo_plo_task(clo_list, plo_list):
    """
    Background task to analyze CLO-PLO mapping using Gemini AI.
    """
    container = Container()
    ai_service = container.ai_service()
    
    # In a real scenario, this might take 10-20 seconds
    result = ai_service.analyze_clo_plo_mapping(clo_list, plo_list)
    return result

@shared_task(ignore_result=False)
def generate_syllabus_summary_task(content):
    """
    Background task to generate a summary for a syllabus.
    """
    container = Container()
    ai_service = container.ai_service()
    
    result = ai_service.summarize_syllabus(content)
    return result

@shared_task(ignore_result=False)
def compare_syllabuses_task(content_old, content_new):
    """
    Background task to compare two syllabus versions.
    """
    container = Container()
    ai_service = container.ai_service()
    
    result = ai_service.compare_versions(content_old, content_new)
    return result

@shared_task(ignore_result=True)
def check_deadlines_periodic_task():
    """
    Periodic task to check for overdue syllabus deadlines and send notifications.
    """
    container = Container()
    syllabus_service = container.syllabus_service()
    
    logger.info("Starting periodic deadline check...")
    count = syllabus_service.check_workflow_deadlines()
    logger.info(f"Deadline check completed. {count} notifications sent.")
    return count
