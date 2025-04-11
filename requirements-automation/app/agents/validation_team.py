# requirements_automation/validation_team.py

from typing import Dict, Any, Tuple, List, Optional, TypedDict, Annotated
import json
from pydantic import BaseModel, Field

from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import Tool
from langgraph.checkpoint.memory import MemorySaver

from base import (
    ValidationState, 
    create_llm_node, 
    with_error_handling,
    Config
)

# JSON Schema for validation outputs
class CompletenessCheckResult(BaseModel):
    is_complete: bool = Field(description="Whether the requirements are complete")
    missing_fields: List[str] = Field(default_factory=list, description="List of missing fields")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    completeness_score: float = Field(description="Score from 0-1 indicating completeness")

class QualityCheckResult(BaseModel):
    is_valid: bool = Field(description="Whether the requirements meet quality standards")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Quality issues found")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    quality_score: float = Field(description="Score from 0-1 indicating quality")

class ValidationSummary(BaseModel):
    overall_valid: bool = Field(description="Whether the requirements are valid overall")
    completeness_score: float = Field(description="Completeness score from 0-1")
    quality_score: float = Field(description="Quality score from 0-1")
    overall_score: float = Field(description="Overall validation score from 0-1")
    issues_count: int = Field(description="Total number of issues found")
    critical_issues_count: int = Field(description="Number of critical issues found")
    recommendations: List[str] = Field(default_factory=list, description="Overall recommendations")

# Define the human input tool using LangGraph's built-in support
class RequirementsClarification(TypedDict):
    """Request for clarification on requirements issues"""
    question: str
    context: str


def ask_human_for_clarification(state: ValidationState) -> RequirementsClarification:
    """
    Requests clarification from a human when requirements are invalid.
    This is a special node that will pause graph execution and wait for human input.
    """
    # Extract issues from validation results
    completeness_issues = state.completeness_check.get("missing_fields", []) if state.completeness_check else []
    completeness_recommendations = state.completeness_check.get("recommendations", []) if state.completeness_check else []
    
    quality_issues = state.quality_check.get("issues", []) if state.quality_check else []
    quality_suggestions = state.quality_check.get("suggestions", []) if state.quality_check else []
    
    # Create context information
    context = {
        "completeness_issues": completeness_issues,
        "completeness_recommendations": completeness_recommendations,
        "quality_issues": quality_issues,
        "quality_suggestions": quality_suggestions,
        "preprocessed_data": state.preprocessed_data
    }
    
    # Create the clarification message
    clarification_prompt = """
    The requirements provided need clarification before they can be processed further.
    
    Issues identified:
    """
    
    if completeness_issues:
        clarification_prompt += "\n\nCompleteness Issues:\n- " + "\n- ".join(completeness_issues)
    
    if completeness_recommendations:
        clarification_prompt += "\n\nRecommendations for Completeness:\n- " + "\n- ".join(completeness_recommendations)
    
    if quality_issues:
        issues_text = []
        for issue in quality_issues:
            if isinstance(issue, dict):
                issue_str = f"{issue.get('requirement_id', 'Unknown')}: {issue.get('description', 'No description')}"
                issues_text.append(issue_str)
            else:
                issues_text.append(str(issue))
        
        clarification_prompt += "\n\nQuality Issues:\n- " + "\n- ".join(issues_text)
    
    if quality_suggestions:
        clarification_prompt += "\n\nSuggestions for Improvement:\n- " + "\n- ".join(quality_suggestions)
    
    clarification_prompt += """
    
    Please provide improved requirements that address these issues.
    """
    
    return {"question": clarification_prompt, "context": json.dumps(context)}

