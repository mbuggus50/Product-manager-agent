from typing import Dict, List, Any, TypedDict, Optional
import logging

from langgraph.graph import StateGraph
from agents.validation_agent import ValidationAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define state structure for validation node
class ValidationState(TypedDict):
    """State maintained during validation."""
    requirement_data: Dict[str, Any]
    validation_results: Optional[Dict[str, Any]]
    messages: List[Dict[str, str]]
    current_node: str
    error: Optional[str]

# Workflow states
VALIDATION_NODE = "validation"
NEXT_NODE = "next_node"  # Placeholder for whatever comes after validation
ERROR_NODE = "error"

def validation_node(state: ValidationState) -> Dict[str, Any]:
    """
    LangGraph node function for validation.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        Updated state with validation results
    """
    logger.info("Executing validation node")
    
    try:
        # Create the validation agent
        agent = ValidationAgent()
        
        # Validate the input
        validation_results = agent.validate(state["requirement_data"])
        
        # Update the state
        return {
            "validation_results": validation_results,
            "messages": state["messages"] + [
                {"role": "system", "content": f"Validation complete: {validation_results['is_valid']}"}
            ],
            "current_node": VALIDATION_NODE
        }
    except Exception as e:
        logger.error(f"Error in validation node: {str(e)}")
        return {
            "error": f"Error in validation node: {str(e)}",
            "current_node": ERROR_NODE,
            "messages": state["messages"] + [
                {"role": "system", "content": f"Error during validation: {str(e)}"}
            ]
        }

def determine_next_step(state: ValidationState) -> str:
    """
    Determine the next node after validation.
    
    Args:
        state: The current workflow state
        
    Returns:
        Next node name
    """
    if state.get("error"):
        return ERROR_NODE
    
    validation_results = state.get("validation_results", {})
    is_valid = validation_results.get("is_valid", False)
    
    return NEXT_NODE if is_valid else ERROR_NODE

# Set up a simplified LangGraph workflow
def create_validation_workflow():
    """
    Create a LangGraph workflow for validation.
    
    Returns:
        Compiled workflow
    """
    # Create the state graph
    workflow = StateGraph(ValidationState)
    
    # Add nodes
    workflow.add_node(VALIDATION_NODE, validation_node)
    workflow.add_node(NEXT_NODE, lambda x: x)  # Placeholder for next step
    workflow.add_node(ERROR_NODE, lambda x: x)  # Placeholder for error handling
    
    # Add conditional edges
    workflow.add_conditional_edges(
        VALIDATION_NODE,
        determine_next_step,
        {
            NEXT_NODE: lambda state: state.get("validation_results", {}).get("is_valid", False),
            ERROR_NODE: lambda state: not state.get("validation_results", {}).get("is_valid", False)
        }
    )
    
    # Set entry point
    workflow.set_entry_point(VALIDATION_NODE)
    
    # Compile the workflow
    return workflow.compile()

# Example function to execute validation workflow
def execute_validation(requirement_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the validation workflow with the given requirement data.
    
    Args:
        requirement_data: The requirement data to validate
        
    Returns:
        Validation results
    """
    logger.info("Starting validation workflow")
    
    # Initialize the state
    initial_state = ValidationState(
        requirement_data=requirement_data,
        validation_results=None,
        messages=[],
        current_node="",
        error=None
    )
    
    # Create and execute the workflow
    app = create_validation_workflow()
    for state in app.stream(initial_state):
        logger.debug(f"Workflow state: {state['current_node']}")
    
    # Get the final state
    final_state = state
    
    # Create a simplified result
    result = {
        "success": final_state["current_node"] == NEXT_NODE,
        "validation_results": final_state.get("validation_results", {}),
        "messages": final_state["messages"],
        "error": final_state.get("error")
    }
    
    logger.info(f"Validation workflow complete: {result['success']}")
    return result

# Example usage
if __name__ == "__main__":
    test_input = {
        "business_need": "We need to track foreign bank account indicators for tax filing customers to enable personalized expert matching for customers with complex tax situations.",
        "requirements": "To hyperpersonalize PY expert match use cases. Post engagement, no action, FS only, should trigger when a customer who auths in, but doesn't take any action like uploading a document OR expert chat OR expert call for over 5 days",
        "business_impact": "CS will not be able to launch certain aspects of their PY Expert Match campaign without this data. The data will be used for both segmentation and personalization",
        "delivery_date": "02/28/2025",
        "campaign_date": "03/05/2025",
        "contributors": ["Sarah Johnson", "Data Analytics Team"]
    }
    
    result = execute_validation(test_input)
    print("Workflow result:", result)