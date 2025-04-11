# requirements_automation/app.py

import json
import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from app.agents.base import ExecutiveState
from app.agents.executive_supervisor import create_executive_workflow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("requirements-automation")

class RequirementsAutomationSystem:
    """
    Main application class for the Requirements Automation System.
    """
    
    def __init__(self, debug=False):
        """Initialize the system."""
        self.executive_workflow = create_executive_workflow()
        self.debug = debug
        logger.info("Requirements Automation System initialized")
    
    def process_requirements(self, requirements_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requirements data through the entire workflow.
        
        Args:
            requirements_data: Dictionary containing the requirements data
            
        Returns:
            Dictionary with the results of the processing
        """
        logger.info("Starting requirements processing workflow")
        
        # Create initial state
        initial_state = ExecutiveState(
            input_requirements=requirements_data,
            status="initialized"
        )
        
        try:
            # Run the executive workflow
            result = self.executive_workflow.invoke(initial_state)
            
            # Log results
            logger.info(f"Workflow completed with status: {result.status}")
            if result.is_error():
                logger.error(f"Workflow error: {result.error}")
            
            # Return results
            return {
                "status": result.status,
                "error": result.error,
                "validation_results": result.validation_results,
                "content_results": result.content_results,
                "integration_results": result.integration_results,
                "final_output": result.final_output,
                "metadata": result.metadata
            }
            
        except Exception as e:
            logger.exception(f"Error processing requirements: {e}")
            return {
                "status": "error",
                "error": str(e),
                "validation_results": None,
                "content_results": None,
                "integration_results": None,
                "final_output": None,
                "metadata": {}
            }
    
    def load_requirements_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load requirements data from a file (JSON or text).
        
        Args:
            file_path: Path to the requirements file
            
        Returns:
            Dictionary with the loaded requirements data
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle different file types
        if path.suffix.lower() == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        else:
            # Assume text file
            with open(path, 'r') as f:
                text_content = f.read()
                # Convert text to a simple dict structure
                return {
                    "type": "text",
                    "content": text_content,
                    "file_name": path.name
                }
    
    def save_results_to_file(self, results: Dict[str, Any], file_path: str) -> None:
        """
        Save processing results to a file.
        
        Args:
            results: Dictionary with processing results
            file_path: Path to save the results file
        """
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {file_path}")