# Agent implementations
@with_error_handling
def data_preprocessor(state: ValidationState) -> ValidationState:
    """
    Preprocesses the input requirements data, ensuring it's in a consistent format
    for further processing.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the preprocessor agent
    preprocessor_prompt = """
    You are a Requirements Data Preprocessor. Your job is to:
    1. Parse the incoming requirements data
    2. Normalize the format to a consistent structure
    3. Extract key requirement elements (ID, description, priority, etc.)
    4. Clean up any inconsistencies or formatting issues
    
    Return a JSON object with the preprocessed requirements data.
    """
    
    preprocessor_agent = create_llm_node(
        system_prompt=preprocessor_prompt,
        user_prompt="Process the following requirements data:\n\n{input_data}",
        output_parser=JsonOutputParser()
    )
    
    # Process the input data
    new_state.preprocessed_data = preprocessor_agent.invoke({"input_data": json.dumps(new_state.input_data)})
    new_state.status = "preprocessed"
    
    return new_state

@with_error_handling
def completeness_checker(state: ValidationState) -> ValidationState:
    """
    Checks the completeness of the requirements, ensuring all necessary fields
    and elements are present.
    """
    new_state = state.model_copy(deep=True)
    
    if not new_state.preprocessed_data:
        new_state.status = "error"
        new_state.error = "Missing preprocessed data"
        return new_state
    
    # Define the completeness checker agent
    completeness_prompt = """
    You are a Requirements Completeness Checker. Your job is to:
    1. Analyze the preprocessed requirements data
    2. Check if all mandatory fields are present for each requirement
    3. Verify that all requirements have necessary elements (ID, description, acceptance criteria, etc.)
    4. Identify any missing information or incomplete requirements
    5. Assess the overall completeness of the requirements set
    
    Mandatory fields include:
    - Requirement ID
    - Description
    - Priority or Importance
    - Source or Origin
    - Acceptance Criteria
    
    Return a JSON object with the completeness check results, following this schema:
    {
        "is_complete": boolean,
        "missing_fields": ["field1", "field2", ...],
        "recommendations": ["recommendation1", "recommendation2", ...],
        "completeness_score": float (0-1)
    }
    """
    
    completeness_agent = create_llm_node(
        system_prompt=completeness_prompt,
        user_prompt="Check the completeness of the following preprocessed requirements:\n\n{preprocessed_data}",
        output_parser=JsonOutputParser()
    )
    
    # Check completeness
    new_state.completeness_check = completeness_agent.invoke({"preprocessed_data": json.dumps(new_state.preprocessed_data)})
    new_state.status = "completeness_checked"
    
    return new_state

@with_error_handling
def quality_validator(state: ValidationState) -> ValidationState:
    """
    Validates the quality of requirements, checking for clarity, testability,
    consistency, and other quality attributes.
    """
    new_state = state.model_copy(deep=True)
    
    if not new_state.preprocessed_data:
        new_state.status = "error"
        new_state.error = "Missing preprocessed data"
        return new_state
    
    # Define the quality validator agent
    quality_prompt = """
    You are a Requirements Quality Validator. Your job is to:
    1. Analyze the requirements for quality issues
    2. Check for clarity, unambiguity, consistency, and testability
    3. Identify vague language, contradictions, or implementation details
    4. Assess whether requirements follow SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
    5. Verify proper use of requirement language (shall, should, will, etc.)
    
    Return a JSON object with the quality validation results, following this schema:
    {
        "is_valid": boolean,
        "issues": [
            {"requirement_id": "id", "issue_type": "type", "description": "description", "severity": "high/medium/low"},
            ...
        ],
        "suggestions": ["suggestion1", "suggestion2", ...],
        "quality_score": float (0-1)
    }
    """
    
    quality_agent = create_llm_node(
        system_prompt=quality_prompt,
        user_prompt="Validate the quality of the following requirements:\n\n{preprocessed_data}",
        output_parser=JsonOutputParser()
    )
    
    # Validate quality
    new_state.quality_check = quality_agent.invoke({"preprocessed_data": json.dumps(new_state.preprocessed_data)})
    new_state.status = "quality_validated"
    
    return new_state

@with_error_handling
def validation_finalizer(state: ValidationState) -> ValidationState:
    """
    Finalizes the validation process by combining results from completeness and quality
    checks into a comprehensive validation summary.
    """
    new_state = state.model_copy(deep=True)
    
    if not new_state.completeness_check or not new_state.quality_check:
        new_state.status = "error"
        new_state.error = "Missing completeness or quality check results"
        return new_state
    
    # Define the validation finalizer agent
    finalizer_prompt = """
    You are a Validation Finalizer. Your job is to:
    1. Analyze the results from completeness and quality checks
    2. Synthesize a comprehensive validation summary
    3. Determine if the requirements are valid overall
    4. Calculate an overall validation score
    5. Provide actionable recommendations for improvement
    
    Return a JSON object with the validation summary, following this schema:
    {
        "overall_valid": boolean,
        "completeness_score": float (0-1),
        "quality_score": float (0-1),
        "overall_score": float (0-1),
        "issues_count": integer,
        "critical_issues_count": integer,
        "recommendations": ["recommendation1", "recommendation2", ...]
    }
    """
    
    finalizer_agent = create_llm_node(
        system_prompt=finalizer_prompt,
        user_prompt="""Finalize the validation based on the following results:
        
        Completeness Check:
        {completeness_check}
        
        Quality Check:
        {quality_check}
        """,
        output_parser=JsonOutputParser()
    )
    
    # Finalize validation
    new_state.validation_summary = finalizer_agent.invoke({
        "completeness_check": json.dumps(new_state.completeness_check),
        "quality_check": json.dumps(new_state.quality_check)
    })
    new_state.status = "completed"
    
    return new_state

@with_error_handling
def process_human_clarification(state: ValidationState, clarification_response: str) -> ValidationState:
    """
    Processes the human's clarification response and updates the requirements.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the clarification processor agent
    processor_prompt = """
    You are a Requirements Clarification Processor. Your job is to:
    1. Analyze the user's response to clarification requests
    2. Update the original requirements data based on the clarifications
    3. Ensure all identified issues are addressed
    4. Create an improved version of the requirements data
    
    Return a JSON object with the updated requirements data.
    """
    
    processor_agent = create_llm_node(
        system_prompt=processor_prompt,
        user_prompt="""Process the user's clarification and update the requirements:
        
        Original Requirements Data:
        {preprocessed_data}
        
        Validation Issues:
        {validation_issues}
        
        User's Clarification:
        {clarification_response}
        
        Return the updated requirements data as a complete, structured JSON.
        """,
        output_parser=JsonOutputParser()
    )
    
    # Process the clarification
    validation_issues = {}
    if new_state.completeness_check:
        validation_issues["completeness"] = new_state.completeness_check
    if new_state.quality_check:
        validation_issues["quality"] = new_state.quality_check
    
    # Update the preprocessed data with the clarified information
    updated_data = processor_agent.invoke({
        "preprocessed_data": json.dumps(new_state.preprocessed_data),
        "validation_issues": json.dumps(validation_issues),
        "clarification_response": clarification_response
    })
    
    # Reset validation state to trigger re-validation
    new_state.preprocessed_data = updated_data
    new_state.completeness_check = None
    new_state.quality_check = None
    new_state.validation_summary = None
    new_state.status = "clarified"
    
    return new_state

