import os
from typing import Dict, List, Any, TypedDict, Annotated
from enum import Enum

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser

# Custom tool imports for integration
from custom_tools.slack_integration import SlackIntegrationTool
from custom_tools.jira_integration import JiraIntegrationTool
from custom_tools.gdocs_integration import GoogleDocsIntegrationTool
from custom_tools.wiki_integration import WikiIntegrationTool
from custom_tools.database import DatabaseTool


# Define state structure
class RequirementState(TypedDict):
    """State maintained in the workflow."""
    # Raw input from Slack
    raw_input: Dict[str, Any]
    # Validation results and feedback
    validation_results: Dict[str, Any]
    # Formatted PRD content
    formatted_prd: Dict[str, Any]
    # Document creation results
    document_results: Dict[str, Any]
    # Design document content
    design_document: Dict[str, Any]
    # Messages for context
    messages: List[Dict[str, Any]]
    # Current node in workflow
    current_node: str
    # Next steps
    next_steps: List[str]


# Define workflow states
class WorkflowState(str, Enum):
    VALIDATION = "validation"
    FORMATTING = "formatting"
    DOCUMENT_CREATION = "document_creation"
    DESIGN_DOCUMENT = "design_document"
    COMPLETE = "complete"
    FEEDBACK = "feedback"


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.1,
)

# 1. Validation Agent
validation_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
    You are a requirements validation expert. Your task is to analyze the user's input and determine 
    if they have provided all necessary information for a Data Engineering project requirement.

    Specifically, check for:
    1. Clear business need description
    2. Detailed requirements with who/what/where/when/why
    3. Business impact description
    4. Timeline information (delivery date, campaign date)
    5. Contributors information
    6. Data attributes and definitions if applicable

    If any required information is missing or unclear, provide SPECIFIC feedback with examples of how 
    to improve the submission. If all required information is present and clear, validate the submission.

    Output format:
    {
        "is_valid": true/false,
        "missing_fields": ["field1", "field2"],
        "feedback": "Detailed feedback with examples",
        "examples": {"field1": "Example of good input for this field"}
    }
    """),
    HumanMessage(content="{input}"),
])

validation_agent = validation_prompt | llm | JsonOutputParser()

# 2. Formatting Agent
formatting_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
    You are a PRD formatting expert. Your task is to take validated requirement information and format it 
    according to the Intuit Data Engineering PRD template.

    Follow these guidelines:
    1. Extract key business need information and format it clearly
    2. Structure requirements in the standard format with who/what/where/when/why
    3. Format business impact statements concisely
    4. Structure timeline information properly
    5. Format contributor information
    6. Create properly formatted tables for definitions and mappings if provided

    Output the formatted content for each section of the PRD template.

    Output format:
    {
        "business_need": "formatted business need",
        "requirements": [{"name": "req name", "description": "desc", "who_what_where_when_why": "details"}],
        "business_impact": "formatted impact statement",
        "timeline": {"delivery_date": "date", "campaign_date": "date"},
        "contributors": ["person1", "person2"],
        "definitions": [{"attribute": "attr1", "definition": "def1"}],
        "mapping_tables": [{"attribute": "attr", "type": "type", "source": "src", "destination": "dest"}]
    }
    """),
    HumanMessage(content="{input}"),
])

formatting_agent = formatting_prompt | llm | JsonOutputParser()

# 3. Document Creation Agent
document_creation_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
    You are a document creation expert. Your task is to create professional documentation based on 
    formatted PRD content.

    You need to:
    1. Generate a Google Doc with proper formatting, headings, tables, and styling
    2. Create a JIRA ticket with all relevant information
    3. Ensure all links and references are correctly set up
    4. Add appropriate metadata and tags

    Use the provided Python tools to interact with Google Docs and JIRA.

    Output format:
    {
        "gdoc_creation": {"success": true/false, "doc_id": "id", "doc_url": "url"},
        "jira_creation": {"success": true/false, "ticket_key": "key", "ticket_url": "url"},
        "errors": ["error1", "error2"]
    }
    """),
    HumanMessage(content="{input}")
])

document_creation_agent = document_creation_prompt | llm | JsonOutputParser()

# 4. Design Document Agent
design_document_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
    You are a technical design document expert for Data Engineering projects. Your task is to create 
    a detailed technical design wiki page based on the requirements.

    You need to:
    1. Extract technical specifications from the requirements
    2. Create data mapping tables with source and destination fields
    3. Document SQL queries needed for implementation
    4. Specify dependencies and technical prerequisites
    5. Detail security and compliance considerations

    Use the provided Python tools to create and format wiki pages.

    Output format:
    {
        "design_content": {
            "overview": "technical overview",
            "mapping_tables": [{"attribute": "attr", "type": "type", "source": "src", "destination": "dest"}],
            "queries": ["SQL query 1", "SQL query 2"],
            "dependencies": ["dependency1", "dependency2"],
            "security": ["security consideration 1", "security consideration 2"]
        },
        "wiki_creation": {"success": true/false, "page_id": "id", "page_url": "url"},
        "errors": ["error1", "error2"]
    }
    """),
    HumanMessage(content="{input}")
])

