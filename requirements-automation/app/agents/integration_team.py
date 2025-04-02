# requirements_automation/integration_team.py

from typing import Dict, Any, List, Optional
import json
from pydantic import BaseModel, Field

from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

from requirements_automation.base import (
    IntegrationState, 
    create_llm_node, 
    with_error_handling,
    Config
)

# JSON Schema for integration outputs
class GoogleDocsStatus(BaseModel):
    document_id: Optional[str] = Field(default=None, description="Google Docs document ID")
    document_url: Optional[str] = Field(default=None, description="Google Docs document URL")
    created_sections: List[str] = Field(description="Sections created in the document")
    is_successful: bool = Field(description="Whether the integration was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if any")

class JiraStatus(BaseModel):
    project_key: str = Field(description="JIRA project key")
    created_items: List[Dict[str, Any]] = Field(description="Items created in JIRA")
    epic_key: Optional[str] = Field(default=None, description="Epic key if created")
    is_successful: bool = Field(description="Whether the integration was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if any")

class WikiStatus(BaseModel):
    page_id: Optional[str] = Field(default=None, description="Wiki page ID")
    page_url: Optional[str] = Field(default=None, description="Wiki page URL")
    created_sections: List[str] = Field(description="Sections created in the wiki")
    is_successful: bool = Field(description="Whether the integration was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if any")

class SlackStatus(BaseModel):
    channel: str = Field(description="Slack channel")
    message_id: Optional[str] = Field(default=None, description="Slack message ID")
    notification_type: str = Field(description="Type of notification sent")
    is_successful: bool = Field(description="Whether the notification was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if any")

class IntegrationSummary(BaseModel):
    overall_successful: bool = Field(description="Whether all integrations were successful")
    successful_integrations: List[str] = Field(description="List of successful integrations")
    failed_integrations: List[str] = Field(description="List of failed integrations")
    links: Dict[str, str] = Field(description="Links to created resources")
    summary_message: str = Field(description="Summary message for distribution")

# Agent implementations
@with_error_handling
def google_docs_agent(state: IntegrationState) -> IntegrationState:
    """
    Integrates the document content with Google Docs.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the Google Docs agent
    gdocs_prompt = """
    You are a Google Docs Integration Agent. Your job is to:
    1. Format the document content for Google Docs
    2. Create a new Google Docs document or update an existing one
    3. Apply appropriate styles and formatting
    4. Add headers, footers, and page numbers
    5. Generate a table of contents and other document elements
    
    Since this is a simulation, describe how you would perform these actions.
    
    Return a JSON object with the Google Docs integration status, following this schema:
    {
        "document_id": "doc_id",
        "document_url": "doc_url",
        "created_sections": ["section1", "section2", ...],
        "is_successful": boolean,
        "error_message": "error_message (if any)"
    }
    """
    
    gdocs_agent = create_llm_node(
        system_prompt=gdocs_prompt,
        user_prompt="Integrate the following document content with Google Docs:\n\n{document_content}",
        output_parser=JsonOutputParser()
    )
    
    # Perform Google Docs integration
    new_state.google_docs_status = gdocs_agent.invoke({"document_content": json.dumps(new_state.document_content)})
    new_state.status = "gdocs_integrated"
    
    return new_state

@with_error_handling
def jira_agent(state: IntegrationState) -> IntegrationState:
    """
    Integrates the requirements with JIRA, creating epics, stories, and tasks.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the JIRA agent
    jira_prompt = """
    You are a JIRA Integration Agent. Your job is to:
    1. Extract actionable requirements from the document
    2. Create appropriate JIRA items (epics, stories, tasks)
    3. Set priorities, assignees, and other metadata
    4. Establish relationships between items
    5. Link requirements to the document
    
    Since this is a simulation, describe how you would perform these actions.
    
    Return a JSON object with the JIRA integration status, following this schema:
    {
        "project_key": "project_key",
        "created_items": [
            {"type": "item_type", "key": "item_key", "summary": "item_summary"},
            ...
        ],
        "epic_key": "epic_key (if created)",
        "is_successful": boolean,
        "error_message": "error_message (if any)"
    }
    """
    
    jira_agent = create_llm_node(
        system_prompt=jira_prompt,
        user_prompt="Integrate the following requirements with JIRA:\n\n{document_content}",
        output_parser=JsonOutputParser()
    )
    
    # Perform JIRA integration
    new_state.jira_status = jira_agent.invoke({"document_content": json.dumps(new_state.document_content)})
    new_state.status = "jira_integrated"
    
    return new_state

