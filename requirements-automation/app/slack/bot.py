from typing import Dict, Any
import logging
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.agents.orchestrator import RequirementWorkflow
from app.slack.forms import get_requirement_form_blocks
from app.slack.interactive import handle_requirement_form_submission

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SlackBot:
    """Slack Bot for requirements automation."""
    
    def __init__(self):
        """Initialize the Slack bot."""
        # Initialize Slack app
        self.app = App(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
        )
        
        # Initialize workflow
        self.workflow = RequirementWorkflow(
            google_docs_credentials=os.environ.get("GOOGLE_DOCS_CREDENTIALS_PATH"),
            jira_credentials={
                "server": os.environ.get("JIRA_SERVER"),
                "username": os.environ.get("JIRA_USERNAME"),
                "api_token": os.environ.get("JIRA_API_TOKEN")
            },
            wiki_credentials={
                "url": os.environ.get("WIKI_URL"),
                "username": os.environ.get("WIKI_USERNAME"),
                "api_token": os.environ.get("WIKI_API_TOKEN")
            }
        )
        
        # Register command handlers
        self.app.command("/new-requirement", self.handle_new_requirement_command)
        
        # Register view submission handlers
        self.app.view("requirement_form", handle_requirement_form_submission)
    
    def handle_new_requirement_command(self, ack, command, client):
        """Handle the /new-requirement slash command."""
        # Acknowledge the command
        ack()
        
        try:
            # Open a modal with the requirement form
            client.views_open(
                trigger_id=command["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "requirement_form",
                    "title": {
                        "type": "plain_text",
                        "text": "New Requirement"
                    },
                    "submit": {
                        "type": "plain_text",
                        "text": "Submit"
                    },
                    "blocks": get_requirement_form_blocks()
                }
            )
        except Exception as e:
            logger.error(f"Error opening modal: {str(e)}")
            client.chat_postMessage(
                channel=command["channel_id"],
                text=f"Error opening requirement form: {str(e)}"
            )
    
    def start(self):
        """Start the Slack bot."""
        # Use Socket Mode if specified
        if os.environ.get("SLACK_APP_TOKEN"):
            handler = SocketModeHandler(self.app, os.environ["SLACK_APP_TOKEN"])
            handler.start()
        else:
            # Use HTTP mode
            self.app.start(port=int(os.environ.get("PORT", 3000)))