# Modified validation router to include human-in-the-loop
def validation_router(state: ValidationState) -> str:
    """Routes the workflow based on the current state"""
    if state.is_error():
        return "error"
    
    if not state.preprocessed_data:
        return "preprocess"
    elif not state.completeness_check:
        return "check_completeness"
    elif not state.quality_check:
        return "validate_quality"
    elif not state.validation_summary:
        return "finalize"
    else:
        # Check if validation failed but we haven't requested clarification
        validation_result = state.validation_summary.get("overall_valid", False) if state.validation_summary else False
        
        if not validation_result and state.status != "clarified" and state.status != "awaiting_clarification":
            # Validation failed, request human clarification
            return "request_clarification"
        elif state.status == "awaiting_clarification":
            # Waiting for human input, don't proceed
            return "wait_for_human"
        elif state.status == "clarified":
            # Human provided clarification, restart validation
            return "check_completeness"
        elif validation_result:
            # Validation succeeded
            return "end"
        else:
            # Something unexpected
            return "error"

# Create the Validation Team workflow with human-in-the-loop
def create_validation_workflow() -> StateGraph:
    """Creates the Validation Team workflow graph with human-in-the-loop capability"""
    # Create the workflow
    workflow = StateGraph(ValidationState)
    
    # Add nodes
    workflow.add_node("preprocess", data_preprocessor)
    workflow.add_node("check_completeness", completeness_checker)
    workflow.add_node("validate_quality", quality_validator)
    workflow.add_node("finalize", validation_finalizer)
    
    # Add the human-in-the-loop nodes using LangGraph's built-in support
    # This creates a node that will pause execution and wait for human input
    workflow.add_node("request_clarification", ToolNode(Tool(
    name="ask_human_for_clarification",
    description="Request clarification from a human when requirements are invalid",
    func=ask_human_for_clarification)))
    workflow.add_node("process_clarification", process_human_clarification)
    
    # A special "wait" node that just returns the current state, useful for human-in-the-loop
    workflow.add_node("wait_for_human", lambda state: state)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        None,
        validation_router,
        {
            "preprocess": "preprocess",
            "check_completeness": "check_completeness",
            "validate_quality": "validate_quality",
            "finalize": "finalize",
            "request_clarification": "request_clarification",
            "wait_for_human": "wait_for_human",
            "error": END,
            "end": END
        }
    )
    
    workflow.add_edge("preprocess", None)
    workflow.add_edge("check_completeness", None)
    workflow.add_edge("validate_quality", None)
    workflow.add_edge("finalize", None)
    
    # The request_clarification node updates the state to indicate it's waiting for human input
    # and the execution gets paused
    workflow.add_edge("request_clarification", lambda state: {
        **state.dict(),
        "status": "awaiting_clarification"
    })
    
    # When human input is received, it goes to the process_clarification node
    workflow.add_edge("request_clarification", "process_clarification", 
                     # This edge is taken when human input is provided
                     condition=lambda state, human_input: human_input is not None)
    
    workflow.add_edge("process_clarification", None)
    
    # Create memory saver for persistence during human interaction
    memory_saver = MemorySaver()
    
    # Return the compiled workflow with the checkpoint
    return workflow.compile(checkpointer=memory_saver)