@with_error_handling
def wiki_agent(state: IntegrationState) -> IntegrationState:
    """
    Integrates the document content with a wiki system.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the Wiki agent
    wiki_prompt = """
    You are a Wiki Integration Agent. Your job is to:
    1. Format the document content for wiki publishing
    2. Create or update wiki pages
    3. Apply appropriate wiki formatting and styles
    4. Create navigation and links between pages
    5. Add metadata, tags, and categorization
    
    Since this is a simulation, describe how you would perform these actions.
    
    Return a JSON object with the Wiki integration status, following this schema:
    {
        "page_id": "page_id",
        "page_url": "page_url",
        "created_sections": ["section1", "section2", ...],
        "is_successful": boolean,
        "error_message": "error_message (if any)"
    }
    """
    
    wiki_agent = create_llm_node(
        system_prompt=wiki_prompt,
        user_prompt="Integrate the following document content with the Wiki:\n\n{document_content}",
        output_parser=JsonOutputParser()
    )
    
    # Perform Wiki integration
    new_state.wiki_status = wiki_agent.invoke({"document_content": json.dumps(new_state.document_content)})
    new_state.status = "wiki_integrated"
    
    return new_state

@with_error_handling
def slack_agent(state: IntegrationState) -> IntegrationState:
    """
    Sends notifications about the requirements document to Slack.
    """
    new_state = state.model_copy(deep=True)
    
    # Gather integration statuses
    integration_data = {
        "google_docs": new_state.google_docs_status,
        "jira": new_state.jira_status,
        "wiki": new_state.wiki_status,
        "document_title": new_state.document_content.get("title", "Requirements Document")
    }
    
    # Define the Slack agent
    slack_prompt = """
    You are a Slack Notification Agent. Your job is to:
    1. Create a concise notification about the requirements document
    2. Include links to all integrated systems (Google Docs, JIRA, Wiki)
    3. Summarize key information and status
    4. Format the message appropriately for Slack
    5. Mention relevant stakeholders
    
    Since this is a simulation, describe how you would perform these actions.
    
    Return a JSON object with the Slack notification status, following this schema:
    {
        "channel": "channel_name",
        "message_id": "message_id (if available)",
        "notification_type": "type_of_notification",
        "is_successful": boolean,
        "error_message": "error_message (if any)"
    }
    """
    
    slack_agent = create_llm_node(
        system_prompt=slack_prompt,
        user_prompt="Create a Slack notification for the following document and integration results:\n\n{integration_data}",
        output_parser=JsonOutputParser()
    )
    
    # Send Slack notification
    new_state.slack_status = slack_agent.invoke({"integration_data": json.dumps(integration_data)})
    new_state.status = "slack_notified"
    
    return new_state

@with_error_handling
def integration_finalizer(state: IntegrationState) -> IntegrationState:
    """
    Finalizes the integration process by combining results from all integrations
    into a comprehensive summary.
    """
    new_state = state.model_copy(deep=True)
    
    if not new_state.google_docs_status or not new_state.jira_status or not new_state.wiki_status or not new_state.slack_status:
        new_state.status = "error"
        new_state.error = "Missing integration results"
        return new_state
    
    # Define the integration finalizer agent
    finalizer_prompt = """
    You are an Integration Finalizer. Your job is to:
    1. Analyze the results from all integration systems
    2. Create a comprehensive summary of the integration process
    3. Determine if all integrations were successful
    4. Compile links to all created resources
    5. Create a summary message for distribution
    
    Return a JSON object with the integration summary, following this schema:
    {
        "overall_successful": boolean,
        "successful_integrations": ["integration1", "integration2", ...],
        "failed_integrations": ["integration3", ...],
        "links": {
            "google_docs": "doc_url",
            "jira_epic": "epic_url",
            "wiki": "wiki_url",
            ...
        },
        "summary_message": "summary_message"
    }
    """
    
    finalizer_agent = create_llm_node(
        system_prompt=finalizer_prompt,
        user_prompt="""Finalize the integration based on the following results:
        
        Google Docs Status:
        {google_docs_status}
        
        JIRA Status:
        {jira_status}
        
        Wiki Status:
        {wiki_status}
        
        Slack Status:
        {slack_status}
        """,
        output_parser=JsonOutputParser()
    )
    
    # Finalize integration
    new_state.integration_summary = finalizer_agent.invoke({
        "google_docs_status": json.dumps(new_state.google_docs_status),
        "jira_status": json.dumps(new_state.jira_status),
        "wiki_status": json.dumps(new_state.wiki_status),
        "slack_status": json.dumps(new_state.slack_status)
    })
    new_state.status = "completed"
    
    return new_state

# Integration Supervisor - Decision function for workflow routing
def integration_router(state: IntegrationState) -> str:
    """Routes the workflow based on the current state"""
    if state.is_error():
        return "error"
    
    # Determine the next step based on what's missing
    integrations_to_do = []
    
    if not state.google_docs_status:
        integrations_to_do.append("gdocs")
    if not state.jira_status:
        integrations_to_do.append("jira")
    if not state.wiki_status:
        integrations_to_do.append("wiki")
    if state.google_docs_status and state.jira_status and state.wiki_status and not state.slack_status:
        integrations_to_do.append("slack")
    if state.google_docs_status and state.jira_status and state.wiki_status and state.slack_status and not state.integration_summary:
        integrations_to_do.append("finalize")
    
    if not integrations_to_do:
        return "end"
    
    # Prioritize finalizing if all integrations are done
    if "finalize" in integrations_to_do:
        return "finalize"
    # Prioritize notification after all system integrations
    if "slack" in integrations_to_do:
        return "slack"
    
    # Otherwise, just pick the first integration to do
    return integrations_to_do[0]

# Create the Integration Team workflow
def create_integration_workflow() -> StateGraph:
    """Creates the Integration Team workflow graph"""
    workflow = StateGraph(IntegrationState)
    
    # Add nodes
    workflow.add_node("gdocs", google_docs_agent)
    workflow.add_node("jira", jira_agent)
    workflow.add_node("wiki", wiki_agent)
    workflow.add_node("slack", slack_agent)
    workflow.add_node("finalize", integration_finalizer)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        None,
        integration_router,
        {
            "gdocs": "gdocs",
            "jira": "jira",
            "wiki": "wiki",
            "slack": "slack",
            "finalize": "finalize",
            "error": END,
            "end": END
        }
    )
    
    # Add edges from each node back to the router
    workflow.add_edge("gdocs", None)
    workflow.add_edge("jira", None)
    workflow.add_edge("wiki", None)
    workflow.add_edge("slack", None)
    workflow.add_edge("finalize", None)
    
    return workflow.compile()