from typing import Dict, List, Any
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from app.integrations.google_docs import GoogleDocsIntegration
from app.integrations.jira import JiraIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentAgent:
    """
    Document agent to create Google Docs and JIRA tickets.
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4-turbo-preview", 
                 temperature: float = 0.1,
                 google_docs_credentials: str = None,
                 jira_credentials: Dict[str, str] = None):
        """Initialize the document agent with specified LLM and integrations."""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        # Initialize integrations if credentials are provided
        self.google_docs = GoogleDocsIntegration(google_docs_credentials) if google_docs_credentials else None
        self.jira = JiraIntegration(**jira_credentials) if jira_credentials else None
        
        # Create the document generation prompt
        self.document_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are a document creation expert. Your task is to prepare content for a PRD document 
            and a JIRA ticket based on the formatted requirement information.
            
            For the PRD document:
            1. Create a well-structured document with proper headings and sections
            2. Format content professionally with clear formatting for readability
            3. Create properly formatted tables for definitions and mappings
            4. Include all requirement details in appropriate sections
            
            For the JIRA ticket:
            1. Create a concise summary that captures the requirement essence
            2. Provide a detailed description with key requirement information
            3. Include stakeholders and timeline information
            4. Add appropriate labels and metadata
            
            Output format:
            {
                "prd_document": {
                    "title": "PRD title",
                    "content": "Full PRD content with formatting"
                },
                "jira_ticket": {
                    "summary": "Ticket summary",
                    "description": "Ticket description",
                    "labels": ["label1", "label2"],
                    "due_date": "due date",
                    "priority": "Medium"
                }
            }
            """),
            HumanMessage(content="{input}"),
        ])
        
        # Create the parser
        self.output_parser = JsonOutputParser()
        
        # Create the chain
        self.document_chain = self.document_prompt | self.llm | self.output_parser
    
    def create_documents(self, formatted_prd: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Google Doc and JIRA ticket based on formatted PRD content.
        
        Args:
            formatted_prd: The formatted PRD content
            
        Returns:
            Document creation results as a dictionary
        """
        logger.info("Starting document creation")
        
        try:
            # Prepare input for LLM
            document_input = {
                "input": formatted_prd
            }
            
            # Generate document content
            document_content = self.document_chain.invoke(document_input)
            
            # Create documents using integrations
            results = {
                "document_content": document_content,
                "documents_created": {}
            }
            
            # Create Google Doc if integration is available
            if self.google_docs:
                try:
                    gdoc_result = self.google_docs.create_document(
                        title=document_content["prd_document"]["title"],
                        content=document_content["prd_document"]["content"]
                    )
                    results["documents_created"]["google_doc"] = gdoc_result
                except Exception as e:
                    logger.error(f"Error creating Google Doc: {str(e)}")
                    results["documents_created"]["google_doc"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Create JIRA ticket if integration is available
            if self.jira:
                try:
                    jira_result = self.jira.create_ticket(
                        project_key="DENG",
                        summary=document_content["jira_ticket"]["summary"],
                        description=document_content["jira_ticket"]["description"],
                        issue_type="Story",
                        custom_fields={
                            "labels": document_content["jira_ticket"]["labels"],
                            "duedate": document_content["jira_ticket"]["due_date"],
                            "priority": document_content["jira_ticket"]["priority"]
                        }
                    )
                    results["documents_created"]["jira_ticket"] = jira_result
                except Exception as e:
                    logger.error(f"Error creating JIRA ticket: {str(e)}")
                    results["documents_created"]["jira_ticket"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            logger.info("Document creation complete")
            return results
        
        except Exception as e:
            logger.error(f"Error during document creation: {str(e)}")
            return {
                "error": f"Error during document creation: {str(e)}",
                "documents_created": {}
            }