from typing import Dict, Any
import logging
from app.agents.orchestrator import RequirementWorkflow
from app.slack.forms import parse_form_submission

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize workflow
workflow = RequirementWorkflow()

def handle_requirement_form_submission(ack, body, client, view):
    """
    Handle the requirement form submission.
    
    Args:
        ack: Acknowledge function
        body: Request body
        client: Slack client
        view: View state
    """
    # Acknowledge the submission
    ack()
    
    # Get the user ID
    user_id = body["user"]["id"]
    
    try:
        # Parse the form data
        requirement_data = parse_form_submission(view)
        
        # Add metadata
        requirement_data["user_id"] = user_id
        requirement_data["team_id"] = body["team"]["id"]
        
        # Send acknowledgment message
        client.chat_postMessage(
            channel=user_id,
            text=":hourglass: Processing your requirement submission..."
        )
        
        # Process the requirement asynchronously
        # In a real implementation, this would be done in a background task
        process_requirement(client, user_id, requirement_data)
    
    except Exception as e:
        logger.error(f"Error processing requirement submission: {str(e)}")
        client.chat_postMessage(
            channel=user_id,
            text=f":x: Error processing your requirement: {str(e)}"
        )

def process_requirement(client, user_id, requirement_data):
    """
    Process the requirement using the workflow.
    
    Args:
        client: Slack client
        user_id: User ID to send messages to
        requirement_data: The parsed requirement data
    """
    try:
        # Execute the workflow
        result = workflow.execute(requirement_data)
        
        if result["success"]:
            # Success message with links
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":white_check_mark: *Your requirement has been processed successfully!*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Generated Documents:*"
                    }
                }
            ]
            
            # Add links to documents
            if result["links"]["google_doc"]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• <{result['links']['google_doc']}|PRD Document>"
                    }
                })
            
            if result["links"]["jira_ticket"]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• <{result['links']['jira_ticket']}|JIRA Ticket>"
                    }
                })
            
            if result["links"]["wiki_page"]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• <{result['links']['wiki_page']}|Technical Design Document>"
                    }
                })
            
            client.chat_postMessage(
                channel=user_id,
                text="Your requirement has been processed successfully!",
                blocks=blocks
            )
        else:
            # Error message
            error_message = result.get("error", "Unknown error")
            
            if "validation_results" in result and not result["validation_results"].get("is_valid", False):
                # Validation failed - show feedback
                feedback = result["validation_results"].get("feedback", "No specific feedback provided")
                missing_fields = result["validation_results"].get("missing_fields", [])
                
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":warning: *Your requirement needs more information:*"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": feedback
                        }
                    }
                ]
                
                if missing_fields:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Missing fields:* {', '.join(missing_fields)}"
                        }
                    })
                
                # Add examples if available
                examples = result["validation_results"].get("examples", [])
                if examples:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Examples:*"
                        }
                    })
                    for example in examples:
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"• {example}"
                            }
                        })