# Constants

# Define any constants used throughout the application here. 
# For example, you might define API version, error messages, or configuration keys.

API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Workflow Status Constants
class WorkflowStatus:
    """Syllabus workflow status constants."""
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    PENDING_APPROVAL = 'PENDING APPROVAL'
    PENDING_FINAL_APPROVAL = 'PENDING FINAL APPROVAL'
    APPROVED = 'APPROVED'
    PUBLISHED = 'PUBLISHED'
    REJECTED = 'REJECTED'
    RETURNED = 'RETURNED'
    
    # Valid states for each action
    VALID_FOR_SUBMISSION = (DRAFT, RETURNED, REJECTED)
    VALID_FOR_EVALUATION = (PENDING, PENDING_APPROVAL, PENDING_FINAL_APPROVAL)
    PUBLIC_STATUSES = (APPROVED, PUBLISHED)
    
    ALL_STATES = (DRAFT, PENDING, PENDING_APPROVAL, PENDING_FINAL_APPROVAL, APPROVED, PUBLISHED, REJECTED, RETURNED)

# Add more constants as needed for your application.