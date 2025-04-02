# requirements_automation/validation_team.py

from typing import Dict, Any, Tuple, List
import json
from pydantic import BaseModel, Field

from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

from requirements_automation.base import (
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

# Validation Supervisor - Decision function for workflow routing
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
        return "end"

# Create the Validation Team workflow
def create_validation_workflow() -> StateGraph:
    """Creates the Validation Team workflow graph"""
    workflow = StateGraph(ValidationState)
    
    # Add nodes
    workflow.add_node("preprocess", data_preprocessor)
    workflow.add_node("check_completeness", completeness_checker)
    workflow.add_node("validate_quality", quality_validator)
    workflow.add_node("finalize", validation_finalizer)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        None,
        validation_router,
        {
            "preprocess": "preprocess",
            "check_completeness": "check_completeness",
            "validate_quality": "validate_quality",
            "finalize": "finalize",
            "error": END,
            "end": END
        }
    )
    
    workflow.add_edge("preprocess", None)
    workflow.add_edge("check_completeness", None)
    workflow.add_edge("validate_quality", None)
    workflow.add_edge("finalize", None)
    
    return workflow.compile()