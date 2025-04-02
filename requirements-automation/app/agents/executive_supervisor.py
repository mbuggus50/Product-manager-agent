# requirements_automation/executive_supervisor.py

from typing import Dict, Any, List, Optional
import json
from pydantic import BaseModel, Field

from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

from requirements_automation.base import (
    ExecutiveState,
    ValidationState,
    ContentState,
    IntegrationState,
    create_llm_node, 
    with_error_handling,
    Config
)
from requirements_automation.validation_team import create_validation_workflow
from requirements_automation.content_team import create_content_workflow
from requirements_automation.integration_team import create_integration_workflow

# Agent implementations
@with_error_handling
def workflow_initializer(state: ExecutiveState) -> ExecutiveState:
    """
    Initializes the workflow by preprocessing input data and setting up the state.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the initializer agent
    initializer_prompt = """
    You are a Workflow Initializer. Your job is to:
    1. Analyze the input requirements data
    2. Identify document type and purpose
    3. Extract key metadata for the workflow
    4. Set up initial parameters for processing
    5. Prepare the requirements for validation
    
    Return a JSON object with the initialized parameters and metadata.
    """
    
    initializer_agent = create_llm_node(
        system_prompt=initializer_prompt,
        user_prompt="Initialize the workflow for the following requirements:\n\n{input_requirements}",
        output_parser=JsonOutputParser()
    )
    
    # Initialize workflow
    if not new_state.metadata.get("initialized"):
        workflow_metadata = initializer_agent.invoke({"input_requirements": json.dumps(new_state.input_requirements)})
        new_state.metadata.update(workflow_metadata)
        new_state.metadata["initialized"] = True
    
    new_state.status = "initialized"
    
    return new_state

@with_error_handling
def validation_team_handler(state: ExecutiveState) -> ExecutiveState:
    """
    Handles interaction with the Validation Team.
    """
    new_state = state.model_copy(deep=True)
    
    # Create Validation Team input state
    validation_state = ValidationState(
        input_data=new_state.input_requirements,
        status="initialized",
        metadata=new_state.metadata.copy()  # Share relevant metadata
    )
    
    # Get the Validation Team workflow
    validation_workflow = create_validation_workflow()
    
    # Run the Validation Team workflow
    validation_results = validation_workflow.invoke(validation_state)
    
    # Update the Executive state with validation results
    new_state.validation_results = {
        "summary": validation_results.validation_summary,
        "preprocessed_data": validation_results.preprocessed_data,
        "completeness_check": validation_results.completeness_check,
        "quality_check": validation_results.quality_check
    }
    
    # Update the current team
    new_state.current_team = "validation_completed"
    
    # Determine if validation was successful
    validation_successful = (
        validation_results.validation_summary is not None and 
        validation_results.validation_summary.get("overall_valid", False)
    )
    
    # Add validation status to metadata
    new_state.metadata["validation_successful"] = validation_successful
    
    # Update overall status
    if validation_successful:
        new_state.status = "validation_successful"
    else:
        new_state.status = "validation_failed"
    
    return new_state

@with_error_handling
def content_team_handler(state: ExecutiveState) -> ExecutiveState:
    """
    Handles interaction with the Content Team.
    """
    new_state = state.model_copy(deep=True)
    
    # Ensure validation was successful
    if not new_state.metadata.get("validation_successful", False):
        new_state.status = "error"
        new_state.error = "Cannot proceed to content creation without successful validation"
        return new_state
    
    # Create Content Team input state
    content_state = ContentState(
        validated_requirements=new_state.validation_results["preprocessed_data"],
        status="initialized",
        metadata=new_state.metadata.copy()  # Share relevant metadata
    )
    
    # Get the Content Team workflow
    content_workflow = create_content_workflow()
    
    # Run the Content Team workflow
    content_results = content_workflow.invoke(content_state)
    
    # Update the Executive state with content results
    new_state.content_results = {
        "final_document": content_results.final_document,
        "formatted_content": content_results.formatted_content,
        "document_structure": content_results.document_structure,
        "design_elements": content_results.design_elements
    }
    
    # Update the current team
    new_state.current_team = "content_completed"
    
    # Determine if content creation was successful
    content_successful = content_results.final_document is not None
    
    # Add content status to metadata
    new_state.metadata["content_successful"] = content_successful
    
    # Update overall status
    if content_successful:
        new_state.status = "content_successful"
    else:
        new_state.status = "content_failed"
    
    return new_state

@with_error_handling
def integration_team_handler(state: ExecutiveState) -> ExecutiveState:
    """
    Handles interaction with the Integration Team.
    """
    new_state = state.model_copy(deep=True)
    
    # Ensure content creation was successful
    if not new_state.metadata.get("content_successful", False):
        new_state.status = "error"
        new_state.error = "Cannot proceed to integration without successful content creation"
        return new_state
    
    # Create Integration Team input state
    integration_state = IntegrationState(
        document_content=new_state.content_results["final_document"],
        status="initialized",
        metadata=new_state.metadata.copy()  # Share relevant metadata
    )
    
    # Get the Integration Team workflow
    integration_workflow = create_integration_workflow()
    
    # Run the Integration Team workflow
    integration_results = integration_workflow.invoke(integration_state)
    
    # Update the Executive state with integration results
    new_state.integration_results = {
        "summary": integration_results.integration_summary,
        "google_docs_status": integration_results.google_docs_status,
        "jira_status": integration_results.jira_status,
        "wiki_status": integration_results.wiki_status,
        "slack_status": integration_results.slack_status
    }
    
    # Update the current team
    new_state.current_team = "integration_completed"
    
    # Determine if integration was successful
    integration_successful = (
        integration_results.integration_summary is not None and 
        integration_results.integration_summary.get("overall_successful", False)
    )
    
    # Add integration status to metadata
    new_state.metadata["integration_successful"] = integration_successful
    
    # Update overall status
    if integration_successful:
        new_state.status = "integration_successful"
    else:
        new_state.status = "integration_failed"
    
    return new_state

@with_error_handling
def workflow_finalizer(state: ExecutiveState) -> ExecutiveState:
    """
    Finalizes the overall workflow by generating a comprehensive summary and output.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the finalizer agent
    finalizer_prompt = """
    You are a Workflow Finalizer. Your job is to:
    1. Analyze the results from all teams
    2. Create a comprehensive summary of the entire process
    3. Compile all relevant outputs, links, and resources
    4. Generate a final report on the requirements automation process
    5. Provide recommendations for future improvements
    
    Return a JSON object with the finalized workflow results.
    """
    
    finalizer_agent = create_llm_node(
        system_prompt=finalizer_prompt,
        user_prompt="""Finalize the workflow based on the following results:
        
        Validation Results:
        {validation_results}
        
        Content Results:
        {content_results}
        
        Integration Results:
        {integration_results}
        
        Workflow Metadata:
        {metadata}
        """,
        output_parser=JsonOutputParser()
    )
    
    # Finalize workflow
    new_state.final_output = finalizer_agent.invoke({
        "validation_results": json.dumps(new_state.validation_results),
        "content_results": json.dumps(new_state.content_results),
        "integration_results": json.dumps(new_state.integration_results),
        "metadata": json.dumps(new_state.metadata)
    })
    
    new_state.status = "completed"
    new_state.current_team = "completed"
    
    return new_state