####################################################




######################################################
# Usage example:
def standalone_validation_example():
    """
    Example of using the Validation team in isolation with human-in-the-loop.
    """
    # Create a validation workflow
    validation_workflow = create_validation_workflow()
    
    # Sample requirements data with intentional issues to trigger validation failures
    incomplete_requirements = {
        "project": "Smart Home Control System",
        "version": "1.0",
        "requirements": [
            {
                "id": "REQ-001",
                # Missing priority and source
                "description": "The system shall allow users to control home lighting remotely.",
                "category": "Functional"
                # Missing acceptance criteria
            },
            {
                "id": "REQ-002",
                "description": "The system shall respond to commands quickly.",  # Vague, not measurable
                "priority": "Medium",
                "category": "Performance",
                "source": "Technical Specification",
                "acceptance_criteria": "Commands are executed promptly."  # Not specific enough
            }
        ]
    }
    
    # Create initial validation state
    initial_state = ValidationState(
        input_data=incomplete_requirements,
        status="initialized"
    )
    
    print("\n=== STEP 1: Initial Validation ===")
    print("Starting validation with incomplete requirements...")
    
    # Run validation workflow
    result = validation_workflow.invoke(initial_state)
    
    # Check for human-in-the-loop pause
    if result.status == "awaiting_clarification":
        thread_id = validation_workflow.get_current_thread_id()
        print(f"\n=== STEP 2: Validation Paused ===")
        print(f"Workflow paused, awaiting human input. Thread ID: {thread_id}")
        
        # Extract the clarification request
        clarification_context = result.metadata.get("clarification_request", {}).get("context", "{}")
        clarification_question = result.metadata.get("clarification_request", {}).get("question", "No question available")
        
        print("\nClarification needed:")
        print(clarification_question)
        
        # Simulate user providing clarification
        print("\n=== STEP 3: User Provides Clarification ===")
        user_input = """
        I've updated the requirements:
        
        1. REQ-001:
           - Added priority: "High"
           - Added source: "Customer Interview"
           - Added acceptance criteria: "User can turn lights on/off from the mobile app from any location with internet access."
        
        2. REQ-002:
           - Updated description: "The system shall respond to lighting commands within 1 second under normal network conditions."
           - Updated acceptance criteria: "Command response time is measured as less than 1 second in 95% of test cases."
        """
        
        print("User response:")
        print(user_input)
        
        # Continue the workflow with user input
        print("\n=== STEP 4: Continuing Validation ===")
        print("Continuing validation with updated requirements...")
        
        # Resume workflow with user input
        updated_result = validation_workflow.continue_from_thread(
            thread_id,
            user_input
        )
        
        # Check if validation is now successful
        validation_summary = updated_result.validation_summary or {}
        is_valid = validation_summary.get("overall_valid", False)
        
        print("\n=== STEP 5: Validation Results ===")
        if updated_result.status == "completed" and is_valid:
            print("✅ Validation successful!")
            print(f"Completeness Score: {validation_summary.get('completeness_score', 0) * 100:.1f}%")
            print(f"Quality Score: {validation_summary.get('quality_score', 0) * 100:.1f}%")
            print(f"Overall Score: {validation_summary.get('overall_score', 0) * 100:.1f}%")
        elif updated_result.status == "awaiting_clarification":
            print("⚠️ Still awaiting clarification. Additional input needed.")
        else:
            print("❌ Validation failed after clarification.")
            
        # Print the actual updated requirements that were processed
        print("\n=== Updated Requirements ===")
        if updated_result.preprocessed_data:
            print(json.dumps(updated_result.preprocessed_data, indent=2))
    else:
        print("Unexpected result: Validation did not request clarification.")
    
    return result

if __name__ == "__main__":
    print("\n🔍 REQUIREMENTS VALIDATION EXAMPLE WITH HUMAN-IN-THE-LOOP 🔍\n")
    print("This example demonstrates how the validation team works in isolation")
    print("with LangGraph's human-in-the-loop capabilities.\n")
    standalone_validation_example()
