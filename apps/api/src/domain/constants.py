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
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    
    # Valid states for each action
    VALID_FOR_SUBMISSION = (DRAFT, REJECTED)
    VALID_FOR_EVALUATION = (PENDING,)
    
    ALL_STATES = (DRAFT, PENDING, APPROVED, REJECTED)

# Add more constants as needed for your application.