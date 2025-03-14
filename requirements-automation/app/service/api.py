"""API service for the requirements automation system."""
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
import logging
import sys
import os

# Ensure app module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.requirement import Requirement, RequirementStatus, RequirementStep


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In-memory storage for development (would use a database in production)
_requirements: Dict[str, Requirement] = {}


def get_requirements_by_user(user_id: str) -> List[Requirement]:
    """Get all requirements for a user."""
    return [req for req in _requirements.values() if req.user_id == user_id]


def get_requirement_by_id(req_id: str) -> Optional[Requirement]:
    """Get a requirement by ID."""
    return _requirements.get(req_id)


def create_requirement(data: Dict[str, Any]) -> Requirement:
    """Create a new requirement."""
    # Create requirement ID
    req_id = str(uuid.uuid4())
    
    # Create requirement
    requirement = Requirement(
        id=req_id,
        title=data.get('businessNeed', 'Untitled Requirement'),
        description=data.get('requirements', ''),
        status=RequirementStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_id=data.get('user_id')
    )
    
    # Additional data
    requirement.business_impact = data.get('businessImpact', '')
    requirement.delivery_date = data.get('deliveryDate', '')
    requirement.campaign_date = data.get('campaignDate', '')
    
    # Store requirement
    _requirements[req_id] = requirement
    
    logger.info(f"Created requirement: {req_id}")
    
    return requirement


def update_requirement_status(req_id: str, status: RequirementStatus) -> bool:
    """Update the status of a requirement."""
    requirement = get_requirement_by_id(req_id)
    if not requirement:
        return False
    
    requirement.status = status
    requirement.updated_at = datetime.now()
    
    logger.info(f"Updated requirement status: {req_id} -> {status.value}")
    
    return True


def update_step_status(req_id: str, step_name: str, status: str, 
                     details: Optional[Dict] = None, error: Optional[str] = None) -> bool:
    """Update the status of a step in a requirement."""
    requirement = get_requirement_by_id(req_id)
    if not requirement:
        return False
    
    result = requirement.update_step_status(step_name, status, details, error)
    
    if result:
        logger.info(f"Updated step status: {req_id} -> {step_name} -> {status}")
    
    return result


def add_document_link(req_id: str, doc_type: str, url: str) -> bool:
    """Add a document link to a requirement."""
    requirement = get_requirement_by_id(req_id)
    if not requirement:
        return False
    
    if not hasattr(requirement, 'document_links'):
        requirement.document_links = {}
    
    requirement.document_links[doc_type] = url
    requirement.updated_at = datetime.now()
    
    logger.info(f"Added document link: {req_id} -> {doc_type}")
    
    return True


def get_all_requirements() -> List[Requirement]:
    """Get all requirements (admin only)."""
    return list(_requirements.values())


# Add some seed data for testing
def _create_sample_requirements():
    """Create sample requirements for testing."""
    # User 1 requirements
    for i in range(1, 4):
        req = Requirement(
            id=f"sample-{i}",
            title=f"Sample Requirement {i}",
            description=f"This is a sample requirement {i} for testing purposes.",
            status=RequirementStatus.COMPLETED if i == 1 else
                  RequirementStatus.PROCESSING if i == 2 else
                  RequirementStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user_id="admin"
        )
        req.business_impact = "High business impact for testing"
        req.delivery_date = "2023-06-01"
        req.campaign_date = "2023-07-01"
        
        if i == 1:  # Completed requirement
            req.result_url = "https://docs.google.com/document/d/sample"
            for step in req.steps:
                req.update_step_status(step.name, "completed")
        
        if i == 2:  # In-progress requirement
            req.update_step_status("validation", "completed")
            req.update_step_status("design", "processing")
        
        _requirements[req.id] = req
    
    # User 2 requirements
    for i in range(4, 6):
        req = Requirement(
            id=f"sample-{i}",
            title=f"User Sample Requirement {i}",
            description=f"This is a sample requirement {i} for user 2.",
            status=RequirementStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user_id="user"
        )
        _requirements[req.id] = req

# Create sample data
_create_sample_requirements()