design_document_agent = design_document_prompt | llm | JsonOutputParser()


# Define node functions
def validation_node(state: RequirementState) -> Dict[str, Any]:
    """Validate the user input and provide feedback."""
    input_data = {
        "input": state["raw_input"]
    }
    validation_results = validation_agent.invoke(input_data)

    return {
        "validation_results": validation_results,
        "messages": state["messages"] + [{"role": "system",
                                          "content": f"Validation complete: {validation_results['is_valid']}"}],
        "current_node": WorkflowState.VALIDATION,
    }


def formatting_node(state: RequirementState) -> Dict[str, Any]:
    """Format validated input into PRD structure."""
    input_data = {
        "input": {
            "raw_input": state["raw_input"],
            "validation_results": state["validation_results"]
        }
    }
    formatted_prd = formatting_agent.invoke(input_data)

    return {
        "formatted_prd": formatted_prd,
        "messages": state["messages"] + [
            {"role": "system", "content": "PRD formatting complete"}],
        "current_node": WorkflowState.FORMATTING,
    }


def document_creation_node(state: RequirementState) -> Dict[str, Any]:
    """Create Google Doc and JIRA ticket."""
    input_data = {
        "input": {
            "formatted_prd": state["formatted_prd"]
        }
    }
    document_results = document_creation_agent.invoke(input_data)

    return {
        "document_results": document_results,
        "messages": state["messages"] + [{"role": "system",
                                          "content": f"Document creation complete: Google Doc: {document_results['gdoc_creation']['success']}, JIRA: {document_results['jira_creation']['success']}"}],
        "current_node": WorkflowState.DOCUMENT_CREATION,
    }


def design_document_node(state: RequirementState) -> Dict[str, Any]:
    """Create design document in wiki."""
    input_data = {
        "input": {
            "formatted_prd": state["formatted_prd"],
            "document_results": state["document_results"]
        }
    }
    design_document = design_document_agent.invoke(input_data)

    return {
        "design_document": design_document,
        "messages": state["messages"] + [{"role": "system",
                                          "content": f"Design document creation complete: {design_document['wiki_creation']['success']}"}],
        "current_node": WorkflowState.DESIGN_DOCUMENT,
    }


def determine_next_step(state: RequirementState) -> List[str]:
    """Determine the next step in the workflow based on validation results."""
    if state["current_node"] == WorkflowState.VALIDATION:
        if state["validation_results"]["is_valid"]:
            return [WorkflowState.FORMATTING]
        else:
            return [WorkflowState.FEEDBACK]

    elif state["current_node"] == WorkflowState.FORMATTING:
        return [WorkflowState.DOCUMENT_CREATION]

    elif state["current_node"] == WorkflowState.DOCUMENT_CREATION:
        return [WorkflowState.DESIGN_DOCUMENT]

    elif state["current_node"] == WorkflowState.DESIGN_DOCUMENT:
        return [WorkflowState.COMPLETE]

    return [END]


def process_feedback(state: RequirementState) -> Dict[str, Any]:
    """Process feedback for invalid submissions."""
    # Here we would integrate with Slack to send feedback to the user
    slack_tool = SlackIntegrationTool()
    feedback_message = f"Your requirement submission needs more information. Here's the feedback:\n\n{state['validation_results']['feedback']}\n\nExamples of good inputs:\n{state['validation_results']['examples']}"

    slack_tool.send_message(
        channel=state["raw_input"]["channel_id"],
        user=state["raw_input"]["user_id"],
        message=feedback_message
    )

    return {
        "messages": state["messages"] + [
            {"role": "system", "content": "Feedback sent to user"}],
        "current_node": WorkflowState.FEEDBACK,
        "next_steps": ["Wait for user resubmission"]
    }


# Custom Python tools implementation examples

class SlackIntegrationTool:
    """Tool for Slack integration."""

    def send_message(self, channel: str, user: str, message: str) -> Dict[
        str, Any]:
        """Send a message to a Slack channel or user."""
        # Implementation would use Slack API
        print(
            f"Sending message to {channel} for user {user}: {message[:50]}...")
        return {"success": True, "channel": channel, "user": user}


class JiraIntegrationTool:
    """Tool for JIRA integration."""

    def create_ticket(self, project: str, summary: str, description: str,
                      issue_type: str = "Story",
                      custom_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a JIRA ticket."""
        # Implementation would use JIRA API
        print(f"Creating JIRA ticket in {project}: {summary}")
        return {"success": True, "ticket_key": "DENG-123",
                "ticket_url": "https://jira.intuit.com/browse/DENG-123"}


class GoogleDocsIntegrationTool:
    """Tool for Google Docs integration."""

    def create_document(self, title: str, content: Dict[str, Any]) -> Dict[
        str, Any]:
        """Create a Google Doc with the PRD content."""
        # Implementation would use Google Docs API
        print(f"Creating Google Doc: {title}")
        return {"success": True, "doc_id": "abc123",
                "doc_url": "https://docs.google.com/document/d/abc123"}


class WikiIntegrationTool:
    """Tool for Wiki integration."""

    def create_page(self, space: str, title: str, content: Dict[str, Any]) -> \
    Dict[str, Any]:
        """Create a Wiki page with the design document content."""
        # Implementation would use Wiki API (e.g., Confluence)
        print(f"Creating Wiki page in {space}: {title}")
        return {"success": True, "page_id": "def456",
                "page_url": "https://wiki.intuit.com/display/DENG/Design+Doc"}


# Set up the LangGraph workflow
workflow = StateGraph(RequirementState)

# Add nodes
workflow.add_node(WorkflowState.VALIDATION, validation_node)
workflow.add_node(WorkflowState.FORMATTING, formatting_node)
workflow.add_node(WorkflowState.DOCUMENT_CREATION, document_creation_node)
workflow.add_node(WorkflowState.DESIGN_DOCUMENT, design_document_node)
workflow.add_node(WorkflowState.FEEDBACK, process_feedback)

# Add edges
workflow.add_conditional_edges(
    WorkflowState.VALIDATION,
    determine_next_step
)
workflow.add_edge(WorkflowState.FORMATTING, WorkflowState.DOCUMENT_CREATION)
workflow.add_edge(WorkflowState.DOCUMENT_CREATION,
                  WorkflowState.DESIGN_DOCUMENT)
workflow.add_edge(WorkflowState.DESIGN_DOCUMENT, END)
workflow.add_edge(WorkflowState.FEEDBACK, END)

# Set the entry point
workflow.set_entry_point(WorkflowState.VALIDATION)

# Compile the workflow
app = workflow.compile()


# Example function to initiate the workflow
def start_requirement_workflow(slack_input: Dict[str, Any]) -> Dict[str, Any]:
    """Start the requirement workflow with input from Slack."""
    initial_state = {
        "raw_input": slack_input,
        "validation_results": {},
        "formatted_prd": {},
        "document_results": {},
        "design_document": {},
        "messages": [],
        "current_node": "",
        "next_steps": []
    }

    # Run the workflow
    for event in app.stream(initial_state):
        if "messages" in event:
            # Log messages for tracing
            for message in event["messages"]:
                if message not in initial_state.get("messages", []):
                    print(
                        f"[{event.get('current_node', 'unknown')}] {message['content']}")

    # Get the final state
    final_state = event
    return final_state


# Example usage (this would be triggered by a Slack event in production)
if __name__ == "__main__":
    # Example Slack input
    example_input = {
        "user_id": "U123456",
        "channel_id": "C123456",
        "business_need": "We need to provide auth signal for PY expert match use cases",
        "requirements": "To hyperpersonalize PY expert match use cases",
        "business_impact": "CS will not be able to launch certain aspects of their PY Expert Match campaign without this data",
        "delivery_date": "12/9/2024",
        "campaign_date": "12/15/2024",
        "contributors": ["Shweta Dhingra"],
        "definitions": [{"attribute": "Has Foreign Bank Accounts",
                         "definition": "Provide bank accounts that are of type Foreign"}]
    }

    # Start the workflow
    result = start_requirement_workflow(example_input)
    print("Workflow completed with result:", result)