# Executive Supervisor - Decision function for workflow routing
def executive_router(state: ExecutiveState) -> str:
    """Routes the workflow based on the current state"""
    if state.is_error():
        return "error"
    
    if not state.metadata.get("initialized"):
        return "initialize"
    elif not state.validation_results:
        return "validate"
    elif state.validation_results and not state.content_results and state.metadata.get("validation_successful", False):
        return "create_content"
    elif state.content_results and not state.integration_results and state.metadata.get("content_successful", False):
        return "integrate"
    elif state.validation_results and state.content_results and state.integration_results and not state.final_output:
        return "finalize"
    else:
        return "end"

# Create the Executive Supervisor workflow
def create_executive_workflow() -> StateGraph:
    """Creates the Executive Supervisor workflow graph"""
    workflow = StateGraph(ExecutiveState)
    
    # Add nodes
    workflow.add_node("initialize", workflow_initializer)
    workflow.add_node("validate", validation_team_handler)
    workflow.add_node("create_content", content_team_handler)
    workflow.add_node("integrate", integration_team_handler)
    workflow.add_node("finalize", workflow_finalizer)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        None,
        executive_router,
        {
            "initialize": "initialize",
            "validate": "validate",
            "create_content": "create_content",
            "integrate": "integrate",
            "finalize": "finalize",
            "error": END,
            "end": END
        }
    )
    
    # Add edges from each node back to the router
    workflow.add_edge("initialize", None)
    workflow.add_edge("validate", None)
    workflow.add_edge("create_content", None)
    workflow.add_edge("integrate", None)
    workflow.add_edge("finalize", None)
    
    return workflow.compile()