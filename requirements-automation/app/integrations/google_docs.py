from typing import Dict, Any, Optional
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GoogleDocsIntegration:
    """Integration with Google Docs API for document creation."""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the Google Docs integration.

        Args:
            credentials_path: Path to the service account credentials file
        """
        self.credentials = None
        self.service = None

        if credentials_path:
            try:
                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/documents']
                )
                self.service = build('docs', 'v1', credentials=self.credentials)
                logger.info("Google Docs integration initialized")
            except Exception as e:
                logger.error(
                    f"Error initializing Google Docs integration: {str(e)}")

    def create_document(self, title: str, content: str) -> Dict[str, Any]:
        """
        Create a new Google Doc with the provided content.

        Args:
            title: The document title
            content: The document content (can include markdown-like formatting)

        Returns:
            Document creation result with doc_id and doc_url
        """
        if not self.service:
            logger.error("Google Docs service not initialized")
            return {
                "success": False,
                "error": "Google Docs service not initialized"
            }

        try:
            # Create a new document
            document = self.service.documents().create(
                body={'title': title}).execute()
            document_id = document.get('documentId')

            # Prepare content for insertion (simplified for this example)
            # In a real implementation, this would parse the content and create appropriate
            # formatting requests based on markdown or other structured content

            # For this example, we'll just insert the content as plain text
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]

            # Execute the requests
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            logger.info(f"Created Google Doc with ID: {document_id}")

            return {
                "success": True,
                "doc_id": document_id,
                "doc_url": f"https://docs.google.com/document/d/{document_id}/edit"
            }

        except Exception as e:
            logger.error(f"Error creating Google Doc: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }