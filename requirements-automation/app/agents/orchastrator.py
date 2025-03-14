from typing import Dict, List, Any, TypedDict, Optional
import logging

from langgraph.graph import StateGraph
from app.agents.validation_agent import ValidationAgent
from app.agents.formatting_agent import FormattingAgent
from app.agents.document_agent import DocumentAgent
from app.agents.design_agent import DesignAgent

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Define state structure
class WorkflowState(TypedDict):
    """State maintained in the workflow."""
    requirement_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    formatted_prd: Dict[str, Any]
    document_results: Dict[str, Any]
    design_document: Dict[str, Any]
    messages: List[Dict[str, str]]
    current_node: str
    error: Optional[str]


# Workflow states
VALIDATION_NODE = "validation"
FORMATTING_NODE = "formatting"
DOCUMENT_CREATION_NODE = "document_creation"
DESIGN_DOCUMENT_NODE = "design_document"
COMPLETE_NODE = "complete"
ERROR_NODE = "error"


class RequirementWorkflow:
    """
    Orchestrates the requirement workflow using LangGraph.
    """

    def __init__(self,
                 model_name: str = "gpt-4-turbo-preview",
                 google_docs_credentials: str = None,
                 jira_credentials: Dict[str, str] = None,
                 wiki_credentials: Dict[str, str] = None):
        """Initialize the workflow orchestrator with agents."""
        # Initialize agents
        self.validation_agent = ValidationAgent(model_name=model_name)
        self.formatting_agent = FormattingAgent(model_name=model_name)
        self.document_agent = DocumentAgent(
            model_name=model_name,
            google_docs_credentials=google_docs_credentials,
            jira_credentials=jira_credentials
        )
        self.design_agent = DesignAgent(
            model_name=model_name,
            wiki_credentials=wiki_credentials
        )

        # Set up the workflow
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        # Create the state graph
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node(VALIDATION_NODE, self._validation_node)
        workflow.add_node(FORMATTING_NODE, self._formatting_node)
        workflow.add_node(DOCUMENT_CREATION_NODE, self._document_creation_node)
        workflow.add_node(DESIGN_DOCUMENT_NODE, self._design_document_node)
        workflow.add_node(COMPLETE_NODE, self._complete_node)
        workflow.add_node(ERROR_NODE, self._error_node)

        # Add conditional edges
        workflow.add_conditional_edges(
            VALIDATION_NODE,
            self._route_after_validation,
            {
                FORMATTING_NODE: self._condition_is_valid,
                ERROR_NODE: self._condition_is_invalid
            }
        )

        # Add standard edges
        workflow.add_edge(FORMATTING_NODE, DOCUMENT_CREATION_NODE)
        workflow.add_edge(DOCUMENT_CREATION_NODE, DESIGN_DOCUMENT_NODE)
        workflow.add_edge(DESIGN_DOCUMENT_NODE, COMPLETE_NODE)

        # Set entry point
        workflow.set_entry_point(VALIDATION_NODE)

        return workflow

    def _validation_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate the requirement data."""
        logger.info("Executing validation node")

        try:
            validation_results = self.validation_agent.validate(
                state["requirement_data"])

            return {
                "validation_results": validation_results,
                "messages": state["messages"] + [{"role": "system",
                                                  "content": f"Validation complete: {validation_results['is_valid']}"}],
                "current_node": VALIDATION_NODE
            }
        except Exception as e:
            logger.error(f"Error in validation node: {str(e)}")
            return {
                "error": f"Error in validation node: {str(e)}",
                "current_node": ERROR_NODE,
                "messages": state["messages"] + [{"role": "system",
                                                  "content": f"Error during validation: {str(e)}"}]
            }

    def _route_after_validation(self, state: WorkflowState) -> str:
        """Determine next node after validation."""
        if state.get("error"):
            return ERROR_NODE

        validation_results = state.get("validation_results", {})
        is_valid = validation_results.get("is_valid", False)

        return FORMATTING_NODE if is_valid else ERROR_NODE

    def _condition_is_valid(self, state: WorkflowState) -> bool:
        """Check if requirement is valid."""
        validation_results = state.get("validation_results", {})
        return validation_results.get("is_valid", False)

    def _condition_is_invalid(self, state: WorkflowState) -> bool:
        """Check if requirement is invalid."""
        validation_results = state.get("validation_results", {})
        return not validation_results.get("is_valid", False)

    def _formatting_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Format the validated requirement data."""
        logger.info("Executing formatting node")

        try:
            formatted_prd = self.formatting_agent.format(
                state["requirement_data"],
                state["validation_results"]
            )

            return {
                "formatted_prd": formatted_prd,
                "messages": state["messages"] + [
                    {"role": "system", "content": "Formatting complete"}],
                "current_node": FORMATTING_NODE
            }
        except Exception as e:
            logger.error(f"Error in formatting node: {str(e)}")
            return {
                "error": f"Error in formatting node: {str(e)}",
                "current_node": ERROR_NODE,
                "messages": state["messages"] + [{"role": "system",
                                                  "content": f"Error during formatting: {str(e)}"}]
            }

    def _document_creation_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Create Google Doc and JIRA ticket."""
        logger.info("Executing document creation node")

        try:
            document_results = self.document_agent.create_documents(
                state["formatted_prd"])

            # Extract document links
            doc_links = {}
            if "documents_created" in document_results:
                if "google_doc" in document_results["documents_created"]:
                    doc_links["google_doc_url"] = \
                    document_results["documents_created"]["google_doc"].get(
                        "doc_url", "")
                if "jira_ticket" in document_results["documents_created"]:
                    doc_links["jira_ticket_url"] = \
                    document_results["documents_created"]["jira_ticket"].get(
                        "ticket_url", "")

            return {
                "document_results": document_results,
                "doc_links": doc_links,
                "messages": state["messages"] + [{"role": "system",
                                                  "content": "Document creation complete"}],
                "current_node": DOCUMENT_CREATION_NODE
            }
        except Exception as e:
            logger.error(f"Error in document creation node: {str(e)}")
            return {
                "error": f"Error in document creation node: {str(e)}",
                "current_node": ERROR_NODE,
                "messages": state["messages"] + [{"role": "system",
                                                  "content": f"Error during document creation: {str(e)}"}]
            }

    def _design_document_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Create technical design document."""
        logger.info("Executing design document node")

        try:
            design_document = self.design_agent.create_design_document(
                state["formatted_prd"],
                state["document_results"]
            )

            # Extract wiki link
            wiki_url = ""
            if "wiki_page" in design_document:
                wiki_url = design_document["wiki_page"].get("page_url", "")

            return {
                "design_document": design_document,
                "wiki_url": wiki_url,
                "messages": state["messages"] + [{"role": "system",
                                                  "content": "Design document creation complete"}],
                "current_node": DESIGN_DOCUMENT_NODE
            }
        except Exception as e:
            logger.error(f"Error in design document node: {str(e)}")
            return {
                "error": f"Error in design document node: {str(e)}",
                "current_node": ERROR_NODE,
                "messages": state["messages"] + [{"role": "system",
                                                  "content": f"Error during design document creation: {str(e)}"}]
            }

    def _complete_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Complete the workflow."""
        logger.info("Workflow complete")

        return {
            "messages": state["messages"] + [
                {"role": "system", "content": "Workflow complete"}],
            "current_node": COMPLETE_NODE
        }

    def _error_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Handle workflow errors."""
        error_message = state.get("error", "Unknown error occurred")
        logger.error(f"Workflow error: {error_message}")

        return {
            "messages": state["messages"] + [{"role": "system",
                                              "content": f"Workflow error: {error_message}"}],
            "current_node": ERROR_NODE
        }

    def execute(self, requirement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow with the given requirement data.

        Args:
            requirement_data: The requirement data to process

        Returns:
            The workflow results
        """
        logger.info("Starting requirement workflow execution")

        # Initialize the state
        initial_state = WorkflowState(
            requirement_data=requirement_data,
            validation_results={},
            formatted_prd={},
            document_results={},
            design_document={},
            messages=[],
            current_node="",
            error=None
        )

        # Compile the workflow
        app = self.workflow.compile()

        # Execute the workflow
        for state in app.stream(initial_state):
            # Log state transitions for debugging
            logger.debug(f"Workflow state: {state['current_node']}")

        # Get the final state
        final_state = state

        # Create a simplified result
        result = {
            "success": final_state["current_node"] == COMPLETE_NODE,
            "current_node": final_state["current_node"],
            "validation_results": final_state.get("validation_results", {}),
            "links": {
                "google_doc": final_state.get("doc_links", {}).get(
                    "google_doc_url", ""),
                "jira_ticket": final_state.get("doc_links", {}).get(
                    "jira_ticket_url", ""),
                "wiki_page": final_state.get("wiki_url", "")
            },
            "messages": final_state["messages"],
            "error": final_state.get("error")
        }

        logger.info(f"Workflow execution complete: {result['success']}")
        return result