"""Requirement model with status tracking."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List, Any

class RequirementStatus(Enum):
    """Status of a requirement in the processing pipeline."""
    PENDING = "pending"
    PROCESSING = "processing"
    VALIDATION = "validation"
    DESIGN = "design"
    DOCUMENT = "document"
    FORMATTING = "formatting"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class RequirementStep:
    """A step in the requirement processing pipeline."""
    name: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    details: Optional[Dict] = None
    error: Optional[str] = None

@dataclass
class Requirement:
    """Representation of a product requirement with status tracking."""
    id: str
    title: str
    description: str
    status: RequirementStatus
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    steps: List[RequirementStep] = None
    result_url: Optional[str] = None
    
    # Additional fields matching frontend
    business_impact: Optional[str] = None
    delivery_date: Optional[str] = None
    campaign_date: Optional[str] = None
    document_links: Dict[str, str] = field(default_factory=dict)
    priority: str = "medium"
    owner: Optional[str] = None
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize steps if not provided."""
        if self.steps is None:
            self.steps = [
                RequirementStep(name="validation", status="pending"),
                RequirementStep(name="design", status="pending"),
                RequirementStep(name="document", status="pending"),
                RequirementStep(name="formatting", status="pending")
            ]
        
        # Set owner from user_id if not provided
        if not self.owner and self.user_id:
            self.owner = self.user_id
    
    def update_step_status(self, step_name: str, status: str, details: Optional[Dict] = None, error: Optional[str] = None):
        """Update the status of a processing step."""
        for step in self.steps:
            if step.name == step_name:
                step.status = status
                if status == "completed" and not step.end_time:
                    step.end_time = datetime.now()
                if status == "processing" and not step.start_time:
                    step.start_time = datetime.now()
                if details:
                    step.details = details
                if error:
                    step.error = error
                self.updated_at = datetime.now()
                return True
        return False
    
    def add_feedback(self, feedback_type: str, message: str):
        """Add feedback to the requirement."""
        self.feedback.append({
            "id": f"feedback-{len(self.feedback) + 1}",
            "type": feedback_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self):
        """Convert the requirement to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "user_id": self.user_id,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "details": step.details,
                    "error": step.error
                } for step in self.steps
            ],
            "result_url": self.result_url,
            "business_impact": self.business_impact,
            "delivery_date": self.delivery_date,
            "campaign_date": self.campaign_date,
            "document_links": self.document_links,
            "priority": self.priority,
            "owner": self.owner,
            "feedback": self.feedback,
            "businessNeed": self.title,  # For frontend compatibility
            "requirements": self.description  # For frontend compatibility
        }